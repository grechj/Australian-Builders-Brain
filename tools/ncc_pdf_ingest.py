"""Convert the ABCB's NCC 2022 PDFs into OKF pages under brain/ncc/2022/.

Usage:
    python tools/ncc_pdf_ingest.py --pdf-dir ~/Downloads            # all four volumes
    python tools/ncc_pdf_ingest.py --pdf-dir ~/Downloads --only volume_two --check

Reads ncc2022-volume-one.pdf, ncc2022-volume-two.pdf, ncc2022-volume-three.pdf
and ncc2022-abcb-housing-provisions.pdf (the ABCB's base NCC 2022 PDFs,
1 May 2023). Writes the same layout as tools/ncc_ingest.py writes for 2025:
one page per Part with every clause under an anchored heading, state and
territory variations quoted under the clause they change, definitions, a
state_variations list and a clause index.

--check compares the clause codes found in the body with the volume's table
of contents and lists any that are missing.

Why PDFs: the ABCB's NCC 2022 XML download is an older, incomplete export
(see raw/ncc/README.md). The PDFs are the published text. They predate NCC
2022 Amendments 1 and 2; a full run then merges those from
tools/ncc2022_amendments.yaml (tools/apply_ncc_amendments.py).

Needs pdfplumber (pip install pdfplumber).
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parent.parent
VOLUMES = {
    "volume_one": ("ncc2022-volume-one.pdf", "Volume One", "Vol One"),
    "volume_two": ("ncc2022-volume-two.pdf", "Volume Two", "Vol Two"),
    "volume_three": ("ncc2022-volume-three.pdf", "Volume Three", "Vol Three"),
    "housing_provisions": ("ncc2022-abcb-housing-provisions.pdf", "Housing Provisions", "Housing Provisions"),
}
STATES = {"Australian Capital Territory": "ACT", "New South Wales": "NSW", "Northern Territory": "NT", "Queensland": "QLD",
          "South Australia": "SA", "Tasmania": "TAS", "Victoria": "VIC", "Western Australia": "WA"}
CODES = ("ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA")
ATTRIBUTION = ("[^abcb_ncc]: The National Construction Code 2022 was provided by the Australian Building Codes Board under the "
               "CC BY 4.0 licence. Converted to markdown from the ABCB's NCC 2022 PDFs (1 May 2023) by tools/ncc_pdf_ingest.py; "
               "figures not reproduced. Read with NCC 2022 Amendment 1 (from 1 May 2025) and Amendment 2 (from 29 July 2025). "
               "The authoritative text is at https://ncc.abcb.gov.au/editions/ncc-2022")
AMENDMENT_NOTE = ("> **NCC 2022 as published (1 May 2023).** For work under NCC 2022 it must be read with "
                  "Amendment 1 (from 1 May 2025) and Amendment 2 (from 29 July 2025), which change some clauses. "
                  "See [NCC editions](/ncc/editions.md).")

BARE_CODE = r"(?:[A-J]\d{1,2}[OFPVDG]\d{1,2}|S\d{1,2}C\d{1,2}[a-z]?|\d{1,2}\.\d{1,2}\.\d{1,2})"
CLAUSE_CODE = r"(?:(?:ACT|NSW|NT|QLD|SA|TAS|VIC|WA)\s+)?" + BARE_CODE
CLAUSE_HEAD = re.compile(rf"^({CLAUSE_CODE})\s+(.+)$")
PART_HEAD = re.compile(r"^(?:((?:ACT|NSW|NT|QLD|SA|TAS|VIC|WA)\s+)?Part\s+([A-J]\d{1,2}|\d{1,2}\.\d{1,2}))\s+(.+)$")
SPEC_HEAD = re.compile(r"^((?:ACT|NSW|NT|QLD|SA|TAS|VIC|WA)\s+)?Specification\s+(\d{1,2})\s+(.+)$")
SECTION_HEAD = re.compile(r"^Section\s+([A-J]|\d{1,2})\s+(.+)$")
SCHEDULE_HEAD = re.compile(r"^Schedule\s+(\d{1,2})\s+(.+)$")
LABEL = re.compile(r"^\((?:[a-z]{1,4}|[ivxlc]+|\d{1,2}|[A-Z]{1,2})\)$")
ARCHIVE = re.compile(r"^\[\d{4}:.*\]$")
VARMARK = re.compile(r"^((?:ACT|NSW|NT|QLD|SA|TAS|VIC|WA)\s+(?:" + BARE_CODE + r"|Part\s+\S+|Specification\s+\d+|Schedule\s+\d+)(?:\(\w+\))*\s*)+$")
SUBTOPICS = {"Objectives", "Functional Statements", "Performance Requirements", "Verification Methods",
             "Deemed-to-Satisfy Provisions", "Governing Requirements", "Introduction to this Part"}


def slug(text: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", text.lower().replace("&", "and"))).strip("_")


def bare(code: str) -> str:
    """'NSW H1D4' -> 'H1D4'."""
    return re.sub(r"^(?:ACT|NSW|NT|QLD|SA|TAS|VIC|WA)\s+", "", code).strip()


# --------------------------------------------------------------------------
# Lines out of the PDF
# --------------------------------------------------------------------------

class Line:
    __slots__ = ("page", "top", "x", "size", "bold", "text", "kind")

    def __init__(self, page, top, x, size, bold, text, kind="text"):
        self.page, self.top, self.x, self.size, self.bold, self.text, self.kind = page, top, x, size, bold, text, kind

    def __repr__(self):
        return f"<{self.kind} p{self.page} x{self.x:.0f} s{self.size:.0f} {self.text[:50]!r}>"


def _style(fontname: str) -> str:
    f = fontname.split("+")[-1]
    if "Italic" in f:
        return "i"
    if f.startswith("Arial-Bold"):
        return "b"
    return ""


def page_lines(page, pno: int) -> list[Line]:
    """Text lines (with *italic* and **bold** runs) plus table placeholders, in reading order."""
    tables = []
    try:
        for tb in page.find_tables():
            x0, top, x1, bottom = tb.bbox
            if bottom - top > 20 and x1 - x0 > 150:
                tables.append(tb)
    except Exception:
        tables = []
    boxes = [tb.bbox for tb in tables]

    def in_table(c):
        return any(b[0] - 1 <= c["x0"] <= b[2] + 1 and b[1] - 1 <= c["top"] <= b[3] + 1 for b in boxes)

    rows: dict[int, list] = defaultdict(list)
    for c in page.chars:
        if in_table(c):
            continue
        rows[round(c["top"])].append(c)
    # Merge rows whose tops are within 1.5 pt (labels sit 1 pt off their text).
    keys = sorted(rows)
    merged: list[list] = []
    last = None
    for k in keys:
        if last is not None and k - last <= 1:
            merged[-1].extend(rows[k])
        else:
            merged.append(list(rows[k]))
        last = k
    out: list[Line] = []
    for cs in merged:
        cs.sort(key=lambda c: c["x0"])
        visible = [c for c in cs if c["text"].strip()]
        if not visible:
            if cs and cs[0]["size"] < 5:
                out.append(Line(pno, cs[0]["top"], cs[0]["x0"], cs[0]["size"], False, "", "break"))
            continue
        # A row is one line: labels, codes and titles are joined with a space.
        segs = [visible]
        for seg in segs:
            text, style, prev = "", "", None
            for c in seg:
                st = _style(c["fontname"])
                gap = prev is not None and c["x0"] - prev["x1"] > c["size"] * 0.12
                if st != style:
                    if style == "i":
                        text = text.rstrip() + "*" + (" " if gap or text.endswith(" ") else "")
                    elif style == "b":
                        text = text.rstrip() + "**" + (" " if gap or text.endswith(" ") else "")
                    if gap and not text.endswith(" "):
                        text += " "
                    if st == "i":
                        text += "*"
                    elif st == "b":
                        text += "**"
                    style = st
                elif gap:
                    text += " "
                text += c["text"]
                prev = c
            if style == "i":
                text = text.rstrip() + "*"
            elif style == "b":
                text = text.rstrip() + "**"
            text = re.sub(r"\*\*?\s*\*\*?", lambda m: " " if m.group(0).count("*") % 2 == 0 and " " in m.group(0) else m.group(0), text)
            text = text.replace("**", "\x00").replace("* *", " ").replace("\x00", "**")
            text = re.sub(r"\s+", " ", text).strip()
            fonts = {c["fontname"].split("+")[-1] for c in seg}
            bold = any(("Bold" in f or "Semi" in f) and "Arial" not in f for f in fonts)
            out.append(Line(pno, seg[0]["top"], seg[0]["x0"], seg[0]["size"], bold, text))
    for tb in tables:
        out.append(Line(pno, tb.bbox[1], tb.bbox[0], 10, False, "", "table"))
        out[-1].text = tb.extract()
    out.sort(key=lambda l: (round(l.top), l.x))
    # Attach a lone label to the text beside it.
    fixed: list[Line] = []
    for ln in out:
        if fixed and ln.kind == "text" and LABEL.match(ln.text) and fixed[-1].kind == "text" \
                and abs(fixed[-1].top - ln.top) <= 2.5 and fixed[-1].x > ln.x:
            fixed[-1].text = f"{ln.text} {fixed[-1].text}"
            fixed[-1].x = ln.x
            continue
        if fixed and ln.kind == "text" and fixed[-1].kind == "text" and LABEL.match(fixed[-1].text) \
                and abs(fixed[-1].top - ln.top) <= 2.5 and ln.x > fixed[-1].x:
            fixed[-1].text = f"{fixed[-1].text} {ln.text}"
            continue
        fixed.append(ln)
    return fixed


def clean(lines: list[Line]) -> list[Line]:
    out = []
    for ln in lines:
        if ln.kind == "text":
            t = ln.text.strip("* ").strip()
            if ln.top < 50 or ln.top > 812:            # running header / footer
                continue
            if ARCHIVE.match(t) or not t:
                continue
            # Stray drawing labels ("m m", "A", "B"): too short to be text, and not a list label or a number.
            if len(t.replace(" ", "")) <= 3 and not LABEL.match(t) and not t.replace(".", "").isdigit() and t != "•":
                continue
            if t == "•":
                ln.kind = "bullet"
        out.append(ln)
    return out


# --------------------------------------------------------------------------
# Structure
# --------------------------------------------------------------------------

def classify(ln: Line) -> tuple[str, re.Match | None]:
    if ln.kind != "text":
        return ln.kind, None
    t = ln.text.strip("* ").strip()
    if ln.size >= 13.5:
        for name, pat in (("schedule", SCHEDULE_HEAD), ("section", SECTION_HEAD), ("part", PART_HEAD), ("spec", SPEC_HEAD)):
            m = pat.match(t)
            if m:
                return name, m
        return "bighead", None
    if ln.size >= 11.5 and ln.bold:
        for name, pat in (("part", PART_HEAD), ("spec", SPEC_HEAD), ("clause", CLAUSE_HEAD)):
            m = pat.match(t)
            if m:
                return name, m
        if t in SUBTOPICS:
            return "subtopic", None
        return "head", None
    if ln.bold and ln.size >= 9.5 and t in ("Explanatory Information", "Notes", "Table Notes", "Note", "Applications"):
        return "callout", None
    if ln.size < 9.6 and VARMARK.match(t.strip("* ")):
        return "varmark", None
    return "text", None


def level(x: float) -> int:
    if x < 45:
        return 0
    if x < 66:
        return 1
    if x < 88:
        return 2
    return 3


def render_table(rows: list) -> list[str]:
    rows = [[re.sub(r"\s+", " ", (c or "")).strip().replace("|", "\\|") for c in r] for r in rows if r]
    rows = [r for r in rows if any(r)]
    if not rows:
        return []
    width = max(len(r) for r in rows)
    notes = [r[0] for r in rows if r[0].startswith(("Table Notes", "Notes")) and not any(r[1:])]
    rows = [r for r in rows if not (r[0].startswith(("Table Notes", "Notes")) and not any(r[1:]))]
    rows = [r + [""] * (width - len(r)) for r in rows]
    if not rows:
        return [f"> {n}" for n in notes]
    out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width] + ["| " + " | ".join(r) + " |" for r in rows[1:]]
    for n in notes:
        out += ["", "> " + n]
    return out + [""]


class Clause:
    def __init__(self, code: str, title: str):
        self.code, self.title = code, title
        self.lines: list[str] = []


class Part:
    def __init__(self, kind: str, num: str, title: str, section: str, state: str | None = None):
        self.kind, self.num, self.title, self.section, self.state = kind, num, title, section, state
        self.intro: list[str] = []
        self.items: list = []          # ("subtopic", label) or Clause

    @property
    def label(self) -> str:
        base = "Specification" if self.kind == "spec" else "Part"
        return " ".join(x for x in (self.state, base, self.num) if x)

    @property
    def filename(self) -> str:
        return slug(f"{self.label} {self.title}").removeprefix("part_") + ".md"


class Writer:
    """Turns classified lines into markdown lines with list nesting."""

    def __init__(self):
        self.out: list[str] = []
        self.para: list[str] = []
        self.para_level = 0
        self.callout = False

    def flush(self):
        if self.para:
            text = " ".join(self.para).strip()
            text = re.sub(r"\s+", " ", text)
            if LABEL.match(text.split(" ")[0]) and self.para_level > 0:
                line = "  " * (self.para_level - 1) + "- " + text
            else:
                line = text
            self.out.append(("> " + line) if self.callout else line)
            if not LABEL.match(text.split(" ")[0]) or self.para_level == 0:
                self.out.append(">" if self.callout else "")
        self.para = []

    def text(self, ln: Line):
        lvl = level(ln.x)
        t = ln.text
        starts_item = bool(re.match(r"^\((?:[a-z]{1,4}|[ivxlc]+|\d{1,2}|[A-Z]{1,2})\)\s", t)) or ln.kind == "bullet_text"
        if starts_item or not self.para:
            self.flush()
            self.para_level = lvl if starts_item else lvl
        self.para.append(t)

    def block(self, lines: list[str]):
        self.flush()
        if self.out and self.out[-1] not in ("", ">"):
            self.out.append("")
        self.out.extend(lines)

    def end_callout(self):
        self.flush()
        if self.callout:
            self.callout = False
            self.out.append("")

    def start_callout(self, title: str):
        self.end_callout()
        self.callout = True
        if self.out and self.out[-1] != "":
            self.out.append("")
        self.out += [f"> **{title}**", ">"]


def parse_volume(path: Path, vol: str) -> dict:
    pdf = pdfplumber.open(str(path))
    toc_codes: set[str] = set()
    parts: list[Part] = []
    variations: list[dict] = []      # state schedule entries
    definitions: list[tuple[str, str]] = []
    referenced: list[str] = []
    section_title = ""
    mode = "front"                    # front | body | schedule_defs | schedule_refs | schedule_state | schedule_other
    state = None
    part: Part | None = None
    clause: Clause | None = None
    writer = Writer()
    pending_bullet = False
    var_entry: dict | None = None
    figure_re = re.compile(r"^(Figure\s+[\w.]+?):?\s+([A-Z(].*)$")
    table_caption = re.compile(r"^(Table\s+[\w.]+?):?\s+([A-Z(].*)$")
    in_figure = False
    defs_term: list = []

    def close_clause():
        nonlocal clause
        if clause is not None:
            writer.end_callout()
            writer.flush()
            clause.lines = writer.out
            writer.out = []
        clause = None

    def close_var():
        nonlocal var_entry
        if var_entry is not None:
            writer.end_callout()
            writer.flush()
            var_entry["lines"] = writer.out
            writer.out = []
            variations.append(var_entry)
        var_entry = None

    def switch_schedule(title: str):
        nonlocal mode, state, part, var_entry
        close_clause(); close_var()
        part = None
        if title in STATES:
            mode, state = "schedule_state", STATES[title]
        elif state and title.startswith(("Definitions", "Referenced")):
            # A state's own Schedule 1 or 2 inside its schedule: keep it with that state.
            mode = "schedule_state"
            var_entry = {"state": state, "code": "", "target": "", "title": f"{state} {title}", "instruction": f"{state} {title.lower()} (additions to Schedule {'1' if title.startswith('Def') else '2'})", "lines": []}
        elif title.startswith("Definitions"):
            mode, state = "schedule_defs", None
        elif title.startswith("Referenced"):
            mode, state = "schedule_refs", None
        else:
            mode, state = "schedule_other", None

    for pno, page in enumerate(pdf.pages):
        lines = clean(page_lines(page, pno))
        # Contents pages list clause codes in small regular type; body headings are 12 pt bold.
        toc_hits = [l for l in lines if l.kind == "text" and l.size < 11 and not l.bold
                    and CLAUSE_HEAD.match(l.text.strip("* ")) and len(l.text) < 120 and l.x > 100]
        if len(toc_hits) >= 5:
            for l in toc_hits:
                toc_codes.add(bare(CLAUSE_HEAD.match(l.text.strip("* ")).group(1)))
            for l in lines:                       # a schedule can start on a contents page
                k, mm = classify(l)
                if k == "schedule":
                    switch_schedule(mm.group(2).strip())
            continue
        for ln in lines:
            kind, m = classify(ln)
            if kind == "schedule":
                switch_schedule(m.group(2).strip())
                continue
            if kind == "section" and mode in ("front", "body"):
                close_clause()
                mode = "body"
                section_title = m.group(2).strip()
                continue
            if mode == "front":
                if kind in ("part", "spec"):
                    mode = "body"
                else:
                    continue
            if mode == "schedule_defs":
                if ln.kind != "text":
                    continue
                t = ln.text
                if kind in ("bighead", "head", "subtopic") or ln.size > 11:
                    continue
                mt = re.match(r"^\*\*(.+?)\*\*\s*(.*)$", t)
                if mt and ln.x < 40:
                    definitions.append([mt.group(1).strip(), mt.group(2).strip()])
                elif definitions and ln.kind == "text":
                    definitions[-1][1] += " " + t
                continue
            if mode == "schedule_refs":
                if ln.kind == "table":
                    referenced.extend(render_table(ln.text))
                elif ln.kind == "text" and kind == "text":
                    referenced.append(ln.text)
                continue
            if mode == "schedule_other":
                continue
            if mode == "schedule_state":
                if kind in ("part", "spec", "section", "bighead"):
                    close_var()
                    if kind in ("part", "spec") and m and (m.group(1) or "").strip():
                        variations.append({"state": state, "code": f"{state} Part {m.group(2)}", "target": f"Part {m.group(2)}",
                                           "title": m.group(3).strip(), "instruction": f"{state} replaces or adds Part {m.group(2)} {m.group(3).strip()}", "lines": []})
                    continue
                if kind == "clause":
                    code = m.group(1)
                    if var_entry is not None and not var_entry.get("lines_started") and not var_entry["code"] and var_entry["instruction"]:
                        var_entry.update(code=code, title=m.group(2).strip(), target=var_entry["target"] or bare(code))
                        continue
                    close_var()
                    var_entry = {"state": state, "code": code, "target": bare(code), "title": m.group(2).strip(), "instruction": "", "lines": []}
                    continue
                if ln.kind == "text" and re.match(r"^\*?(Delete|Insert|Replace|Add|Amend|Vary)\b", ln.text) and ln.text.rstrip("*").rstrip().endswith((":", ".")) and len(ln.text) < 260:
                    instr = ln.text.strip("* ")
                    target = re.search("(" + BARE_CODE + ")", instr)
                    if var_entry is None or var_entry.get("lines_started"):
                        close_var()
                        var_entry = {"state": state, "code": "", "target": target.group(1) if target else "", "title": "", "instruction": instr, "lines": []}
                    else:
                        var_entry["instruction"] = (var_entry["instruction"] + " " + instr).strip()
                        if not var_entry["target"] and target:
                            var_entry["target"] = target.group(1)
                    continue
                if var_entry is None:
                    continue
                var_entry["lines_started"] = True
            # ---- body (and the text of a state variation) ----
            if kind in ("part", "spec") and mode == "body":
                close_clause()
                st = (m.group(1) or "").strip() or None
                part = Part(kind, m.group(2), m.group(3).strip(), section_title, st)
                parts.append(part)
                continue
            if kind == "clause" and mode == "body":
                close_clause()
                if part is None:
                    part = Part("part", "", section_title or "Front matter", section_title)
                    parts.append(part)
                clause = Clause(m.group(1), m.group(2).strip())
                part.items.append(clause)
                continue
            if kind == "subtopic" and mode == "body":
                close_clause()
                if part is not None and ln.text.strip() != "Introduction to this Part":
                    part.items.append(("subtopic", ln.text.strip("* ")))
                continue
            if kind in ("clause", "part", "spec", "subtopic", "callout", "head", "bighead", "varmark", "section") or ln.kind in ("table", "break"):
                in_figure = False
            if kind == "varmark":
                writer.end_callout()
                writer.flush()
                writer.out += [f"> *{ln.text.strip('* ')} applies here: see the state variation below.*", ""]
                continue
            if kind == "callout":
                writer.start_callout(ln.text.strip("* ").replace("Information", "information"))
                continue
            if ln.kind == "break":
                writer.end_callout()
                continue
            if ln.kind == "table":
                writer.block(render_table(ln.text))
                continue
            if ln.kind == "bullet":
                pending_bullet = True
                continue
            if kind in ("head", "bighead"):
                t = ln.text.strip("* ")
                fm = figure_re.match(t)
                tm = table_caption.match(t)
                if fm:
                    writer.block([f"*{fm.group(1)}: {fm.group(2)}* (figure not reproduced; see the PDF)", ""])
                    in_figure = True
                elif tm:
                    writer.block([f"**{tm.group(1)}: {tm.group(2)}**", ""])
                else:
                    writer.block([f"**{t}**", ""])
                continue
            t = ln.text
            bare_t = t.strip("* ")
            fm = figure_re.match(bare_t)
            tm = table_caption.match(bare_t)
            if fm and len(bare_t) < 160 and not bare_t.endswith("."):
                writer.block([f"*{fm.group(1)}: {fm.group(2)}* (figure not reproduced; see the PDF)", ""])
                in_figure = True
                continue
            if tm and len(bare_t) < 160 and not bare_t.endswith("."):
                writer.block([f"**{tm.group(1)}: {tm.group(2)}**", ""])
                in_figure = False
                continue
            if in_figure:
                # Labels drawn inside a figure: short fragments, not sentences or numbered provisions.
                if not re.match(r"^\((?:[a-z]{1,4}|[ivxlc]+|\d{1,2})\)\s", bare_t) and (len(bare_t) < 70 or not bare_t.rstrip("*").endswith((".", ";", ":", "—", "-"))):
                    continue
                in_figure = False
            if pending_bullet:
                ln.text = "- " + t
                writer.flush()
                writer.para_level = 0
                writer.para = [ln.text]
                pending_bullet = False
                writer.flush()
                if writer.out and writer.out[-1] in ("", ">"):
                    writer.out.pop()
                continue
            if part is not None and clause is None and mode == "body":
                part.intro.append(t)
                continue
            writer.text(ln)
        # page loop
    close_clause(); close_var()
    return {"parts": parts, "variations": variations, "definitions": definitions, "referenced": referenced, "toc": toc_codes}


# --------------------------------------------------------------------------
# Writing pages
# --------------------------------------------------------------------------

def anchor(code: str) -> str:
    return slug(code) or "clause"


def front(meta: dict) -> str:
    out = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            out.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        elif k in ("sources", "generated"):
            out.append(v if k == "sources" else f"{k}: {v}")
        elif isinstance(v, str):
            out.append(f'{k}: "' + v.replace('\\', '\\\\').replace('"', '\\"') + '"')
        else:
            out.append(f"{k}: {v}")
    return "\n".join(out + ["---", ""]) + "\n"


SOURCES = """sources:
  - id: abcb_ncc
    resource: https://ncc.abcb.gov.au/editions/ncc-2022
    title: NCC 2022 (1 May 2023), Australian Building Codes Board (CC BY 4.0)
    author: org:abcb"""


def write_volume(vol: str, data: dict, out: Path, now: str) -> dict:
    _, title, short = VOLUMES[vol]
    vdir = out / vol
    if vdir.exists():
        shutil.rmtree(vdir)
    vdir.mkdir(parents=True)
    gen = f"{{ by: process:ncc_pdf_ingest/0.1, at: {now} }}"
    by_target: dict[str, list[dict]] = defaultdict(list)
    for v in data["variations"]:
        if v["target"]:
            by_target[v["target"]].append(v)
    attached: set[int] = set()
    index_rows = []
    stats = {"parts": 0, "clauses": 0}
    for order, part in enumerate(data["parts"], 1):
        if not part.items and not part.intro:
            continue
        page = f"/ncc/2022/{vol}/{part.filename}"
        body = [AMENDMENT_NOTE, ""]
        if part.intro:
            body += [re.sub(r"\s+", " ", " ".join(part.intro)), ""]
        part_vars = by_target.get(f"Part {part.num}", [])
        codes = []
        for item in part.items:
            if isinstance(item, tuple):
                body += [f"## {item[1]}", ""]
                continue
            code = item.code
            codes.append(code)
            body += [f'<a id="{anchor(code)}"></a>', "", f"### {code} {item.title}", ""]
            body += item.lines
            for v in by_target.get(bare(code), []):
                attached.add(id(v))
                head = f"> **{v['state']} variation**: {v['instruction'] or (v['state'] + ' ' + bare(code) + ' ' + v['title'])}"
                body += ["", head, ">"] + [("> " + l if l not in ("", ">") else ">") for l in v["lines"] if l != ">"] + [""]
            index_rows.append((code, f"{part.label} {part.title}", page))
        if not codes and not part.intro:
            continue
        states = sorted({v["state"] for c in codes for v in by_target.get(bare(c), [])})
        meta = {"type": "Code Reference", "title": f"NCC 2022 {short}, {part.label} {part.title}",
                "description": (re.split(r"(?<=\.)\s", " ".join(part.intro))[0] if part.intro else f"NCC 2022 {short} {part.label} {part.title}.")[:240],
                "tags": ["ncc", "ncc_2022", vol] + ([slug(part.section)] if part.section else []),
                "status": "stable", "resource": "https://ncc.abcb.gov.au/editions/ncc-2022", "edition": "NCC 2022",
                "volume": title, "part": part.num, "order": order, "clauses": codes, "state_variations": states,
                "sources": SOURCES, "generated": gen}
        intro = [f"From **NCC 2022 {title}**{', ' + part.section if part.section else ''}.[^abcb_ncc] Defined terms are in *italics*; see [definitions](definitions.md).", ""]
        text = front(meta) + "\n".join(intro + body + ["", ATTRIBUTION, ""])
        (vdir / part.filename).write_text(re.sub(r"\n{3,}", "\n\n", text))
        stats["parts"] += 1
        stats["clauses"] += len(codes)
    # Clauses that exist only in a state's schedule (a state-only Part, or a
    # clause the state adds) get a state-only page, like the 2025 pages.
    part_titles = {(v["state"], v["target"].split(" ", 1)[1]): v["title"] for v in data["variations"] if v["target"].startswith("Part ")}
    groups: dict[tuple, list] = defaultdict(list)
    for v in data["variations"]:
        if id(v) in attached or not v["code"] or v["target"].startswith("Part "):
            continue
        num = re.match(r"([A-J]\d{1,2}|S\d{1,2}|\d{1,2}\.\d{1,2})", v["target"])
        if num:
            groups[(v["state"], num.group(1).rstrip("C") if num.group(1).startswith("S") else num.group(1))].append(v)
    for (st, num), entries in sorted(groups.items()):
        ptitle = part_titles.get((st, num), "additions")
        fname = slug(f"{st} Part {num} {ptitle}") + ".md"
        page = f"/ncc/2022/{vol}/{fname}"
        body = [AMENDMENT_NOTE, "", f"Clauses that apply only in {st}, from the {st} schedule of **NCC 2022 {title}**.[^abcb_ncc]", ""]
        codes = []
        for v in entries:
            attached.add(id(v))
            code = v["code"] or f"{st} {v['target']}"
            codes.append(code)
            body += [f'<a id="{anchor(code)}"></a>', "", f"### {code} {v['title']}".rstrip(), ""]
            if v["instruction"]:
                body += [f"*{v['instruction']}*", ""]
            body += v["lines"]
            index_rows.append((code, f"{st} Part {num} {ptitle}", page))
        meta = {"type": "Code Reference", "title": f"NCC 2022 {short}, {st} Part {num} {ptitle}",
                "description": f"Clauses that apply only in {st}: NCC 2022 {title} {st} Part {num} {ptitle}.",
                "tags": ["ncc", "ncc_2022", vol, "states"], "status": "stable", "resource": "https://ncc.abcb.gov.au/editions/ncc-2022",
                "edition": "NCC 2022", "volume": title, "part": num, "order": 800, "clauses": codes, "state_variations": [st],
                "sources": SOURCES, "generated": gen}
        (vdir / fname).write_text(re.sub(r"\n{3,}", "\n\n", front(meta) + "\n".join(body + ["", ATTRIBUTION, ""])))
        stats["parts"] += 1
        stats["clauses"] += len(codes)

    # Definitions
    if data["definitions"]:
        lines = []
        for term, d in data["definitions"]:
            lines += [f'<a id="{slug(term)}"></a>', "", f"### {term}", "", re.sub(r"\s+", " ", d).strip(), ""]
        meta = {"type": "Code Reference", "title": f"NCC 2022 {short}, Schedule 1 Definitions",
                "description": f"Defined terms used in NCC 2022 {title} (the words shown in italics).",
                "tags": ["ncc", "ncc_2022", vol], "status": "stable", "resource": "https://ncc.abcb.gov.au/editions/ncc-2022",
                "edition": "NCC 2022", "volume": title, "order": 900, "sources": SOURCES, "generated": gen}
        (vdir / "definitions.md").write_text(front(meta) + f"From **NCC 2022 {title}**.[^abcb_ncc]\n\n" + "\n".join(lines) + "\n" + ATTRIBUTION + "\n")
    if data["referenced"]:
        meta = {"type": "Code Reference", "title": f"NCC 2022 {short}, Schedule 2 Referenced documents",
                "description": f"Standards and documents NCC 2022 {title} calls up.", "tags": ["ncc", "ncc_2022", vol],
                "status": "stable", "resource": "https://ncc.abcb.gov.au/editions/ncc-2022", "edition": "NCC 2022",
                "volume": title, "order": 901, "sources": SOURCES, "generated": gen}
        (vdir / "referenced_documents.md").write_text(front(meta) + f"From **NCC 2022 {title}**.[^abcb_ncc]\n\n" + "\n".join(data["referenced"]) + "\n\n" + ATTRIBUTION + "\n")
    # State variations list (every entry, attached or not)
    rows = []
    for v in data["variations"]:
        target = v["target"] or "(see the state schedule)"
        page = next((r[2] for r in index_rows if bare(r[0]) == v["target"]), "")
        link = f"[{target}]({page}#{anchor(v['target'])})" if page else target
        what = (v["instruction"] or f"{v['state']} {v['code']} {v['title']}").replace("|", "\\|")[:160]
        rows.append(f"| {v['state']} | {what} | {link} |")
    if rows:
        meta = {"type": "Code Reference", "title": f"NCC 2022 {short}, state and territory variations",
                "description": f"Every state and territory variation in NCC 2022 {title}, linked to the clause it changes.",
                "tags": ["ncc", "ncc_2022", vol, "states"], "status": "stable", "resource": "https://ncc.abcb.gov.au/editions/ncc-2022",
                "edition": "NCC 2022", "volume": title, "order": 902, "sources": SOURCES, "generated": gen}
        body = [AMENDMENT_NOTE, "", f"From the state and territory schedules of **NCC 2022 {title}**.[^abcb_ncc]", "",
                "| State | Variation | Clause or Part |", "|---|---|---|"] + rows
        (vdir / "state_variations.md").write_text(front(meta) + "\n".join(body) + "\n\n" + ATTRIBUTION + "\n")
    stats["variations"] = len(data["variations"])
    stats["variations_attached"] = len(attached)
    stats["definitions"] = len(data["definitions"])
    stats["index"] = index_rows
    return stats


def main() -> None:
    sys.path.insert(0, str(Path(__file__).parent))
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--pdf-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, default=ROOT / "brain" / "ncc" / "2022")
    parser.add_argument("--only", choices=list(VOLUMES))
    parser.add_argument("--check", action="store_true", help="report clause codes in the contents but not found in the body")
    args = parser.parse_args()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    all_index = []
    for vol, (fname, title, short) in VOLUMES.items():
        if args.only and vol != args.only:
            continue
        path = args.pdf_dir.expanduser() / fname
        if not path.exists():
            print(f"skipping {vol}: {path} not found")
            continue
        data = parse_volume(path, vol)
        stats = write_volume(vol, data, args.out, now)
        found = {bare(c) for c, _, _ in stats["index"]}
        missing = sorted(data["toc"] - found)
        print(f"{title}: {stats['parts']} parts, {stats['clauses']} clauses, {stats['variations']} state variation entries "
              f"({stats['variations_attached']} attached to a clause), {stats['definitions']} definitions; "
              f"contents lists {len(data['toc'])} codes, {len(missing)} not found in the body")
        if args.check and missing:
            print("  missing:", ", ".join(missing[:60]) + (" ..." if len(missing) > 60 else ""))
        all_index += [(title, *r) for r in stats["index"]]
    if not args.only:
        meta = {"type": "Reference", "title": "NCC 2022 clause index",
                "description": "Every NCC 2022 clause code with its Part and page, across all volumes.",
                "tags": ["ncc", "ncc_2022", "index"], "status": "stable", "order": 0, "sources": SOURCES,
                "generated": f"{{ by: process:ncc_pdf_ingest/0.1, at: {now} }}"}
        lines = [AMENDMENT_NOTE, "", "Look up a clause code here, then open its page.[^abcb_ncc]", "",
                 "| Clause | Volume | Part | Page |", "|---|---|---|---|"]
        lines += [f"| {code} | {title} | {part} | [open]({page}#{anchor(code)}) |" for title, code, part, page in all_index]
        (args.out / "clause_index.md").write_text(front(meta) + "\n".join(lines) + "\n\n" + ATTRIBUTION + "\n")
        # Merge Amendments 1 and 2 (tools/ncc2022_amendments.yaml).
        import apply_ncc_amendments
        apply_ncc_amendments.main()


if __name__ == "__main__":
    main()

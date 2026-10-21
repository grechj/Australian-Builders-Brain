"""Convert the ABCB's NCC XML datasets into OKF pages under brain/ncc/<edition>/.

Usage:
    python tools/ncc_ingest.py                      # reads raw/ncc/ncc-2025-*/contents.xml
    python tools/ncc_ingest.py --edition 2025 --raw raw/ncc --out brain/ncc/2025

Download the zips from data.gov.au (see raw/ncc/README.md) and unzip each
into its own folder under raw/ncc first.

Output, per volume:
    <volume>/<part>.md            one page per Part, every clause under an anchored heading
    <volume>/definitions.md       Schedule 1 defined terms
    <volume>/referenced_documents.md
    <volume>/state_variations.md  every state and territory variation, linked to its clause
and for the edition:
    clause_index.md               every clause code, its title and page

The text is the ABCB's, unchanged apart from formatting (CC BY 4.0).
Defined terms appear in *italics*, as in the printed NCC. Figures are not
reproduced; each is listed by its title so the reader can find it on
ncc.abcb.gov.au.
"""

from __future__ import annotations

import argparse
import re
import shutil
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOOL = "process:ncc_ingest"

VOLUMES = {
    "vol1": ("volume_one", "Volume One", "Class 2 to 9 buildings: apartments, commercial, industrial and public buildings"),
    "vol2": ("volume_two", "Volume Two", "Class 1 and 10 buildings: houses, townhouses, garages, sheds, pools"),
    "vol3": ("volume_three", "Volume Three", "Plumbing and drainage for all classes of building"),
    "housing": ("housing_provisions", "Housing Provisions", "ABCB Housing Provisions Standard: deemed-to-satisfy solutions for Class 1 and 10 buildings"),
    "livable": ("livable_housing_design", "Livable Housing Design", "ABCB Livable Housing Design Standard"),
}
STATES = ["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"]
SUBTOPIC_LABELS = {
    "governance": "Governing requirements",
    "objective": "Objectives",
    "functional": "Functional Statements",
    "performance": "Performance Requirements",
    "verification": "Verification Methods",
    "dts": "Deemed-to-Satisfy Provisions",
    "explanatory": "Explanatory information",
}
VARIATION_WORDS = {"REPLACE": "replaces", "ADD": "adds", "DELETE": "deletes", "INSERT": "adds"}


def tag(e: ET.Element) -> str:
    return e.tag.split("}")[-1]


def slug(text: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", text.lower())).strip("_")


def anchor(code: str) -> str:
    return slug(code) or "clause"


def oneline(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def yaml_str(text: str) -> str:
    return '"' + text.replace("\\", "\\\\").replace('"', '\\"') + '"'


# --------------------------------------------------------------------------
# Pass 1: where does every id live? (so links can point at the right page)
# --------------------------------------------------------------------------

@dataclass
class Target:
    page: str          # bundle-relative path, e.g. /ncc/2025/volume_two/h2_damp_and_weatherproofing.md
    anchor: str = ""
    label: str = ""


@dataclass
class Volume:
    pub_id: str
    root: ET.Element
    folder: str
    title: str
    blurb: str
    parts: list = field(default_factory=list)   # (part element, filename, order)


def part_num(part: ET.Element) -> str:
    return re.sub(r"^Part\s+", "", part.get("num", "")).strip()


def part_title(part: ET.Element) -> str:
    title = oneline("".join(part.find("title").itertext())) if part.find("title") is not None else ""
    return "(removed)" if re.fullmatch(r"[*\s]+", title or "x") else title


def part_label(part: ET.Element) -> str:
    """'Part H2', 'Specification 42' or 'SA Part H10' (a Part only one state has)."""
    kind = "Specification" if tag(part) == "specification" else "Part"
    state = part.get("state") if part.get("state") in STATES else ""
    return " ".join(x for x in (state, kind, part_num(part)) if x)


def part_filename(part: ET.Element) -> str:
    return slug(f"{part_label(part)} {part_title(part)}").removeprefix("part_") + ".md"


def build_targets(volumes: list[Volume], base: str) -> dict[str, Target]:
    targets: dict[str, Target] = {}
    for vol in volumes:
        vbase = f"{base}/{vol.folder}"
        order = 0
        for section in vol.root.iter():
            if tag(section) != "ncc-section":
                continue
            stype = section.get("type")
            stitle = oneline(section.findtext("title") or "")
            if stype == "schedule" and stitle == "Definitions":
                page = f"{vbase}/definitions.md"
                for g in section.iter():
                    if tag(g) in ("glossentry", "glossentry-variation") and g.get("id"):
                        term = oneline("".join(g.find("glossterm").itertext())) if g.find("glossterm") is not None else ""
                        targets[g.get("id")] = Target(page, slug(term), term)
                continue
            if stype == "schedule" and stitle == "Referenced documents":
                targets[section.get("id")] = Target(f"{vbase}/referenced_documents.md")
                continue
            for part in section:
                if tag(part) not in ("part", "specification"):
                    continue
                order += 1
                fname = part_filename(part)
                vol.parts.append((part, fname, order, stitle))
                page = f"{vbase}/{fname}"
                targets[part.get("id")] = Target(page, "", part_label(part))
                for e in part.iter():
                    t = tag(e)
                    if t in ("clause", "clause-variation", "standard-clause"):
                        code = oneline(e.findtext("sptc") or e.get("sptc") or "")
                        if e.get("id"):
                            targets[e.get("id")] = Target(page, anchor(code), code)
                        for sub in e.iter():
                            if tag(sub) in ("subclause", "subclause-variation") and sub.get("id"):
                                targets[sub.get("id")] = Target(page, anchor(code), code)
                    elif t in ("table-reference", "image-reference", "table-reference-variation",
                               "image-reference-variation", "part", "part-variation") and e.get("id"):
                        kind = "table" if "table" in t else "figure" if "image" in t else "part"
                        label = oneline("".join(e.find("title").itertext())) if e.find("title") is not None else ""
                        targets.setdefault(e.get("id"), Target(page, slug(f"{kind} {e.get('id')[-8:]}"), label))
    return targets


# --------------------------------------------------------------------------
# Pass 2: render XML to markdown
# --------------------------------------------------------------------------

def roman(n: int) -> str:
    vals = [(10, "x"), (9, "ix"), (5, "v"), (4, "iv"), (1, "i")]
    out = ""
    for v, s in vals:
        while n >= v:
            out += s
            n -= v
    return out


def list_label(cls: str, i: int) -> str:
    if cls == "alpha":
        return f"({chr(96 + i)})" if i <= 26 else f"({i})"
    if cls == "roman":
        return f"({roman(i)})"
    if cls in ("upper-alpha", "alpha-upper"):
        return f"({chr(64 + i)})"
    if cls == "bullet":
        return "-"
    return f"({i})"


class Renderer:
    def __init__(self, targets: dict[str, Target], page: str):
        self.targets = targets
        self.page = page
        self.figures = 0

    # ---- inline ----
    def inline(self, e: ET.Element) -> str:
        out = [e.text or ""]
        for ch in e:
            out.append(self.inline_el(ch))
            out.append(ch.tail or "")
        return "".join(out)

    def inline_el(self, e: ET.Element) -> str:
        out = self._inline_el(e)
        # Keep whitespace the XML puts inside a tag ("<a>pool </a>drainage").
        text = self.inline(e)
        if out and text[:1].isspace() and not out[:1].isspace():
            out = " " + out
        if out and text[-1:].isspace() and not out[-1:].isspace():
            out += " "
        return out

    def _inline_el(self, e: ET.Element) -> str:
        t = tag(e)
        text = self.inline(e)
        if t == "a":
            kind = e.get("type")
            if kind in ("abcb-glossentry", "glossterm"):
                return f"*{oneline(text)}*" if oneline(text) else ""
            ref = self.targets.get((e.get("href") or "").lstrip("#"))
            if ref and oneline(text):
                link = ref.page if ref.page != self.page else ""
                return f"[{oneline(text)}]({link}{'#' + ref.anchor if ref.anchor else ''})"
            return text
        if t in ("em", "i"):
            return f"*{oneline(text)}*" if oneline(text) else ""
        if t == "strong":
            return f"**{oneline(text)}**" if oneline(text) else ""
        if t == "sup":
            return f"<sup>{text}</sup>"
        if t == "sub":
            return f"<sub>{text}</sub>"
        if t in ("equation-inline", "mathML", "math", "semantics"):
            return self.math(e)
        if t == "annotation" or t == "img":
            return ""
        if t in ("ol", "ul", "table", "table-reference", "image-reference"):
            return "\n" + "\n".join(self.block(e, 0)) + "\n"
        return text

    def math(self, e: ET.Element) -> str:
        parts = []
        for m in e.iter():
            if tag(m) == "annotation":
                continue
            if tag(m) in ("mi", "mn", "mo", "mtext") and m.text:
                parts.append(m.text.strip())
        return "".join(parts)

    # ---- blocks ----
    def block(self, e: ET.Element, depth: int) -> list[str]:
        """Render a block element as markdown lines."""
        t = tag(e)
        pad = "  " * depth
        if t in ("content", "intro-part", "glossdef", "desc-note"):
            lines: list[str] = []
            pending_num = ""
            for ch in e:
                if tag(ch) == "num":
                    pending_num = oneline(ch.text or "")
                    continue
                sub = self.block(ch, depth)
                if pending_num and sub:
                    sub[0] = sub[0].replace(pad, pad + pending_num + " ", 1) if sub[0].startswith(pad) else pending_num + " " + sub[0]
                    pending_num = ""
                lines += sub
            return lines
        if t == "p":
            text = oneline(self.inline(e))
            return [pad + text, ""] if text else []
        if t in ("ol", "ul"):
            cls = e.get("class") or ("bullet" if t == "ul" else "numeric")
            lines = []
            i = 0
            for li in e:
                if tag(li) != "li":
                    continue
                i += 1
                label = list_label(cls, i)
                head = [li.text or ""]
                nested = []
                for ch in li:
                    if tag(ch) in ("ol", "ul", "table-reference", "image-reference", "p"):
                        nested.append(ch)
                    else:
                        head.append(self.inline_el(ch))
                    head.append(ch.tail or "")
                marker = "-" if label == "-" else f"- {label}"
                lines.append(f"{pad}{marker} {oneline(''.join(head))}".rstrip())
                for ch in nested:
                    lines += [x for x in self.block(ch, depth + 1) if x]
            return lines + [""]
        if t in ("table-reference", "table-reference-variation"):
            return self.table_ref(e, depth)
        if t in ("image-reference", "image-reference-variation"):
            title = oneline("".join(e.find("title").itertext())) if e.find("title") is not None else ""
            ref = self.targets.get(e.get("id", ""))
            anchor_html = f'<a id="{ref.anchor}"></a>' if ref and ref.anchor else ""
            self.figures += 1
            lines = [f"{pad}{anchor_html}*Figure{': ' + title if title else ''}* (not reproduced here, see the figure on ncc.abcb.gov.au)", ""]
            note = e.find("desc-note")
            if note is not None:
                lines += [pad + "> " + x if x else pad + ">" for x in self.block(note, 0)]
                lines.append("")
            return lines
        if t == "callout":
            kind = (e.get("callout-type") or "note").replace("-", " ").capitalize()
            title = e.find("title")
            head = f"**{kind}{': ' + oneline(''.join(title.itertext())) if title is not None and oneline(''.join(title.itertext())) else ''}**"
            body = []
            for ch in e:
                if tag(ch) != "title":
                    body += self.block(ch, 0)
            return [pad + "> " + head, pad + ">"] + [pad + ("> " + x if x else ">") for x in body] + [""]
        if t in ("equation-block",):
            return [pad + "`" + self.math(e) + "`", ""]
        if t in ("title", "sptc", "num", "img", "colgroup", "col"):
            return []
        # Unknown container: render its children, or its text.
        kids = list(e)
        if kids:
            out = []
            for ch in kids:
                out += self.block(ch, depth)
            return out
        text = oneline(e.text or "")
        return [pad + text, ""] if text else []

    def table_ref(self, e: ET.Element, depth: int) -> list[str]:
        pad = "  " * depth
        title = oneline("".join(e.find("title").itertext())) if e.find("title") is not None else ""
        ref = self.targets.get(e.get("id", ""))
        anchor_html = f'<a id="{ref.anchor}"></a>' if ref and ref.anchor else ""
        num = e.get("num") or ""
        lines = [f"{pad}{anchor_html}**Table{' ' + num if num else ''}{': ' + title if title else ''}**", ""]
        table = next((x for x in e.iter() if tag(x) == "table"), None)
        if table is not None:
            lines += [pad + x for x in self.table(table)]
            lines.append("")
        note = e.find("desc-note")
        if note is not None:
            lines += [pad + "> " + x if x else pad + ">" for x in self.block(note, 0)]
            lines.append("")
        return lines

    def table(self, table: ET.Element) -> list[str]:
        rows: list[list[str]] = []
        header_rows = 0
        spans: dict[int, tuple[int, str]] = {}   # column -> (rows left, text) for rowspan
        for section in table:
            st = tag(section)
            if st not in ("thead", "tbody", "tr"):
                continue
            trs = [section] if st == "tr" else [x for x in section if tag(x) == "tr"]
            for tr in trs:
                row: list[str] = []
                col = 0
                cells = [c for c in tr if tag(c) in ("td", "th")]
                ci = 0
                while ci < len(cells) or col in spans:
                    if col in spans:
                        left, text = spans[col]
                        row.append("")
                        spans[col] = (left - 1, text)
                        if left - 1 <= 0:
                            del spans[col]
                        col += 1
                        continue
                    c = cells[ci]
                    ci += 1
                    text = oneline(self.cell(c)).replace("|", "\\|")
                    span = int(c.get("colspan") or 1)
                    rspan = int(c.get("rowspan") or 1)
                    row.append(text)
                    if rspan > 1:
                        spans[col] = (rspan - 1, text)
                    for _ in range(span - 1):
                        col += 1
                        row.append("")
                    col += 1
                rows.append(row)
                if st == "thead":
                    header_rows += 1
        if not rows:
            return []
        width = max(len(r) for r in rows)
        rows = [r + [""] * (width - len(r)) for r in rows]
        if header_rows > 1:
            # Merge stacked header rows into one.
            merged = [" ".join(x for x in col if x).strip() for col in zip(*rows[:header_rows])]
            rows = [merged] + rows[header_rows:]
        elif header_rows == 0:
            rows = [[""] * width] + rows
        out = ["| " + " | ".join(rows[0]) + " |", "|" + "---|" * width]
        out += ["| " + " | ".join(r) + " |" for r in rows[1:]]
        return out

    def cell(self, c: ET.Element) -> str:
        bits = [c.text or ""]
        for ch in c:
            if tag(ch) in ("p",):
                bits.append(" " + self.inline(ch) + " ")
            elif tag(ch) in ("ol", "ul"):
                cls = ch.get("class") or ("bullet" if tag(ch) == "ul" else "numeric")
                items = [f"{list_label(cls, i)} {oneline(self.inline(li))}" for i, li in enumerate((x for x in ch if tag(x) == 'li'), 1)]
                bits.append(" " + "; ".join(items) + " ")
            else:
                bits.append(self.inline_el(ch))
            bits.append(ch.tail or "")
        return "".join(bits)

    # ---- structural ----
    def clause(self, e: ET.Element, level: int = 3) -> list[str]:
        t = tag(e)
        code = oneline(e.findtext("sptc") or e.get("sptc") or "")
        title = oneline("".join(e.find("title").itertext())) if e.find("title") is not None else ""
        lines = []
        if t == "clause-variation":
            state = e.get("state", "")
            verb = VARIATION_WORDS.get(e.get("type", ""), "varies")
            lines += [f"> **{state} variation**: {state} {verb} {code}{' ' + title if title else ''}.", ">"]
            body = self.clause_body(e)
            lines += [("> " + x if x else ">") for x in body] + [""]
            return lines
        lines += [f'<a id="{anchor(code)}"></a>', "", f"{'#' * level} {code} {title}".rstrip(), ""]
        lines += self.clause_body(e)
        return lines

    def clause_body(self, e: ET.Element) -> list[str]:
        lines = []
        for ch in e:
            t = tag(ch)
            if t in ("sptc", "title"):
                continue
            if t in ("subclause", "subclause-variation"):
                if t == "subclause-variation":
                    state = ch.get("state", "")
                    verb = VARIATION_WORDS.get(ch.get("type", ""), "varies")
                    body = []
                    for g in ch:
                        if tag(g) != "title":
                            body += self.block(g, 0)
                    lines += [f"> **{state} variation**: {state} {verb} subclause ({ch.get('num', '')}).", ">"]
                    lines += [("> " + x if x else ">") for x in body] + [""]
                    continue
                for g in ch:
                    if tag(g) in ("subclause-variation", "clause-variation"):
                        lines += self.clause(g) if tag(g) == "clause-variation" else self.clause_body_wrap(g)
                    else:
                        lines += self.block(g, 0)
            elif t == "clause-variation":
                lines += self.clause(ch)
            else:
                lines += self.block(ch, 0)
        return lines

    def clause_body_wrap(self, e: ET.Element) -> list[str]:
        wrapper = ET.Element("x")
        wrapper.append(e)
        return self.clause_body(wrapper)

    def part(self, part: ET.Element, level: int = 2) -> list[str]:
        lines = []
        for ch in part:
            t = tag(ch)
            if t in ("title",):
                continue
            if t == "intro-part":
                lines += self.block(ch, 0)
            elif t == "subtopic":
                label = SUBTOPIC_LABELS.get(ch.get("subtopic-type", ""), "")
                if label:
                    lines += [f"{'#' * level} {label}", ""]
                for g in ch:
                    lines += self.part_child(g, level)
            else:
                lines += self.part_child(ch, level)
        return lines

    def part_child(self, ch: ET.Element, level: int) -> list[str]:
        t = tag(ch)
        if t in ("clause", "standard-clause", "clause-variation"):
            return self.clause(ch, level + 1)
        if t in ("part", "part-variation"):
            num = ch.get("num", "")
            title = part_title(ch)
            head = f"{'#' * level} Part {num} {title}".replace("  ", " ").rstrip()
            if t == "part-variation":
                state = ch.get("state", "")
                verb = VARIATION_WORDS.get(ch.get("type", ""), "varies")
                head = f"{'#' * level} {state} variation: {state} {verb} Part {num} {title}".rstrip()
            return [head, ""] + self.part(ch, level + 1)
        if t == "spec-topic":
            title = oneline(ch.findtext("title") or "")
            return ([f"{'#' * level} {title}", ""] if title else []) + self.part(ch, level + 1)
        if t == "title":
            return []
        return self.block(ch, 0)


# --------------------------------------------------------------------------
# Writing pages
# --------------------------------------------------------------------------

def source_block(edition: str, vol_title: str, dataset_url: str) -> str:
    return f"""sources:
  - id: abcb_ncc
    resource: {dataset_url}
    title: NCC {edition} {vol_title}, Australian Building Codes Board (CC BY 4.0)
    author: org:abcb"""


def attribution(edition: str) -> str:
    return (f"[^abcb_ncc]: NCC {edition}. © Commonwealth of Australia and the States and Territories of Australia, "
            f"published by the Australian Building Codes Board, licensed under CC BY 4.0. "
            f"Converted to markdown by tools/ncc_ingest.py; figures not reproduced. "
            f"The authoritative text is at https://ncc.abcb.gov.au/")


def front(meta: dict) -> str:
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            lines.append(f"{k}: [{', '.join(str(x) for x in v)}]")
        elif isinstance(v, str) and k not in ("sources", "generated"):
            lines.append(f"{k}: {yaml_str(v)}")
        else:
            lines.append(f"{k}: {v}" if k != "sources" else v)
    lines.append("---")
    return "\n".join(lines) + "\n\n"


def write_volume(vol: Volume, targets: dict, out: Path, base: str, edition: str,
                 dataset_url: str, now: str, index: list) -> dict:
    vdir = out / vol.folder
    vdir.mkdir(parents=True, exist_ok=True)
    gen = f"{{ by: {TOOL}/0.1, at: {now} }}"
    src = source_block(edition, vol.title, dataset_url)
    vol_short = vol.title.replace("Volume ", "Vol ")
    stats = {"parts": 0, "clauses": 0, "figures": 0}
    has_defs = any(tag(x) == "ncc-section" and oneline(x.findtext("title") or "") == "Definitions"
                   for x in vol.root.iter())
    # The Livable Housing Design Standard uses the Volume Two definitions.
    defs_link = "definitions.md" if has_defs else f"{base}/volume_two/definitions.md"

    for part, fname, order, section_title in vol.parts:
        page = f"{base}/{vol.folder}/{fname}"
        r = Renderer(targets, page)
        body = r.part(part)
        num = part_num(part)
        title = part_title(part)
        label = part_label(part)
        kind = "Specification" if tag(part) == "specification" else "Part"
        codes = []
        states = set()
        for e in part.iter():
            if tag(e) in ("clause", "standard-clause"):
                c = oneline(e.findtext("sptc") or "")
                if c:
                    codes.append(c)
            if e.get("state") in STATES:
                states.add(e.get("state"))
        intro = part.find("intro-part")
        desc_src = oneline("".join(intro.itertext())) if intro is not None else ""
        desc = (re.split(r"(?<=\.)\s", desc_src)[0] if desc_src else f"NCC {edition} {vol_short} {label} {title}.")[:240]
        for c in codes:
            index.append((vol.title, c, f"{label} {title}", page, anchor(c)))
        meta = {
            "type": "Code Reference",
            "title": f"NCC {edition} {vol_short}, {label} {title}",
            "description": desc,
            "tags": ["ncc", f"ncc_{edition}", vol.folder] + ([slug(section_title)] if section_title else []),
            "status": "stable",
            "resource": "https://ncc.abcb.gov.au/",
            "edition": f"NCC {edition}",
            "volume": vol.title,
            "part": num,
            "order": order,
            "clauses": codes,
            "state_variations": sorted(states),
            "sources": src,
            "generated": gen,
        }
        head = [f"From **NCC {edition} {vol.title}**{', ' + section_title if section_title else ''}.[^abcb_ncc] "
                f"Defined terms are in *italics*; see [definitions]({defs_link}). "
                + (f"State and territory variations ({', '.join(sorted(states))}) are shown in quotes beside the clause they change." if states else ""), ""]
        text = front(meta) + "\n".join(head + body + ["", attribution(edition), ""])
        (vdir / fname).write_text(re.sub(r"\n{3,}", "\n\n", text))
        stats["parts"] += 1
        stats["clauses"] += len(codes)
        stats["figures"] += r.figures

    # Definitions and referenced documents
    for section in (x for x in vol.root.iter() if tag(x) == "ncc-section" and x.get("type") == "schedule"):
        stitle = oneline(section.findtext("title") or "")
        page = None
        if stitle == "Definitions":
            page, fname = f"{base}/{vol.folder}/definitions.md", "definitions.md"
            r = Renderer(targets, page)
            lines = []
            entries = [g for g in section.iter() if tag(g) in ("glossentry", "glossentry-variation")]
            for g in entries:
                term = oneline("".join(g.find("glossterm").itertext())) if g.find("glossterm") is not None else ""
                if not term:
                    continue
                prefix = ""
                if tag(g) == "glossentry-variation":
                    prefix = f"{g.get('state', '')} variation: "
                lines += [f'<a id="{slug(term)}"></a>', "", f"### {prefix}{term}", ""]
                d = g.find("glossdef")
                if d is not None:
                    lines += r.block(d, 0)
                for v in g:
                    if tag(v) == "glossentry-variation":
                        vd = v.find("glossdef")
                        lines += [f"> **{v.get('state', '')} variation**:", ">"]
                        lines += [("> " + x if x else ">") for x in (r.block(vd, 0) if vd is not None else [])] + [""]
            meta_title, desc = f"NCC {edition} {vol_short}, Schedule 1 Definitions", f"Defined terms used in NCC {edition} {vol.title} (the words shown in italics)."
            body = lines
        elif stitle == "Referenced documents":
            page, fname = f"{base}/{vol.folder}/referenced_documents.md", "referenced_documents.md"
            r = Renderer(targets, page)
            body = []
            for ch in section:
                if tag(ch) != "title":
                    body += r.block(ch, 0)
            meta_title, desc = f"NCC {edition} {vol_short}, Schedule 2 Referenced documents", f"Standards and documents NCC {edition} {vol.title} calls up, with the editions referenced."
        if page:
            meta = {"type": "Code Reference", "title": meta_title, "description": desc,
                    "tags": ["ncc", f"ncc_{edition}", vol.folder], "status": "stable",
                    "resource": "https://ncc.abcb.gov.au/", "edition": f"NCC {edition}", "volume": vol.title,
                    "order": 900 if fname == "definitions.md" else 901, "sources": src, "generated": gen}
            intro = f"From **NCC {edition} {vol.title}**.[^abcb_ncc]\n\n"
            (vdir / fname).write_text(re.sub(r"\n{3,}", "\n\n", front(meta) + intro + "\n".join(body) + "\n\n" + attribution(edition) + "\n"))

    # State variations summary
    rows = []
    for section in (x for x in vol.root.iter() if tag(x) == "ncc-section" and x.get("state") in STATES):
        state = section.get("state")
        for e in section.iter():
            if tag(e) not in ("variation", "schedule-part-variation"):
                continue
            ref = targets.get(e.get("reference", "")) or targets.get(e.get("id", ""))
            code = e.get("sptc") or (f"Part {e.get('num')}" if e.get("num") else "")
            what = VARIATION_WORDS.get(e.get("type", ""), "varies")
            link = f"[{code}]({ref.page}{'#' + ref.anchor if ref and ref.anchor else ''})" if ref and code else code
            rows.append((state, f"| {state} | {what} | {link} |"))
    if rows:
        meta = {"type": "Code Reference", "title": f"NCC {edition} {vol_short}, state and territory variations",
                "description": f"Every state and territory variation to NCC {edition} {vol.title}, linked to the clause it changes.",
                "tags": ["ncc", f"ncc_{edition}", vol.folder, "states"], "status": "stable",
                "resource": "https://ncc.abcb.gov.au/", "edition": f"NCC {edition}", "volume": vol.title,
                "order": 902, "sources": src, "generated": gen}
        body = [f"From the state and territory schedules of **NCC {edition} {vol.title}**.[^abcb_ncc] "
                "Always check this list for the job's state: a variation can replace, add to or delete a national clause.", "",
                "| State | Variation | Clause or Part |", "|---|---|---|"] + [r for _, r in sorted(rows, key=lambda x: x[0])]
        (vdir / "state_variations.md").write_text(front(meta) + "\n".join(body) + "\n\n" + attribution(edition) + "\n")
    return stats


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--edition", default="2025")
    parser.add_argument("--raw", type=Path, default=ROOT / "raw" / "ncc")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--dataset_url", default="https://data.gov.au/data/dataset/national-construction-code-2025-version-1-2")
    args = parser.parse_args()
    out = args.out or ROOT / "brain" / "ncc" / args.edition
    base = "/" + out.resolve().relative_to((ROOT / "brain").resolve()).as_posix()
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    volumes = []
    for xml in sorted(args.raw.glob(f"ncc-{args.edition}-*/contents.xml")):
        root = ET.parse(xml).getroot()
        pub = root.get("publishing-id")
        if pub not in VOLUMES:
            print(f"skipping {xml.parent.name}: unknown publishing-id {pub!r}")
            continue
        folder, title, blurb = VOLUMES[pub]
        volumes.append(Volume(pub, root, folder, title, blurb))
    if not volumes:
        raise SystemExit(f"No NCC {args.edition} contents.xml found under {args.raw}")

    for vol in volumes:
        if (out / vol.folder).exists():
            shutil.rmtree(out / vol.folder)
    targets = build_targets(volumes, base)
    index: list = []
    for vol in volumes:
        stats = write_volume(vol, targets, out, base, args.edition, args.dataset_url, now, index)
        print(f"{vol.title}: {stats['parts']} parts, {stats['clauses']} clauses, {stats['figures']} figures referenced")

    gen = f"{{ by: {TOOL}/0.1, at: {now} }}"
    meta = {"type": "Reference", "title": f"NCC {args.edition} clause index",
            "description": f"Every NCC {args.edition} clause code with its Part and page, across all volumes.",
            "tags": ["ncc", f"ncc_{args.edition}", "index"], "status": "stable", "order": 0,
            "sources": source_block(args.edition, "datasets", args.dataset_url), "generated": gen}
    lines = [f"Look up a clause code here, then open its page.[^abcb_ncc] Codes in the A section (governing "
             "requirements) repeat in each volume.", "", "| Clause | Volume | Part | Page |", "|---|---|---|---|"]
    for vol_title, code, part, page, anc in index:
        lines.append(f"| {code} | {vol_title} | {part} | [open]({page}#{anc}) |")
    (out / "clause_index.md").write_text(front(meta) + "\n".join(lines) + "\n\n" + attribution(args.edition) + "\n")
    print(f"{len(index)} clauses indexed in {out.relative_to(ROOT)}/clause_index.md")
    # Last step: give state-added clauses their anchors and point any link without a target at its page.
    import ncc_anchor_repair
    print(f"anchors: {ncc_anchor_repair.repair(args.edition, folder=out)}")
    print("Now run tools/build_state_pages.py, then tools/okf_lint.py.")


if __name__ == "__main__":
    main()

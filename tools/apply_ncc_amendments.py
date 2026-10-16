"""Merge NCC 2022 Amendments 1 and 2 into the brain/ncc/2022 pages.

Usage:
    python tools/apply_ncc_amendments.py

Reads tools/ncc2022_amendments.yaml (transcribed from the ABCB's amendment
documents) and, for each change, puts a notice with the amended text directly
under the clause it changes. State changes are labelled "WA variation" (and
so on), so the state filter in tools/ncc_lookup.py treats them like any other
variation. New Parts get their own pages. Writes brain/ncc/2022/amendments.md
listing every change, and updates the edition notice on every 2022 page.

Idempotent: earlier notices are removed and rewritten on each run.
tools/ncc_pdf_ingest.py runs this automatically after converting the PDFs.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
NCC = ROOT / "brain" / "ncc" / "2022"
DATA = ROOT / "tools" / "ncc2022_amendments.yaml"
BLOCK = re.compile(r"\n?<!-- AMDT [^>]*-->.*?<!-- /AMDT -->\n?", re.S)
OLD_NOTE = re.compile(r"> \*\*NCC 2022[^\n]*\n(?:>[^\n]*\n)*", re.S)
NOTE = ("> **NCC 2022 with Amendments 1 and 2.** The text is NCC 2022 as published (1 May 2023). Changes made by "
        "Amendment 1 (from 1 May 2025) and Amendment 2 (from 29 July 2025) are shown as notices under the clause "
        "they change; the amended text takes precedence. See [NCC 2022 amendments](/ncc/2022/amendments.md).\n")


def slug(text: str) -> str:
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", text.lower())).strip("_")


def quote(text: str) -> list[str]:
    return [("> " + l) if l.strip() else ">" for l in text.strip("\n").split("\n")]


def notice(change: dict, meta: dict, key: str) -> str:
    a = meta[change["amendment"]]
    head = (f"> **{change['state']} variation, {a['title']} (from {a['effective']})**: {change['instruction']}."
            if change.get("state") else
            f"> **Amended by {a['title']} (from {a['effective']})**: {change['instruction']}.")
    body = [head]
    if change.get("text", "").strip():
        body += [">"] + quote(change["text"])
    return f"<!-- AMDT {key} -->\n" + "\n".join(body) + "\n<!-- /AMDT -->"


def insert_after_heading(text: str, anchor: str | None, block: str) -> tuple[str, bool]:
    if anchor:
        m = re.search(rf"^### {re.escape(anchor)}(?:\s|$)[^\n]*\n", text, re.M)
        if not m:
            return text, False
        pos = m.end()
    else:
        # Part-level: after the page's opening "From **NCC 2022 ...**" paragraph.
        m = re.search(r"^From \*\*NCC 2022[^\n]*\n", text, re.M)
        if not m:
            return text, False
        pos = m.end()
    return text[:pos] + "\n" + block + "\n" + text[pos:], True


def volumes(v) -> list[str]:
    return v if isinstance(v, list) else [v]


def main() -> None:
    data = yaml.safe_load(DATA.read_text())
    meta = data["amendments"]
    if not NCC.is_dir():
        sys.exit("brain/ncc/2022 not found: run tools/ncc_pdf_ingest.py first")

    # 1. Clear earlier notices and refresh the edition note on every 2022 page.
    for page in NCC.rglob("*.md"):
        if page.name == "index.md":
            continue
        text = BLOCK.sub("\n", page.read_text())
        text = OLD_NOTE.sub(NOTE, text, count=1)
        page.write_text(re.sub(r"\n{3,}", "\n\n", text))

    applied, missing, rows = [], [], []
    # 2. Notices under the clauses they change.
    for i, change in enumerate(data["changes"], 1):
        for vol in volumes(change["volume"]):
            page = NCC / vol / change["page"]
            if not page.exists():
                missing.append(f"{vol}/{change['page']} (page not found)")
                continue
            key = f"{change['amendment']}.{i}.{vol}"
            text, ok = insert_after_heading(page.read_text(), change.get("anchor"), notice(change, meta, key))
            if not ok:
                missing.append(f"{vol}/{change['page']} {change.get('anchor', '(part)')} (heading not found)")
                continue
            page.write_text(text)
            applied.append((change, vol))
            link = f"/ncc/2022/{vol}/{change['page']}" + (f"#{slug(change['anchor'])}" if change.get("anchor") else "")
            rows.append(f"| {meta[change['amendment']]['title']} | {vol.replace('_', ' ').title()} | "
                        f"[{change.get('anchor') or change['page'].removesuffix('.md').replace('_', ' ')}]({link}) | "
                        f"{change.get('state') or 'national'} | {change['instruction']} |")

    # 3. New Parts.
    for np in data.get("new_pages", []):
        a = meta[np["amendment"]]
        prefix = f"{np['state']} {np['part']}"
        lines = [f"From **{a['title']}** (from {a['effective']}), which inserts this {np['state']}-only Part into NCC 2022 "
                 f"{np['volume'].replace('_', ' ').title()}.[^abcb_ncc]", "", NOTE.rstrip(), "",
                 "## Introduction to this Part", "", np["intro"], "", "## Deemed-to-Satisfy Provisions", ""]
        codes = []
        for c in np["clauses"]:
            code = c["code"].format(p=prefix)
            codes.append(code)
            lines += [f'<a id="{slug(code)}"></a>', "", f"### {code} {c['title']}", "",
                      c["text"].replace("this clause", code).rstrip(), ""]
            rows.append(f"| {a['title']} | {np['volume'].replace('_', ' ').title()} | [{code}](/ncc/2022/{np['volume']}/{np['filename']}#{slug(code)}) | "
                        f"{np['state']} | Inserted (new {np['state']} Part {np['part']}) |")
        front = ["---", "type: Code Reference", f'title: "NCC 2022 {np["volume"].replace("_", " ").title().replace("Volume ", "Vol ")}, {np["state"]} Part {np["part"]} {np["title"]}"',
                 f'description: "{np["intro"]}"', f"tags: [ncc, ncc_2022, {np['volume']}, states]", "status: stable",
                 f"resource: {a['url']}", 'edition: "NCC 2022"', f"part: {np['part']}", "order: 801",
                 f"clauses: [{', '.join(codes)}]", f"state_variations: [{np['state']}]",
                 "sources:", "  - id: abcb_ncc", f"    resource: {a['url']}", f"    title: {a['title']} (CC BY 4.0)", "    author: org:abcb",
                 "generated: { by: process:apply_ncc_amendments/0.1, at: 2026-10-17T00:00:00Z }", "---", ""]
        attribution = (f"[^abcb_ncc]: The National Construction Code 2022 was provided by the Australian Building Codes Board under the CC BY 4.0 licence. "
                       f"This Part is from {a['title']}, version {a['version']}: {a['url']}")
        (NCC / np["volume"] / np["filename"]).write_text("\n".join(front + lines + [attribution, ""]))
        # Index and state variation rows for the new clauses.
        idx = NCC / "clause_index.md"
        it = idx.read_text()
        for code in codes:
            row = f"| {code} | {np['volume'].replace('_', ' ').title()} | {np['state']} Part {np['part']} {np['title']} | [open](/ncc/2022/{np['volume']}/{np['filename']}#{slug(code)}) |"
            if row not in it:
                it = it.replace("\n\n[^abcb_ncc]", f"\n{row}\n\n[^abcb_ncc]", 1)
        idx.write_text(it)

    # 4. State variation lists pick up the amendment's state changes.
    for vol_page in NCC.glob("*/state_variations.md"):
        vol = vol_page.parent.name
        text = re.sub(r"\n\| [A-Z]{2,3} \| \(Amendment \d\)[^\n]*", "", vol_page.read_text())
        extra = []
        for change, v in applied:
            if v == vol and change.get("state"):
                link = f"/ncc/2022/{vol}/{change['page']}" + (f"#{slug(change['anchor'])}" if change.get("anchor") else "")
                extra.append(f"| {change['state']} | (Amendment {change['amendment']}) {change['instruction']} | [{change.get('anchor') or 'Part'}]({link}) |")
        for np in data.get("new_pages", []):
            if np["volume"] == vol:
                extra.append(f"| {np['state']} | (Amendment {np['amendment']}) Insert {np['state']} Part {np['part']} {np['title']} | [{np['state']} Part {np['part']}](/ncc/2022/{vol}/{np['filename']}) |")
        if extra:
            text = text.replace("\n\n[^abcb_ncc]", "\n" + "\n".join(extra) + "\n\n[^abcb_ncc]", 1)
        vol_page.write_text(text)

    # 5. The amendments page.
    out = ["---", "type: Code Reference", "title: NCC 2022 amendments",
           'description: "Every change made to NCC 2022 by Amendment 1 (from 1 May 2025) and Amendment 2 (from 29 July 2025), linked to the clause it changes."',
           "tags: [ncc, ncc_2022, amendments]", "status: stable", "resource: https://ncc.abcb.gov.au/editions/ncc-2022", "order: 1",
           "sources:"]
    for k, a in meta.items():
        out += [f"  - id: amdt{k}", f"    resource: {a['url']}", f"    title: {a['title']}, version {a['version']}", "    author: org:abcb"]
    out += ["generated: { by: process:apply_ncc_amendments/0.1, at: 2026-10-17T00:00:00Z }", "---", "",
            "NCC 2022 as published (1 May 2023) has been amended twice. The 2022 pages in this brain keep the published text "
            "and show each amendment as a notice under the clause it changes, so you can see both what changed and when.", ""]
    for k, a in meta.items():
        out += [f"# {a['title']}", "", f"- **In force from:** {a['effective']}", f"- **Version:** {a['version']}",
                f"- **Purpose:** {a['purpose']}", f"- **Source:** [{a['title']}]({a['url']})[^amdt{k}]", ""]
    out += ["# Changes to provisions", "", "| Amendment | Volume | Where | Applies | Change |", "|---|---|---|---|---|"] + rows + [""]
    out += ["# Preface-only changes", ""] + [f"- ({meta[p['amendment']]['title']}) {p['note']}" for p in data.get("preface_only", [])] + [""]
    if missing:
        out += ["# Not applied", "", "These changes couldn't be placed automatically; check them against the amendment:", ""] + [f"- {m}" for m in missing] + [""]
    out += [f"[^amdt{k}]: {a['title']}, version {a['version']}" for k, a in meta.items()]
    (NCC / "amendments.md").write_text("\n".join(out) + "\n")
    print(f"{len(applied)} notices applied, {len(data.get('new_pages', []))} new Parts, {len(missing)} not placed")
    for m in missing:
        print("  not placed:", m)


if __name__ == "__main__":
    main()

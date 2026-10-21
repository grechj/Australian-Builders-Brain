"""Make every link into the NCC pages land on something: the last step of the NCC ingest.

Usage:
    python tools/ncc_anchor_repair.py                 # repair brain/ncc/2025 and brain/ncc/2022, then report
    python tools/ncc_anchor_repair.py --check         # report only; exit 1 if any link points nowhere

The ingests (tools/ncc_ingest.py for 2025, tools/ncc_pdf_ingest.py for
2022) call repair() on their output, so a fresh ingest and a repaired page
are the same. Three things went wrong before this step existed:

1. NCC 2025 state variations are quoted beside the clause they change, but a
   clause a state adds or replaces had no anchor of its own (SA's 10.2.33,
   every clause on NSW's Part I5 page), so links to it went nowhere. Each
   variation now gets the clause's anchor, unless the page already has it.
2. NCC 2022 state-only pages anchored clauses with the state in front
   (`nsw_9_4_3`) while links used the plain code (`9_4_3`). Those clauses now
   carry both.
3. A few links pointed at things the conversion can't anchor: Part
   variations (`#part_ariation`) and tables inside quoted variations. Those
   links now point at the page (or, within a page, become plain text).

Standard library only. Idempotent: running it twice changes nothing.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BRAIN = ROOT / "brain"
STATES = ("act", "nsw", "nt", "qld", "sa", "tas", "vic", "wa")
ANCHOR = re.compile(r'<a id="([^"]+)"></a>')
LINK = re.compile(r"(\[([^\]]*)\])\(([^)\s#]*)#([^)\s]+)\)")
VARIATION = re.compile(r"^> \*\*(ACT|NSW|NT|QLD|SA|TAS|VIC|WA) variation\*\*: \1 (?:replaces|adds|inserts|substitutes) ([A-Z]{0,2}\d+[A-Z]\d+|S\d+C\d+|\d+(?:\.\d+)+)\b")


def slug(text: str) -> str:
    """The ingest's anchor for a clause code (tools/ncc_ingest.py anchor())."""
    return re.sub(r"_+", "_", re.sub(r"[^a-z0-9]+", "_", text.lower())).strip("_") or "clause"


def anchors(text: str) -> set[str]:
    return set(ANCHOR.findall(text))


def add_variation_anchors(text: str) -> tuple[str, int]:
    """Give each state-added or state-replaced clause an anchor, before its quoted variation."""
    have = anchors(text)
    out, added = [], 0
    for line in text.split("\n"):
        m = VARIATION.match(line)
        if m:
            a = slug(m.group(2))
            if a not in have:
                out += [f'<a id="{a}"></a>', ""]
                have.add(a)
                added += 1
        out.append(line)
    return "\n".join(out), added


def add_plain_state_anchors(text: str) -> tuple[str, int]:
    """On a state-only page, `nsw_9_4_3` also answers to `9_4_3` (both on one line, so lookups still see the clause)."""
    have = anchors(text)
    added = 0

    def plain(m: re.Match) -> str:
        nonlocal added
        full = m.group(1)
        state, _, rest = full.partition("_")
        if state in STATES and rest and rest not in have and not rest.startswith(("table_", "figure_")):
            have.add(rest)
            added += 1
            return f'<a id="{rest}"></a>{m.group(0)}'
        return m.group(0)

    return re.sub(r'(?<!</a>)<a id="([^"]+)"></a>', plain, text), added


def page_for(target: str, here: Path) -> Path:
    if not target:
        return here
    return BRAIN / target.lstrip("/") if target.startswith("/") else (here.parent / target)


def drop_dead_anchors(path: Path, text: str, cache: dict) -> tuple[str, int]:
    """A link to an anchor that doesn't exist points at the page instead; within a page it becomes plain text."""
    fixed = 0

    def fix(m: re.Match) -> str:
        nonlocal fixed
        label, words, target, anchor = m.group(1), m.group(2), m.group(3), m.group(4)
        if re.match(r"^[a-z]+:", target):
            return m.group(0)
        dest = page_for(target, path)
        if not dest.exists():
            return m.group(0)
        have = cache.setdefault(dest, anchors(dest.read_text())) if dest != path else anchors(text)
        if anchor in have:
            return m.group(0)
        fixed += 1
        return words if not target else f"{label}({target})"

    return LINK.sub(fix, text), fixed


def ncc_pages(folder: Path) -> list[Path]:
    return sorted(p for p in folder.rglob("*.md") if p.name != "index.md")


def repair(edition: str, write: bool = True, folder: Path | None = None) -> dict:
    """Add the missing anchors to one edition's pages, then point any link that still has no target at its page."""
    stats = {"variation_anchors": 0, "plain_state_anchors": 0, "links_to_page": 0}
    pages = ncc_pages(folder or BRAIN / "ncc" / edition)
    texts = {p: p.read_text() for p in pages}
    for p in pages:
        t = texts[p]
        if edition == "2025":
            t, n = add_variation_anchors(t)
            stats["variation_anchors"] += n
        if p.name.split("_")[0] in STATES:
            t, n = add_plain_state_anchors(t)
            stats["plain_state_anchors"] += n
        texts[p] = t
    cache = {p: anchors(t) for p, t in texts.items()}
    for p in pages:
        t, n = drop_dead_anchors(p, texts[p], cache)
        stats["links_to_page"] += n
        texts[p] = t
    if write:
        for p, t in texts.items():
            if p.read_text() != t:
                p.write_text(t)
    return stats


def dead_links(paths=None) -> list[str]:
    """Every link anywhere in the brain whose anchor isn't on the page it points to."""
    out, cache = [], {}
    for p in sorted(paths or BRAIN.rglob("*.md")):
        text = p.read_text()
        for m in LINK.finditer(text):
            target, anchor = m.group(3), m.group(4)
            if re.match(r"^[a-z]+:", target):
                continue
            dest = page_for(target, p)
            if not dest.exists():
                continue
            have = cache.setdefault(dest, anchors(dest.read_text()))
            if anchor not in have:
                out.append(f"{p.relative_to(ROOT)}: {target or '(this page)'}#{anchor}")
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--edition", choices=["2025", "2022"], action="append")
    parser.add_argument("--check", action="store_true", help="report only")
    a = parser.parse_args()
    if not a.check:
        for ed in a.edition or ["2025", "2022"]:
            print(f"NCC {ed}: {repair(ed)}")
    dead = dead_links()
    print(f"{len(dead)} link(s) in the brain point to an anchor that isn't there")
    for d in dead[:20]:
        print("  " + d)
    sys.exit(1 if a.check and dead else 0)


if __name__ == "__main__":
    main()

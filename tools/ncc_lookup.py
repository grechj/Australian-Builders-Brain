"""Look things up in the NCC pages under brain/ncc/<edition>/.

Usage:
    python tools/ncc_lookup.py clause H2D2                    # full clause text, every volume that has it
    python tools/ncc_lookup.py clause 10.2.1 --volume housing_provisions
    python tools/ncc_lookup.py search "wet area waterproofing shower" --volume housing_provisions
    python tools/ncc_lookup.py define "wet area" --volume volume_two
    python tools/ncc_lookup.py variations --state NSW --volume volume_two

Volumes: volume_one, volume_two, volume_three, housing_provisions,
livable_housing_design. Output is markdown, with the page path to cite.
Standard library only.
"""

from __future__ import annotations

import argparse
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BLOCK = re.compile(r'<a id="([^"]+)"></a>\s*\n\s*\n(#{2,6}) (.+)\n')
WORD = re.compile(r"[a-z0-9]+(?:\.[0-9]+)*")
STOP = set("a an and are as at be by for from in is it of on or that the to with where which must be not".split())


@dataclass
class Block:
    volume: str
    page: Path
    anchor: str
    heading: str
    text: str
    kind: str        # clause | definition

    @property
    def code(self) -> str:
        return self.heading.split(" ", 1)[0]

    def cite(self, edition: str) -> str:
        rel = self.page.relative_to(ROOT).as_posix()
        return f"NCC {edition} {self.volume.replace('_', ' ').title()}: `{rel}#{self.anchor}`"


def stem(word: str) -> str:
    for suffix in ("ing", "es", "s"):
        if len(word) > 4 and word.endswith(suffix):
            return word[: -len(suffix)]
    return word


def terms(text: str) -> list[str]:
    return [stem(w) for w in WORD.findall(text.lower()) if w not in STOP]


def load(edition: str, volume: str | None) -> list[Block]:
    base = ROOT / "brain" / "ncc" / edition
    if not base.is_dir():
        raise SystemExit(f"No NCC {edition} pages at {base.relative_to(ROOT)}. Run tools/ncc_ingest.py first.")
    blocks = []
    for page in sorted(base.glob("*/*.md")):
        vol = page.parent.name
        if volume and vol != volume:
            continue
        if page.name in ("index.md", "log.md", "state_variations.md", "referenced_documents.md"):
            continue
        text = page.read_text()
        body = text.split("---", 2)[2] if text.startswith("---") else text
        body = body.split("\n[^abcb_ncc]:")[0]
        kind = "definition" if page.name == "definitions.md" else "clause"
        matches = list(BLOCK.finditer(body))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
            chunk = body[m.end():end]
            # Stop at the next section heading of the same or higher level.
            nxt = re.search(rf"\n#{{2,{len(m.group(2))}}} ", chunk)
            if nxt:
                chunk = chunk[: nxt.start()]
            blocks.append(Block(vol, page, m.group(1), m.group(3).strip(), chunk.strip(), kind))
    return blocks


def show(block: Block, edition: str) -> str:
    return f"## {block.heading}\n\n{block.text}\n\nSource: {block.cite(edition)}\n"


def cmd_clause(args, blocks: list[Block]) -> None:
    want = args.code.upper().strip()
    hits = [b for b in blocks if b.kind == "clause" and b.code.upper() == want]
    if not hits:
        near = sorted({b.code for b in blocks if b.kind == "clause" and b.code.upper().startswith(want[:3])})[:15]
        raise SystemExit(f"No clause {want}." + (f" Nearby codes: {', '.join(near)}" if near else ""))
    print("\n---\n\n".join(show(b, args.edition) for b in hits))


def cmd_define(args, blocks: list[Block]) -> None:
    want = args.term.lower().strip()
    defs = [b for b in blocks if b.kind == "definition"]
    hits = [b for b in defs if b.heading.lower().split(": ")[-1] == want] or \
           [b for b in defs if want in b.heading.lower()]
    if not hits:
        raise SystemExit(f"No definition matching {args.term!r}.")
    print("\n---\n\n".join(show(b, args.edition) for b in hits[:6]))


def cmd_search(args, blocks: list[Block]) -> None:
    pool = [b for b in blocks if b.kind == "clause"]
    docs = [Counter(terms(b.heading + " " + b.heading + " " + b.text)) for b in pool]
    df = Counter(t for d in docs for t in d)
    q = terms(args.query)
    n = len(pool)
    scored = []
    for b, d in zip(pool, docs):
        length = sum(d.values()) or 1
        score = sum((d[t] / (d[t] + 1.2 * (0.25 + 0.75 * length / 200))) * math.log(1 + n / (1 + df[t]))
                    for t in q if d[t])
        hit_terms = sum(1 for t in q if d[t])
        if score:
            scored.append((score * hit_terms / len(q), b))
    scored.sort(key=lambda x: -x[0])
    if not scored:
        raise SystemExit("No matches. Try fewer or different words.")
    for score, b in scored[: args.limit]:
        snippet = re.sub(r"\s+", " ", re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", b.text))[:220]
        print(f"- **{b.heading}** ({b.volume}) score {score:.2f}\n  {snippet}...\n  `{b.page.relative_to(ROOT).as_posix()}#{b.anchor}`")


def cmd_variations(args, _blocks) -> None:
    base = ROOT / "brain" / "ncc" / args.edition
    pages = sorted(base.glob(f"{args.volume or '*'}/state_variations.md"))
    for page in pages:
        rows = [line for line in page.read_text().splitlines() if line.startswith(f"| {args.state.upper()} |")]
        print(f"## {page.parent.name}: {len(rows)} {args.state.upper()} variations\n")
        print("\n".join(rows) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--edition", default="2025")
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("clause"); p.add_argument("code")
    p = sub.add_parser("define"); p.add_argument("term")
    p = sub.add_parser("search"); p.add_argument("query"); p.add_argument("--limit", type=int, default=8)
    p = sub.add_parser("variations"); p.add_argument("--state", required=True)
    for name in ("clause", "define", "search", "variations"):
        sub.choices[name].add_argument("--volume")
    args = parser.parse_args()
    blocks = [] if args.cmd == "variations" else load(args.edition, args.volume)
    {"clause": cmd_clause, "define": cmd_define, "search": cmd_search, "variations": cmd_variations}[args.cmd](args, blocks)


if __name__ == "__main__":
    main()

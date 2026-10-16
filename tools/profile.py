"""Filter the brain by trade and location.

Usage:
    python tools/profile.py trades                                  # every trade, with aliases
    python tools/profile.py show --trade sparky --state QLD         # what an electrician in QLD needs
    python tools/profile.py show --project my_project.yaml          # reads `trade` and `state` from the project file
    python tools/profile.py show --trade builder --state NSW --json

A profile is one trade (or `builder` / `all`, which see everything) plus a
state or territory. `show` resolves:

- the NCC pages in the trade's scope, with other states' state-only Parts removed
- the NCC variations for the state that touch those pages
- the skills, takeoff jobs, typical materials and supplier types for the trade
- the state page (regulator, licensing, climate, materials, costs)

Other tools import `resolve_profile()` to apply the same filter.
"""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
BRAIN = ROOT / "brain"
NCC = BRAIN / "ncc" / "2025"
STATES = ["ACT", "NSW", "NT", "QLD", "SA", "TAS", "VIC", "WA"]
EVERYTHING = {"builder", "all"}


def _front(path: Path) -> tuple[dict, str]:
    text = path.read_text()
    _, front, body = text.split("---\n", 2)
    return yaml.safe_load(front), body


def trades() -> dict[str, dict]:
    out = {}
    for p in sorted((BRAIN / "trades").glob("*.md")):
        if p.name == "index.md":
            continue
        meta, body = _front(p)
        meta["_body"] = body
        meta["_page"] = p
        out[meta["trade"]] = meta
    return out


def find_trade(name: str | None) -> str:
    if not name:
        return "all"
    key = name.strip().lower().replace("-", "_")
    if key in EVERYTHING:
        return key
    table = trades()
    if key in table:
        return key
    for tid, meta in table.items():
        if key.replace("_", " ") in [a.lower() for a in meta.get("aliases", [])]:
            return tid
    raise SystemExit(f"Unknown trade {name!r}. Run: python tools/profile.py trades")


def find_state(name: str | None) -> str | None:
    if not name:
        return None
    code = name.strip().upper()
    if code not in STATES:
        raise SystemExit(f"State must be one of {', '.join(STATES)}")
    return code


def ncc_pages() -> list[str]:
    return sorted(p.relative_to(NCC).with_suffix("").as_posix() for p in NCC.glob("*/*.md")
                  if p.name != "index.md" and not p.name.startswith(("definitions", "referenced", "state_var")))


def _state_of(page: str) -> str | None:
    m = re.match(r"([a-z]+)_part_", page.split("/")[1])
    return m.group(1).upper() if m and m.group(1).upper() in STATES else None


def _bullets(body: str, heading: str) -> list[str]:
    m = re.search(re.escape(heading) + r"\n\n((?:- .*\n?)+)", body)
    return [l[2:].strip() for l in m.group(1).splitlines()] if m else []


def resolve_profile(trade: str | None = None, state: str | None = None) -> dict:
    tid, code = find_trade(trade), find_state(state)
    pages = ncc_pages()
    if tid in EVERYTHING:
        patterns, meta = ["**"], trades().get("builder", {})
    else:
        meta = trades()[tid]
        patterns = meta.get("ncc_scope") or []
    scope = []
    for pat in patterns:
        for p in pages:
            if pat == "**" or fnmatch.fnmatch(p, pat) or (pat.endswith("/**") and p.startswith(pat[:-2])):
                if p not in scope:
                    scope.append(p)
    # State-only Parts: keep the user's state's, drop everyone else's.
    scope = [p for p in scope if _state_of(p) in (None, code)] if code else [p for p in scope if _state_of(p) is None]
    variations = []
    if code:
        for vol in sorted(NCC.glob("*/state_variations.md")):
            for line in vol.read_text().splitlines():
                if not line.startswith(f"| {code} |"):
                    continue
                m = re.search(r"\(/ncc/2025/([^#)]+)\.md", line)
                if m and m.group(1) in scope:
                    variations.append(line)
    skills = meta.get("skills", []) if tid not in EVERYTHING else trades()["builder"]["skills"]
    return {
        "trade": tid,
        "trade_title": "All trades" if tid == "all" else meta.get("title", tid),
        "state": code,
        "ncc_scope": scope,
        "state_variations": variations,
        "skills": skills,
        "takeoff_jobs": meta.get("takeoff_jobs", []),
        "typical_materials": _bullets(meta.get("_body", ""), "Typical materials:"),
        "suppliers": _bullets(meta.get("_body", ""), "Where to price them (beyond the Bunnings retail guide):"),
        "standards": _bullets(meta.get("_body", ""), "# Key standards and rules (referenced, not reproduced)"),
        "trade_page": str(meta["_page"].relative_to(ROOT)) if meta.get("_page") else "",
        "state_page": f"brain/states/{code.lower()}.md" if code else "brain/states/overview.md",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("trades")
    p = sub.add_parser("show")
    p.add_argument("--trade"); p.add_argument("--state"); p.add_argument("--project", type=Path)
    p.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.cmd == "trades":
        print("builder: sees every trade and all of the NCC\nall: no filter (same scope as builder)")
        for tid, meta in trades().items():
            if tid != "builder":
                print(f"{tid}: {meta['title']} ({', '.join(meta.get('aliases', []))})")
        return

    trade, state = args.trade, args.state
    if args.project:
        data = yaml.load(args.project.read_text(), Loader=yaml.BaseLoader) or {}
        flat = {k: v for section in data.values() if isinstance(section, dict) for k, v in section.items()}
        trade, state = trade or flat.get("trade"), state or flat.get("state")
    prof = resolve_profile(trade, state)
    if args.json:
        print(json.dumps(prof, indent=2))
        return
    print(f"Profile: {prof['trade_title']} in {prof['state'] or 'no state set (state-only Parts and variations hidden)'}")
    print(f"Trade page: {prof['trade_page']}   State page: {prof['state_page']}")
    print(f"\nSkills: {', '.join(prof['skills'])}")
    print(f"Takeoff jobs: {', '.join(prof['takeoff_jobs']) or 'none (use the typical materials as a checklist)'}")
    print(f"\nNCC pages in scope ({len(prof['ncc_scope'])}):")
    for p in prof["ncc_scope"][:60]:
        print(f"  brain/ncc/2025/{p}.md")
    if len(prof["ncc_scope"]) > 60:
        print(f"  ... and {len(prof['ncc_scope']) - 60} more")
    if prof["state"]:
        print(f"\n{prof['state']} variations touching these pages: {len(prof['state_variations'])}")
        for v in prof["state_variations"][:25]:
            print("  " + v)
    if prof["typical_materials"]:
        print("\nTypical materials:\n  " + "\n  ".join(prof["typical_materials"]))
    if prof["suppliers"]:
        print("\nSuppliers:\n  " + "\n  ".join(prof["suppliers"]))


if __name__ == "__main__":
    main()

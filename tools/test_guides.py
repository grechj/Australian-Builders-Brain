"""Check the plain-English guides: they're found for the questions trades ask,
every figure they quote is pinned to the NCC text, and the pin really bites.

Usage:
    python tools/test_guides.py
"""

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ncc_lookup  # noqa: E402
import okf_lint  # noqa: E402

failures = 0


def expect(name: str, got, want) -> None:
    global failures
    if got == want:
        print(f"OK   {name}")
    else:
        failures += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def top(query: str, trade: str | None = None) -> str:
    found = ncc_lookup.guide_matches(query, trade, 1)
    return Path(found[0][1]["path"]).stem if found else ""


def main() -> None:
    # The questions trades actually ask land on the right guide.
    questions = {
        "how high does a deck balustrade need to be": "decks_balconies_and_stairs",
        "riser and going for outdoor steps": "decks_balconies_and_stairs",
        "waling plate fixing deck to house": "decks_balconies_and_stairs",
        "how high do I waterproof a shower wall": "wet_area_waterproofing",
        "falls to floor waste in bathroom": "wet_area_waterproofing",
        "does a timber deck need termite protection": "termite_management",
        "BAL 29 deck construction": "bushfire_construction",
        "7 star energy rating whole of home": "energy_efficiency",
        "where do smoke alarms go": "smoke_alarms",
        "minimum ceiling height bedroom": "room_heights",
        "vapour barrier under a slab": "footings_and_slabs",
        "how deep do deck stumps go": "footings_and_slabs",
        # Material guides
        "what treatment level for retaining wall posts": "timber_treatment_and_grades",
        "MGP10 vs MGP12 framing grade": "timber_treatment_and_grades",
        "which screws for treated pine near the coast": "fixings_and_corrosion",
        "merbau or spotted gum decking boards": "decking",
        "fire rated plasterboard garage wall": "plasterboard_and_linings",
        "what grade concrete for a driveway": "concrete",
        "how many premix bags": "concrete",
        "silicone or polyurethane sealant": "membranes_and_sealants",
        "liquid membrane bond breaker": "membranes_and_sealants",
        "ceiling batts R value compressed": "insulation",
        "vapour permeable wall wrap condensation": "sarking_and_wraps",
        "primer for galvanised steel": "paint_systems",
    }
    for q, want in questions.items():
        expect(f"guide for '{q}'", top(q), want)
    expect("trade filter keeps a tiler on wet areas", top("waterproofing shower", "tiler"), "wet_area_waterproofing")
    expect("trade filter hides guides for other trades", ncc_lookup.guide_matches("shower waterproofing", "electrician", 3), [])

    # Every guide pins its figures to the NCC, and links into the NCC land on real clauses.
    guides = [p for p in (ROOT / "brain" / "guides").rglob("*.md") if p.name != "index.md"]
    code_guides = [p for p in guides if p.parent.name == "code"]
    missing = [p.name for p in code_guides if "checks:" not in p.read_text()]
    expect("every code guide pins its figures (checks:)", missing, [])
    expect("nine material guides", len([p for p in guides if p.parent.name == "materials"]), 9)
    both = [p.name for p in code_guides if "/ncc/2022/" not in p.read_text() or "/ncc/2025/" not in p.read_text()]
    expect("every code guide cites both NCC 2022 and 2025", both, [])
    errors: list[str] = []
    okf_lint.check_anchors_and_quotes(errors)
    expect("all pinned figures and clause links check out", errors, [])

    # The pin bites: a guide quoting the wrong figure, or a missing clause, fails the lint.
    with tempfile.TemporaryDirectory() as tmp:
        brain = Path(tmp) / "brain"
        page = brain / "ncc" / "2025" / "housing_provisions" / "11_3_barriers_and_handrails.md"
        page.parent.mkdir(parents=True)
        shutil.copy(ROOT / "brain" / "ncc" / "2025" / "housing_provisions" / page.name, page)
        bad = brain / "guides" / "code" / "bad.md"
        bad.parent.mkdir(parents=True)
        bad.write_text("---\ntype: Reference\ntitle: Bad\nchecks:\n"
                       "  - { page: /ncc/2025/housing_provisions/11_3_barriers_and_handrails.md, text: \"not less than 900 mm above the floor of any landing\" }\n"
                       "---\n[x](/ncc/2025/housing_provisions/11_3_barriers_and_handrails.md#11_3_99)\n")
        saved = okf_lint.BRAIN
        okf_lint.BRAIN = brain
        try:
            errors = []
            okf_lint.check_anchors_and_quotes(errors)
        finally:
            okf_lint.BRAIN = saved
        expect("a wrong figure is caught", any("checks text not found" in e for e in errors), True)
        expect("a link to a clause that doesn't exist is caught", any("isn't on that page" in e for e in errors), True)

    p = subprocess.run([sys.executable, str(ROOT / "tools" / "ncc_lookup.py"), "search", "balustrade height deck",
                        "--volume", "housing_provisions", "--limit", "2"], capture_output=True, text=True)
    expect("a code search points to the plain-English guide", "decks_balconies_and_stairs.md" in p.stdout, True)

    print(f"\n{'all guide checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

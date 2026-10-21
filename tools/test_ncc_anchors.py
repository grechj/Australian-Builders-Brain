"""Check the NCC anchor repair: state-added clauses get anchors, NCC 2022 state
clauses answer to their plain code, dead anchors fall back to the page, it
changes nothing the second time, and nothing in the brain links to an anchor
that isn't there.

Usage:
    python tools/test_ncc_anchors.py
"""

import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import ncc_anchor_repair as r  # noqa: E402
import ncc_lookup  # noqa: E402

failures = 0


def expect(name, got, want):
    global failures
    if got == want:
        print(f"OK   {name}")
    else:
        failures += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


NATIONAL = """---
type: Code Reference
---

<a id="10_2_32"></a>

### 10.2.32 Something

Text, see [SA 10.2.33](#10_2_33) and [Part 13.2](/ncc/2025/housing_provisions/13_2.md#part_ariation)
and [NT Table 13.7.3](#table_abc).

> **SA variation**: SA adds 10.2.33 Provision of floor wastes.
>
> A floor waste is required.
>

> **NSW variation**: NSW replaces 10.2.32 Something.
>
> Other text.
>
"""

STATE_2022 = """---
type: Code Reference
---

<a id="nsw_9_4_3"></a>

### NSW 9.4.3 Construction of walls

(1) A wall must be built.
"""


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        brain = Path(tmp) / "brain"
        n25 = brain / "ncc" / "2025" / "housing_provisions"
        n22 = brain / "ncc" / "2022" / "housing_provisions"
        n25.mkdir(parents=True)
        n22.mkdir(parents=True)
        (n25 / "10_2.md").write_text(NATIONAL)
        (n25 / "13_2.md").write_text("---\ntype: Code Reference\n---\n\nPart 13.2\n")
        (n22 / "nsw_part_9_4.md").write_text(STATE_2022)
        (n22 / "state_variations.md").write_text("| NSW | adds | [9.4.3](/ncc/2022/housing_provisions/nsw_part_9_4.md#9_4_3) |\n")
        saved = r.BRAIN
        r.BRAIN = brain
        try:
            s25 = r.repair("2025")
            s22 = r.repair("2022")
            again = (r.repair("2025"), r.repair("2022"))
            dead = r.dead_links()
        finally:
            r.BRAIN = saved
        page = (n25 / "10_2.md").read_text()
        expect("a clause SA adds gets its anchor, before the quoted variation",
               '<a id="10_2_33"></a>\n\n> **SA variation**: SA adds 10.2.33' in page, True)
        expect("a replaced clause already anchored isn't anchored twice", page.count('<a id="10_2_32"></a>'), 1)
        expect("a Part variation link points at the page", "[Part 13.2](/ncc/2025/housing_provisions/13_2.md)" in page, True)
        expect("a link to an unanchored table on the same page becomes plain text", "and NT Table 13.7.3." in page, True)
        expect("2025 counts", s25, {"variation_anchors": 1, "plain_state_anchors": 0, "links_to_page": 2})
        state = (n22 / "nsw_part_9_4.md").read_text()
        expect("NCC 2022 state clause answers to its plain code", '<a id="9_4_3"></a><a id="nsw_9_4_3"></a>' in state, True)
        expect("2022 counts", s22, {"variation_anchors": 0, "plain_state_anchors": 1, "links_to_page": 0})
        zero = {"variation_anchors": 0, "plain_state_anchors": 0, "links_to_page": 0}
        expect("running it again changes nothing", again, (zero, zero))
        expect("no dead links left in the test pages", dead, [])
        expect("the clause lookup still sees the state clause under its own anchor",
               [m.group(1) for m in ncc_lookup.BLOCK.finditer(state)], ["nsw_9_4_3"])

    expect("nothing in the brain links to an anchor that isn't there", r.dead_links()[:5], [])
    print(f"\n{'all anchor checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

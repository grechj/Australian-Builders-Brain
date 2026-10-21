"""Check the product catalogue: lines land in the right family, pack sizes are
read correctly off product names, the cheapest pack mix is right, and the
brain page is current.

Usage:
    python tools/test_catalogue.py
"""

import sys
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import catalogue  # noqa: E402

failures = 0


def expect(name, got, want):
    global failures
    if got == want:
        print(f"OK   {name}")
    else:
        failures += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def main() -> None:
    for text, fam in {
        "Joists 140x45 H3 treated pine": "framing_timber",
        "Decking boards 90x19 merbau": "decking",
        "Decking screws stainless or class 4": "decking_screws",
        "Plasterboard screws": "plasterboard_screws",
        "Concrete premix 20 kg bags": "premix_concrete",
        "Wall wrap vapour permeable": "sarking_and_wrap",
        "Insulation batts R6.0 ceiling batts": "insulation_batts",
        "Sleepers 200x75 H4 treated pine sleeper": "sleepers",
        "Paint low sheen acrylic": "paint",
        "Waterproofing membrane liquid": "membrane",
        "Slotted drainage pipe with sock": "ag_pipe",
    }.items():
        expect(f"'{text}' is {fam}", catalogue.family_of(text), fam)

    for product, unit, want in [
        ("Low Sheen White 10L", "litres", "10"),
        ("Primer sealer undercoat 4 Litre", "litres", "4"),
        ("316 stainless decking screws 10g x 50mm - 500 pack", "screws", "500"),
        ("Galvanised triple grip 20pk", "each", "20"),
        ("Box of 1000 plasterboard screws", "each", "1000"),
        ("Wall wrap 2.75 x 30m", "m²", "82.5"),
        ("Builders film 4m x 50m 200um", "m²", "200"),
        ("Foil sarking 1350mm x 30m", "m²", "40.5"),
        ("Agpipe 100mm x 20m slotted with sock", "lineal metres", "20"),
        ("Cup head bolt M12 x 150mm galvanised", "each", None),       # a bolt size, not a pack
        ("140x45 H3 treated pine 4.8m", "lengths of 4.8 m", None),   # sold as one length
        ("Concrete mix 20kg", "bags", None),                         # the bag is the unit
    ]:
        r = catalogue.infer_pack(product, unit)
        expect(f"pack size of '{product}' in {unit}", str(r[0]) if r else None, want)

    D = Decimal
    expect("23 L from 4/10/15 L tins", catalogue.cheapest_mix(D("23"), [(D(4), D(89)), (D(10), D(199)), (D(15), D(279))]),
           [(D(15), 1), (D(4), 2)])
    expect("exact fit wins a tie on price", catalogue.cheapest_mix(D("20"), [(D(10), D(100)), (D(4), D(40))]), [(D(10), 2)])
    expect("936 screws from boxes of 500 and 1000", catalogue.cheapest_mix(D("936"), [(D(500), D(120)), (D(1000), D(200))]),
           [(D(1000), 1)])
    expect("same paint in two sizes compares equal",
           catalogue.base_name("Acrylic low sheen white 4L") == catalogue.base_name("Acrylic Low Sheen White 10 L"), True)
    expect("different paint doesn't", catalogue.base_name("Acrylic low sheen white 4L") == catalogue.base_name("Acrylic matt white 4L"), False)
    expect("catalogue page is current", (ROOT / "brain/references/product_catalogue.md").read_text() == catalogue.page(), True)

    print(f"\n{'all catalogue checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

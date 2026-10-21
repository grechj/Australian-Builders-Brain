"""Tests for tools/price_list.py matching: the wrong size, length or treatment must never match.

Usage:
    python tools/test_price_list.py
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("price_list", ROOT / "tools" / "price_list.py")
pl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pl)

CASES = [
    # (wanted, product, should match)
    ("140x45 H3 treated pine 3.6m", "140 x 45 H3 Treated Pine 3.6 m", True),
    ("cup head bolt M12 galvanised", "Cup head bolt M12 x 150mm galvanised", True),
    ("140x45 H3 treated pine 3.6m", "140x45 H3 treated pine 4.8m", False),   # wrong length
    ("90x90 H4 treated pine 2.4m", "90x90 H3 treated pine 2.4m", False),     # wrong treatment class
    ("90x45 MGP10 pine 2.4m", "90x35 MGP10 pine 2.4m", False),               # wrong section
    ("concrete mix 20kg", "Concrete mix 30kg", False),                       # wrong bag size
]


def main() -> None:
    failures = 0
    for want, product, expect in CASES:
        got = pl.score(want, product) >= 0.6
        ok = got == expect
        failures += not ok
        print(("OK   " if ok else "FAIL ") + f"{want!r} vs {product!r}: {'match' if got else 'no match'}")

    # End to end: the example deck takeoff against the example price list.
    with tempfile.TemporaryDirectory() as tmp:
        job = {"type": "timber_deck", "length_m": 4.8, "width_m": 3.6, "joist_size": "140x45 H3 treated pine",
               "bearer_size": "2/140x45 H3 treated pine", "post_size": "90x90 H4 treated pine", "board": "90x22 H3 treated pine decking"}
        takeoff = Path(tmp) / "takeoff.json"
        takeoff.write_text(subprocess.run([sys.executable, str(ROOT / "tools/compute.py"), "materials_takeoff", "--param", "job=" + json.dumps(job)],
                                          capture_output=True, text=True, check=True).stdout)
        out = subprocess.run([sys.executable, str(ROOT / "tools/price_list.py"), "match", str(takeoff),
                              "--prices", str(ROOT / "examples/price_list_example.csv"), "--no-log"], capture_output=True, text=True, check=True)
        result = json.loads(out.stdout)
        missing = [x["item"] for x in result["to_look_up"]]
        ok = missing == ["Concrete premix"]
        failures += not ok
        print(("OK   " if ok else "FAIL ") + f"deck example: {result['summary']}; to look up: {missing}")

        # Pack sizes, per-metre prices and tin mixes (catalogue-aware matching). Prices are made up.
        prices = Path(tmp) / "prices.csv"
        prices.write_text(
            "product,item_number,unit,pack_size,price_inc_gst,supplier,url,checked_on,notes\n"
            f"Acrylic low sheen white 4L,,tin,1,89.00,Test,,{pl.date.today().strftime('%d/%m/%Y')},\n"
            f"Acrylic low sheen white 10L,,tin,1,199.00,Test,,{pl.date.today().strftime('%d/%m/%Y')},\n"
            f"Acrylic low sheen white 15L,,tin,1,279.00,Test,,{pl.date.today().strftime('%d/%m/%Y')},\n"
            f"Decking screws stainless 10g x 50mm 500 pack,,box,1,120.00,Test,,{pl.date.today().strftime('%d/%m/%Y')},\n"
            f"90x19 merbau decking,,metre,1,9.50,Test,,{pl.date.today().strftime('%d/%m/%Y')},\n")
        lines = {"items": [
            {"key": "paint", "item": "Paint", "spec": "", "quantity": "23", "unit": "litres", "search": "acrylic low sheen white"},
            {"key": "decking_screws", "item": "Decking screws", "spec": "", "quantity": "936", "unit": "screws", "search": "decking screws stainless"},
            {"key": "decking", "item": "Decking boards", "spec": "", "quantity": "41", "unit": "lengths of 5.4 m", "search": "90x19 merbau decking"}]}
        tk = Path(tmp) / "lines.json"
        tk.write_text(json.dumps({"result": lines}))
        out = json.loads(subprocess.run([sys.executable, str(ROOT / "tools/price_list.py"), "match", str(tk), "--prices", str(prices)],
                                        capture_output=True, text=True, check=True).stdout)
        got = {(l["item"], l.get("pack_size"), l.get("quantity"), l.get("unit_price_inc_gst")) for l in out["lines"]}
        checks = {
            # 23 L: one 15 L tin and two 4 L tins ($457) beat 10 + 10 + 4 ($487) and 15 + 10 ($478)
            "cheapest mix of tins": {("Paint (15 litres each)", "15", "15", "279.00"), ("Paint (4 litres each)", "4", "8", "89.00")} <= got,
            # the box price is for 500 screws, read off the name, not 1 screw
            "pack size read from the product name": ("Decking screws", "500", "936", "120.00") in got,
            # $9.50 a metre x 5.4 m length
            "per-metre price turned into the length": ("Decking boards", "1", "41", "51.30") in got,
        }
        for name, ok in checks.items():
            failures += not ok
            print(("OK   " if ok else "FAIL ") + name)
        if not all(checks.values()):
            print(json.dumps(out["lines"], indent=2))
        log = Path(tmp) / "materials_log.csv"
        logged = log.read_text() if log.exists() else ""
        ok = "Decking screws" in logged and "51.30" not in logged and "9.50" not in logged and "120.00" not in logged
        failures += not ok
        print(("OK   " if ok else "FAIL ") + "products used are logged next to the price list, without prices")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

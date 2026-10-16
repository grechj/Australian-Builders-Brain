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
                              "--prices", str(ROOT / "examples/price_list_example.csv")], capture_output=True, text=True, check=True)
        result = json.loads(out.stdout)
        missing = [x["item"] for x in result["to_look_up"]]
        ok = missing == ["Concrete premix"]
        failures += not ok
        print(("OK   " if ok else "FAIL ") + f"deck example: {result['summary']}; to look up: {missing}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

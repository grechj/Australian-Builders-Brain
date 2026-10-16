"""Tests for trade and location filtering (tools/profile.py, tools/ncc_lookup.py).

Usage:
    python tools/test_profile.py
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from profile import resolve_profile, trades  # noqa: E402

failures = 0


def check(name: str, ok: bool) -> None:
    global failures
    failures += not ok
    print(("OK   " if ok else "FAIL ") + name)


def lookup(*args: str) -> str:
    return subprocess.run([sys.executable, str(ROOT / "tools/ncc_lookup.py"), *args], capture_output=True, text=True).stdout


elec = resolve_profile("sparky", "QLD")
check("alias 'sparky' resolves to electrician", elec["trade"] == "electrician")
check("electrician scope includes smoke alarms", "housing_provisions/9_5_smoke_alarms_and_evacuation_lighting" in elec["ncc_scope"])
check("electrician scope excludes footings", not any(p.startswith("housing_provisions/4_") for p in elec["ncc_scope"]))
builder = resolve_profile("builder", "NSW")
check("builder sees far more than an electrician", len(builder["ncc_scope"]) > 10 * len(elec["ncc_scope"]))
check("all = builder scope", len(resolve_profile("all", "NSW")["ncc_scope"]) == len(builder["ncc_scope"]))
vic, nsw = resolve_profile("plumber", "VIC"), resolve_profile("plumber", "NSW")
check("VIC plumber gets VIC-only Volume Three Parts", any("vic_part_" in p for p in vic["ncc_scope"]))
check("NSW plumber gets no other state's Parts", not any("_part_" in p.split("/")[1] and p.split("/")[1].split("_")[0] in ("vic", "tas", "wa", "sa", "nsw", "nt", "qld", "act") for p in nsw["ncc_scope"]))
check("state variations are only the profile's state", all(v.startswith("| NSW |") for v in builder["state_variations"]))
check("every trade page resolves", all(resolve_profile(t, "NSW")["trade"] == t for t in trades()))
out_all, out_nsw, out_qld = lookup("clause", "A2G2", "--volume", "volume_two"), lookup("clause", "A2G2", "--volume", "volume_two", "--state", "NSW"), lookup("clause", "A2G2", "--volume", "volume_two", "--state", "QLD")
check("unfiltered clause shows several states' variations", "NSW variation" in out_all and "VIC variation" in out_all)
check("--state NSW shows only NSW's variation", "NSW variation" in out_nsw and "VIC variation" not in out_nsw)
check("--state QLD hides other states' variations", "variation" not in out_qld)
check("--trade keeps an electrician out of footings", "4.2.2" not in lookup("clause", "4.2.2", "--trade", "electrician"))
# NCC 2022
e22 = resolve_profile("electrician", "NSW", "2022")
check("NCC 2022: electrician scope resolves", len(e22["ncc_scope"]) >= 10 and e22["ncc_edition"] == "2022")
check("NCC 2022: VIC plumber gets VIC-only Volume Three Parts", any("vic_part_" in p for p in resolve_profile("plumber", "VIC", "2022")["ncc_scope"]))
h22_sa, h22_nsw = lookup("--edition", "2022", "clause", "H2D4", "--state", "SA"), lookup("--edition", "2022", "clause", "H2D4", "--state", "NSW")
check("NCC 2022: H2D4 shows SA's variations for SA", "SA variation" in h22_sa)
check("NCC 2022: H2D4 hides SA's variations and markers for NSW", "SA" not in h22_nsw and "H2D4" in h22_nsw)
check("NCC 2022 pages carry the amendment notice", "Amendment 2" in (ROOT / "brain/ncc/2022/volume_two/h2_damp_and_weatherproofing.md").read_text())
sys.exit(1 if failures else 0)

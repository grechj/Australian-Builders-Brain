"""Hand-checked tests for the materials takeoff (brain/references/computations/materials.py).

Usage:
    python tools/test_takeoff.py

Each expected figure was worked out by hand from the rule in the takeoff's
`basis`. If a rule changes on purpose, re-check by hand and update here.
"""

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("materials", ROOT / "brain/references/computations/materials.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

CASES = [
    # (job, {item key: expected quantity})
    ({"type": "timber_deck", "length_m": 4.8, "width_m": 3.6, "bearer_size": "2/140x45 H3"},
     {"joists": "12", "bearers": "6", "decking": "41", "decking_screws": "936", "concrete": "69"}),
    ({"type": "electrical_rough_in", "power_points": 14, "light_points": 12, "smoke_alarms": 3, "data_points": 2},
     # power (14x7 + 2x15) x 1.1 = 140.8 m -> 2 rolls; lighting (12x5 + 4x4 + 15) x 1.1 = 100.1 m -> 2 rolls
     {"power_cable": "2", "lighting_cable": "2", "switches": "4", "rcbos": "3", "data_cable": "1", "smoke_cable": "20"}),
    ({"type": "plumbing_rough_in", "toilets": 1, "basins": 1, "showers": 1},
     # water (5 outlets x 6 + 25) x 1.1 = 60.5 m -> 2 coils; 100 mm (3 + 15) x 1.1 / 6 -> 4; 50 mm 6 x 1.1 / 6 -> 2
     {"water_pipe": "2", "water_fittings": "15", "drain_100": "4", "drain_50": "2", "valves": "5", "tempering_valve": "1"}),
    ({"type": "roofing", "building_length_m": 10, "building_width_m": 6},
     # plan 10.6 x 6.9 / cos 22.5 = 79.17 m2; 2 x ceil(10.6 / 0.762) = 28 sheets x 3.734 m x 1.1 = 115.01 m
     {"roof_area": "79.17", "sheets": "115.01", "battens": "24", "screws": "555", "gutter": "23.32", "downpipes": "2"}),
    ({"type": "roofing", "building_length_m": 10, "building_width_m": 6, "roof_type": "hip", "material": "tile"},
     # ridge 3.1 m + 4 hips of 5.084 m = 23.44 m x 3 x 1.1 -> 78 ridge tiles; gutter 2 x (10 + 6.9) = 33.8 m x 1.1
     {"roof_area": "74.69", "tiles": "863", "ridge_tiles": "78", "gutter": "37.18", "downpipes": "4"}),
    ({"type": "cladding", "length_m": 10, "height_m": 2.7, "openings_m2": 4, "external_corners": 2, "cavity": True},
     # (27 - 4) m2 x 1000 / 150 mm = 153.33 m x 1.1 / 4.2 m -> 41 boards; 18 rows x 18 studs x 1.1 -> 357;
     # wrap 27 x 1.1; battens 18 studs x 2 lengths; corners 2 x 2.7 x 1.1 / 3 -> 2
     {"boards": "41", "fixings": "357", "wrap": "29.70", "cavity_battens": "36", "corners": "2"}),
    ({"type": "cladding", "length_m": 10, "height_m": 2.7, "cladding_type": "sheet"},
     # 27 m2 / 3.24 m2 x 1.1 -> 10 sheets; 27 x 12 x 1.1 -> 357 fixings
     {"sheets": "10", "fixings": "357"}),
    ({"type": "insulation", "area_m2": 100, "pack_m2": 8.4, "r_value": "R6.0"},
     # 100 x 1.05 = 105 m2 / 8.4 -> 13 packs
     {"batts": "13"}),
    ({"type": "insulation", "length_m": 10, "width_m": 8},
     {"batts": "84.00"}),
    ({"type": "retaining_wall", "length_m": 6, "height_m": 0.8},
     # 0.8 / 0.2 = 4 rows x ceil(6 / 2.4) = 3 -> 12; 6 / 1.2 + 1 = 6 posts at 1.6 m;
     # 6 x 0.3 x 0.3 x 0.8 = 0.432 m3 / 0.0095 -> 46 bags; gravel 6 x 0.8 x 0.3; fabric 6 x 1.4 x 1.1
     {"sleepers": "12", "posts": "6", "concrete": "46", "fixings": "48", "ag_pipe": "6.60", "gravel": "1.44", "geofabric": "9.24"}),
    ({"type": "pergola", "length_m": 6, "width_m": 4, "roof": "sheet"},
     # 2 x (6 / 3 + 1) = 6 posts; 6000 / 900 -> 7 + 1 = 8 rafters; 6 x 0.3 x 0.3 x 0.6 / 0.0095 -> 35 bags;
     # ceil(6 / 0.762) = 8 sheets; 8 x 8 x 3 x 1.1 -> 212 screws
     {"posts": "6", "beams": "2", "rafters": "8", "rafter_brackets": "16", "concrete": "35", "roof_sheets": "8", "roof_screws": "212"}),
]


def main() -> None:
    failures = 0
    for job, expected in CASES:
        items = {i["key"]: i["quantity"] for i in m.materials_takeoff(job)["result"]["items"]}
        for key, want in expected.items():
            ok = items.get(key) == want
            failures += not ok
            if not ok:
                print(f"FAIL {job['type']} {key}: expected {want}, got {items.get(key)}")
        print(("OK   " if all(items.get(k) == v for k, v in expected.items()) else "FAIL ") + f"{job['type']} {job.get('roof_type', '')}".strip())
    for bad in ({"type": "cladding", "length_m": 5, "cladding_type": "brick"}, {"type": "pergola", "length_m": 3, "width_m": 3, "roof": "tile"},
                {"type": "retaining_wall", "length_m": 5}, {"type": "electrical_rough_in"}, {"type": "plumbing_rough_in"}, {"type": "roofing", "building_length_m": 5, "building_width_m": 4, "roof_type": "dome"}):
        try:
            m.materials_takeoff(bad)
            print(f"FAIL {bad} should be refused"); failures += 1
        except ValueError:
            print(f"OK   refuses {bad}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

---
type: Attested Computation
title: Materials takeoff
description: Turns a job (timber deck, stud wall, plasterboard, concrete slab, paling fence, tiling, painting, electrical rough-in, plumbing rough-in, roofing) into a materials list with quantities, purchase lengths or packs, and the rule behind each line.
tags: [materials, estimating, takeoff, quantities]
status: draft
runtime: python
computation: /references/computations/materials.py
entry_point: materials_takeoff
computation_sha256: b4456331c0e09e517064fa29ec70801d162d197bf3df106ae407e750328a1a95
parameters:
  - { name: job, type: json, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-17T00:00:00Z }
---

> **Draft: rules of thumb.** The quantity rules are standard estimating
> practice, but spacings, coverages and waste allowances vary by product and
> site. Every default the computation used is listed in `assumptions`:
> check them, and override any that don't suit the job.

# Definition

`job` is JSON with a `type` and its dimensions. Anything not given falls
back to a default, which is then reported in `assumptions`.

| type | Required | Main options (defaults) |
|---|---|---|
| `timber_deck` | `length_m` (along the boards), `width_m` | `height_m` 0.6, `joist_spacing_mm` 450, `bearer_spacing_mm` 1800, `post_spacing_mm` 1800, `board_width_mm` 90, `board_gap_mm` 4, `board_length_m` 5.4, `footing_mm` 300, `footing_depth_mm` 600, `joist_size`, `bearer_size`, `post_size`, `board` |
| `stud_wall` | `length_m` | `height_m` 2.4, `stud_spacing_mm` 450, `openings` 0, `junctions` 0, `stud_size` (non-load-bearing only) |
| `plasterboard` | `length_m`, `width_m` (room) or `area_m2` | `height_m` 2.4, `ceiling` true, `openings_m2` 0, `sheet_length_m` 2.4, `spare_pct` 10, `screws_per_m2` 14, `compound_kg_per_m2` 0.6, `board` |
| `concrete_slab` | `length_m`, `width_m` | `thickness_mm` 100, `waste_pct` 10, `bar_chair_spacing_m` 0.8, `mesh` SL72 (paths and shed slabs only) |
| `paling_fence` | `length_m` | `height_m` 1.8, `post_spacing_m` 2.4, `paling_cover_mm` 100, `rails` (3 over 1.5 m), `concrete_bags_per_post` 2 |
| `tiling` | `area_m2` | `tile_length_mm` 600, `tile_width_mm` 300, `joint_mm` 3, `waste_pct` 10, `box_m2` 1.44, `adhesive_kg_per_m2` 4, `waterproofing_m2` 0 |
| `painting` | `area_m2` | `coats` 2, `coverage_m2_per_l` 16, `primer` false |
| `electrical_rough_in` | at least one of `power_points`, `light_points`, `smoke_alarms`, `data_points`, `fan_points` | `switch_locations` (1 per 3 lights), `power_circuits` (8 points each), `lighting_circuits` (15 each), `power_run_m` 7, `light_run_m` 5, `switch_drop_m` 4, `board_distance_m` 15, `data_run_m` 25, `cable_roll_m` 100 |
| `plumbing_rough_in` | a count of any of `toilets`, `basins`, `showers`, `baths`, `kitchen_sinks`, `laundry_tubs`, `washing_machines`, `dishwashers`, `external_taps` | `water_run_m` 6, `cold_main_m` 15, `hot_main_m` 10, `drain_branch_m` 3, `drain_main_m` 15, `fittings_per_outlet` 3, `water_pipe` 16 mm PEX |
| `roofing` | `building_length_m` (along the ridge), `building_width_m` | `roof_type` gable, hip or skillion; `pitch_deg` 22.5 (skillion 5); `eave_overhang_m` 0.45; `gable_overhang_m` 0.3; `material` sheet or tile; `sheet_cover_m` 0.762; `batten_spacing_m` 0.9 (tile 0.33); `screws_per_sheet_per_batten` 3; `tiles_per_m2` 10.5; `downpipe_spacing_m` 12 |

Each item in the result has the quantity and unit to buy, its `basis` (the
arithmetic, so it can be checked), and a `search` phrase for finding the
product. Timber is counted by member and matched to stock lengths (2.4 m
to 6.0 m); members longer than 6 m are joined.

Roof area is plan area (with overhangs) ÷ cos(pitch), which holds for gable,
hip and skillion roofs alike; hip and ridge lengths come from the geometry.
Electrical and plumbing takeoffs count points and fixtures and use average
runs. They never design circuits or size pipes: that is the licensed
electrician's or plumber's job (AS/NZS 3000, AS/NZS 3500).

The computation counts quantities only. It never sizes structural members:
joist, bearer, post and stud sizes come from AS 1684, the supplier's span
tables or an engineer, and the user passes them in as text.

# Computation

Runs `materials_takeoff()` in [materials.py](/references/computations/materials.py).

    python tools/compute.py materials_takeoff --param 'job={"type": "timber_deck", "length_m": 4.8, "width_m": 3.6}'

Price the result with [materials ROM](/computations/materials_rom.md).

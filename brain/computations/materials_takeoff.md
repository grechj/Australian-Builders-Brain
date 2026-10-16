---
type: Attested Computation
title: Materials takeoff
description: Turns a job (timber deck, stud wall, plasterboard, concrete slab, paling fence, tiling, painting) into a materials list with quantities, purchase lengths or packs, and the rule behind each line.
tags: [materials, estimating, takeoff, quantities]
status: draft
runtime: python
computation: /references/computations/materials.py
entry_point: materials_takeoff
computation_sha256: 11c90ecedca08a612db3acfff06f635d138941f1627e925c6550b3cd5dc37d4c
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

Each item in the result has the quantity and unit to buy, its `basis` (the
arithmetic, so it can be checked), and a `search` phrase for finding the
product. Timber is counted by member and matched to stock lengths (2.4 m
to 6.0 m); members longer than 6 m are joined.

The computation counts quantities only. It never sizes structural members:
joist, bearer, post and stud sizes come from AS 1684, the supplier's span
tables or an engineer, and the user passes them in as text.

# Computation

Runs `materials_takeoff()` in [materials.py](/references/computations/materials.py).

    python tools/compute.py materials_takeoff --param 'job={"type": "timber_deck", "length_m": 4.8, "width_m": 3.6}'

Price the result with [materials ROM](/computations/materials_rom.md).

---
type: Attested Computation
title: Materials rough order of magnitude
description: Prices a materials list from unit prices (for example Bunnings retail prices), works out packs to buy, and gives the total inc and ex GST with a rough order of magnitude range.
tags: [materials, estimating, pricing, rom]
status: stable
runtime: python
computation: /references/computations/materials.py
entry_point: materials_rom
computation_sha256: b4456331c0e09e517064fa29ec70801d162d197bf3df106ae407e750328a1a95
parameters:
  - { name: lines, type: json, required: true }
  - { name: low_pct, type: decimal, required: false, default: 15 }
  - { name: high_pct, type: decimal, required: false, default: 30 }
  - { name: location_loading_pct, type: decimal, required: false, default: 0 }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-17T00:00:00Z }
---

# Definition

For each line: **packs** = quantity ÷ `pack_size`, rounded up (a box of 500
screws, a 4 L tin; `pack_size` 1 when the price is per unit), and the line
total = packs × unit price inc GST. Lines with no price are listed in
`unpriced` and left out of the total. Say so, and don't present the total
as complete.

- **Location loading**: `location_loading_pct` adds freight or remoteness on top of the priced lines, for regional and remote jobs priced from metro retail. Take the figure from local suppliers or the user, never guess it, and leave it at 0 when prices are already local. The [state pages](/states/index.md) say where loadings are typical.
- Total inc GST (priced lines plus any loading), its GST (1/11), and ex GST
- **Rough order of magnitude range**: total − `low_pct` to total + `high_pct` (default −15% / +30%). The range is skewed upwards because takeoffs usually miss items and retail prices move.

A ROM is for deciding whether a job is worth pursuing and for budgeting.
It is not a quote: see [materials estimating](/contracts/materials_estimating.md)
for the qualifications that must go with it.

# Computation

Runs `materials_rom()` in [materials.py](/references/computations/materials.py).

    python tools/compute.py materials_rom --param 'lines=[{"item": "Decking screws", "quantity": 936, "pack_size": 500, "unit_price_inc_gst": 89.00}]'

---
type: Reference
title: Product catalogue (what materials are sold as)
description: Supplier-neutral stock sizes and pack sizes for common building materials, and how the brain turns a takeoff quantity into things to buy. No prices.
tags: [materials, catalogue, packs, stock_lengths, pricing]
status: draft
generated: { by: tool:catalogue.py, at: 2026-10-21T00:00:00Z }
---

> **Generated from `tools/catalogue.yaml`** by `python tools/catalogue.py page`. Edit the YAML, not this page.
> "Usual" sizes are what's commonly stocked in Australia: always check the actual product.

Prices never live here: each user keeps their own (see [materials estimating](/contracts/materials_estimating.md)).
When the brain matches a takeoff line to a user's price, it uses this catalogue to:

- read the pack size off the product's name (a 10 L tin, a box of 500 screws, a 1.35 x 30 m roll) when it isn't recorded;
- convert a per-metre price to the stock length the takeoff counts;
- buy the cheapest mix of pack sizes when the user has prices for more than one (two 10 L tins and a 4 L tin, say).

| Family | Sold as | Usual stock | Notes |
|---|---|---|---|
| [Framing and structural timber (pine, hardwood, LVL)](/guides/materials/timber_treatment_and_grades.md) | length | sizes 70x35, 70x45, 90x35, 90x45, 140x45, 190x45, 240x45, 290x45; lengths 2.4, 3, 3.6, 4.2, 4.8, 5.4, 6 m | Match section, grade (MGP10, MGP12, F17) and treatment (H2, H3) exactly. Some timber is priced per metre; the price list converts it to the length. |
| [Posts](/guides/materials/timber_treatment_and_grades.md) | length | sizes 90x90, 100x100, 125x125, 100x75; lengths 2.4, 2.7, 3, 3.6 m | In-ground structural posts H5; fence posts H4; posts on stirrups H3 or hardwood. |
| [Decking boards](/guides/materials/decking.md) | length | sizes 70x19, 86x19, 90x19, 140x19, 90x22, 140x22; lengths 1.8, 2.4, 3, 3.6, 4.2, 4.8, 5.4, 6 m | Hardwood is often priced per lineal metre in random lengths; pine and composite in set lengths. |
| [Landscaping sleepers](/guides/materials/timber_treatment_and_grades.md) | length | sizes 200x50, 200x75, 200x100; lengths 1.8, 2.4, 3 m | – |
| Fence palings and rails | each | sizes 100x12, 150x12; lengths 1.5, 1.65, 1.8, 2.1 m | – |
| [Plasterboard](/guides/materials/plasterboard_and_linings.md) | sheet | sizes 10mm, 13mm, 16mm; sheets 1.2x2.4, 1.2x2.7, 1.2x3.0, 1.2x3.6, 1.2x4.2, 1.2x4.8, 1.2x6.0, 1.35x2.4, 1.35x3.6, 1.35x4.8, 1.35x6.0 m | Match thickness, type (standard, ceiling, wet area, fire, impact) and sheet size. |
| [Fibre-cement sheet and cladding](/guides/materials/plasterboard_and_linings.md) | sheet | sizes 4.5mm, 6mm, 9mm; sheets 0.45x2.4, 1.2x1.8, 1.2x2.4, 1.2x2.7, 1.2x3.0 m | – |
| [Weatherboards](/guides/materials/sarking_and_wraps.md) | length | lengths 4.2, 4.8, 5.4 m | Cover per board depends on the profile and lap; check the maker's guide. |
| [Concrete premix bags](/guides/materials/concrete.md) | bag | 20 kg bags | Coverage: 0.0095 m³ per 20 kg bag (takeoff default; check the bag). The takeoff counts 20 kg bags; a 30 kg bag isn't a match. |
| [Ready-mix concrete](/guides/materials/concrete.md) | m3 | – | Not a hardware store product. Ordered by grade and slump from a concrete plant; minimum loads apply. |
| [Reinforcing mesh and trench mesh](/guides/materials/concrete.md) | sheet | sheets 6.0x2.4 m | Coverage: 12.76 m² per 6.0 x 2.4 sheet after 200 mm laps (takeoff default). |
| Bar chairs | pack | packs of 50, 100 | – |
| [Vapour barrier and builder's film](/guides/code/footings_and_slabs.md) | roll (priced per m²) | – | Read the roll's m² off the label (width x length) and use it as the pack size. Under house slabs it must be 0.2 mm, branded AS 2870. |
| [Decking and batten screws](/guides/materials/fixings_and_corrosion.md) | box | packs of 100, 200, 250, 500, 1000, 2000 | Stainless (304 or 316) or Class 4 to suit the treatment and distance from the coast. |
| Plasterboard screws | box | packs of 500, 1000, 2000 | – |
| Nails | box | packs of 100, 250, 500, 1000, 2000 | Some nails are sold by weight (1 kg, 5 kg); count per kg is on the box. |
| [Roofing screws](/guides/materials/fixings_and_corrosion.md) | box | packs of 50, 100, 250, 500, 1000 | Class 3 or 4 to the sheet maker's spec and the environment. |
| [Framing connectors (triple grips, joist hangers, stirrups, brackets)](/guides/materials/fixings_and_corrosion.md) | each | packs of 1, 10, 20, 50 | Often sold singly and in packs; match the finish (galvanised, stainless). |
| [Bolts and anchors](/guides/materials/fixings_and_corrosion.md) | each | packs of 1, 2, 4, 10, 25, 50 | – |
| [Paint, primer and sealer](/guides/materials/paint_systems.md) | tin | packs of 1, 2, 4, 10, 15 | Coverage: 16 m² per litre per coat (takeoff default for acrylic walls; check the tin). Buy the mix of tin sizes that costs least; the price list does this when it has prices for several sizes. |
| [Waterproofing membrane](/guides/materials/membranes_and_sealants.md) | tin | packs of 1, 4, 15 | Must be a wet area membrane to AS/NZS 4858 for bathrooms. |
| Tile adhesive | bag | 20 kg bags | – |
| Grout | bag | 2, 5 kg bags | – |
| Plaster jointing compound | bag | 4.5, 20 kg bags | – |
| Paper jointing tape | roll | packs of 75, 150 | – |
| Cornice | length | lengths 3.6, 4.2, 4.8, 6 m | – |
| [Sealants and adhesives (cartridges)](/guides/materials/membranes_and_sealants.md) | each | – | – |
| [Insulation batts](/guides/materials/insulation.md) | pack (priced per m²) | – | Read the m² per pack off the label for the R-value and width; pass it to the takeoff as pack_m2. |
| [Sarking, roof blanket and wall wrap](/guides/materials/sarking_and_wraps.md) | roll (priced per m²) | – | Read the roll's m² off the label and use it as the pack size. |
| Roof sheeting | lineal m | – | Cut to length; priced per lineal metre of sheet. Cover width depends on the profile (about 0.762 m corrugated). |
| Gutter and downpipe | length | lengths 3, 6 m | – |
| Slotted drainage pipe | roll (priced per lineal m) | packs of 20, 50 | – |
| Gravel, sand and soil | m3 | – | Bulk by the cubic metre from a landscape supplier, or in 20 to 25 kg bags for small jobs (gravel weighs about 1.5 to 1.7 tonnes per m³, so 60 to 85 bags of 20 to 25 kg; check the bag). |
| Geotextile fabric | roll (priced per m²) | – | – |

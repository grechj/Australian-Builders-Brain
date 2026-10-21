---
type: Reference
title: Fixings and corrosion
description: Choosing nails, screws, bolts and brackets that won't rust out (galvanised coating classes, 304 vs 316 stainless, treated pine, distance from the coast) and the NCC's corrosion rules for steel and deck attachments.
tags: [guides, materials, fixings, fasteners, corrosion, galvanised, stainless, treated_pine, coastal, carpenter]
status: draft
trades: [carpenter, builder, fencer, landscaper, roofer, steel_fixer]
sources:
  - id: ncc_2025_hp
    resource: https://ncc.abcb.gov.au/
    title: NCC 2025 Housing Provisions, Parts 6.3 and 12.3 (ABCB, CC BY 4.0)
  - id: woodsolutions_treatments
    resource: https://www.woodsolutions.com.au/publications/preservative-treatments-and-use-classes
    title: Preservative treatments and use classes (WoodSolutions)
  - id: anzor_stainless
    resource: https://www.anzor.co.nz/blog/use-stainless-steel-fasteners-with-treated-timber
    title: Use stainless steel fasteners with treated timber (Anzor, citing BRANZ)
checks:
  - { page: /ncc/2025/housing_provisions/6_3_structural_steel_members.md, text: "Typically extends from 100 m inland from breaking surf to 200 m inland from breaking surf" }
  - { page: /ncc/2025/housing_provisions/6_3_structural_steel_members.md, text: "Typically remote inland areas or more than 1 km from sheltered bays | HDG75" }
  - { page: /ncc/2025/housing_provisions/6_3_structural_steel_members.md, text: "when cut or welded on-site, have those areas and any other areas of damage to protective coatings comply with (a)" }
  - { page: /ncc/2025/housing_provisions/12_3_attachment_of_framed_decks_and_balconies_to_external_walls_of_buildings_using_a_waling_plate.md, text: "stainless steel where the building is located within 200 m of breaking surf" }
  - { page: /ncc/2025/housing_provisions/12_3_attachment_of_framed_decks_and_balconies_to_external_walls_of_buildings_using_a_waling_plate.md, text: "hot-dipped galvanised, stainless steel or monel metal for all other areas" }
generated: { by: claude/opus-5.5, at: 2026-10-21T00:00:00Z }
stale_after: 2027-10-21T00:00:00Z
---

> **Guide, draft.** Fixing schedules (what fixing, how many, where) come
> from AS 1684, the connector maker's tables or the engineer. This page is
> about choosing a fixing that lasts.

# Three things decide it

1. **Where the job is:** distance from breaking surf or a sheltered bay, and industrial fallout.
2. **What it's fixing into:** treated pine and some hardwoods attack plain and lightly galvanised steel.
3. **Whether it's exposed:** to rain, to splashing, or to salt spray in a sheltered spot that never gets rinsed.

# How far from the sea

The NCC's corrosion table for structural steel (Housing Provisions 6.3.9)
uses these environments:[^ncc_2025_hp]

| Environment | Typically | Hot-dip galvanising for steel members |
|---|---|---|
| Low | Remote inland, or more than 1 km from sheltered bays | HDG75 |
| Medium | More than 1 km from breaking surf, or more than 50 m from sheltered bays | HDG225 |
| High | More than 200 m from breaking surf, or within 50 m of sheltered bays | HDG450 (or a duplex system) |
| Very high | 100 to 200 m inland from breaking surf | HDG900 (or a duplex system) |

Within 100 m of breaking surf is more severe again: use stainless (316)
or an engineered system. Steel cut or welded on site has to be
re-protected to the same level. The figures are coating classes (grams of
zinc per square metre), so a bracket marked "galvanised" isn't
necessarily HDG450.

For decks attached to the house under NCC 2025 (Part 12.3), the fixings
must be **stainless within 200 m of breaking surf**, and hot-dip
galvanised, stainless or monel elsewhere.

# Treated pine

Modern copper-based treatments (ACQ, copper azole) are much harder on
fixings than the old CCA. Plain steel and electro-galvanised (zinc-plated)
fixings corrode in them.[^anzor_stainless]

- **Minimum:** hot-dip galvanised fixings and connectors in treated pine.[^woodsolutions_treatments]
- **Outside, wet, or near the coast:** stainless steel (304 or 316). Use **316** near the coast.
- **Class 4 coated screws** (a common decking and batten screw coating) are a step up from zinc plating but below stainless; check the maker's rating for the treatment and the environment.
- Don't mix metals: stainless screws through a galvanised bracket is fine; galvanised screws in a stainless bracket isn't.

# Quick picks

| Job | Inland | Coastal (within about 1 km of surf) |
|---|---|---|
| Decking screws into H3 pine or hardwood | Class 4 or stainless 304 | Stainless 316 |
| Joist hangers, triple grips, post stirrups | Hot-dip galvanised | Stainless, or heavier galvanising per the table above |
| Bolts through posts and bearers | Hot-dip galvanised | Stainless 316 |
| Framing nails inside the house (H2 framing) | Galvanised or bright as specified | Galvanised |
| Fence paling nails | Galvanised | Stainless or hot-dip galvanised |
| Roof sheeting screws | Class 3 to the sheet maker's spec | Class 4 or the maker's coastal spec |

See also: [timber treatment and grades](timber_treatment_and_grades.md),
[decking](decking.md), [decks, balconies and stairs](../code/decks_balconies_and_stairs.md).

[^ncc_2025_hp]: NCC 2025 Housing Provisions, Table 6.3.9a and Part 12.3.
[^woodsolutions_treatments]: WoodSolutions, Preservative treatments and use classes.
[^anzor_stainless]: Anzor, Use stainless steel fasteners with treated timber.

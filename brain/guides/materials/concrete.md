---
type: Reference
title: Concrete
description: Ordering concrete for house jobs (strength grades like N20 and N32, slump, aggregate, how much to order), premix bags for small pours, reinforcement and vapour barrier basics, curing, and the NCC's minimum for footings and slabs.
tags: [guides, materials, concrete, ready_mix, premix, n20, n25, n32, slump, curing, concreter, builder]
status: draft
trades: [concreter, builder, carpenter, landscaper, fencer, earthworks]
sources:
  - id: ncc_2025_hp
    resource: https://ncc.abcb.gov.au/
    title: NCC 2025 Housing Provisions, Part 4.2 (ABCB, CC BY 4.0)
  - id: holcim_standard
    resource: https://www.holcim.com.au/products-and-services/concrete-readymix/standard
    title: Standard concrete (Holcim Australia)
checks:
  - { page: /ncc/2025/housing_provisions/4_2_footings_slabs_and_associated_elements.md, text: "have a strength at 28 days of not less than 20 MPa (denoted as N20 grade)" }
  - { page: /ncc/2025/housing_provisions/4_2_footings_slabs_and_associated_elements.md, text: "have a 20 mm maximum nominal aggregate size" }
  - { page: /ncc/2025/housing_provisions/4_2_footings_slabs_and_associated_elements.md, text: "have a nominal 100 mm slump" }
  - { page: /ncc/2025/housing_provisions/4_2_footings_slabs_and_associated_elements.md, text: "Water must not be added to the mix to increase the slump" }
generated: { by: claude/opus-5.5, at: 2026-10-21T00:00:00Z }
stale_after: 2027-10-21T00:00:00Z
---

> **Guide, draft.** The engineer's drawings set the grade, slump,
> reinforcement and cover for anything structural. Use this to order and
> check, not to design.

# Grades

Ready-mix is ordered by strength grade: N20, N25, N32, N40 and N50 are the
normal-class mixes (the number is the strength in MPa at 28 days).[^holcim_standard]

| Grade | Typical use (unless the engineer says otherwise) |
|---|---|
| **N20** | The NCC's minimum for house footings and slabs under the deemed-to-satisfy rules, with 20 mm aggregate and 100 mm slump (Housing Provisions 4.2.10) |
| **N25** | Common for house slabs, paths and patios |
| **N32** | Driveways, garage floors, exposed or coastal work, and wherever the engineer specifies it |
| N40 and up | Engineered and commercial work |

When ordering, give: grade, slump (80 or 100 mm typical), maximum aggregate
size (usually 20 mm), volume, any additive (accelerator in winter,
retarder in heat), whether you need a pump, and the time.

**Never add water on site** to make it flow: it weakens the concrete and
the NCC forbids it for footings and slabs. Ask for a higher slump or a
plasticiser instead.

# How much to order

- Volume in m³ = length x width x depth (in metres). The [slab takeoff](/computations/materials_takeoff.md) does this and adds the mesh, chairs, membrane and edge forms.
- Allow extra for uneven subgrade and spillage, typically 5 to 10%, and round up to the plant's minimum increment.
- Small loads attract short-load fees: check the plant's minimum.

# Premix bags (small pours)

20 kg premix bags suit post holes, small pads and patches. The brain's
takeoff allows **0.0095 m³ per 20 kg bag** (about 105 bags per m³); check
the bag's stated yield.
Beyond about half a cubic metre, ready-mix is usually cheaper and better.
"Rapid set" mixes are for posts only, not slabs.

# Reinforcement, membrane, cover

- Mesh (e.g. SL72 or SL82 sheets) and trench mesh as drawn, lapped, tied and up on bar chairs.
- 0.2 mm polyethylene vapour barrier under house slabs, lapped 200 mm.
- Cover to the steel: 40 mm to the ground, 30 mm to a membrane, 20 mm inside, 40 mm to the weather.

See [footings and slabs](../code/footings_and_slabs.md) for the NCC detail.

# Curing

Keep new concrete damp and covered (curing compound, plastic, or
wetting) for at least the first few days, and longer in hot, windy or
cold weather. Don't pour onto frozen ground or when the forecast is very
hot without precautions; ask the plant about additives.

[^holcim_standard]: Holcim Australia, Standard concrete.

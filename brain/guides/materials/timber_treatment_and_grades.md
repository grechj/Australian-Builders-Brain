---
type: Reference
title: Timber treatment and grades
description: Which treated pine hazard level (H1 to H6) goes where, what stress grades like MGP10 and F17 mean, engineered timber (LVL, glulam, I-joists), reading the brand, and sealing cut ends.
tags: [guides, materials, timber, treated_pine, h3, h4, mgp10, lvl, framing, carpenter]
status: draft
trades: [carpenter, builder, fencer, landscaper, cabinet_maker]
sources:
  - id: qld_treated_timber
    resource: https://www.business.qld.gov.au/industries/building-property-development/building-construction/laws-codes-standards/using-timber/treated
    title: Using treated timber (Business Queensland)
  - id: woodsolutions_treatments
    resource: https://www.woodsolutions.com.au/publications/preservative-treatments-and-use-classes
    title: Preservative treatments and use classes (WoodSolutions)
  - id: tpaa_1604
    resource: https://tpaa.com.au/wp-content/uploads/2025/06/TN-14-1604-explained.pdf
    title: TN 14, AS/NZS 1604 explained (Timber Preservers Association of Australia)
  - id: ncc_2025_hp
    resource: https://ncc.abcb.gov.au/
    title: NCC 2025 Housing Provisions, Parts 3.4 and 6.2 (ABCB, CC BY 4.0)
checks:
  - { page: /ncc/2025/housing_provisions/6_2_subfloor_ventilation.md, text: "Where the ground or subfloor space is excessively damp or subject to frequent flooding" }
  - { page: /ncc/2025/housing_provisions/6_2_subfloor_ventilation.md, text: "above ground durability Class 1 or 2 timbers or H3 preservative treated timbers" }
  - { page: /ncc/2022/housing_provisions/6_2_subfloor_ventilation.md, text: "above ground durability Class 1 or 2 timbers or H3 preservative treated timbers" }
  - { page: /ncc/2022/housing_provisions/6_2_subfloor_ventilation.md, text: "in-ground durability Class 1 or 2 timbers or H5 preservative treated timbers" }
  - { page: /ncc/2025/housing_provisions/3_4_termite_risk_management.md, text: "Timber — preservative treated in accordance with Appendix D of AS 3660.1" }
generated: { by: claude/opus-5.5, at: 2026-10-21T00:00:00Z }
stale_after: 2027-10-21T00:00:00Z
---

> **Guide, draft.** Treatment levels come from AS/NZS 1604 and timber
> framing from AS 1684, neither reproduced here. Member sizes and spans
> always come from AS 1684 span tables, the supplier's span tables or an
> engineer.

# Hazard levels: which treatment goes where

Each level covers the hazards of the levels below it.[^qld_treated_timber][^tpaa_1604]

| Level | Where it's used | Protects against | Typical jobs |
|---|---|---|---|
| **H1** | Inside, dry, off the ground | Borers (not termites) | Mouldings, interior joinery |
| **H2** | Inside, dry, off the ground | Borers and termites | Wall and roof framing in termite areas (H2, or H2F for the envelope-treated product sold south of the Tropic of Capricorn) |
| **H3** | Outside, above ground, gets wet and dries out | Decay and termites | Deck joists and bearers, pergolas, fence rails, cladding, decking |
| **H4** | In the ground or always damp | Severe decay | Fence posts, landscaping sleepers, garden edging |
| **H5** | In the ground or fresh water, where failure matters | Very severe decay | Structural posts, retaining wall posts, house stumps, poles |
| **H6** | Sea water | Marine borers | Jetties, marine piles |

Rules of thumb that catch people out:

- **Retaining walls and structural posts in the ground: H5**, not H4. H4 is for things like fence posts and garden sleepers.
- **Decks:** H3 above ground for joists and bearers; posts set in the ground H5 (or on stirrups above ground, H3).
- **Damp subfloors:** where the subfloor is excessively damp or floods, one of the NCC's options is subfloor framing of H3 (above ground) or H5 (in ground) treated timber, or naturally durable Class 1 or 2 timber (Housing Provisions 6.2.1(5)); the others are 50% more ventilation or a ground membrane.
- **Termites:** framing treated to AS 3660.1 Appendix D isn't susceptible to termites for the NCC's purposes, so it can remove the need for a termite system for the frame. See [termite management](../code/termite_management.md).

# Reading the brand

Every treated piece (or, for battens and palings, the pack) carries a brand
with the treatment plant's number, the preservative code and the hazard
level, with characters at least 4 mm high.[^qld_treated_timber] **No brand,
no proof**: check it on delivery, and photograph it for the job file.

# Cutting treated timber

Treatment mostly penetrates the sapwood, so a cut, notch or drill hole
exposes untreated timber. **Seal every cut end, hole and rebate on site
with a suitable end-seal preservative or primer** before it goes in.[^woodsolutions_treatments]
Dense hardwoods like spotted gum and blackbutt can't be pressure-treated to
H3 or H4 through the heartwood: rely on their natural durability instead.

Wear a dust mask and gloves, and never burn offcuts.

# Stress grades

| Grade | What it is | Typical use |
|---|---|---|
| **MGP10, MGP12, MGP15** | Machine-graded pine; higher number is stiffer | MGP10 for most wall framing; MGP12 for longer spans and roof framing |
| **F5, F7, F8** | Older visual or machine grades, mostly pine | Framing, battens |
| **F14, F17, F27** | Hardwood grades | Bearers, posts, beams (F17 is the common hardwood framing grade) |
| **GL** (GL8 to GL18) | Glulam, laminated beams | Exposed beams, long spans |
| **LVL** | Laminated veneer lumber (various brands, e.g. E13 or E14 stiffness) | Lintels, beams, rafters where long spans or straightness matter |
| **I-joists** | Engineered joists with LVL flanges | Long-span floors |

Span tables are grade-specific: a 140 x 45 MGP10 and a 140 x 45 MGP12 span
differently. Never swap grades without re-checking the span table, and use
the engineered product's own span tables and fixing details for LVL,
glulam and I-joists.

# Naturally durable timbers

Hardwoods are rated by natural durability class (Class 1 most durable to
Class 4), separately for above ground and in ground. Class 1 and 2 species
(for example spotted gum, ironbark, tallowwood) can be used outside without
treatment where a standard allows; sapwood isn't durable, so check it's
excluded or treated. Ask the supplier for the species' class.

See also: [decking](decking.md), [fixings and corrosion](fixings_and_corrosion.md).

[^qld_treated_timber]: Business Queensland, Using treated timber.
[^woodsolutions_treatments]: WoodSolutions, Preservative treatments and use classes.
[^tpaa_1604]: TPAA, TN 14 AS/NZS 1604 explained.

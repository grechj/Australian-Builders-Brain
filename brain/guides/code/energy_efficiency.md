---
type: Reference
title: Energy efficiency for houses
description: What the NCC asks for on house energy efficiency (the 7-star thermal rating, the whole-of-home energy budget, the deemed-to-satisfy fabric, glazing, sealing, fan and lighting rules) and which states do it differently, in plain words with the clauses.
tags: [guides, ncc, energy, nathers, insulation, glazing, sealing, lighting, builder, electrician, insulation_installer, glazier]
status: draft
applies_to: [Class 1, Class 10a]
trades: [builder, insulation_installer, glazier, electrician, hvac, plumber, carpenter, plasterer]
sources:
  - id: ncc_2025_v2
    resource: https://ncc.abcb.gov.au/
    title: NCC 2025 Volume Two, Part H6 and Specification 42; Housing Provisions Section 13 (ABCB, CC BY 4.0)
  - id: ncc_2022_v2
    resource: https://ncc.abcb.gov.au/
    title: NCC 2022 Volume Two, Part H6 and Specification 42 (ABCB, CC BY 4.0)
checks:
  - { page: /ncc/2025/volume_two/specification_42_house_energy_rating_software.md, text: "7 stars; or" }
  - { page: /ncc/2025/volume_two/specification_42_house_energy_rating_software.md, text: "for a building in climate zones 1 or 2, 6.5 stars if the building has an outdoor living area" }
  - { page: /ncc/2022/volume_two/specification_42_house_energy_rating_software.md, text: "7 stars; or" }
  - { page: /ncc/2025/volume_two/h6_energy_efficiency.md, text: "must not exceed 70% of the energy value with" }
  - { page: /ncc/2025/volume_two/h6_energy_efficiency.md, text: "for a building with a total floor area not greater than 500 m²" }
  - { page: /ncc/2025/volume_two/h6_energy_efficiency.md, text: "NSW Part H6 of NCC 2022 Volume Two Amendment 2 applies in NSW" }
  - { page: /ncc/2025/volume_two/h6_energy_efficiency.md, text: "In Tasmania, Part H6 is replaced with BCA 2019 Amendment 1 Part 2.6" }
  - { page: /ncc/2025/housing_provisions/13_7_services.md, text: "5 W/m<sup>2</sup> in a Class 1 building" }
  - { page: /ncc/2025/housing_provisions/13_7_services.md, text: "4 W/m<sup>2</sup> on a verandah, balcony or the like attached to a Class 1 building" }
  - { page: /ncc/2025/housing_provisions/13_5_ceiling_fans.md, text: "climate zone 5 in New South Wales and Queensland" }
generated: { by: claude/opus-5.5, at: 2026-10-21T00:00:00Z }
stale_after: 2027-10-21T00:00:00Z
---

> **Plain-English guide, draft.** Energy efficiency varies more between
> states than anything else in the NCC: **NSW uses BASIX and keeps the NCC
> 2022 Amendment 2 version of H6; Tasmania still uses BCA 2019; the NT has
> its own H6**. States also adopted the 7-star rules on different dates.
> Check the state page and the clause page for the job's state, and use the
> edition in force when the permit application was lodged.

Part H6 ([2025](/ncc/2025/volume_two/h6_energy_efficiency.md#h6d2), [2022](/ncc/2022/volume_two/h6_energy_efficiency.md#h6d2)). A new house has to pass two tests.

# 1. Thermal performance: the star rating

Two ways to comply (H6D2(1)):

- **A NatHERS rating (most houses):** an accredited assessor models the plans and the house must reach **7 stars**, plus separate heating and cooling load limits (Specification 42, S42C2). In climate zones 1 and 2 (the tropics) it can be 6.5 stars with a qualifying covered outdoor living area, or 6 stars if that area also has a ceiling fan.
- **The deemed-to-satisfy elemental route:** meet Housing Provisions Parts 13.2 (insulation of roof, ceiling, walls and floor), 13.3 (glazing and shading), 13.4 (sealing) and 13.5 (ceiling fans) item by item.

# 2. Energy usage: the whole-of-home budget

New in NCC 2022 and carried into 2025 (H6P2): the house's heating, cooling,
hot water, lighting, and pool and spa pumps must use no more than **70%** of
a reference house with a 3-star ducted heat pump, a 5-star instant gas hot
water unit and 4 W/m² lighting. Solar PV counts against the total.

Comply through the NatHERS whole-of-home calculation (S42C3), or for houses
of 500 m² or less, through Housing Provisions Parts 13.6 (the
net-equivalent energy formula) and 13.7 (services).

# What each trade owns

- **Insulation installers and carpenters:** the R-values in the rating or in Part 13.2, installed without gaps or compression. See [insulation](../materials/insulation.md).
- **Glaziers:** the window U-value and SHGC the rating assumed (13.3 for the elemental route). Swap a window spec and the rating may fail.
- **Everyone on the envelope:** sealing (13.4): weatherstrips on external doors and windows, sealed exhaust fans, sealed roof lights, chimneys with dampers, gaps around penetrations sealed. See [sarking and wraps](../materials/sarking_and_wraps.md).
- **Electricians:** lighting power density no more than **5 W/m²** inside the house, 4 W/m² on verandahs and balconies, 3 W/m² in an attached garage, with outside lighting on a daylight sensor or at least 40 lm/W (13.7.6).
- **Ceiling fans** (13.5.2): required in climate zones 1 to 3, and zone 5 in NSW and Queensland, sized by room area.
- **Plumbers and HVAC:** pipe and duct insulation (13.7.2 to 13.7.4), and the hot water and heating systems the whole-of-home calculation assumed.

**Keep the stamped energy report on site.** Any change to windows,
insulation, hot water, heating or cooling, or the PV system needs checking
against it before it's made.

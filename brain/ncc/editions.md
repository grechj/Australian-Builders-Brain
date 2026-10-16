---
type: Code Reference
title: NCC editions and how to cite them
description: Which NCC edition applies to a job, what each volume covers, and the citation format the brain uses.
tags: [ncc, building_code, citations]
status: draft
resource: https://ncc.abcb.gov.au/
sources:
  - id: abcb_ncc
    resource: https://ncc.abcb.gov.au/
    title: National Construction Code, Australian Building Codes Board
    author: org:abcb
  - id: datagov_ncc2022
    resource: https://data.gov.au/data/dataset/national-construction-code-ncc-2022
    title: NCC 2022 dataset (CC BY 4.0)
    author: org:abcb
  - id: datagov_ncc2025
    resource: https://data.gov.au/data/dataset/national-construction-code-2025-version-1-2
    title: NCC 2025 v1.2 dataset (CC BY 4.0)
    author: org:abcb
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

The National Construction Code (NCC) is published free by the Australian
Building Codes Board (ABCB) at [ncc.abcb.gov.au](https://ncc.abcb.gov.au/).[^abcb_ncc]
The ABCB also publishes it as structured XML under a Creative Commons
Attribution 4.0 licence,[^datagov_ncc2022][^datagov_ncc2025] which is what
lets this brain load the code itself, with attribution.

# Which edition applies

The edition that applies is generally the one in force in that state when
the building permit or development application was lodged. NCC 2022 and
NCC 2025 can both be live for a while. Record the applicable edition in the
project file before answering any code question.

# Volumes

| Volume | Covers | Who mostly uses it |
|---|---|---|
| Volume One | Class 2 to 9 buildings (apartments, commercial, public) | Commercial builders |
| Volume Two | Class 1 and 10 buildings (houses, garages, sheds) | Residential builders |
| Volume Three | Plumbing and drainage | Plumbers |
| ABCB Housing Provisions | Deemed-to-satisfy solutions for Class 1 and 10 (from NCC 2022) | Residential builders |
| Livable Housing Design Standard | Livable housing requirements (NCC 2025 dataset) | Residential builders |

# Citation format

Cite every code statement as edition, volume and clause, with a link:

> NCC 2022 Vol Two, H2D2 ([ncc.abcb.gov.au](https://ncc.abcb.gov.au/))

Never cite a clause from memory. Look it up in the ingested XML (see
`raw/ncc/README.md`) or on the ABCB site, and note the state variation if
there is one.

# What's not in the NCC

The NCC calls up Australian Standards (for example timber framing,
waterproofing, concrete). Standards Australia owns those, so the brain names
the standard and what it covers but never reproduces its content.

[^abcb_ncc]: National Construction Code, Australian Building Codes Board
[^datagov_ncc2022]: NCC 2022 dataset (CC BY 4.0)
[^datagov_ncc2025]: NCC 2025 v1.2 dataset (CC BY 4.0)

---
type: "Code Reference"
title: "NCC 2025 Vol One, Specification 47 Calculation of climate specific part load value for chillers"
description: "NCC 2025 Vol One Specification 47 Calculation of climate specific part load value for chillers."
tags: [ncc, ncc_2025, volume_one, energy_efficiency]
status: "stable"
resource: "https://ncc.abcb.gov.au/"
edition: "NCC 2025"
volume: "Volume One"
part: "47"
order: 114
clauses: [S47C1, S47C2]
state_variations: []
sources:
  - id: abcb_ncc
    resource: https://data.gov.au/data/dataset/national-construction-code-2025-version-1-2
    title: NCC 2025 Volume One, Australian Building Codes Board (CC BY 4.0)
    author: org:abcb
generated: { by: process:ncc_ingest/0.1, at: 2026-10-16T10:00:55Z }
---

From **NCC 2025 Volume One**, Energy efficiency.[^abcb_ncc] Defined terms are in *italics*; see [definitions](definitions.md). 

<a id="s47c1"></a>

### S47C1 Scope

This Specification contains the method to calculate the *climate specific part load value* for a connected group of chillers that serves a common load, for the purposes of assessing compliance with [J6D11](/ncc/2025/volume_one/j6_air_conditioning_and_ventilation.md#j6d11).

<a id="s47c2"></a>

### S47C2 Calculation of climate specific part load value for chillers

(1) The *climate specific part load value* for a group of one or more chillers must be calculated in accordance with the following formula:

`CSPLV=α100EER100+α75EER75+α50EER50+α25EER25`

where—

- (a) CSPLV= *climate specific part load value*; and

- (a) EERn = the weighted average energy efficiency ratio of the chillers that operate to provide n% of the design *cooling load* under the staging strategy to be deployed, determined in accordance with (2) and (3); and
- (b) αn = load weighting factors specified in—
  - (1) [Table S47C2a](#table_40dcc5c1) for chillers serving a Class 5, 6, 7, 8 or 9b building or a Class 9a building other than a *ward area*; or
  - (2) [Table S47C2b](#table_f84e7080) for chillers serving a Class 3 or 9c building or a Class 9a *ward area*.

(2) EERn is determined as the weighted average energy efficiency ratio of the chillers operating to meet n% of the design *cooling load* under the staging strategy to be deployed, allowing for the part load efficiencies at—

- (a) a chilled water leaving temperature of 7°C; and
- (b) a chilled water flow rate that corresponds to a 6°C difference between entering and leaving temperatures at the rated cooling capacity, when determined in accordance with AHRI 551/591; and
- (c) for water-cooled chillers—
  - (1) a condenser water entering temperature that is determined by adding the design approach temperature to the outside wet bulb temperature listed in—
    - (1) Table S47C2c for chillers serving a Class 5, 6, 7, 8 or 9b building or a Class 9a building other than a *ward area*; or
    - (2) Table S47C2d for chillers serving a Class 3 or 9c building or a Class 9a *ward area*; and
  - (2) a condenser water flow rate that corresponds to a 6°C difference between entering and leaving temperature at the rated cooling capacity, when determined in accordance with AHRI 551/591; and
- (d) for air-cooled chillers, the outside dry bulb temperature listed in—
  - (1) Table S47C2e for chillers serving a Class 5, 6, 7, 8 or 9b building or a Class 9a building other than a *ward area*; or
  - (2) Table S47C2f for a Class 3 or 9c building or a Class 9a *ward area*.

(3) The EERn values in (2) must be determined using test measurements and calculations performed in accordance with the procedures of AHRI 551/591.

<a id="table_40dcc5c1"></a>**Table S47C2a: Load weighting factors - Class 5, 6, 7, 8 or 9b building or Class 9a building other than a ward area**

| Load | CZ 1 | CZ 2 | CZ 3 | CZ 4 | CZ 5 | CZ 6 | CZ 7 | CZ 8 |
|---|---|---|---|---|---|---|---|---|
| 25% | 7% | 25% | 23% | 25% | 24% | 42% | 28% | 20% |
| 50% | 48% | 43% | 48% | 35% | 46% | 31% | 36% | 27% |
| 75% | 43% | 31% | 28% | 37% | 30% | 26% | 34% | 42% |
| 100% | 2% | 1% | 1% | 3% | 0% | 1% | 2% | 11% |

> - (1) Load is the proportion of the total design load served by a connected group of chillers.
> - (2) CZ = *climate zone*.
>

<a id="table_f84e7080"></a>**Table S47C2b: Load weighting factors - Class 3 or 9c building or Class 9a ward area**

| Load | CZ 1 | CZ 2 | CZ 3 | CZ 4 | CZ 5 | CZ 6 | CZ 7 | CZ 8 |
|---|---|---|---|---|---|---|---|---|
| 25% | 7% | 31% | 23% | 43% | 41% | 60% | 40% | 16% |
| 50% | 31% | 39% | 44% | 39% | 35% | 24% | 31% | 32% |
| 75% | 61% | 28% | 32% | 18% | 23% | 15% | 26% | 49% |
| 100% | 1% | 2% | 1% | 0% | 1% | 1% | 3% | 3% |

> - (1) Load is the proportion of the total design load served by a connected group of chillers.
> - (2) CZ = *climate zone*.
>

<a id="table_1dc87ae0"></a>**Table S47C2c: Part load evaluation points - outdoor wet bulb temperature (°C), Class 5, 6, 7, 8 or 9b building or Class 9a building other than a ward area**

| Load | CZ 1 | CZ 2 | CZ 3 | CZ 4 | CZ 5 | CZ 6 | CZ 7 | CZ 8 |
|---|---|---|---|---|---|---|---|---|
| 25% | 17 | 16 | 12 | 12 | 14 | 12 | 12 | 10 |
| 50% | 24 | 22 | 17 | 17 | 20 | 18 | 17 | 13 |
| 75% | 27 | 25 | 21 | 20 | 23 | 20 | 19 | 15 |
| 100% | 28 | 27 | 23 | 22 | 25 | 24 | 21 | 14 |

> - (1) Load is the proportion of the total design load served by a connected group of chillers.
> - (2) CZ = *climate zone*.
>

<a id="table_e1f35f87"></a>**Table S47C2d: Part load evaluation points - outdoor wet bulb temperature (°C), Class 3 or 9c building or Class 9a ward area**

| Load | CZ 1 | CZ 2 | CZ 3 | CZ 4 | CZ 5 | CZ 6 | CZ 7 | CZ 8 |
|---|---|---|---|---|---|---|---|---|
| 25% | 19 | 18 | 12 | 14 | 17 | 14 | 14 | 10 |
| 50% | 24 | 22 | 17 | 18 | 21 | 19 | 17 | 13 |
| 75% | 27 | 25 | 20 | 20 | 23 | 21 | 19 | 14 |
| 100% | 29 | 27 | 24 | 23 | 26 | 23 | 20 | 17 |

> - (1) Load is proportion of the total design load served by a connected group of chillers.
> - (2) CZ = *climate zone*.
>

<a id="table_d0a2e0f9"></a>**Table S47C2e: Part load evaluation points - outdoor dry bulb temperature (°C), Class 5, 6, 7, 8 or 9b building or Class 9a building other than a ward area**

| Load | CZ 1 | CZ 2 | CZ 3 | CZ 4 | CZ 5 | CZ 6 | CZ 7 | CZ 8 |
|---|---|---|---|---|---|---|---|---|
| 25% | 27 | 21 | 21 | 18 | 19 | 17 | 17 | 14 |
| 50% | 31 | 27 | 32 | 27 | 25 | 26 | 25 | 20 |
| 75% | 32 | 29 | 34 | 31 | 28 | 31 | 29 | 23 |
| 100% | 29 | 29 | 28 | 32 | 27 | 36 | 32 | 25 |

> - (1) Load is the proportion of the total design load served by a connected group of chillers.
> - (2) CZ = *climate zone*.
>

<a id="table_c75ff786"></a>**Table S47C2f: Part load evaluation points - outdoor dry bulb temperature (°C), Class 3 or 9c building or Class 9a ward area**

| Load | CZ 1 | CZ 2 | CZ 3 | CZ 4 | CZ 5 | CZ 6 | CZ 7 | CZ 8 |
|---|---|---|---|---|---|---|---|---|
| 25% | 24 | 22 | 21 | 20 | 21 | 19 | 18 | 14 |
| 50% | 29 | 27 | 31 | 29 | 26 | 27 | 26 | 17 |
| 75% | 31 | 29 | 36 | 34 | 29 | 33 | 31 | 22 |
| 100% | 34 | 32 | 39 | 41 | 32 | 41 | 36 | 27 |

> - (1) Load is the proportion of the total design load served by a connected group of chillers.
> - (2) CZ = *climate zone*.
>

[^abcb_ncc]: NCC 2025. © Commonwealth of Australia and the States and Territories of Australia, published by the Australian Building Codes Board, licensed under CC BY 4.0. Converted to markdown by tools/ncc_ingest.py; figures not reproduced. The authoritative text is at https://ncc.abcb.gov.au/

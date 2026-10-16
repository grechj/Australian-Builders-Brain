---
type: "Code Reference"
title: "NCC 2025 Vol Two, Specification 44 Calculation of heating load limit, cooling load limit and thermal energy load limit"
description: "NCC 2025 Vol Two Specification 44 Calculation of heating load limit, cooling load limit and thermal energy load limit."
tags: [ncc, ncc_2025, volume_two, class_1_and_10_buildings]
status: "stable"
resource: "https://ncc.abcb.gov.au/"
edition: "NCC 2025"
volume: "Volume Two"
part: "44"
order: 24
clauses: [S44C1, S44C2, S44C3, S44C4]
state_variations: []
sources:
  - id: abcb_ncc
    resource: https://data.gov.au/data/dataset/national-construction-code-2025-version-1-2
    title: NCC 2025 Volume Two, Australian Building Codes Board (CC BY 4.0)
    author: org:abcb
generated: { by: process:ncc_ingest/0.1, at: 2026-10-16T10:00:55Z }
---

From **NCC 2025 Volume Two**, Class 1 and 10 buildings.[^abcb_ncc] Defined terms are in *italics*; see [definitions](definitions.md). 

This specification has been deliberately left blank. Specification 44 of the ABCB Housing Provisions 2025 does not apply in NSW.

<a id="s44c1"></a>

### S44C1 Scope

This Specification contains the method of calculating the *heating load* limit, *cooling load* limit and *thermal energy load* limit for compliance with [J1P2](/ncc/2025/volume_one/j1_energy_efficiency_performance_requirements.md#j1p2) and [H6P1](/ncc/2025/volume_two/h6_energy_efficiency.md#h6p1).

<a id="s44c2"></a>

### S44C2 Heating load limit

The *heating load* limit of a space, measured in MJ/m<sup>2</sup>.annum, is equal to the greater of—

- (a) 4; and
- (b) ((0.0044×HDH)−5.9)×FH, where—
  - (1) HDH = the total annual *heating degree hours* of the building location; and
  - (2) FH = the area adjustment factor for the *heating load* limit, determined in accordance with [Table S44C2](/ncc/2025/volume_one/specification_44_calculation_of_heating_load_limit_cooling_load_limit_and_thermal_energy_load_limit.md#table_7fc09f72).

<a id="table_7fc09f72"></a>**Table S44C2: Area adjustment factors for the heating load limit**

| Total area of *habitable rooms* (A<sub>H</sub>) | Area adjustment factor (F<sub>H</sub>) |
|---|---|
| ≤ 50 m<sup>2</sup> | 1.37 |
| > 50 m<sup>2</sup> to ≤ 350 m<sup>2</sup> | (5.11×10−6)AH2−(3.82×10−3)AH+1.55 |
| > 350 m<sup>2</sup> | 0.84 |

> **Explanatory**
>
> Annual total *heating degree hours* for various locations may be found in Table S45C3a.
>

<a id="s44c3"></a>

### S44C3 Cooling load limit

(1) The *cooling load* limit of a space, measured in MJ/m<sup>2</sup>.annum, is calculated in accordance with the following formula:

`CLL=(5.4+0.00617×(CDH+1.85DGH))×FC`

(2) In the formula at (1)—

- (a) CLL = the *cooling load* limit (MJ/m<sup>2</sup>.annum); and
- (b) CDH = the total annual *cooling degree hours* of the building location; and
- (c) DGH = the total annual *dehumidification gram hours* of the building location; and
- (d) FC = the area adjustment factor for the *cooling load* limit, determined in accordance with [Table S44C3](/ncc/2025/volume_one/specification_44_calculation_of_heating_load_limit_cooling_load_limit_and_thermal_energy_load_limit.md#table_c7addc21).

<a id="table_c7addc21"></a>**Table S44C3: Area adjustment factors for the cooling load limit**

| Total area of the *habitable rooms* (A<sub>H</sub>) | Area adjustment factor (F<sub>C</sub>) |
|---|---|
| ≤ 50 m<sup>2</sup> | 1.34 |
| > 50 m<sup>2</sup> and ≤ 200 m<sup>2</sup> | (1.29×10−5)AH2−(5.55×10−3)AH+1.58 |
| > 200 m<sup>2</sup> and ≤ 1000 m<sup>2</sup> | (3.76×10−7)AH2−(7.82×10−4)AH+1.12 |
| > 1000 m<sup>2</sup> | 0.71 |

> **Explanatory**
>
> Annual total *cooling degree hours* and *dehumidification gram hours* for various locations may be found in Table S45C3a.
>

<a id="s44c4"></a>

### S44C4 Thermal energy load limit

(1) The *thermal energy load* limit of a space, measured in MJ/m<sup>2</sup>.annum, is calculated in accordance with the following formula:

TLL=19.3HLL+22.6CLL−8.4Tr+10.74−15

(2) In the formula at (1)—

- (a) TLL = the *thermal energy load* limit; and
- (b) HLL = the *heating load* limit; and
- (c) CLL = the *cooling load* limit; and
- (d) Tr = the annual average *daily* *outdoor temperature range*.

[^abcb_ncc]: NCC 2025. © Commonwealth of Australia and the States and Territories of Australia, published by the Australian Building Codes Board, licensed under CC BY 4.0. Converted to markdown by tools/ncc_ingest.py; figures not reproduced. The authoritative text is at https://ncc.abcb.gov.au/

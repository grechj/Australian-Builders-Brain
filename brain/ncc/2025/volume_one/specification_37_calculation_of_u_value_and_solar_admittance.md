---
type: "Code Reference"
title: "NCC 2025 Vol One, Specification 37 Calculation of U-Value and solar admittance"
description: "NCC 2025 Vol One Specification 37 Calculation of U-Value and solar admittance."
tags: [ncc, ncc_2025, volume_one, energy_efficiency]
status: "stable"
resource: "https://ncc.abcb.gov.au/"
edition: "NCC 2025"
volume: "Volume One"
part: "37"
order: 108
clauses: [S37C1, S37C2, S37C3, S37C4, S37C5, S37C6, S37C7]
state_variations: []
sources:
  - id: abcb_ncc
    resource: https://data.gov.au/data/dataset/national-construction-code-2025-version-1-2
    title: NCC 2025 Volume One, Australian Building Codes Board (CC BY 4.0)
    author: org:abcb
generated: { by: process:ncc_ingest/0.1, at: 2026-10-16T10:00:55Z }
---

From **NCC 2025 Volume One**, Energy efficiency.[^abcb_ncc] Defined terms are in *italics*; see [definitions](definitions.md). 

<a id="s37c1"></a>

### S37C1 Scope

This specification describes the methods of calculating the U-Value and *solar admittance* of a *wall-glazing construction*.

<a id="s37c2"></a>

### S37C2 General

For determining the aspect of a *wall-glazing construction* —

- (a) the northern aspect is within 45° of true north; and
- (b) the southern aspect is within 45° of true south; and
- (c) the eastern aspect is within 45° of true east; and
- (d) the western aspect is within 45° of true west.

<a id="s37c3"></a>

### S37C3 U-Value — Method 1 (Single Aspect)

(1) For the purposes of this method, a *wall-glazing construction* only includes the walls and *glazing* facing a single aspect.

(2) The *Total System U-Value* of the wall component of a *wall-glazing construction* must be calculated as the inverse of the *Total R-Value*, including allowance for thermal bridging, in accordance with—

- (a) AS/NZS 4859.2; or
- (b) [Specification 38](/ncc/2025/volume_one/specification_38_spandrel_panel_thermal_performance.md) for *spandrel panels*.

(3) The *Total System U-Value* of a *wall-glazing construction* must be calculated as the area-weighted average of the *Total System U-Value* of each of the components of the *wall-glazing construction*.

<a id="s37c4"></a>

### S37C4 U-Value — Method 2 (Multiple Aspects)

(1) For the purposes of this method, a *wall-glazing construction* only includes the walls and *glazing* facing multiple aspects.

(2) The *Total System U-Value* of the wall component of a *wall-glazing construction* must be calculated as the inverse of the *Total R-Value*, including allowance for thermal bridging, in accordance with—

- (a) AS/NZS 4859.2; or
- (b) [Specification 38](/ncc/2025/volume_one/specification_38_spandrel_panel_thermal_performance.md) for *spandrel panels*.

(3) The *Total System U-Value* of a *wall-glazing construction* must be calculated as the area-weighted average of the *Total System U-Value* of each of the components of the *wall-glazing construction*.

<a id="s37c5"></a>

### S37C5 Solar admittance — Method 1 (Single Aspect)

(1) The *solar admittance* of a *wall-glazing construction* must be calculated in accordance with the following formula:

`SA=AW1×SW1×SHGCW1AWALL+AW2×SW2×SHGCW2AWALL+...`

(2) In the formula at (1)—

- (a) SA = the *wall-glazing construction* *solar admittance*; and
- (b) AW1,AW2,... = the area of each *glazing* element; and
- (c) SW1,SW2,...= the shading multiplier for each *glazing* element in accordance with [S37C7](#s37c7); and
- (d) SHGCW1,W2,...= the *total system SHGC* of each *glazing* element; and
- (e) AWALL = the total *wall-glazing construction* area.

<a id="s37c6"></a>

### S37C6 Solar admittance — Method 2 (Multiple Aspects)

(1) The *solar admittance* of *wall-glazing construction* must achieve a representative *air-conditioning* energy value less than that achieved by the reference *solar admittance*, when using the following formula:

`ER=ANαNSAN+AEαESAE+ASαSSAS+AWαWSAW`

(2) In the formula at (1)—

- (a) ER = the representative *air-conditioning* energy value; and
- (b) AN,E,S,W = the area of the *wall-glazing construction* facing each aspect; and
- (c) αN,E,S,W = the *solar admittance* weighting coefficient of each aspect equal to—
  - (1) where the *glazing* area on an aspect is less than 20% of the *wall-glazing construction* area, 0; and
  - (2) the values in [Table S37C6a](#table_d17f9e25) and [Table S37C6b](#table_9bf5cad0); and
- (d) SAN,E,S,W = the *wall-glazing construction* *solar admittance* of each aspect—
  - (1) equal to the applicable value in [J4D6(5)](/ncc/2025/volume_one/j4_building_fabric.md#j4d6) in the reference case; and
  - (2) calculated in accordance with [S37C5(1)](#s37c5) in the proposed case.

<a id="table_d17f9e25"></a>**Table S37C6a: Solar admittance weighting coefficient — Class 5, 6, 7, 8 or 9b building or Class 9a building other than a ward area**

| Aspect | *Climate zone* 1 | *Climate zone* 2 | *Climate zone* 3 | *Climate zone* 4 | *Climate zone* 5 | *Climate zone* 6 | *Climate zone* 7 | *Climate zone* 8 |
|---|---|---|---|---|---|---|---|---|
| Northern | 1.47 | 1.95 | 1.95 | 2.05 | 2.28 | 2.12 | 2.40 | 1.88 |
| Southern | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Eastern | 1.39 | 1.58 | 1.63 | 1.72 | 1.72 | 1.62 | 1.84 | 1.92 |
| Western | 1.41 | 1.68 | 1.65 | 1.69 | 1.75 | 1.67 | 1.92 | 1.25 |

<a id="table_9bf5cad0"></a>**Table S37C6b: Solar admittance weighting coefficient — Class 3 or 9c building or Class 9a ward area**

| Aspect | *Climate zone* 1 | *Climate zone* 2 | *Climate zone* 3 | *Climate zone* 4 | *Climate zone* 5 | *Climate zone* 6 | *Climate zone* 7 | *Climate zone* 8 |
|---|---|---|---|---|---|---|---|---|
| Northern | 1.42 | 1.77 | 1.72 | 1.55 | 1.88 | 1.52 | 1.60 | 1.24 |
| Southern | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Eastern | 1.30 | 1.49 | 1.48 | 1.37 | 1.48 | 1.28 | 1.35 | 1.26 |
| Western | 1.37 | 1.54 | 1.50 | 1.36 | 1.52 | 1.33 | 1.40 | 1.05 |

<a id="s37c7"></a>

### S37C7 Shading

For the purpose of calculating *solar admittance*, the shading multiplier for each *glazing* element is the lesser of—

- (a) for shading provided by an external permanent projection that extends horizontally on both sides of the *glazing* for the same project distance P, as shown in [Figure S37C7a](#figure_ca80c889) —
  - (1) the value in [Table S37C7a](#table_9d7734ac) for shading on the northern, eastern or western aspects; or
  - (2) the value in [Table S37C7b](#table_5ac0b1c0) for shading on the southern aspect; or
- (b) for shading provided by an external permanent projection that extends vertically for the height of the *glazing* for the same projection distance D, as shown in [Figure S37C7b](#figure_17be233c) —
  - (1) the value in [Table S37C7c](#table_05c14a58) for shading on the northern aspect; or
  - (2) the value in [Table S37C7d](#table_86fbe92e) for shading on the western aspect; or
  - (3) the value in [Table S37C7e](#table_78d5ce63) for shading on the eastern aspect; or
  - (4) 1.0 for shading on the southern aspect; or
- (c) 0.35 for shading that is provided by an external shading device such as a shutter, blind, vertical or horizontal building screen with blades, battens or slats, which—
  - (1) is capable of restricting at least 80% of summer solar radiation; and
  - (2) if adjustable, will operate automatically in response to the level of solar radiation.

<a id="table_9d7734ac"></a>**Table S37C7a: Horizontal shading multipliers — Northern, eastern and western aspects**

| G/H | P/H = 0 | P/H = 0.1 | P/H = 0.2 | P/H = 0.3 | P/H = 0.4 | P/H = 0.5 | P/H = 0.6 | P/H = 0.7 | P/H = 0.8 | P/H = 0.9 | P/H = 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1.00 | 0.90 | 0.80 | 0.72 | 0.64 | 0.57 | 0.51 | 0.46 | 0.41 | 0.38 | 0.35 |
| 0.1 | 1.00 | 0.95 | 0.89 | 0.81 | 0.74 | 0.66 | 0.59 | 0.52 | 0.47 | 0.42 | 0.40 |
| 0.2 | 1.00 | 0.98 | 0.94 | 0.89 | 0.82 | 0.75 | 0.68 | 0.62 | 0.56 | 0.51 | 0.47 |
| 0.3 | 1.00 | 1.00 | 0.97 | 0.94 | 0.89 | 0.84 | 0.78 | 0.72 | 0.66 | 0.61 | 0.57 |
| 0.4 | 1.00 | 1.00 | 0.99 | 0.97 | 0.94 | 0.90 | 0.86 | 0.82 | 0.77 | 0.73 | 0.68 |
| 0.5 | 1.00 | 1.00 | 1.00 | 0.99 | 0.97 | 0.95 | 0.92 | 0.90 | 0.86 | 0.83 | 0.79 |

<a id="table_5ac0b1c0"></a>**Table S37C7b: Horizontal shading multipliers — Southern aspect**

| G/H | P/H = 0 | P/H = 0.1 | P/H = 0.2 | P/H = 0.3 | P/H = 0.4 | P/H = 0.5 | P/H = 0.6 | P/H = 0.7 | P/H = 0.8 | P/H = 0.9 | P/H = 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1.00 | 0.93 | 0.87 | 0.82 | 0.77 | 0.73 | 0.69 | 0.65 | 0.62 | 0.60 | 0.58 |
| 0.1 | 1.00 | 0.97 | 0.93 | 0.88 | 0.84 | 0.79 | 0.75 | 0.71 | 0.67 | 0.64 | 0.62 |
| 0.2 | 1.00 | 0.98 | 0.96 | 0.93 | 0.89 | 0.85 | 0.81 | 0.77 | 0.73 | 0.70 | 0.68 |
| 0.3 | 1.00 | 0.99 | 0.98 | 0.96 | 0.93 | 0.90 | 0.87 | 0.83 | 0.80 | 0.77 | 0.74 |
| 0.4 | 1.00 | 1.00 | 0.99 | 0.98 | 0.96 | 0.94 | 0.91 | 0.89 | 0.86 | 0.84 | 0.81 |
| 0.5 | 1.00 | 1.00 | 0.99 | 0.99 | 0.98 | 0.96 | 0.95 | 0.93 | 0.91 | 0.90 | 0.88 |

<a id="table_05c14a58"></a>**Table S37C7c: Vertical shading multipliers — Northern aspect**

| *Climate zone* | D | W = 1.7 H | W = H | W = 0.7 H | W = 0.5 H |
|---|---|---|---|---|---|
| 1, 2, 3, 5, 6 | 0.1 W | 0.91 | 0.90 | 0.90 | 0.90 |
| 1, 2, 3, 5, 6 | 0.3 W | 0.85 | 0.83 | 0.82 | 0.81 |
| 1, 2, 3, 5, 6 | 0.5 W | 0.82 | 0.78 | 0.76 | 0.74 |
| 1, 2, 3, 5, 6 | 0.7 W | 0.81 | 0.76 | 0.73 | 0.70 |
| 4 | 0.1 W | 0.91 | 0.91 | 0.90 | 0.90 |
| 4 | 0.3 W | 0.87 | 0.84 | 0.83 | 0.82 |
| 4 | 0.5 W | 0.84 | 0.80 | 0.78 | 0.76 |
| 4 | 0.7 W | 0.83 | 0.78 | 0.75 | 0.73 |
| 7 | 0.1 W | 0.92 | 0.91 | 0.91 | 0.90 |
| 7 | 0.3 W | 0.87 | 0.85 | 0.83 | 0.82 |
| 7 | 0.5 W | 0.86 | 0.82 | 0.79 | 0.78 |
| 7 | 0.7 W | 0.85 | 0.80 | 0.78 | 0.75 |
| 8 | 0.1 W | 0.92 | 0.92 | 0.91 | 0.91 |
| 8 | 0.3 W | 0.90 | 0.88 | 0.86 | 0.85 |
| 8 | 0.5 W | 0.91 | 0.87 | 0.85 | 0.83 |
| 8 | 0.7 W | 0.91 | 0.88 | 0.86 | 0.84 |

<a id="table_86fbe92e"></a>**Table S37C7d: Vertical shading multipliers — Western aspect**

| *Climate zone* | D | W = 1.7 H | W = H | W = 0.7 H | W = 0.5 H |
|---|---|---|---|---|---|
| 1, 2, 3, 5, 6 | 0.1 W | 0.93 | 0.91 | 0.90 | 0.90 |
| 1, 2, 3, 5, 6 | 0.3 W | 0.87 | 0.85 | 0.84 | 0.84 |
| 1, 2, 3, 5, 6 | 0.5 W | 0.85 | 0.82 | 0.80 | 0.79 |
| 1, 2, 3, 5, 6 | 0.7 W | 0.83 | 0.79 | 0.77 | 0.75 |
| 4 | 0.1 W | 0.93 | 0.90 | 0.90 | 0.89 |
| 4 | 0.3 W | 0.88 | 0.86 | 0.85 | 0.84 |
| 4 | 0.5 W | 0.87 | 0.84 | 0.82 | 0.81 |
| 4 | 0.7 W | 0.86 | 0.83 | 0.81 | 0.79 |
| 7 | 0.1 W | 0.96 | 0.95 | 0.95 | 0.95 |
| 7 | 0.3 W | 0.94 | 0.94 | 0.94 | 0.93 |
| 7 | 0.5 W | 0.94 | 0.93 | 0.93 | 0.93 |
| 7 | 0.7 W | 0.94 | 0.93 | 0.93 | 0.92 |
| 8 | 0.1 W | 0.93 | 0.90 | 0.89 | 0.89 |
| 8 | 0.3 W | 0.90 | 0.88 | 0.87 | 0.87 |
| 8 | 0.5 W | 0.90 | 0.88 | 0.87 | 0.86 |
| 8 | 0.7 W | 0.90 | 0.89 | 0.87 | 0.86 |

<a id="table_78d5ce63"></a>**Table S37C7e: Vertical shading multipliers — Eastern aspect**

| *Climate zone* | D | W = 1.7 H | W = H | W = 0.7 H | W = 0.5 H |
|---|---|---|---|---|---|
| 1, 2, 3, 5, 6 | 0.1 W | 0.94 | 0.94 | 0.93 | 0.93 |
| 1, 2, 3, 5, 6 | 0.3 W | 0.90 | 0.89 | 0.88 | 0.87 |
| 1, 2, 3, 5, 6 | 0.5 W | 0.88 | 0.85 | 0.84 | 0.83 |
| 1, 2, 3, 5, 6 | 0.7 W | 0.87 | 0.83 | 0.81 | 0.79 |
| 4 | 0.1 W | 0.94 | 0.93 | 0.92 | 0.92 |
| 4 | 0.3 W | 0.91 | 0.89 | 0.89 | 0.88 |
| 4 | 0.5 W | 0.90 | 0.88 | 0.86 | 0.85 |
| 4 | 0.7 W | 0.89 | 0.87 | 0.85 | 0.83 |
| 7 | 0.1 W | 0.95 | 0.94 | 0.94 | 0.93 |
| 7 | 0.3 W | 0.91 | 0.92 | 0.91 | 0.91 |
| 7 | 0.5 W | 0.93 | 0.91 | 0.90 | 0.89 |
| 7 | 0.7 W | 0.93 | 0.91 | 0.90 | 0.88 |
| 8 | 0.1 W | 0.94 | 0.93 | 0.93 | 0.92 |
| 8 | 0.3 W | 0.94 | 0.93 | 0.93 | 0.92 |
| 8 | 0.5 W | 0.95 | 0.94 | 0.93 | 0.92 |
| 8 | 0.7 W | 0.95 | 0.95 | 0.94 | 0.93 |

<a id="figure_ca80c889"></a>*Figure: Permanent external horizontal shading – measurement of P, G and H* (not reproduced here, see the figure on ncc.abcb.gov.au)

<a id="figure_17be233c"></a>*Figure: Permanent external vertical shading – measurement of D, W and H* (not reproduced here, see the figure on ncc.abcb.gov.au)

[^abcb_ncc]: NCC 2025. © Commonwealth of Australia and the States and Territories of Australia, published by the Australian Building Codes Board, licensed under CC BY 4.0. Converted to markdown by tools/ncc_ingest.py; figures not reproduced. The authoritative text is at https://ncc.abcb.gov.au/

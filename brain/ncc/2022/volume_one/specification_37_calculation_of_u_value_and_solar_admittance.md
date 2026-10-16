---
type: "Code Reference"
title: "NCC 2022 Vol One, Specification 37 Calculation of U-Value and solar admittance"
description: "NCC 2022 Vol One Specification 37 Calculation of U-Value and solar admittance."
tags: [ncc, ncc_2022, volume_one]
status: "stable"
resource: "https://ncc.abcb.gov.au/editions/ncc-2022"
edition: "NCC 2022"
volume: "Volume One"
part: "37"
order: 78
clauses: [S37C1, S37C2, S37C3, S37C4, S37C5, S37C6, S37C7]
state_variations: []
sources:
  - id: abcb_ncc
    resource: https://ncc.abcb.gov.au/editions/ncc-2022
    title: NCC 2022 (1 May 2023), Australian Building Codes Board (CC BY 4.0)
    author: org:abcb
generated: { by: process:ncc_pdf_ingest/0.1, at: 2026-10-16T22:24:57Z }
---

From **NCC 2022 Volume One**.[^abcb_ncc] Defined terms are in *italics*; see [definitions](definitions.md).

> **NCC 2022 with Amendments 1 and 2.** The text is NCC 2022 as published (1 May 2023). Changes made by Amendment 1 (from 1 May 2025) and Amendment 2 (from 29 July 2025) are shown as notices under the clause they change; the amended text takes precedence. See [NCC 2022 amendments](/ncc/2022/amendments.md).

<a id="s37c1"></a>

### S37C1 Scope

This specification describes the methods of calculating the U-Value and *solar admittance* of a *wall-glazing construction*.

<a id="s37c2"></a>

### S37C2 General

For determining the aspect of a *wall-glazing construction*—

- (a) the northern aspect is at or within 45° of true north; and
- (b) the southern aspect is at or within 45° of true south; and
- (c) the eastern aspect is within 45° of true east; and
- (d) the western aspect is within 45° of true west.
<a id="s37c3"></a>

### S37C3 U-Value — Method 1 (Single Aspect)

(1) For the purposes of this method, a *wall-glazing construction* only includes the walls and *glazing* facing a single aspect.

(2) The *Total System U-Value* of the wall component of a *wall-glazing construction* must be calculated as the inverse of the *Total R-Value*, including allowance for thermal bridging, in accordance with—

- (a) AS/NZS 4859.2; or
- (b) Specification 38 for *spandrel panels*.
(3) The *Total System U-Value* of a *wall-glazing construction* must be calculated as the area-weighted average of the *Total System U-Value* of each of the components of the *wall-glazing construction*.

(4) The *Total System U-Value* must not exceed the applicable value in J4D6(1).

<a id="s37c4"></a>

### S37C4 U-Value — Method 2 (Multiple Aspects)

(1) For the purposes of this method, a *wall-glazing construction* only includes the walls and *glazing* facing multiple aspects.

(2) The *Total System U-Value* of the wall component of a *wall-glazing construction* must be calculated as the inverse of the *Total R-Value*, including allowance for thermal bridging, in accordance with—

- (a) AS/NZS 4859.2; or
- (b) Specification 38 for *spandrel panels*.
(3) The *Total System U-Value* of a *wall-glazing construction* must be calculated as the area-weighted average of the *Total System U-Value* of each of the components of the *wall-glazing construction*.

(4) The *Total System U-Value* must not exceed the applicable value in J4D6(1).

<a id="s37c5"></a>

### S37C5 Solar admittance — Method 1 (Single Aspect)

(1) The *solar admittance* of a *wall-glazing construction* must be calculated in accordance with the following formula: A (cid:4)S (cid:4)SHGC A (cid:4)S (cid:4)SHGC W 1 W 1 W 1 W 2 W 2 W 2 SA (cid:3) (cid:1) (cid:1)(cid:2)(cid:2)(cid:2) WALL WALL

(2) In the formula at (1)—

- (a) SA = the *wall-glazing construction solar admittance*; and
- (b) A (cid:1)A (cid:1)(cid:2)(cid:2)(cid:2) = the area of each *glazing* element; and W 1 W 2
- (c) S (cid:1)S = the shading multiplier for each *glazing* element in accordance with S37C7; and W 1 W 2(cid:1)(cid:2)(cid:2)(cid:2)
- (d) SHGC = the *total system SHGC* of each *glazing* element; and W 1(cid:1)W 2(cid:1)(cid:2)(cid:2)(cid:2)
- (e) AWALL = the total *wall-glazing construction* area.
(3) The *solar admittance* of the *wall-glazing construction* must not exceed the applicable value in J4D6(5).

<a id="s37c6"></a>

### S37C6 Solar admittance — Method 2 (Multiple Aspects)

(1) The *solar admittance* of *wall-glazing construction* must achieve a representative *air-conditioning* energy value less than that achieved by the reference *solar admittance*, when using the following formula: E (cid:2) A  SA (cid:1)A  SA (cid:1)A  SA (cid:1)A  SA R N N N E E E S S S W W W

(2) In the formula at (1)—

- (a) ER = the representative *air-conditioning* energy value; and
- (b) = the area of the *wall-glazing construction* facing each aspect; and N (cid:1)E(cid:1)S(cid:1)W
- (c)  = the *solar admittance* weighting coefficient of each aspect equal to— N (cid:1)E(cid:1)S(cid:1)W
  - (i) where the *glazing* area on an aspect is less than 20% of the *wall-glazing construction* area, 0; and
  - (ii) the values in Table S37C6a and Table S37C6b; and
- (d) = the *wall-glazing construction solar admittance* of each aspect— N (cid:1)E(cid:1)S(cid:1)W
  - (i) equal to the applicable value in J4D6(5) in the reference case; and
  - (ii) calculated in accordance with S37C5(1) in the proposed case.

**Table S37C6a: Solar admittance weighting coefficient — Class 2 common area, Class 5, 6, 7, 8 or 9b**

building or Class 9a building other than a ward area

| Aspect | Climate zone 1 | Climate zone 2 | Climate zone 3 | Climate zone 4 | Climate zone 5 | Climate zone 6 | Climate zone 7 | Climate zone 8 |
|---|---|---|---|---|---|---|---|---|
| Northern | 1.47 | 1.95 | 1.95 | 2.05 | 2.28 | 2.12 | 2.40 | 1.88 |
| Southern | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Eastern | 1.39 | 1.58 | 1.63 | 1.72 | 1.72 | 1.62 | 1.84 | 1.92 |
| Western | 1.41 | 1.68 | 1.65 | 1.69 | 1.75 | 1.67 | 1.92 | 1.25 |

**Table S37C6b: Solar admittance weighting coefficient — Class 3 or 9c building or Class 9a ward area**

| Aspect | Climate zone 1 | Climate zone 2 | Climate zone 3 | Climate zone 4 | Climate zone 5 | Climate zone 6 | Climate zone 7 | Climate zone 8 |
|---|---|---|---|---|---|---|---|---|
| Northern | 1.42 | 1.77 | 1.72 | 1.55 | 1.88 | 1.52 | 1.60 | 1.24 |
| Southern | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 | 1.00 |
| Eastern | 1.30 | 1.49 | 1.48 | 1.37 | 1.48 | 1.28 | 1.35 | 1.26 |

| Aspect | Climate zone 1 | Climate zone 2 | Climate zone 3 | Climate zone 4 | Climate zone 5 | Climate zone 6 | Climate zone 7 | Climate zone 8 |
|---|---|---|---|---|---|---|---|---|
| Western | 1.37 | 1.54 | 1.50 | 1.36 | 1.52 | 1.33 | 1.40 | 1.05 |

<a id="s37c7"></a>

### S37C7 Shading

For the purpose of calculating *solar admittance*, the shading multiplier is—

- (a) for shading provided by an external permanent projection that extends horizontally on both sides of the *glazing* for the same projection distance P, as shown in Figure S37C7—
  - (i) the value in Table S37C7a for shading on the northern, eastern or western aspects; or
  - (ii) the value in Table S37C7b for shading on the southern aspect; or
- (b) 0.35 for shading that is provided by an external shading device such as a shutter, blind, vertical or horizontal building screen with blades, battens or slats, which—
  - (i) is capable of restricting at least 80% of summer solar radiation; and
  - (ii) if adjustable, will operate automatically in response to the level of solar radiation.

**Table S37C7a: Shading multipliers — Northern, eastern and western aspects**

| G/H | P/H = 0 | P/H = 0.1 | P/H = 0.2 | P/H = 0.3 | P/H = 0.4 | P/H = 0.5 | P/H = 0.6 | P/H = 0.7 | P/H = 0.8 | P/H = 0.9 | P/H = 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1.00 | 0.90 | 0.80 | 0.72 | 0.64 | 0.57 | 0.51 | 0.46 | 0.41 | 0.38 | 0.35 |
| 0.1 | 1.00 | 0.95 | 0.89 | 0.81 | 0.74 | 0.66 | 0.59 | 0.52 | 0.47 | 0.42 | 0.40 |
| 0.2 | 1.00 | 0.98 | 0.94 | 0.89 | 0.82 | 0.75 | 0.68 | 0.62 | 0.56 | 0.51 | 0.47 |
| 0.3 | 1.00 | 1.00 | 0.97 | 0.94 | 0.89 | 0.84 | 0.78 | 0.72 | 0.66 | 0.61 | 0.57 |
| 0.4 | 1.00 | 1.00 | 0.99 | 0.97 | 0.94 | 0.90 | 0.86 | 0.82 | 0.77 | 0.73 | 0.68 |
| 0.5 | 1.00 | 1.00 | 1.00 | 0.99 | 0.97 | 0.95 | 0.92 | 0.90 | 0.86 | 0.83 | 0.79 |

**Table S37C7b: Shading multipliers — Southern aspect**

| G/H | P/H = 0 | P/H = 0.1 | P/H = 0.2 | P/H = 0.3 | P/H = 0.4 | P/H = 0.5 | P/H = 0.6 | P/H = 0.7 | P/H = 0.8 | P/H = 0.9 | P/H = 1 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 1.00 | 0.93 | 0.87 | 0.82 | 0.77 | 0.73 | 0.69 | 0.65 | 0.62 | 0.60 | 0.58 |
| 0.1 | 1.00 | 0.97 | 0.93 | 0.88 | 0.84 | 0.79 | 0.75 | 0.71 | 0.67 | 0.64 | 0.62 |
| 0.2 | 1.00 | 0.98 | 0.96 | 0.93 | 0.89 | 0.85 | 0.81 | 0.77 | 0.73 | 0.70 | 0.68 |
| 0.3 | 1.00 | 0.99 | 0.98 | 0.96 | 0.93 | 0.90 | 0.87 | 0.83 | 0.80 | 0.77 | 0.74 |
| 0.4 | 1.00 | 1.00 | 0.99 | 0.98 | 0.96 | 0.94 | 0.91 | 0.89 | 0.86 | 0.84 | 0.81 |
| 0.5 | 1.00 | 1.00 | 0.99 | 0.99 | 0.98 | 0.96 | 0.95 | 0.93 | 0.91 | 0.90 | 0.88 |

*Figure S37C7: Permanent external shading – measurement of P, G and H* (figure not reproduced; see the PDF)

| P (upper story glazing) Shading projection G (upper storey glazing) H (upper storey glazing) Shading projection G (lower storey glazing) P (lower storey glazing) H (lower storey glazing) |  |
|---|---|

[^abcb_ncc]: The National Construction Code 2022 was provided by the Australian Building Codes Board under the CC BY 4.0 licence. Converted to markdown from the ABCB's NCC 2022 PDFs (1 May 2023) by tools/ncc_pdf_ingest.py; figures not reproduced. Read with NCC 2022 Amendment 1 (from 1 May 2025) and Amendment 2 (from 29 July 2025). The authoritative text is at https://ncc.abcb.gov.au/editions/ncc-2022

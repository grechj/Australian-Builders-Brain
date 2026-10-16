---
type: "Code Reference"
title: "NCC 2025 Vol One, Specification 46 Determination of peak efficiency and fan power ratio"
description: "NCC 2025 Vol One Specification 46 Determination of peak efficiency and fan power ratio."
tags: [ncc, ncc_2025, volume_one, energy_efficiency]
status: "stable"
resource: "https://ncc.abcb.gov.au/"
edition: "NCC 2025"
volume: "Volume One"
part: "46"
order: 113
clauses: [S46C1, S46C2]
state_variations: []
sources:
  - id: abcb_ncc
    resource: https://data.gov.au/data/dataset/national-construction-code-2025-version-1-2
    title: NCC 2025 Volume One, Australian Building Codes Board (CC BY 4.0)
    author: org:abcb
generated: { by: process:ncc_ingest/0.1, at: 2026-10-16T10:00:55Z }
---

From **NCC 2025 Volume One**, Energy efficiency.[^abcb_ncc] Defined terms are in *italics*; see [definitions](definitions.md). 

<a id="s46c1"></a>

### S46C1 Scope

This Specification contains the method of calculating fan power ratio for the purpose of assessing compliance with J6D5.

<a id="s46c2"></a>

### S46C2 Determination of peak efficiency and fan power ratio

(1) The efficiency of a selected fan is the product of its impeller efficiency (including any casing), motor efficiency and the integrated motor control equipment multiplier in (2).

(2) The value of the integrated motor control equipment multiplier—

- (a) where the fan motor is not capable of variable speed operation or has an external variable speed control device, is 1; or
- (b) where the fan motor has integrated variable speed control capability and the motor input power at peak efficiency point is less than 5 kW, −0.03×In(P)+1.088, where—
  - (1) P = the motor input power of the fan (kW) at peak efficiency point; and
  - (2) In = natural logarithm; or
- (c) where the fan motor has integrated variable speed control capability and the motor input power at peak efficiency point is greater than or equal to 5 KW, is 1.04.

(3) The fan power ratio of an individual fan must be calculated in accordance with the following formula:

`FPRindividualfan=ηrfηdp`

where—

- (a) FPRindividualfan = the fan power ratio of the fan; and
- (b) ηrf = the efficiency calculated using the equation at [J6D5(2)](/ncc/2025/volume_one/j6_air_conditioning_and_ventilation.md#j6d5) or [J6D5(3)](/ncc/2025/volume_one/j6_air_conditioning_and_ventilation.md#j6d5) as applicable, with electrical input power Pdp, as determined at (5); and
- (c) ηdp = the static efficiency of the selected fan at the duty point for installation type A or C, or the total efficiency at the duty point for installation type B or D.

(4) The average fan power ratio of multiple fans must be calculated in accordance with the following formula:

`FPRaverage=∑applicablefansPdp∑applicablefansPrf`

where—

- (a) FPRaverage = the average fan power ratio of multiple fans; and
- (b) Pdp = the electrical input power of each selected fan at duty point, calculated in accordance with (5); and
- (c) Prf = the electrical input power of each reference fan at duty point, calculated in accordance with (6).

(5) Pdp must be calculated in accordance with the following:

`Pdp=pdpQdpηdp`

where—

- (a) pdp = the static pressure (Pa) at the duty point for installation type A or C or the total pressure (Pa) at the duty point for installation type B or D; and
- (b) Qdp = the flow (m<sup>3</sup>/s) at the duty point; and
- (c) ηdp = the static efficiency at the duty point for installation type A or C or the total efficiency at the duty point for installation type B or D.

(6) Prf must be calculated in accordance with the following formula:

`Prf=pdpQdpηrf`

where—

- (a) pdp = the static pressure (Pa) at the duty point for installation type A or C or total pressure (Pa) at the duty point for installation type B or D; and
- (b) Qdp = the flow (m<sup>3</sup>/s) at the duty point; and
- (c) ηrf = the efficiency calculated using the equation at [J6D5(2)](/ncc/2025/volume_one/j6_air_conditioning_and_ventilation.md#j6d5) or [(3)](/ncc/2025/volume_one/j6_air_conditioning_and_ventilation.md#j6d5) as applicable with electrical input power Pdp.

> **Explanatory**
>
> Duty point refers to the operating point of the fan when providing the maximum system design flow at the system design pressure. Where the fan is a fixed speed fan, the full speed efficiency and the pressure where the fan curve intersects the system curve may be used.
>

[^abcb_ncc]: NCC 2025. © Commonwealth of Australia and the States and Territories of Australia, published by the Australian Building Codes Board, licensed under CC BY 4.0. Converted to markdown by tools/ncc_ingest.py; figures not reproduced. The authoritative text is at https://ncc.abcb.gov.au/

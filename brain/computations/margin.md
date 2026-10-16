---
type: Attested Computation
title: Margin achieved
description: Margin in dollars and percent on a quoted item, matching the Variation Register's formula.
tags: [money, margin, job_costing]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: margin
computation_sha256: ed648470cebcfca459ccf06ce34df51582e49c7629861103d3cda1071acdd2d0
parameters:
  - { name: quoted_ex_gst, type: decimal, required: true }
  - { name: actual_cost_ex_gst, type: decimal, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

- **Margin $** = quoted − actual cost (both ex GST).
- **Margin %** = margin ÷ quoted. This is margin on the sell price, the way
  the Variation Register and Job P&L templates calculate it.
- **Markup %** = margin ÷ actual cost.

Builders often mix up margin and markup: a 20% markup is only a 16.67%
margin. Always say which one you mean.

# Computation

Runs `margin()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py margin --param quoted_ex_gst=4560 --param actual_cost_ex_gst=3800

---
type: Attested Computation
title: Margin achieved
description: Margin in dollars and percent on a quoted item, matching the Variation Register's formula.
tags: [money, margin, job_costing]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: margin
computation_sha256: 3a9e44178cc735d6224b516252e10c29c034dea0d8fa6df4f7f517b3258a83bf
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

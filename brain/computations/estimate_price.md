---
type: Attested Computation
title: Estimate to quote price
description: Turns estimated labour, materials and subcontract costs into a quote price with contingency, markup and GST, matching the Trade Based Estimate Workbook.
tags: [money, estimating, quoting, markup, margin]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: estimate_price
computation_sha256: ed648470cebcfca459ccf06ce34df51582e49c7629861103d3cda1071acdd2d0
parameters:
  - { name: labour, type: decimal, required: true }
  - { name: materials, type: decimal, required: true }
  - { name: subcontract, type: decimal, required: false, default: 0 }
  - { name: contingency_pct, type: decimal, required: false, default: 0 }
  - { name: markup_pct, type: decimal, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

All ex GST, the same way the [Trade Based Estimate Workbook](/documents/trade_based_estimate_workbook.md) works:

1. **Direct cost** = labour + materials + subcontract
2. **Contingency** = direct cost × `contingency_pct`
3. **Total cost** = direct cost + contingency
4. **Markup** = total cost × `markup_pct`. This is markup on cost, not margin.
5. **Quote** = total cost + markup, then [GST](/computations/gst.md)

`margin_on_price_pct` shows what the markup is as a margin on the sell price
(20% markup = 16.67% margin), so the builder can compare it with their
target margin. The `*_quote_ex_gst` lines are the client-facing summary,
with markup built into each line, as the workbook's Quote Output sheet
shows them.

# Computation

Runs `estimate_price()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py estimate_price --param labour=18400 --param materials=31250 \
        --param subcontract=42800 --param contingency_pct=5 --param markup_pct=20

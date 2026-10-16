---
type: Attested Computation
title: Variation price
description: Prices a variation from its cost lines, adds the builder's margin, then adds GST.
tags: [money, variations, margin, gst]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: variation_price
computation_sha256: 0081a7682ee41db849cf52598db8d32efcfcc02479741936d45d60b94f497818
parameters:
  - { name: labour, type: decimal, required: true }
  - { name: materials, type: decimal, required: true }
  - { name: subcontractor, type: decimal, required: false, default: 0 }
  - { name: plant, type: decimal, required: false, default: 0 }
  - { name: other, type: decimal, required: false, default: 0 }
  - { name: margin_pct, type: decimal, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

The cost lines match the cost breakdown on the
[Priced Variation Notice](/documents/priced_variation_notice.md): labour,
materials, subcontractor, plant and other, all ex GST.

1. Cost = sum of the lines.
2. Margin = cost × `margin_pct` / 100. Use the margin rate the contract
   schedule allows on variations. Use 0 if the lines are already sell prices.
3. Price ex GST = cost + margin, then [GST](/computations/gst.md) on top.

Residential contracts usually set the builder's margin on variations in the
contract schedule. Read it from the project file (`builders_margin_pct`)
or ask the user; never assume one.

# Computation

Runs `variation_price()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py variation_price --param labour=1200 --param materials=1450 \
        --param plant=150 --param margin_pct=20

`fields` in the receipt gives `[AMOUNT]`, `[AMOUNT_GST]` and `[AMOUNT_TOTAL]`.

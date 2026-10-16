---
type: Attested Computation
title: GST on an ex-GST amount
description: Adds 10% GST to an ex-GST amount and produces the AMOUNT, AMOUNT_GST and AMOUNT_TOTAL template fields.
tags: [money, gst, tax]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: gst
computation_sha256: b6f19cc356118580f48815dea77a7777ff2d76264e6cf690208875f67f469d8f
parameters:
  - { name: amount_ex_gst, type: decimal, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
sources:
  - id: ato_gst
    resource: https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst
    title: ATO, GST
    author: org:ato
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

GST is 10% of the ex-GST price of a taxable supply.[^ato_gst] Each
figure is rounded half-up to the cent, and the total is ex GST plus GST. A
builder registered for GST charges it on contract work, variations and
progress claims.

# Computation

Runs `gst()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py gst --param amount_ex_gst=3800

| Result field | Template field |
|---|---|
| `amount_ex_gst` | `[AMOUNT]` |
| `gst` | `[AMOUNT_GST]` |
| `amount_inc_gst` | `[AMOUNT_TOTAL]` |

[^ato_gst]: ATO, GST

---
type: Attested Computation
title: Ex GST from a GST-inclusive amount
description: Splits a GST-inclusive amount (a contract sum, a supplier invoice) into its ex-GST price and the GST, which is 1/11 of the total.
tags: [money, gst, tax]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: ex_gst
computation_sha256: e5db695c6b28e18cfc851be46cd897eac3acdd435d6b6528cfe7b362f28c4917
parameters:
  - { name: amount_inc_gst, type: decimal, required: true }
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

When a price includes 10% GST, the GST is one eleventh of the total.[^ato_gst]
GST is rounded half-up to the cent, and ex GST is the total less GST, so the
two always add back to the original amount.

Residential contract sums are usually quoted inc GST. Most templates in
this brain work ex GST, so run this first to get `contract_sum_ex_gst`.

# Computation

Runs `ex_gst()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py ex_gst --param amount_inc_gst=485000

[^ato_gst]: ATO, GST

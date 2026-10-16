---
type: Attested Computation
title: Licence and insurance expiry status
description: Works out whether each licence and insurance is current, expiring soon or expired on a given date, and the overall status for the Subbie Insurance and Licence Tracker.
tags: [dates, safety, compliance, subcontractors, insurance]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: expiry_status
computation_sha256: ed648470cebcfca459ccf06ce34df51582e49c7629861103d3cda1071acdd2d0
parameters:
  - { name: items, type: json, required: true }
  - { name: on_date, type: date, required: true }
  - { name: warn_days, type: decimal, required: false, default: 30 }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

For each item: **Expired** if its expiry date is before `on_date`;
**Expiring Soon** if it expires within `warn_days` (default 30); otherwise
**Compliant**. A blank date is **Incomplete**. The overall status is the
worst, in the order Compliant, Expiring Soon, Incomplete, Expired. These are
the values of the Status dropdown in the
[Subbie Insurance and Licence Tracker](/documents/subbie_insurance_licence_tracker.md).

# Computation

Runs `expiry_status()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py expiry_status --param on_date=16/10/2026 \
        --param 'items={"Licence": "30/06/2027", "PL insurance": "01/11/2026", "WC insurance": ""}'

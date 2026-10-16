---
type: Attested Computation
title: Final account
description: Works out the adjusted contract sum and the final claim from the contract sum, variations, PC/PS adjustments, claims to date and retention.
tags: [money, final_account, retention, handover]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: final_account
computation_sha256: e5db695c6b28e18cfc851be46cd897eac3acdd435d6b6528cfe7b362f28c4917
parameters:
  - { name: contract_sum_ex_gst, type: decimal, required: true }
  - { name: variations_additions, type: decimal, required: false, default: 0 }
  - { name: variations_omissions, type: decimal, required: false, default: 0 }
  - { name: pc_ps_adjustments, type: decimal, required: false, default: 0 }
  - { name: claimed_to_date, type: decimal, required: true }
  - { name: retention_held, type: decimal, required: false, default: 0 }
  - { name: retention_released, type: decimal, required: false, default: 0 }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

All ex GST.

1. **Adjusted contract sum** = contract sum + approved variation additions − approved omissions + net PC and provisional sum adjustments (from the [Allowances Register](/documents/allowances_register.md); can be negative)
2. **Net received** = claimed to date (gross) − retention held by the client
3. **Final claim** = adjusted contract sum − claimed to date + retention released now
4. Then [GST](/computations/gst.md)

Retention not released now (`retention_kept`) is usually released at the end
of the defects liability period. A negative final claim means the client has
been over-claimed and is owed a credit; the result warns about it.

This matches the [Final Account Summary](/documents/final_account_summary.md)
workbook and the [Final Claim and Release](/documents/final_claim_release.md).

# Computation

Runs `final_account()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py final_account --param contract_sum_ex_gst=440909.09 \
        --param variations_additions=3360 --param claimed_to_date=391727.27

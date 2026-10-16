---
type: Attested Computation
title: Progress claim
description: Works out a progress claim from the stage schedule (value completed less previous claims), deducts any retention, and adds GST.
tags: [money, claims, retention, gst]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: progress_claim
computation_sha256: e5db695c6b28e18cfc851be46cd897eac3acdd435d6b6528cfe7b362f28c4917
parameters:
  - { name: stages, type: json, required: true }
  - { name: retention_pct, type: decimal, required: false, default: 0 }
  - { name: retention_cap_pct, type: decimal, required: false, default: 0 }
  - { name: retention_held_to_date, type: decimal, required: false, default: 0 }
  - { name: contract_sum_ex_gst, type: decimal, required: false, default: 0 }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

All money is ex GST. For each stage in the contract's payment schedule:

- **Value completed** = stage contract value × % complete
- **This claim** = value completed − previously claimed

Approved variations are added as their own stage. Then:

1. **Gross this claim** = total value completed − total previous claims
2. **Retention** = gross × `retention_pct`. If `retention_cap_pct` is above 0, total retention held stops at that percentage of the contract sum.
3. **Net claim** = gross − retention, then [GST](/computations/gst.md) on top

The result also gives the totals the
[Progress Claim Invoice](/documents/progress_claim_invoice.md) shows:
claimed to date, less previous claims, less retention, net, GST and total.

`warnings` flags a stage claimed past its completed value, and stage values
that don't add up to the contract sum. Read them to the user; don't
ignore them.

Most residential contracts pay on fixed stage percentages (for example base
or slab, frame, lock-up, fixing, practical completion), and some state laws
cap them. Use the schedule in the user's contract, and see
[progress payments](/contracts/progress_payments.md).

# Computation

Runs `progress_claim()` in [builder_maths.py](/references/computations/builder_maths.py).
`stages` is JSON, with `pct_complete` as a whole percentage:

    python tools/compute.py progress_claim --param 'stages=[
      {"name": "Base / Slab", "contract_value": 66136.36, "pct_complete": 100, "previously_claimed": 66136.36},
      {"name": "Frame", "contract_value": 88181.82, "pct_complete": 100, "previously_claimed": 0}]'

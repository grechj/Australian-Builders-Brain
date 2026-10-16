---
type: Attested Computation
title: Payment schedule
description: Turns a contract's stage percentages into stage amounts inc and ex GST, adding up exactly to the contract sum, and flags a deposit over the state cap.
tags: [money, claims, contracts, deposit]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: payment_schedule
computation_sha256: ed648470cebcfca459ccf06ce34df51582e49c7629861103d3cda1071acdd2d0
parameters:
  - { name: contract_sum_inc_gst, type: decimal, required: true }
  - { name: stages, type: json, required: true }
  - { name: deposit_cap_pct, type: decimal, required: false, default: 0 }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

Each stage amount = contract sum × stage %, rounded to the cent. The last
stage takes the rounding difference, so the stages add up exactly to the
contract sum. Each amount is also split into ex GST and GST (1/11).

The percentages must add up to 100. Pass `deposit_cap_pct` from the verified
state rules to have an over-cap deposit flagged; deposit caps for
residential building work differ by state and contract value
([state rules](/states/overview.md)).

Use the result for the payment schedule in the
[Contract Data Summary](/documents/contract_data_summary.md). Its ex-GST
amounts are the stage values for the
[progress claim](/computations/progress_claim.md) computation.

# Computation

Runs `payment_schedule()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py payment_schedule --param contract_sum_inc_gst=485000 --param deposit_cap_pct=10 \
        --param 'stages=[{"name":"Deposit","pct":5},{"name":"Base / Slab","pct":15},{"name":"Frame","pct":20},
                         {"name":"Lock-Up","pct":25},{"name":"Fixing","pct":20},{"name":"Practical Completion","pct":15}]'

---
type: Attested Computation
title: Budget status
description: Status of each cost line (On Track, At Risk, Over Budget, Complete) from budget, committed and spent, with the forecast variance, matching the Budget vs Actual Tracker.
tags: [money, job_costing, budget]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: budget_status
computation_sha256: ed648470cebcfca459ccf06ce34df51582e49c7629861103d3cda1071acdd2d0
parameters:
  - { name: lines, type: json, required: true }
  - { name: at_risk_pct, type: decimal, required: false, default: 90 }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

For each line (ex GST):

- **Forecast** = the higher of committed (orders and subcontracts let) and spent
- **Variance** = budget − forecast. Negative means a forecast overrun.
- **Remaining** = budget − spent
- **Status**: Over Budget if forecast > budget; Complete if the line is finished and not over; At Risk if forecast ≥ `at_risk_pct` of budget (default 90%); otherwise On Track

These match the [Budget vs Actual Tracker](/documents/budget_vs_actual_tracker.md)
columns and its Status dropdown. Committed costs show an overrun weeks
before the invoices do.

# Computation

Runs `budget_status()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py budget_status --param 'lines=[{"item": "Framing", "budget": 18500, "committed": 19200, "spent": 12000}]'

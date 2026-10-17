---
type: Attested Computation
title: Job dashboard figures
description: Works out each job's P&L, receipts, costs by category against budget, margin, labour, days on site and job length, plus monthly series and averages across completed jobs, for the project dashboard and its CSV extracts.
tags: [money, dashboard, job_costing, margin, accounts]
status: stable
runtime: python
computation: /references/computations/finance_maths.py
entry_point: job_dashboard
computation_sha256: e65bf5d2d248f39245fb2427b8f93f0ecba2bdb63a5f2ec2f1798ca7930c7e73
parameters:
  - { name: jobs, type: json, required: true }
  - { name: as_at, type: date, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-17T00:00:00Z }
---

# Definition

For each job in the portfolio file (`tools/dashboard.py`), from its ledger
and timesheets:

| Figure | How it's worked out |
|---|---|
| Revenue | Sales lines coded to contract, variation or other income, ex GST, by invoice date (credit notes subtract) |
| Costs | Purchase lines ex GST by bill date, by role (subcontractors, materials, plant...), plus own labour from timesheets |
| Gross profit and margin | Revenue less costs; margin is profit as a percentage of revenue (not markup) |
| Revised contract | Contract sum ex GST plus variations invoiced |
| Received, outstanding | Payments against sales inc GST; invoiced inc GST less received |
| Paid, unpaid bills | Payments against bills inc GST; billed inc GST less paid |
| Labour hours, days on site | Timesheet hours, and the number of distinct dates worked |
| Days elapsed | Start date to practical completion (or to the as-at date while active), inclusive |
| Time used | Days elapsed as a percentage of the contract period |
| Job length vs average | Days elapsed against the average of completed jobs of the same project type (or all completed jobs) |

| Forecast at completion | Active jobs: revised contract less each cost category at the larger of budget and actual |
| Cost mix | Each category's cost as a percentage of revenue, averaged across completed jobs, by project type |
| Days to settle, days overdue | Per transaction: from its date to the payment that settled it; and from its due date to the as-at date while unpaid |

Retention, deposits held and capital equipment are balance sheet items, so
they are left out of profit. Monthly series give revenue, costs, receipts,
payments and cumulative profit per job; cost categories show actual against
the budget from the estimate. Warnings flag margins below target and jobs
past their contract completion date.

# Computation

Runs `job_dashboard()` in [finance_maths.py](/references/computations/finance_maths.py).

    python tools/dashboard.py examples/jobs_example.yaml --as-at 31/10/2026 --out out/dashboard

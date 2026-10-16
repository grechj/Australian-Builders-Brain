---
type: Contract Topic
title: Job financials
description: "Keeping a job profitable while it runs and learning from it afterwards: budget against committed and actual cost, job profit and margin, and lessons learned."
tags: [financials, job_costing, budget, margin, lessons]
status: stable
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

All amounts ex GST.

# During the job: budget vs actual

Set the budget from the estimate, trade by trade, in the
[Budget vs Actual Tracker](/documents/budget_vs_actual_tracker.md). Update
it weekly:

- **Committed**: what's locked in (orders placed, subcontracts let). It shows an overrun before the invoices arrive.
- **Spent**: invoices received or paid
- **Variance** = budget − committed (or spent, if higher). Negative means a forecast overrun.
- **Status** from the [budget status](/computations/budget_status.md) computation: On Track, At Risk (forecast at or above 90% of budget), Over Budget, or Complete

When a line goes over, ask why: scope change (raise a
[variation](/contracts/variations.md)), a subbie's mistake (a
[back charge](/contracts/site_instructions_and_back_charges.md)), or an
estimating miss (record it as a lesson). Overruns from client changes
should be recovered, not absorbed.

# At the end: job P&L

Fill the [Job Profit and Loss Summary](/documents/job_profit_loss_summary.md)
budget against actual: revenue (contract sum, approved variations, extras)
and costs (labour, materials, subcontractors, plant, preliminaries,
supervision, insurance, fees, waste). Gross margin = gross profit ÷ revenue.
Check it with the [margin](/computations/margin.md) computation, and compare
it with the margin the job was priced at (the
[estimate price](/computations/estimate_price.md) receipt shows
`margin_on_price_pct`).

Supervision and the builder's own time are real costs. Leaving them out
makes a job look better than it was.

# Lessons learned

Close every job with the [Lessons Learned Register](/documents/lessons_learned_register.md):
what happened, its impact, what worked, what to do differently, and one
concrete action for the next job, with an owner. Feed the actions back
into the estimate template, the checklists and the
[pre-construction playbook](/playbooks/pre_construction.md). That is how
the next job's margin improves.

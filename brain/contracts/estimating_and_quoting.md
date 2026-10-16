---
type: Contract Topic
title: Estimating and quoting
description: Building an estimate, pricing it with contingency and markup, comparing trade quotes, clarifying scope, and turning an accepted quote into a contract.
tags: [estimating, quoting, markup, margin, contingency, scope]
status: draft
jurisdiction: [NSW, VIC, QLD, WA, SA, TAS, ACT, NT]
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
stale_after: 2027-04-16T00:00:00Z
---

> **Draft.** The estimating method is general practice. The points about
> contracts, deposits and insurance depend on the state: verify them.

# The estimate

Build it trade by trade in the [Trade Based Estimate Workbook](/documents/trade_based_estimate_workbook.md):

- **Labour**: task, hours or days, and rate. The default rates come from the Setup sheet.
- **Materials**: item, quantity, unit and unit cost, with the supplier noted
- **Subcontractors**: a real quote for each trade, with its reference and date. Compare at least two to three with the [Quote Comparison](/documents/quote_comparison.md): price ex and inc GST, availability, duration, current licence and insurance, inclusions against scope, exclusions, payment terms and warranty.

Allow for the items most often missed: site establishment and fencing,
waste removal, scaffolding, temporary services, council and certification
fees, home warranty insurance, cleaning, and the builder's own supervision
time.

# Contingency and markup

- **Contingency** covers unknowns in this job (ground conditions, old work in renovations). It is a percentage of direct cost, typically higher for renovations than for new work.
- **Markup** covers overheads and profit, as a percentage of cost. The estimate workbook, the quote converter and the sensitivity calculator all use markup on cost.
- **Margin** is profit as a share of the sell price. A 20% markup is a 16.67% margin; a 25% markup is a 20% margin. The Variation Register and the Job P&L report margin. Always say which one you mean.

Price it with the [estimate price](/computations/estimate_price.md)
computation, and test the risk with the
[Margin Sensitivity Calculator](/documents/margin_sensitivity_calculator.md):
what a 5% or 10% cost overrun does to profit at each markup.

# Scope, clarifications and exclusions

Every unclear item at quote time becomes a variation argument later.

- Log questions and assumptions in the [Pre-Contract Clarifications](/documents/pre_contract_clarifications.md) register (RFI-001 ...), with the client's answers and their impact.
- State inclusions, exclusions, prime cost items and provisional sums (with allowances) in writing ([Allowances Register](/documents/allowances_register.md)).
- Give the quote a validity period. Material prices move.

# From quote to contract

- For residential building work, most states require a written contract (above a threshold value) with prescribed content. A signed quote alone may not be enough. Check the [state rules](/states/overview.md) and use an industry standard-form contract where one is required.
- **Deposits are capped** for residential building work in most states, often at 5% to 10% depending on the contract value. A quote that asks for 50% up front can be unlawful for residential work. The estimate workbook's quote terms suggest "50% deposit"; change them for residential jobs.
- Home warranty or domestic building insurance usually has to be in place before taking a deposit or starting work, above the state threshold.
- The [Quote Acceptance Form](/documents/quote_acceptance_form.md) records the client's authority to proceed. For residential work, use it alongside the proper contract, not instead of it.

Then set up the job with the [contract and pre-construction](/lifecycle/contract_and_pre_construction.md) documents.

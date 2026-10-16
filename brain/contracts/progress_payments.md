---
type: Contract Topic
title: Progress payments and claims
description: How builders claim stage payments from clients, what a valid claim needs, retention, and how subcontractor claims differ.
tags: [contracts, claims, payments, retention, sopa]
status: draft
jurisdiction: [NSW, VIC, QLD, WA, SA, TAS, ACT, NT]
sources:
  - id: ato_tax_invoice
    resource: https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst/tax-invoices
    title: ATO, Tax invoices
    author: org:ato
  - id: beam_claim_pack
    resource: /documents/claim_support_pack_checklist.md
    title: Claim Support Pack Checklist (Australian Builder's Brain template pack)
    author: human:grechj
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
stale_after: 2027-04-16T00:00:00Z
---

> **Draft, to verify.** The general practice here is sound. The state law
> points (deposit caps, stage limits, security of payment) need checking
> against each state's legislation before relying on them, and they will
> move into the per-state pages.

# How residential progress payments work

The contract sets a **payment schedule**: a deposit and then payments as
stages are reached. A typical new-home schedule is deposit, base or slab,
frame, lock-up, fixing, and practical completion. Extensions and renovations
often use custom stages.

- Claim only for a stage that is actually reached, as the contract defines it. "Frame" usually means the frame is up and the frame inspection has passed.
- Some states cap the deposit and limit how much each stage can be worth, or require claims to match work done. Check the [state rules](/states/overview.md) before setting up the schedule.
- Approved variations are claimed with the next progress claim, after the client has signed them ([variations](/contracts/variations.md)).
- Prime cost and provisional sum adjustments are claimed when the actual cost is known ([Allowances Register](/documents/allowances_register.md)).

# What a claim needs

1. **A valid tax invoice.**[^ato_tax_invoice] It must:
   - say it's a tax invoice
   - show the builder's identity and ABN, the date, a description of what's claimed, and the GST
   - for $1,000 or more, show the client's identity or ABN
2. **The contract basis.** The stage claimed, the contract and claim numbers, and the due date under the contract's payment terms.
3. **The arithmetic.** Contract value, % complete, claimed to date, previous claims, retention, net, GST and total. Always run it through the [progress claim computation](/computations/progress_claim.md).
4. **Evidence.**[^beam_claim_pack] Dated photos, site diary extracts, inspection certificates for the stage, signed variations, and current insurance certificates. The [Claim Support Pack Checklist](/documents/claim_support_pack_checklist.md) lists them.

A well-supported claim gets paid faster and is harder to dispute.

# Retention

Retention is a percentage held back from each claim as security for defects,
usually capped at a percentage of the contract sum and released in parts at
practical completion and at the end of the defects liability period.

- It is rare in residential contracts with homeowners, but common in subcontracts and commercial work.
- Track what is held and when it falls due with the [Retention Release Tracker](/documents/retention_release_tracker.md).
- Some states have rules on how retention must be held (for example in trust) once a contract passes a threshold value. Check the state rules.

# Security of payment

Each state has a security-of-payment act (listed in the [state rules](/states/overview.md))
that gives a fast statutory process for payment claims, schedules and
adjudication.

- **Builder to homeowner.** Most states exclude residential building work for an owner-occupier from their security-of-payment act, so the contract and the state's home building law govern these claims. Verify for the state.
- **Subcontractor to builder.** These claims are usually covered. The builder must answer a payment claim with a payment schedule within the statutory time, or risk owing the full claimed amount. Diarise every subbie claim the day it arrives.

# Paying subcontractors

- Check each subbie's licence and insurance are current before paying ([Subbie Insurance and Licence Tracker](/documents/subbie_insurance_licence_tracker.md)).
- Track agreed amounts, claims and balances in the [Subbie Payment Schedule](/documents/subbie_payment_schedule.md).
- Deduct back charges only with written notice ([Back Charge Notice](/documents/back_charge_notice.md)).

# Chasing payment

Track every claim in the [Payment Tracking Register](/documents/payment_tracking_register.md).
When a claim is overdue, check the contract's interest and suspension
clauses ([clause map](/contracts/hia_mba_clause_map.md)) before acting.
Suspending work has strict notice requirements, and getting it wrong can
put the builder in breach.

[^ato_tax_invoice]: ATO, Tax invoices
[^beam_claim_pack]: Claim Support Pack Checklist (Australian Builder's Brain template pack)

---
type: Contract Topic
title: Site instructions and back charges
description: Recording instructions given on site, and charging subcontractors for rework, damage or clean-up, so neither turns into a dispute.
tags: [contracts, notices, subcontractors, site_instructions, back_charges]
status: draft
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

> **Draft.** This is general practice. The subcontract's own notice,
> rectification and set-off clauses decide what is allowed.

# Site instructions

A site instruction records a direction given on site, to a trade or about
the work: what to do, where, by when, and why. It turns a conversation into
evidence.

- Issue one whenever a direction changes method, sequence, scope or quality expectations, or resolves a drawing clash.
- Number them (SI-001 ...), have the receiver sign, and keep a copy in the project file.
- **An instruction that changes scope or cost is also a variation.** For the client, raise a [variation](/contracts/variations.md) and reference its number on the instruction. For a subcontractor, agree the price in writing before the work.
- **If it costs time**, note "EOT Required" and follow up with an [extension of time](/contracts/extension_of_time.md) notice.
- Template: [Site Instruction Form](/documents/site_instruction_form.md).

# Back charges

A back charge recovers the builder's cost when a subcontractor's defective
work, damage to other trades' work, unfinished clean-up or non-compliance
with scope forces the builder to pay to fix it.

1. **Give notice and a chance to fix it.** Most subcontracts require written notice and a reasonable time for the subbie to rectify at their own cost before the builder steps in. The template allows 7 days; use the subcontract's period if it differs.
2. **Evidence.** Dated photos, the scope or drawing it breaches, any earlier verbal warnings (with dates), and quotes or invoices for the fix.
3. **Cost it properly.** Itemise labour, materials, third-party costs and other costs ex GST, then add GST. Use the [variation price](/computations/variation_price.md) computation with `margin_pct` at 0 (or the admin margin the subcontract allows). Map Rectification Labour to `labour`, Replacement Materials to `materials`, Third-Party Costs to `subcontractor`, and Other to `other`.
4. **Deduct only what the subcontract allows.** If the subbie's claim falls under security-of-payment law, any amount withheld must appear, with reasons, in the payment schedule sent within the statutory time ([progress payments](/contracts/progress_payments.md)).
5. Template: [Back Charge Notice](/documents/back_charge_notice.md). Record the deduction in the [Subbie Payment Schedule](/documents/subbie_payment_schedule.md).

# Delay notices

See [extension of time](/contracts/extension_of_time.md) and the
[Delay Notification Letter](/documents/delay_notification_letter.md). Work
out the revised completion date with [add days](/computations/add_days.md).

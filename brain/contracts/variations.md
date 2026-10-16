---
type: Contract Topic
title: Variations
description: How a residential variation moves from request to price, approval, invoice and payment, and which templates cover each step.
tags: [contracts, variations, money]
status: draft
sources:
  - id: beam_templates
    resource: /documents/index.md
    title: BEAM Builder Template Pack
    author: human:grechj
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

A variation is any change to the contract works: added, changed or
omitted work. In residential building, an undocumented variation is one of
the most common causes of disputes and unpaid work.

# The rule of thumb

**Nothing changes on site until the variation is in writing, priced and
signed.** Most state home building laws require residential variations to be
in writing and signed by both parties, and some limit what a builder can
recover for a variation that wasn't. See the [state rules](/states/overview.md)
for the job's state.

# Workflow

The status values match the [Variation Register](/documents/variation_register.md).

| Step | Status | Template |
|---|---|---|
| 1. Client asks for a change | Requested | [Client Change Request](/documents/client_change_request.md) |
| 1a. Or the builder raises one (latent conditions, authority requirement, design error) | Requested | [Builder Initiated Variation](/documents/builder_initiated_variation.md) |
| 2. Price it: cost lines, margin, GST, time impact | Priced | [Priced Variation Notice](/documents/priced_variation_notice.md), priced with the [variation price](/computations/variation_price.md) computation |
| 2a. Explain it if the client is likely to push back | Priced | [Variation Explanation Letter](/documents/variation_explanation_letter.md) |
| 3. Client signs | Approved or Rejected | [Variation Approval Form](/documents/variation_approval_form.md) |
| 4. Bill it in the next progress claim | Invoiced | [Progress Claim Invoice](/documents/progress_claim_invoice.md) |
| 5. Payment received | Paid | [Payment Tracking Register](/documents/payment_tracking_register.md) |

Every variation gets a number (VAR-001, VAR-002 ...) and a row in the register.

# What every priced variation states

- What work is added, changed or omitted, where, and the drawing or spec it changes
- The reason: client request, latent conditions, regulatory compliance, design change, other
- Cost breakdown ex GST, the builder's margin, GST and the total inc GST
- Time impact in days, and the revised completion date
- The contract clause it is issued under ([clause map](/contracts/hia_mba_clause_map.md))
- How long the price is valid (7, 14 or 30 days)
- A signature block for both parties

# Time impact

If a variation adds time, say so in the variation itself. A separate
[extension of time](/contracts/extension_of_time.md) claim made later is
harder to support.

# Prime cost and provisional sums

Adjustments to PC items and provisional sums are tracked in the
[Allowances Register](/documents/allowances_register.md). Depending on the
contract they may be claimed as adjustments rather than variations, but the
paperwork discipline is the same.

# Internal margin check

Page 2 of the Priced Variation Notice is internal: it compares actual cost
with the quoted price. Use the [margin](/computations/margin.md) computation,
and never send page 2 to the client.

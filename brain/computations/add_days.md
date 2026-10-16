---
type: Attested Computation
title: Add calendar or working days to a date
description: Moves a date forward by calendar or working days, skipping weekends, public holidays and shutdowns. Used for revised completion dates and notice deadlines.
tags: [dates, delays, eot, notices]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: add_days
computation_sha256: b6f19cc356118580f48815dea77a7777ff2d76264e6cf690208875f67f469d8f
parameters:
  - { name: start_date, type: date, required: true }
  - { name: days, type: decimal, required: true }
  - { name: day_type, type: string, required: true }
  - { name: non_working_days, type: json, required: false, default: "[]" }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

- **Calendar days**: every day counts.
- **Working days**: Monday to Friday, skipping each date in
  `non_working_days`. That covers the state's public holidays, the
  industry Christmas shutdown, and any rostered days off the contract
  excludes.

Contracts differ on whether extensions and notice periods count calendar or
working days, and on which days are non-working. Read the contract (or ask)
and pass the right `day_type`. Never assume. Public holidays differ by state
and year, so get the list for the job's state.

Dates are DD/MM/YYYY. A shutdown can be given as a range:
`"20/12/2026-09/01/2027"`.

# Computation

Runs `add_days()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py add_days --param start_date=30/09/2027 --param days=5 \
        --param day_type=working --param 'non_working_days=["04/10/2027"]'

Use it for the revised completion date on a
[Delay Notification Letter](/documents/delay_notification_letter.md), and
for "notify within N days" deadlines under the
[extension of time](/contracts/extension_of_time.md) clause.

---
type: Attested Computation
title: Add a calendar period to a date
description: Adds years, months, weeks and days to a date. Used for defects liability period end dates and statutory warranty end dates.
tags: [dates, defects, warranty, handover]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: add_period
computation_sha256: e5db695c6b28e18cfc851be46cd897eac3acdd435d6b6528cfe7b362f28c4917
parameters:
  - { name: start_date, type: date, required: true }
  - { name: years, type: decimal, required: false, default: 0 }
  - { name: months, type: decimal, required: false, default: 0 }
  - { name: weeks, type: decimal, required: false, default: 0 }
  - { name: days, type: decimal, required: false, default: 0 }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

Adds years and months first, landing on the same day of the month (or the
last day of a shorter month). Then it adds weeks and days. Every day counts;
for working days use [add days](/computations/add_days.md).

Typical uses, all counted from the date of practical completion (check the
contract and state law for the actual periods):

- Defects liability period end: `weeks=13` is common in residential contracts
- Statutory warranty ends: periods differ by state, see [practical completion and defects](/contracts/practical_completion_and_defects.md)

# Computation

Runs `add_period()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py add_period --param start_date=08/10/2027 --param weeks=13

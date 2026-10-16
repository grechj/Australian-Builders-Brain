---
type: Attested Computation
title: Site week number
description: The construction week number of a date, counting from the site start date, for weekly progress updates.
tags: [dates, site, progress]
status: stable
runtime: python
computation: /references/computations/builder_maths.py
entry_point: site_week
computation_sha256: 146109d8e347ef9f027a3d6fa3bf877aec54fb55635dcc4b5ce367987494f7a7
parameters:
  - { name: start_date, type: date, required: true }
  - { name: on_date, type: date, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

# Definition

Week 1 is the seven days from the site start date (`start_date` in the
project file). Week number = whole weeks since start + 1. It fills
`[WEEK_NUMBER]` on the [Progress Update Email](/documents/progress_update_email.md).

# Computation

Runs `site_week()` in [builder_maths.py](/references/computations/builder_maths.py).

    python tools/compute.py site_week --param start_date=03/02/2027 --param on_date=16/04/2027

---
type: Playbook
title: Run a computation
description: How an agent runs an Attested Computation and checks the receipt before using the numbers.
tags: [computations, money]
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

1. Pick the computation concept in [computations](/computations/index.md) and read its `parameters`.
2. Get every required value from the user or the project file. Never guess a cost or margin.
3. Run `python tools/compute.py <name> --param name=value ...` and save the JSON receipt.
4. Run `python brain/references/attesters/check_receipt.py <receipt.json>`. If it fails, stop and tell the user. Don't use the numbers.
5. Pass the receipt's `fields` to `tools/fill_template.py` as `--set KEY=VALUE`.
6. Quote the numbers to the user exactly as they appear in the receipt.

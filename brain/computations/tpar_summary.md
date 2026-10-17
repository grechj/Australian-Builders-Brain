---
type: Attested Computation
title: TPAR contractor payments
description: Totals the payments made to each contractor in a financial year for the Taxable payments annual report (TPAR) - gross paid including GST, the GST in it, and tax withheld.
tags: [money, tpar, tax, subcontractors, accounts]
status: draft
runtime: python
computation: /references/computations/finance_maths.py
entry_point: tpar_summary
computation_sha256: 9cf62924924f24eaf3dafc99796bdd34e761455239aef66f0566fbc20b28fdfd
parameters:
  - { name: transactions, type: json, required: true }
  - { name: year_ending, type: string, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
sources:
  - id: ato_tpar_building
    resource: https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/reports-and-returns/taxable-payments-annual-report/building-and-construction-industry
    title: ATO, Taxable payments annual report, building and construction industry
    author: org:ato
generated: { by: claude/opus-5.5, at: 2026-10-17T00:00:00Z }
---

> **Draft.** Check what to include against the ATO's TPAR guidance for your
> business; have your accountant or BAS agent review the first report.

# Definition

A business that is mainly in building and construction and pays contractors
for building and construction services reports those payments to the ATO
each year, by 28 August, in the Taxable payments annual report.[^ato_tpar_building]

For each contractor paid in the financial year (1 July to 30 June), the
report needs their ABN, name and address, the gross amount paid including
GST, the GST included, and any tax withheld because no ABN was quoted.

- **Payments, not invoices.** Only what was actually paid in the year counts.
- **Which bills.** Bills marked `tpar: true` in the ledger, which `tools/finance.py` sets for bills coded to the accounts listed in `tpar_accounts` (usually subcontractors). Override it per bill: materials-only supply isn't reportable, a mixed labour and materials invoice is.
- **Grouped by ABN**, so two bills from the same contractor make one row.

The receipt lists each payee, the totals, the due date, and warnings for any
payee with no ABN or address.

# Computation

Runs `tpar_summary()` in [finance_maths.py](/references/computations/finance_maths.py).

    python tools/finance.py tpar ledger.yaml --year 2027

[^ato_tpar_building]: ATO, Taxable payments annual report, building and construction industry

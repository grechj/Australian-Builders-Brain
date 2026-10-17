---
type: Attested Computation
title: BAS GST summary
description: Works out the GST labels of a Business Activity Statement (G1, G2, G3, G4, G10, G11, 1A, 1B) for one period from the job ledger, on a cash or accrual basis.
tags: [money, gst, bas, tax, accounts]
status: draft
runtime: python
computation: /references/computations/finance_maths.py
entry_point: bas_summary
computation_sha256: 9cf62924924f24eaf3dafc99796bdd34e761455239aef66f0566fbc20b28fdfd
parameters:
  - { name: transactions, type: json, required: true }
  - { name: period_start, type: date, required: true }
  - { name: period_end, type: date, required: true }
  - { name: basis, type: string, required: true }
executor:
  resource: /references/run_computation.md
  receipt: [computation, computation_sha256, parameters, result, fields]
attester:
  resource: /references/attesters/check_receipt.py
sources:
  - id: ato_bas_gst
    resource: https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/business-activity-statements-bas/goods-and-services-tax-gst
    title: ATO, Reporting GST on your BAS
    author: org:ato
  - id: ato_accounting_basis
    resource: https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst/in-detail/your-industry/accounting-for-gst-in-your-business
    title: ATO, Choosing an accounting method for GST
    author: org:ato
generated: { by: claude/opus-5.5, at: 2026-10-17T00:00:00Z }
---

> **Draft.** The label rules follow the ATO's BAS instructions as summarised
> here; have your accountant or BAS agent check the first BAS you prepare
> this way. The brain never lodges anything.

# Definition

A BAS reports GST for a period (usually a quarter).[^ato_bas_gst] Using the
job ledger (`tools/finance.py`), each transaction counts in the period:

- **Accrual basis:** in full if its date (the invoice or bill date) is in the period.
- **Cash basis:** to the extent it was paid in the period. A claim paid half this quarter and half next counts half in each.[^ato_accounting_basis]

Credit notes and supplier credits count as negatives. Lines coded
`bas_excluded` (retention held, loans, wages) are left out.

| Label | What goes in it |
|---|---|
| G1 | Total sales, including GST, including GST-free, export and input-taxed sales |
| G2 | Export sales (tax code `export`) |
| G3 | Other GST-free sales (`gst_free`) |
| G4 | Input-taxed sales (`input_taxed`), for example residential rent |
| G10 | Capital purchases, including GST (`capital`) |
| G11 | Non-capital purchases, including GST |
| 1A | GST on sales |
| 1B | GST on purchases (GST credits) |

The receipt shows each label to the cent and in whole dollars with the cents
dropped (as the BAS form takes them), the net GST payable or refundable, and
every transaction counted with its share.

# Computation

Runs `bas_summary()` in [finance_maths.py](/references/computations/finance_maths.py).
`tools/finance.py bas` normalises the ledger and runs it for you:

    python tools/finance.py bas ledger.yaml --from 01/07/2026 --to 30/09/2026 --basis accrual

[^ato_bas_gst]: ATO, Reporting GST on your BAS
[^ato_accounting_basis]: ATO, Choosing an accounting method for GST

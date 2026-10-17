---
type: Contract Topic
title: Accounts and tax
description: "How a builder's claims, invoices and bills become entries in Xero, MYOB or QuickBooks, and what that means for GST, the BAS and the TPAR: the job ledger, account mapping, retention, deposits and the official connectors."
tags: [contracts, accounts, gst, bas, tpar, xero, myob, quickbooks]
status: draft
sources:
  - id: ato_gst_basis
    resource: https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst/in-detail/your-industry/accounting-for-gst-in-your-business
    title: ATO, Choosing an accounting method for GST
    author: org:ato
  - id: ato_bas
    resource: https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/business-activity-statements-bas/goods-and-services-tax-gst
    title: ATO, Reporting GST on your BAS
    author: org:ato
  - id: ato_tpar
    resource: https://www.ato.gov.au/businesses-and-organisations/preparing-lodging-and-paying/reports-and-returns/taxable-payments-annual-report/building-and-construction-industry
    title: ATO, Taxable payments annual report, building and construction industry
    author: org:ato
  - id: ato_tax_invoice
    resource: https://www.ato.gov.au/businesses-and-organisations/gst-excise-and-indirect-taxes/gst/tax-invoices
    title: ATO, Tax invoices
    author: org:ato
  - id: xero_import
    resource: https://central.xero.com/s/article/Import-bills-and-credit-notes
    title: Xero Central, Import bills and credit notes
  - id: myob_fields
    resource: https://www.myob.com/au/support/myob-business/import-export/myob-business-importing-and-exporting-data-import-and-export-fields
    title: MYOB, Import and export fields
  - id: openaccountants
    resource: https://github.com/openaccountants/openaccountants
    title: OpenAccountants, AI skills for tax (AU GST, BAS, TPAR, bookkeeping)
generated: { by: claude/opus-5.5, at: 2026-10-17T00:00:00Z }
stale_after: 2027-04-17T00:00:00Z
---

> **Draft.** This is how the brain hands money to your accounting software,
> not tax advice. Have your accountant or BAS agent check your account
> mapping once and the first BAS and TPAR you prepare this way. The brain
> never lodges anything with the ATO.

# The idea

The brain already produces the documents money moves on: progress claims,
payment claims, tax invoices, variations, subbie payment schedules and back
charges. The **job ledger** (`ledger.yaml`, see
[`examples/ledger_example.yaml`](https://github.com/grechj/Australian-Builders-Brain/blob/main/examples/ledger_example.yaml))
records each one as a transaction, with the payments against it:

- **invoice** or **credit_note**: what you bill (claims, variations, tax invoices)
- **bill** or **supplier_credit**: what you're billed (subbies, suppliers, hire)

Each line has an ex-GST amount, a **role** (contract income, subcontractors,
materials...) and a **tax code** (`gst`, `gst_free`, `export`,
`input_taxed`, `capital`, `bas_excluded`). The **account mapping**
(`accounts.yaml`, see [`examples/accounts_example.yaml`](https://github.com/grechj/Australian-Builders-Brain/blob/main/examples/accounts_example.yaml))
turns roles into your own account codes, once. Then `tools/finance.py`:

1. **checks** the ledger (dates, tax codes, roles, ABN checksums, overpayments)
2. **exports** import files for Xero (CSV), MYOB AccountRight (tab-delimited) or QuickBooks Online (CSV)
3. **builds a payload** for pushing drafts through your own Xero, MYOB or QuickBooks connector
4. works out the **BAS** GST labels ([BAS summary](/computations/bas_summary.md)) and the **TPAR** ([TPAR summary](/computations/tpar_summary.md)) as attested computations

The ledger is per job; the accounting software stays the books of record.

# Getting it into the software

| Software | Import file | Notes |
|---|---|---|
| Xero | Sales invoices CSV and bills CSV | Imports arrive as drafts. Choose "tax exclusive". Credit notes are negative amounts. Account codes, tax rate names and tracking options must match Xero exactly.[^xero_import] |
| MYOB AccountRight | Service Sales and Service Purchases, tab-delimited | Cards, accounts, jobs and tax codes must already exist. Invoice numbers up to 8 characters. Back up first.[^myob_fields] MYOB Business (the browser product) has no invoice import: use the connector. |
| QuickBooks Online | Invoices CSV (and bills where your region offers it) | Columns are mapped on screen. No credit notes, and at most 100 invoices per file. Draft format: check against the sample file. |

**Connectors.** Xero (`mcp.xero.com`), MYOB (`mcp.myob.com`) and QuickBooks
publish official connectors for Claude. Each user signs in with their own
account, so no keys or passwords ever go in the brain. The accounts skill
creates **drafts only**, after showing the user every transaction and getting
a clear yes; the user approves them in their software.

**Job tracking.** Code every line to the job: a Xero tracking category
(`tracking_name` in the mapping, the job number as the option), an MYOB job
or a QuickBooks location. That's what makes the job P&L in your software
match the [Budget vs Actual Tracker](/documents/budget_vs_actual_tracker.md).

# GST timing

- **Accrual basis** (the default for most builders once turnover passes $10 million, and an option below it): GST counts in the period you issue the invoice, or receive any payment, whichever is first.[^ato_gst_basis]
- **Cash basis** (available to smaller businesses): GST counts when you're paid, and only for the part paid. A progress claim paid half this quarter and half next counts half in each.[^ato_gst_basis]
- **Deposits.** A deposit that is part payment of the price counts for GST when it's received (or invoiced, if earlier). Record it as an invoice in the ledger.
- **Tax invoices.** Every claim to a GST-registered client over $82.50 needs to be a valid tax invoice: the Progress Claim Invoice and Tax Invoice templates are.[^ato_tax_invoice]

# Retention

Two common ways, and your accountant should pick one:

- **Invoice in full.** Invoice the whole claim, with a "less retention held" line coded to a retention receivable account and `bas_excluded`. GST is on the full claim, now; the retention sits as an asset until released.
- **Invoice on release.** Invoice only the net claim now, and the retention as a separate invoice when it's released. GST follows each invoice.

On subbie bills it's the mirror image: a negative retention line coded to
retention payable and `bas_excluded` (see bill HS-118 in the example ledger).

# BAS

The [BAS summary](/computations/bas_summary.md) gives G1, G2, G3, G4, G10,
G11, 1A and 1B for the period, on your basis, to the cent and in whole
dollars, with every transaction it counted.[^ato_bas] Your software will
produce the BAS from its own books; use the brain's summary to check the
job's part of it, or when the books aren't in software yet. PAYG
withholding and instalments (W and T labels) come from payroll and the
ATO, not from the job ledger.

# TPAR

A business that is mainly in building and construction (50% or more of its
income or activity) reports its payments to contractors for building and
construction services each year by 28 August.[^ato_tpar] The
[TPAR summary](/computations/tpar_summary.md) totals, per contractor, what
was paid in the year including GST, the GST, and any tax withheld. Bills
coded to subcontractors (or labour hire) count by default; materials-only
supply doesn't. Set `tpar: false` or `true` on a bill to override.

# Dashboard and extracts

`tools/dashboard.py` reads a portfolio file listing every job (current and
completed) with its ledger, timesheets and budget, and runs the
[job dashboard](/computations/job_dashboard.md) computation. It writes CSV
extracts (one row per job, per job and month, per cost category, and the
averages across completed jobs) and a self-contained dashboard page: profit
and margin against target, contract and variations, invoiced and received,
outstanding, costs against budget, cash in and out by month, days on site
and labour, and job length against the contract period and the average of
completed jobs of the same type. The CSVs load straight into Excel, Google
Sheets, Power BI or Looker Studio, and are what a web app would read.

- **Documents.** Each job's documents folder is scanned for what the skills generated (claims, variations, notices, RFIs, minutes, diaries...). The dashboard lists them, typed by template and numbered from the file name, with links to the files, or to the same folder in Dropbox, Google Drive or SharePoint if a `documents_url` is set. `documents.csv` is the register.
- **Modelling.** `transactions.csv` and `transaction_lines.csv` are the job ledgers flattened, with financial year, quarter, days to settle and days overdue: the tables to pivot or model cash flow from. `cost_mix.csv` gives each cost category as a percentage of revenue, averaged across completed jobs by project type, for checking new estimates. `jobs.csv` carries a forecast at completion (each cost category at the larger of budget and actual).
- **Manual import.** `imports/<software>/` holds one set of Xero, MYOB or QuickBooks import files covering every job, tracked by job; `--since` limits it to transactions since the last send.

# Tax questions beyond the job

For tax rules beyond these summaries (BAS labels in depth, PAYG, TPAR edge
cases, chart of accounts design), the OpenAccountants AI skills cover
Australia in detail and can be installed alongside the brain as a separate
Claude plugin. Their content is free to use but can't be copied into this
brain, so the brain points to them rather than including them.[^openaccountants]

[^ato_gst_basis]: ATO, Choosing an accounting method for GST
[^ato_bas]: ATO, Reporting GST on your BAS
[^ato_tpar]: ATO, Taxable payments annual report, building and construction industry
[^ato_tax_invoice]: ATO, Tax invoices
[^xero_import]: Xero Central, Import bills and credit notes
[^myob_fields]: MYOB, Import and export fields
[^openaccountants]: OpenAccountants, AI skills for tax (AU GST, BAS, TPAR, bookkeeping)

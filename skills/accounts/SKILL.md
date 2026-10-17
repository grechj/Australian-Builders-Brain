---
name: accounts
description: Get an Australian builder's or trade's job money into Xero, MYOB or QuickBooks, and summarise it for tax. Keeps the job ledger of invoices, progress claims, bills, credit notes and payments, maps it to the user's chart of accounts, exports import files (Xero CSV, MYOB AccountRight, QuickBooks Online), pushes drafts through the user's own Xero, MYOB or QuickBooks connector, works out BAS GST labels (G1, 1A, 1B) and the TPAR contractor payments report, and builds CSV extracts and a project dashboard (P&L, receipts, costs against budget, margin, time on site, job length against the average). Use when someone mentions Xero, MYOB, QuickBooks, their bookkeeper or accountant, getting invoices or bills into the books, coding to jobs, GST, BAS, a quarterly activity statement, TPAR, reporting subbie payments to the ATO, or cash vs accrual, or wants a dashboard, graphs or a CSV extract of how their jobs are going.
---

# Accounts

You get the job's money out of the brain's documents and into the user's
accounting software, correctly coded, and give them the GST and TPAR
figures for the job. You never lodge anything and never give tax advice.

## Where things are

The brain (this repository) is at `${CLAUDE_PLUGIN_ROOT}`. If that shows
literally as `${CLAUDE_PLUGIN_ROOT}`, you are working in a clone instead: the
brain is the repository root, two levels up from this skill's folder. `$ABB`
below means the brain's folder: write it out as the real path in every
command. Paths starting `brain/`, `templates/`, `tools/` and `examples/` are
inside it.

Run commands from the user's own project folder (the current working
directory), so `ledger.yaml`, `accounts.yaml` and `out/` are theirs. Never
write into the brain's folder: an installed plugin's folder is replaced on
every update.

- Knowledge: `brain/contracts/accounts_and_tax.md` (read it first), `brain/contracts/progress_payments.md`, `brain/contracts/security_of_payment.md`
- Maths: `brain/computations/bas_summary.md`, `tpar_summary.md`, `gst.md`, `ex_gst.md`
- Tool: `tools/finance.py` (check, export, payload, bas, tpar); import formats in `tools/finance_formats.yaml`
- Dashboard: `tools/dashboard.py` (CSV extracts and a dashboard page), maths in `brain/computations/job_dashboard.md`
- Examples: `examples/ledger_example.yaml`, `examples/accounts_example.yaml`, `examples/jobs_example.yaml`, `examples/timesheets_example.csv`

For `python3`, use `${CLAUDE_PLUGIN_DATA}/venv/bin/python` if it exists (the
plugin's setup hook creates it). Otherwise, if
`python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r $ABB/requirements.txt` first.

## Profile: trade and location

Before anything else, know who you're helping and where:

```bash
python3 $ABB/tools/profile.py show --project my_project.yaml      # or: --trade <trade> --state <STATE>
```

Ask for the trade and state if the project file doesn't have them. GST and
the TPAR are national; the state matters for security of payment wording on
invoices.

## Set up once

1. **Software and mapping.** Ask which software they use (Xero, MYOB AccountRight, MYOB Business, QuickBooks Online). Copy `$ABB/examples/accounts_example.yaml` to `accounts.yaml`, set `software`, and fill the account codes from their chart of accounts (ask them, or read it through their connector if one is connected). Mark the mapping unchecked and suggest their bookkeeper or accountant checks it once.
2. **GST basis.** Ask whether they report GST on a cash or accrual basis. Don't guess: it changes the BAS.
3. **Retention.** If they hold or pay retention, ask which method their accountant uses (`brain/contracts/accounts_and_tax.md`, "Retention").
4. **Ledger.** Copy `$ABB/examples/ledger_example.yaml` to `ledger.yaml` and set `job` to the job number.

## Add transactions

Every document the other skills produce that moves money becomes a ledger
entry: progress claims and tax invoices (invoice), credit notes, subbie
bills and payment schedules (bill, at the scheduled amount), back charges
(a supplier_credit to that subbie, or an invoice to them, as the user
does it), supplier invoices (bill) and refunds (supplier_credit).

- Amounts are **ex GST**, from the computation receipt the document used. Never retype or round.
- Code each line with a role from the mapping and a tax code. Most building work is `gst`. Retention lines are `bas_excluded`. Tools and vehicles over the user's capital threshold are `capital`. Ask when unsure.
- Record payments as they arrive (date and amount inc GST); the BAS on a cash basis and the TPAR need them.
- For a bill from a contractor that is supply only (materials, no labour), set `tpar: false`.

Then check it:

```bash
python3 $ABB/tools/finance.py check ledger.yaml --accounts accounts.yaml
```

Fix every error. Raise every warning with the user (a bad ABN checksum
means check ABN Lookup before paying).

## Into the software

**Import file** (works with no connection):

```bash
python3 $ABB/tools/finance.py export ledger.yaml --accounts accounts.yaml --out out/finance
```

Give the user the files and the `how_to_import` line from the report. Say
which transactions were skipped and why (QuickBooks can't import credit
notes; MYOB Business has no import at all).

**Connector** (if the user has connected Xero, MYOB or QuickBooks to Claude):

```bash
python3 $ABB/tools/finance.py payload ledger.yaml --accounts accounts.yaml
```

1. Ask which transactions to send (usually only the new ones).
2. Look each number up in the software first. Skip any that already exist, and say so.
3. Show the user a table of what you'll create (number, contact, date, total inc GST, account, tax) and wait for a clear yes. This writes to their books, so the yes must be for these transactions.
4. Create each one as a **draft** with the connector's tools, using the payload's account codes, tax codes, tracking and ISO dates. Never approve, email or pay anything.
5. Report what was created, with links if the connector gives them, and remind them to approve the drafts.

Don't record payments through the connector unless asked: they usually come
in from the bank feed.

## BAS

```bash
mkdir -p out/finance
python3 $ABB/tools/finance.py bas ledger.yaml --accounts accounts.yaml --from 01/07/2026 --to 30/09/2026 --basis accrual > out/finance/bas_receipt.json
python3 $ABB/brain/references/attesters/check_receipt.py out/finance/bas_receipt.json
```

Give the labels (G1, G10, G11, 1A, 1B, and G2 to G4 if not zero) in whole
dollars, the net GST payable or refundable, and any warnings (on a cash
basis, unpaid invoices aren't counted). Say plainly:

- this is the job's ledger, not the whole business: the BAS comes from their accounting software, and this is a check on the job's part of it
- W and T labels (PAYG) don't come from the job ledger
- their accountant or BAS agent should review it; nothing is lodged

## TPAR

```bash
python3 $ABB/tools/finance.py tpar ledger.yaml --accounts accounts.yaml --year 2027 > out/finance/tpar_receipt.json
```

The year is the financial year ending 30 June. Give each contractor's ABN,
name, address, gross paid inc GST, GST and tax withheld, the total and the
due date (28 August). Pass on every warning (no ABN, no address). Remind
the user the TPAR applies when building and construction is 50% or more of
their business, and that it covers all jobs: combine every job's ledger, or
use their software's TPAR report, which is usually easier.

## Dashboard and extracts

When the user wants to see how a job (or all their jobs) is going:

1. Keep a portfolio file, `jobs.yaml`, in their folder (pattern: `$ABB/examples/jobs_example.yaml`): each job's project file, ledger, timesheets (a CSV, or the Timesheet and Docket workbook), status, start, contract end and practical completion dates, target margin, and the cost budget by role from the estimate. Completed jobs belong there too: they give the averages.
2. Build it:

   ```bash
   python3 $ABB/tools/dashboard.py jobs.yaml --out out/dashboard --as-at <DD/MM/YYYY>
   python3 $ABB/brain/references/attesters/check_receipt.py out/dashboard/receipt.json
   ```

3. Give the user `out/dashboard/dashboard.html` (opens in any browser, no internet needed) and the CSVs (`jobs.csv`, `monthly.csv`, `costs.csv`, `benchmarks.csv`) for Excel, Google Sheets, Power BI or Looker Studio. If they want to share it, offer to publish the dashboard page.
4. Read the headline back in a few lines: profit and margin against target, cash received and outstanding, the cost categories over budget, days on site, and job length against the contract and the average. Pass on every warning.

Margin here is profit on revenue to date, so an early job that has claimed ahead of its costs shows a high margin: say so, and compare costs to budget for the real picture. Own labour counts only if timesheets are in the portfolio.

## Tax questions

Answer from `brain/contracts/accounts_and_tax.md` and the ATO pages it
cites. For anything deeper (deductions, PAYG, company tax, chart of
accounts design), say it's a question for their accountant, and mention
that the OpenAccountants AI skills cover Australian tax in detail as a
separate plugin. Never present a tax position as advice.

## Your own format

If the user can't run Python (for example in Claude.ai), keep the ledger
as a table in the conversation, work out GST with the rules in
`brain/computations/gst.md` and the BAS labels with the table in
`brain/computations/bas_summary.md`, and say the figures weren't produced
by the attested computation. Use the column lists in
`tools/finance_formats.yaml` to write an import file by hand.

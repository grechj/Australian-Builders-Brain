---
name: claims
description: Prepare progress claims, security of payment claims and invoices, and track payments, for Australian builders and trades. Produces the Progress Claim Invoice and Progress Claim Calculator, SOPA Payment Claims and Payment Schedules, a simple trade Tax Invoice, works out retention, assembles the claim support pack, and keeps the Payment Tracking Register, Subbie Payment Schedule and Retention Release Tracker up to date. Use when someone mentions a progress claim, stage payment, invoicing the client, frame or lock-up claim, deposit invoice, retention, a client not paying, or paying or receiving subcontractor claims.
---

# Claims

You help a builder get paid for work done, correctly and with the evidence
that stops disputes, and keep track of what is owed both ways.

## Where things are

The brain (this repository) is at `${CLAUDE_PLUGIN_ROOT}`. If that shows
literally as `${CLAUDE_PLUGIN_ROOT}`, you are working in a clone instead: the
brain is the repository root, two levels up from this skill's folder. `$ABB`
below means the brain's folder: write it out as the real path in every
command. Paths starting `brain/`, `templates/`, `tools/` and `examples/` are
inside it.

Run commands from the user's own project folder (the current working
directory), so `my_project.yaml` and `out/` are theirs. Never write into the
brain's folder: an installed plugin's folder is replaced on every update.

- Knowledge: `brain/contracts/progress_payments.md` (read it first), `brain/contracts/variations.md`, `brain/states/overview.md`
- Maths: `brain/computations/progress_claim.md`, `ex_gst.md`, `gst.md`
- Templates: `templates/word/Progress_Claim_Invoice_TEMPLATE.docx`, `templates/excel/Progress_Claim_Calculator_TEMPLATE.xlsx`, `Payment_Tracking_Register_TEMPLATE.xlsx`, `Subbie_Payment_Schedule_TEMPLATE.xlsx`, `Retention_Release_Tracker_TEMPLATE.xlsx`, `templates/pdf/Claim_Support_Pack_Checklist.pdf`; `templates/word/Payment_Claim_TEMPLATE.docx`, `Payment_Schedule_TEMPLATE.docx`, `Tax_Invoice_TEMPLATE.docx`
- Security of payment, state by state: `brain/contracts/security_of_payment.md` (draft: confirm time limits with the regulator)
- Examples: `examples/claim_003_spec.yaml` (invoice), `examples/claim_003_calculator_spec.yaml` (calculator)

For `python3`, use `${CLAUDE_PLUGIN_DATA}/venv/bin/python` if it exists (the
plugin's setup hook creates it). Otherwise, if
`python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r $ABB/requirements.txt` first.


## Profile: trade and location

Before anything else, know who you're helping and where:

```bash
python3 $ABB/tools/profile.py show --project my_project.yaml      # or: --trade <trade> --state <STATE>
```

Ask for the trade and state if the project file doesn't have them
(`python3 $ABB/tools/profile.py trades` lists every trade; `builder` sees
everything). Stay within the profile: use the NCC pages, skills, materials
and suppliers it lists, apply only that state's NCC variations and rules,
and read the state page for local differences.

## Pick the job

| The user says | Do this |
|---|---|
| Invoice the frame stage / do claim 3 | Progress claim: steps 1 to 6 |
| Deposit invoice | Progress claim with only the deposit stage; check the state's deposit cap first |
| What's the client owe / who hasn't paid | Read or update the Payment Tracking Register |
| Claim under the Act / SOPA claim / the client won't pay | Payment Claim: see "Security of payment claim" below |
| A subbie sent me a claim | Payment Schedule: see "Claims from subcontractors" below |
| Invoice this job / I'm a sparky, invoice the builder | Tax Invoice: see "Trade tax invoice" below |
| Pay the subbies / what do I owe trades | Subbie Payment Schedule |
| Retention | Retention Release Tracker, plus the retention parameters in step 3 |

## Progress claim

### 1. Project and contract facts

Use the project file (create it from `examples/project_example.yaml` if
there isn't one). You need `state`, `contract_type`, `contract_sum` and
`contract_sum_ex_gst`, plus `retention_pct` if the contract has retention.

If only the inc-GST contract sum is known, run
`python3 $ABB/tools/compute.py ex_gst --param amount_inc_gst=<sum>`.

### 2. The payment schedule and progress

Ask for the contract's stage schedule (stage names and values or
percentages), what each stage is at, and what has been claimed before. Add
approved variations not yet fully claimed as a stage called "Approved
Variations". Only include variations the client has **signed**.

Before claiming a stage, check it is really reached as the contract defines
it (for example frame inspection passed). If it isn't, say so.

### 3. Compute and check

```bash
python3 $ABB/tools/compute.py progress_claim --param contract_sum_ex_gst=... \
    --param retention_pct=0 --param 'stages=[{"name": "...", "contract_value": ..., "pct_complete": ..., "previously_claimed": ...}, ...]' \
    > out/claim_N_receipt.json
python3 $ABB/brain/references/attesters/check_receipt.py out/claim_N_receipt.json
```

For retention, also pass `retention_cap_pct` and `retention_held_to_date`.
Read every entry in `warnings` to the user. Take figures only from the
receipt's `display` block.

### 4. Fill the invoice

Write `out/claim_N_spec.yaml` following `examples/claim_003_spec.yaml`:

- `set`: INVOICE_NUMBER, CLAIM_NUMBER, DATE (issue date), DD/MM/YYYY (due date from the contract's payment terms)
- `replace`: "PROGRESS CLAIM INVOICE" with "TAX INVOICE: PROGRESS CLAIM". A claim must be a valid tax invoice.
- `add_row` and `delete_row`: put the job's own stages in place of the template's rows. Each row is `Stage (x%)|$contract value|% complete|$claimed to date|$this claim`. Inserted rows come before the originals, so delete a duplicate label with `#2`.
- `row`: the summary lines, from the receipt:

| Invoice line | Receipt field |
|---|---|
| Subtotal Claimed (excl. GST) | `claimed_to_date_ex_gst` |
| Less: Previous Claims | `previous_claims_ex_gst` |
| Less: Retention | `retention_ex_gst` |
| Net Amount This Claim | `net_claim_ex_gst` |
| GST (10%) | `gst` |
| TOTAL AMOUNT DUE | `total_inc_gst` |

```bash
python3 $ABB/tools/fill_template.py $ABB/templates/word/Progress_Claim_Invoice_TEMPLATE.docx \
    --project my_project.yaml --spec out/claim_N_spec.yaml --out out/INV-00N_Progress_Claim.docx
```

Fix anything in `remaining` (except `[LOGO]`), `instructions_left` or
`unmatched`, and re-run until clean.

### 5. Update the calculator (optional, but builders like it)

Fill `Progress_Claim_Calculator_TEMPLATE.xlsx` with `cell` entries
(`Claims!B5` to `E11`), as in `examples/claim_003_calculator_spec.yaml`.
Percentages go in as `"100%"`. Its totals must match the receipt. If they
don't, trust the receipt and tell the user.

### 6. Claim pack and hand-over

Work through the Claim Support Pack Checklist with the user. At minimum:
dated photos, site diary extracts, the stage inspection certificate, signed
variations and current insurance certificates. Then tell them:

- The file location, the net ex GST, the GST and the total inc GST
- The due date, and to log it in the Payment Tracking Register
- Any warnings from step 3, and anything you assumed

## Security of payment claim

Use the Payment Claim when the user wants the statutory process behind a
claim: a subbie or trade claiming from a builder, or a builder claiming from
a client where the state's Act covers home owners (read
`brain/contracts/security_of_payment.md`; NSW and WA do, VIC, QLD and ACT
don't for an owner occupier's home).

1. Run the progress claim steps 1 to 3 above for the numbers.
2. Set `sopa_act` in the project file to the Act's full name from the state table.
3. Fill it following `examples/payment_claim_003_spec.yaml`: `fill_table` "Item" for the work lines, `row` for "Work Up To:" and the totals, and `replace` the two `[SELECT: ...]` prompts. The "what happens next" paragraph states the schedule deadline: use the state table's figure, and say it's draft if the table marks it to check.
4. NSW head contractors claiming from a principal must attach the approved supporting statement. WA claims for home building work need the prescribed notice to the home owner. Tell the user.
5. Record the date the claim was served: the respondent's clock starts then.

## Trade tax invoice

For trades and small jobs, use the Tax Invoice (`examples/tax_invoice_spec.yaml`):
`fill_table` "Description" for the lines (qty, unit, rate and amount ex GST),
the totals from `compute.py gst`, and the payment terms. If the trade wants
the invoice to count as a payment claim, replace the security of payment
prompt with the statement naming the Act; otherwise replace it with nothing.

## Claims from subcontractors

A subbie's payment claim to the builder is usually covered by the state's
security-of-payment act. The builder may have to reply with a **payment
schedule** within a short statutory time, or owe the full amount claimed.

- Note the date the claim arrived. Give the deadline from the state table in `brain/contracts/security_of_payment.md`, say it is draft, and work out the date with `compute.py add_days` (business days). Where the table says "check", tell the user to confirm with the regulator today.
- Compare the claim with the Subbie Payment Schedule (agreed amount, previous claims, balance) and with work actually done.
- Check their licence and insurance are current (Subbie Insurance and Licence Tracker).
- Deduct back charges only if a Back Charge Notice was issued.
- If the user plans to pay less than claimed, fill the Payment Schedule (`examples/payment_schedule_hs118_spec.yaml`): `set` CLAIM_REF and the subbie's details, `fill_table` "Item" (claimed, scheduled, difference, short reason), the totals `row`s from `compute.py gst`, and every reason in full in the reasons `cell`. Reasons left out may not be usable later. Suggest legal or industry association advice for anything disputed.

## Overdue payments

Use the Payment Tracking Register (days outstanding). Before suggesting
interest, suspension or termination, read the contract clauses
(`brain/contracts/hia_mba_clause_map.md`, marked unverified). Suspension and
termination have strict notice steps. Recommend advice before taking either; the notices skill drafts the Suspension, Breach and Termination notices.

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.

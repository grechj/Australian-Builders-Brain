---
name: claims
description: Prepare progress claims and track payments for Australian builders and trades. Produces the Progress Claim Invoice (tax invoice) and Progress Claim Calculator, works out retention, assembles the claim support pack, and keeps the Payment Tracking Register, Subbie Payment Schedule and Retention Release Tracker up to date. Use when someone mentions a progress claim, stage payment, invoicing the client, frame or lock-up claim, deposit invoice, retention, a client not paying, or paying or receiving subcontractor claims.
---

# Claims

You help a builder get paid for work done, correctly and with the evidence
that stops disputes, and keep track of what is owed both ways.

## Where things are

The repository root is two levels up from this skill's folder. Run commands
from there.

- Knowledge: `brain/contracts/progress_payments.md` (read it first), `brain/contracts/variations.md`, `brain/states/overview.md`
- Maths: `brain/computations/progress_claim.md`, `ex_gst.md`, `gst.md`
- Templates: `templates/word/Progress_Claim_Invoice_TEMPLATE.docx`, `templates/excel/Progress_Claim_Calculator_TEMPLATE.xlsx`, `Payment_Tracking_Register_TEMPLATE.xlsx`, `Subbie_Payment_Schedule_TEMPLATE.xlsx`, `Retention_Release_Tracker_TEMPLATE.xlsx`, `templates/pdf/Claim_Support_Pack_Checklist.pdf`
- Examples: `examples/claim_003_spec.yaml` (invoice), `examples/claim_003_calculator_spec.yaml` (calculator)

If `python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r requirements.txt`.

## Pick the job

| The user says | Do this |
|---|---|
| Invoice the frame stage / do claim 3 | Progress claim: steps 1 to 6 |
| Deposit invoice | Progress claim with only the deposit stage; check the state's deposit cap first |
| What's the client owe / who hasn't paid | Read or update the Payment Tracking Register |
| A subbie sent me a claim | Subbie claim: see "Claims from subcontractors" below |
| Pay the subbies / what do I owe trades | Subbie Payment Schedule |
| Retention | Retention Release Tracker, plus the retention parameters in step 3 |

## Progress claim

### 1. Project and contract facts

Use the project file (create it from `examples/project_example.yaml` if
there isn't one). You need `state`, `contract_type`, `contract_sum` and
`contract_sum_ex_gst`, plus `retention_pct` if the contract has retention.

If only the inc-GST contract sum is known, run
`python3 tools/compute.py ex_gst --param amount_inc_gst=<sum>`.

### 2. The payment schedule and progress

Ask for the contract's stage schedule (stage names and values or
percentages), what each stage is at, and what has been claimed before. Add
approved variations not yet fully claimed as a stage called "Approved
Variations". Only include variations the client has **signed**.

Before claiming a stage, check it is really reached as the contract defines
it (for example frame inspection passed). If it isn't, say so.

### 3. Compute and check

```bash
python3 tools/compute.py progress_claim --param contract_sum_ex_gst=... \
    --param retention_pct=0 --param 'stages=[{"name": "...", "contract_value": ..., "pct_complete": ..., "previously_claimed": ...}, ...]' \
    > out/claim_N_receipt.json
python3 brain/references/attesters/check_receipt.py out/claim_N_receipt.json
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
python3 tools/fill_template.py templates/word/Progress_Claim_Invoice_TEMPLATE.docx \
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

## Claims from subcontractors

A subbie's payment claim to the builder is usually covered by the state's
security-of-payment act. The builder may have to reply with a **payment
schedule** within a short statutory time, or owe the full amount claimed.

- Note the date the claim arrived and tell the user the response deadline is short and fixed by statute. Don't state a number of days unless the state page has a verified figure.
- Compare the claim with the Subbie Payment Schedule (agreed amount, previous claims, balance) and with work actually done.
- Check their licence and insurance are current (Subbie Insurance and Licence Tracker).
- Deduct back charges only if a Back Charge Notice was issued.
- If the user plans to pay less than claimed, recommend a written payment schedule with reasons, and suggest legal or industry association advice.

## Overdue payments

Use the Payment Tracking Register (days outstanding). Before suggesting
interest, suspension or termination, read the contract clauses
(`brain/contracts/hia_mba_clause_map.md`, marked unverified). Suspension and
termination have strict notice steps. Recommend advice before taking either.

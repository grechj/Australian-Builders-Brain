---
name: contracts
description: Set up a building job after the contract is signed, for Australian builders. Produces the Contract Data Summary (with the payment schedule worked out), Scope of Works, Subcontractor Agreements and Trade Scope Confirmations, and runs the pre-construction checklist. Use when someone has just won or signed a job, needs a contract summary or payment schedule, a scope of works or inclusions list, wants to engage or sign up a subbie, confirm a trade's scope or who supplies what, or asks what they need before starting on site.
---

# Contracts

You help a builder lock in the job's paperwork before work starts: what was
agreed with the client, what each trade is doing, and that everything
required is in place.

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

- Knowledge: `brain/contracts/contract_setup.md` (read it first), `brain/playbooks/pre_construction.md`, `brain/contracts/hia_mba_clause_map.md` (unverified), `brain/states/overview.md`
- Maths: `brain/computations/payment_schedule.md`, `gst.md`, `ex_gst.md`
- Templates: `templates/word/Contract_Data_Summary_TEMPLATE.docx`, `Scope_of_Works_TEMPLATE.docx`, `Subcontractor_Agreement_TEMPLATE.docx`, `Trade_Scope_Confirmation_TEMPLATE.docx`; `templates/pdf/Pre_Construction_Checklist.pdf`
- Examples: `examples/contract_summary_spec.yaml`, `scope_of_works_spec.yaml`, `subcontract_spec.yaml`, `trade_scope_spec.yaml`

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

## Pick the document

| The user says | Do this |
|---|---|
| We won the job / contract's signed | Contract Data Summary, Scope of Works, then the pre-construction checklist |
| What's the payment schedule | `payment_schedule` computation, then the Contract Data Summary |
| What's in and out / inclusions | Scope of Works |
| Sign up the sparky / engage a subbie | Subcontractor Agreement and Trade Scope Confirmation |
| Who supplies what | Trade Scope Confirmation |
| Are we ready to start | Pre-construction playbook |

## Contract Data Summary

1. Get the contract details: type and edition, contract number and date, contract sum inc GST, the deposit, the site (lot and DP, council, approval number), dates (signed, commencement, construction period, estimated completion), the DLP, insurance policy numbers and the certifier.
2. Work out the payment schedule:

   ```bash
   python3 $ABB/tools/compute.py payment_schedule --param contract_sum_inc_gst=<sum> \
       --param deposit_cap_pct=<verified state cap, or omit> \
       --param 'stages=[{"name": "Deposit", "pct": 5}, ...]' > out/payment_schedule_receipt.json
   python3 $ABB/brain/references/attesters/check_receipt.py out/payment_schedule_receipt.json
   ```

   Read any warnings. Don't pass a deposit cap you haven't verified; tell the user to check the state's cap instead. Save the ex-GST stage amounts in the project notes: the claims skill uses them as stage values.
3. Fill it following `examples/contract_summary_spec.yaml`. Stage rows are `%|$amount inc GST|☐` (☒ once claimed). If the contract's stages differ from the template's, use `add_row` and `delete_row` as in the claims example. Fill `[Certificate No]` and the two `[Policy No]` placeholders with `replace` or `row`.
4. Check that `contract_sum`, `contract_sum_ex_gst`, `builders_margin_pct` and the dates are in the project file.

## Scope of Works

Follow `examples/scope_of_works_spec.yaml`:
- `cell`: the overview, the exclusions and the standards. Cite NCC 2025 Volume Two and the Housing Provisions for houses; the ncc skill can confirm specific clauses.
- `row`: a description for each trade, or "Not in scope"; the program milestones as `date|notes`
- `fill_table` under `"Item"`: the PC and PS allowances, as `item|PC or PS|$allowance|notes`. The same allowances go in the Allowances Register.

Exclusions protect the builder. Prompt for common ones: landscaping, floor
coverings, window furnishings, asbestos, rock, service upgrades, and
council or authority fees.

## Subcontractor Agreement and Trade Scope Confirmation

1. Get the subbie's details (name, ABN, licence, phone, email), the trade, their quote reference and price ex GST, and the dates.
2. Check whether they are GST-registered (if not, there's no GST on their price), and get evidence of a current licence, public liability (the agreement asks for $10M) and workers compensation before they start. Record it in the Subbie Insurance and Licence Tracker.
3. Price: `python3 $ABB/tools/compute.py gst --param amount_ex_gst=<price>`.
4. Fill the agreement (`examples/subcontract_spec.yaml`) and the trade scope confirmation (`examples/trade_scope_spec.yaml`). Set the supply rows to `☒|☐` (builder supplies) or `☐|☒` (subbie supplies). Spell out inclusions and exclusions; vague trade scopes cause most back charges.

## Pre-construction

Work through `brain/playbooks/pre_construction.md` with the user. Approval
and insurance names follow NSW usage, so translate for other states.
Anything missing is a reason not to start yet; say which items block the
start.

## For every document

Run `tools/fill_template.py` with the project file and spec. The report
must show nothing left over except `[LOGO]`, no `instructions_left`, and no
`unmatched` or `ambiguous` entries. Tell the user which documents need
signing, and by whom.

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.

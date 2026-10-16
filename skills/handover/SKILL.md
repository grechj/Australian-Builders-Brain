---
name: handover
description: Take an Australian building job from practical completion to final account. Runs the PC inspection, produces the Practical Completion Notice, Defects List, As-Built Documentation Register, Warranties and Manuals Index, Final Account Summary and Final Claim and Release, and works out DLP and warranty dates. Use when someone mentions practical completion, PC, handover, the final inspection, defects, the defects liability period or DLP, maintenance period, warranties, as-builts, certificates for handover, the final claim or final account, or releasing retention.
---

# Handover

You help a builder finish the job cleanly: reach practical completion
properly, hand over everything the client needs, fix defects on record, and
settle the final account.

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

- Knowledge: `brain/contracts/practical_completion_and_defects.md` (read it first), `brain/playbooks/practical_completion_inspection.md`, `brain/contracts/extension_of_time.md`
- Maths: `brain/computations/final_account.md`, `add_period.md`, `add_days.md`
- Templates: `templates/word/Practical_Completion_Notice_TEMPLATE.docx`, `Final_Claim_Release_TEMPLATE.docx`; `templates/excel/Defects_List_Tracking_TEMPLATE.xlsx`, `As_Built_Documentation_Register_TEMPLATE.xlsx`, `Warranties_Manuals_Index_TEMPLATE.xlsx`, `Final_Account_Summary_TEMPLATE.xlsx`; `templates/pdf/Practical_Completion_Checklist.pdf`, `Defects_Liability_Explanation.pdf`
- Examples: `examples/pc_notice_spec.yaml`, `final_claim_spec.yaml`, `final_account_spec.yaml`, `defects_list_spec.yaml`

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

## The order of things

1. PC inspection: work through the playbook, then log defects
2. Certificates and handover documents: confirm they're in hand
3. Practical Completion Notice
4. Handover: give the client the documents, warranties and manuals, and the DLP explainer
5. Final account, then the Final Claim and Release
6. During the DLP: track and close defects, release retention at the end

Ask where the job is up to, and start at that step.

## 1. PC inspection

Work through `brain/playbooks/practical_completion_inspection.md` room by
room with the user (or turn their walk-through notes into it). Every failed
item becomes a Defects List row: date, location, description, trade
responsible, and priority (High, Medium or Low, from the sheet's dropdown).
Follow `examples/defects_list_spec.yaml`, with rows from `Defects!B5`.

Major items (anything that stops the home being used, safety, missing
certificates) mean the job is **not** at PC yet. Say so.

## 2. Documents

Check the As-Built Documentation Register list with the user: drawings,
survey, engineering, waterproofing, termite and compliance certificates,
the occupation certificate where the state requires one, and the energy
rating. Record what is in hand and what is missing, and fill the Warranties
and Manuals Index as items are collected.

## 3. Practical Completion Notice

- PC date, the contract completion date and approved EOTs (from DELAY notices)
- If PC is later than the completion date plus approved EOTs, warn about liquidated damages and suggest dealing with any outstanding EOT claims first
- DLP length from the contract, then the end date:

  ```bash
  python3 $ABB/tools/compute.py add_period --param start_date=<PC date> --param weeks=13
  ```

- A proposed handover inspection date and time

Fill it following `examples/pc_notice_spec.yaml` and
`tools/fill_template.py`. The fill must come back with nothing left over
except `[LOGO]`.

## 4. Handover pack

Give the client the documents from step 2, keys and remotes, and the
Defects Liability Explanation PDF (built from
`brain/references/handouts/defects_liability_guide.md`; fill in its key
dates for the client). Don't quote statutory warranty periods without checking the
state (`brain/contracts/practical_completion_and_defects.md`). Use
`add_period` (years) for warranty end dates once the period is confirmed.

## 5. Final account and final claim

Collect, all ex GST:
- Contract sum (`contract_sum_ex_gst`)
- Approved variation additions and omissions (from the Variation Register)
- Net PC and provisional sum adjustments (from the Allowances Register)
- Gross total claimed to date (from the progress claims)
- Retention held, and how much is released now (the rest usually waits for the end of the DLP)

```bash
python3 $ABB/tools/compute.py final_account --param contract_sum_ex_gst=... --param variations_additions=... \
    --param variations_omissions=... --param pc_ps_adjustments=... --param claimed_to_date=... \
    --param retention_held=... --param retention_released=... > out/final_account_receipt.json
python3 $ABB/brain/references/attesters/check_receipt.py out/final_account_receipt.json
```

Read any warnings. A negative final claim means the client is owed a credit.
Then fill:

- **Final Account Summary workbook**: `examples/final_account_spec.yaml`. B6 additions, B7 omissions (put net PC/PS reductions here, or net increases in B6), B12 claimed to date, B13 retention held as a positive number, B19 retention released now.
- **Final Claim and Release**: `examples/final_claim_spec.yaml`. Relabel the lines ("Less: Total Previously Claimed", "Add: Retention Released") so the arithmetic reads correctly, and fill the rows from the receipt's `display`.

Tell the user that the release does not end their warranty or defects
obligations, and that the final claim must also be a valid tax invoice. Use
the claims skill for the invoice.

## 6. During the DLP

Keep the Defects List current: date fixed, and verified (Yes or No). Near
the DLP end date, remind the user to inspect again, close out the list,
get the client's sign-off, and release any remaining retention.

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.

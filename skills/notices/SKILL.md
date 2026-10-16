---
name: notices
description: Write formal construction notices for Australian builders. Produces Delay Notification Letters (extension of time claims), Site Instruction Forms, Back Charge Notices to subcontractors, and Suspension, Breach and Termination notices for non-payment or default, as filled Word documents, with revised completion dates and costs calculated. Use when someone mentions a delay, rain days, an EOT or extension of time, pushing out the completion date, instructing a trade, a site instruction, a subbie who damaged something or left a mess, a back charge, or deducting from a subbie's payment.
---

# Notices

You turn what happened on site into a formal notice that protects the
builder's time, money and position.

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

- Knowledge: `brain/contracts/extension_of_time.md`, `brain/contracts/site_instructions_and_back_charges.md`, `brain/contracts/hia_mba_clause_map.md` (unverified)
- Maths: `brain/computations/add_days.md` (dates), `brain/computations/variation_price.md` (back charge costs)
- Templates: `templates/word/Delay_Notification_Letter_TEMPLATE.docx`, `Site_Instruction_Form_TEMPLATE.docx`, `Back_Charge_Notice_TEMPLATE.docx`, `Suspension_Notice_TEMPLATE.docx`, `Breach_Notice_TEMPLATE.docx`, `Termination_Notice_TEMPLATE.docx`
- Examples: `examples/delay_001_spec.yaml`, `examples/site_instruction_001_spec.yaml`, `examples/back_charge_001_spec.yaml`

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

## Pick the notice

| The user says | Notice | Goes to |
|---|---|---|
| Rain / council hold-up / waiting on the client / we're going to be late | Delay Notification Letter | Client |
| Tell the concreter to... / the engineer changed... / I told the sparky to... | Site Instruction | Trade (or client) |
| The subbie wrecked / didn't clean up / did it wrong and I fixed it | Back Charge Notice | Subcontractor |
| They haven't paid, I'm stopping work | Suspension Notice | Client (or builder, for a trade) |
| They're in breach / I want to get out of this job | Breach Notice, then (only if not remedied) Termination Notice | The other party |

One event can need more than one: an engineer's change might mean a site
instruction to the trade, a variation to the client and a delay notice.
Point this out.

## Delay Notification Letter

### 1. Speed matters

Ask when the delay started and when the builder became aware of it.
Contracts set a notice period from that point. Find it in the contract (or
ask), then work out the deadline:

```bash
python3 $ABB/tools/compute.py add_days --param start_date=<aware date> --param days=<notice period> \
    --param day_type=<calendar|working> --param 'non_working_days=[...]'
```

If the deadline has passed or is close, say so plainly, and recommend
sending the notice today and getting advice.

### 2. Facts

- The cause. Tick the matching box: Inclement weather, Client-directed changes, Latent conditions, Supply chain delays, Council / authority delays, Labour shortage, Client selections pending, Access restrictions.
- The dates affected, and the days lost
- Evidence: site diary entries, BOM rainfall records, emails, authority correspondence
- Whether the contract counts calendar or working days for extensions, and which days are non-working (public holidays for the state, the Christmas shutdown)
- Whether there is extra cost. If so, a variation is issued separately (see the variations skill).

### 3. Revised completion date

```bash
python3 $ABB/tools/compute.py add_days --param start_date=<current completion> --param days=<days claimed> \
    --param day_type=working --param 'non_working_days=["DD/MM/YYYY", "DD/MM/YYYY-DD/MM/YYYY"]' \
    > out/DELAY-00N_receipt.json
python3 $ABB/brain/references/attesters/check_receipt.py out/DELAY-00N_receipt.json
```

### 4. Fill

Follow `examples/delay_001_spec.yaml`: `tick` the cause; `cell` the
description (what happened, where, the dates, why it stopped work, and what
evidence is attached); `row` the current completion date, days of delay
(say "working" or "calendar") and revised date; `replace` the cost choice.
Set `NAME` to the person signing.

```bash
python3 $ABB/tools/fill_template.py $ABB/templates/word/Delay_Notification_Letter_TEMPLATE.docx \
    --project my_project.yaml --spec out/DELAY-00N_spec.yaml --out out/DELAY-00N_Delay_Notification.docx
```

## Site Instruction

Follow `examples/site_instruction_001_spec.yaml`. Get who issued it, who
received it, exactly what is to be done (location, materials, method, the
drawing or spec), the reason (tick one), and the completion date. Then:

- If it changes cost, set Cost Impact to "Variation Required" and reference the VAR number. Raise the variation if it doesn't exist yet.
- If it changes time, set Time Impact to "EOT Required" and offer to draft the delay notice.
- If neither, use "Nil" for both. Replace `[VAR_NUMBER or N/A]` with the number or "N/A".

Remind the user to get the receiver's signature.

## Back Charge Notice

1. Confirm that the subbie was told (when, and how) and given a chance to fix it. The subcontract's rectification period applies; the template says 7 days.
2. Get the cost lines ex GST and price them:

   ```bash
   python3 $ABB/tools/compute.py variation_price --param labour=<rectification labour> --param materials=<replacement materials> \
       --param subcontractor=<third-party costs> --param plant=0 --param other=<other> --param margin_pct=0
   ```

   Use the admin margin instead of 0 only if the subcontract allows one.
3. Fill it following `examples/back_charge_001_spec.yaml`: the subbie's details, `tick` the reason, the description (location, what went wrong, what was done to fix it, earlier warnings with dates), the four cost `row`s, and AMOUNT, AMOUNT_GST and AMOUNT_TOTAL from the receipt's `fields`.
4. Tell the user: attach photos and invoices. Record the deduction in the Subbie Payment Schedule. If the subbie's claim falls under security-of-payment law, the withheld amount and the reasons must be in the payment schedule sent to them on time (see the claims skill).

## Suspension, breach and termination

These are the most dangerous documents in the brain: a builder who suspends
or terminates without the right to can end up in breach themselves. Always:

1. Read the contract's suspension, default and termination clauses (`brain/contracts/hia_mba_clause_map.md`, unverified, or the user's contract) and, for non-payment, `brain/contracts/security_of_payment.md`. Find the notice period, whether it is business, working or calendar days, the required wording and how the notice must be served.
2. Check the money is really overdue: the claim, its due date and whether a payment schedule disputed it (Payment Tracking Register).
3. Tell the user plainly to get legal advice before sending, and that termination affects home warranty insurance.

Then fill:

- **Suspension Notice** (`examples/suspension_notice_spec.yaml`): `set` INVOICE_NUMBER, CONTRACT_CLAUSE and NUMBER (the notice period), `row` "[INVOICE_NUMBER]" for the dates and amount, `replace` the basis and the suspension date. Work out the date with `compute.py add_days`.
- **Breach Notice** (`examples/breach_notice_spec.yaml`): the breach in detail (clause, what was required, what didn't happen, dates and amounts), exactly what must be done to remedy it, and the remedy period from the contract.
- **Termination Notice** (`examples/termination_notice_spec.yaml`): only after the breach notice's period has passed unremedied. The breach notice's date goes in `[DD/MM/YYYY]`; amounts claimed come from the claims and the contract.

## For every notice

Read the JSON report from `fill_template.py`. Anything in `remaining`
(other than `[LOGO]`), `instructions_left` or `unmatched` must be fixed
before handing over. Then give the user the file path, a two-line summary
of the notice, and how to send it under the contract's notices clause (for
example email to the address in the contract). Keep proof that it was sent.

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.

---
name: notices
description: Write formal construction notices for Australian builders. Produces Delay Notification Letters (extension of time claims), Site Instruction Forms and Back Charge Notices to subcontractors as filled Word documents, with revised completion dates and costs calculated. Use when someone mentions a delay, rain days, an EOT or extension of time, pushing out the completion date, instructing a trade, a site instruction, a subbie who damaged something or left a mess, a back charge, or deducting from a subbie's payment.
---

# Notices

You turn what happened on site into a formal notice that protects the
builder's time, money and position.

## Where things are

The repository root is two levels up from this skill's folder. Run commands
from there.

- Knowledge: `brain/contracts/extension_of_time.md`, `brain/contracts/site_instructions_and_back_charges.md`, `brain/contracts/hia_mba_clause_map.md` (unverified)
- Maths: `brain/computations/add_days.md` (dates), `brain/computations/variation_price.md` (back charge costs)
- Templates: `templates/word/Delay_Notification_Letter_TEMPLATE.docx`, `Site_Instruction_Form_TEMPLATE.docx`, `Back_Charge_Notice_TEMPLATE.docx`
- Examples: `examples/delay_001_spec.yaml`, `examples/site_instruction_001_spec.yaml`, `examples/back_charge_001_spec.yaml`

If `python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r requirements.txt`.


## Profile: trade and location

Before anything else, know who you're helping and where:

```bash
python3 tools/profile.py show --project my_project.yaml      # or: --trade <trade> --state <STATE>
```

Ask for the trade and state if the project file doesn't have them
(`python3 tools/profile.py trades` lists every trade; `builder` sees
everything). Stay within the profile: use the NCC pages, skills, materials
and suppliers it lists, apply only that state's NCC variations and rules,
and read the state page for local differences.

## Pick the notice

| The user says | Notice | Goes to |
|---|---|---|
| Rain / council hold-up / waiting on the client / we're going to be late | Delay Notification Letter | Client |
| Tell the concreter to... / the engineer changed... / I told the sparky to... | Site Instruction | Trade (or client) |
| The subbie wrecked / didn't clean up / did it wrong and I fixed it | Back Charge Notice | Subcontractor |

One event can need more than one: an engineer's change might mean a site
instruction to the trade, a variation to the client and a delay notice.
Point this out.

## Delay Notification Letter

### 1. Speed matters

Ask when the delay started and when the builder became aware of it.
Contracts set a notice period from that point. Find it in the contract (or
ask), then work out the deadline:

```bash
python3 tools/compute.py add_days --param start_date=<aware date> --param days=<notice period> \
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
python3 tools/compute.py add_days --param start_date=<current completion> --param days=<days claimed> \
    --param day_type=working --param 'non_working_days=["DD/MM/YYYY", "DD/MM/YYYY-DD/MM/YYYY"]' \
    > out/DELAY-00N_receipt.json
python3 brain/references/attesters/check_receipt.py out/DELAY-00N_receipt.json
```

### 4. Fill

Follow `examples/delay_001_spec.yaml`: `tick` the cause; `cell` the
description (what happened, where, the dates, why it stopped work, and what
evidence is attached); `row` the current completion date, days of delay
(say "working" or "calendar") and revised date; `replace` the cost choice.
Set `NAME` to the person signing.

```bash
python3 tools/fill_template.py templates/word/Delay_Notification_Letter_TEMPLATE.docx \
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
   python3 tools/compute.py variation_price --param labour=<rectification labour> --param materials=<replacement materials> \
       --param subcontractor=<third-party costs> --param plant=0 --param other=<other> --param margin_pct=0
   ```

   Use the admin margin instead of 0 only if the subcontract allows one.
3. Fill it following `examples/back_charge_001_spec.yaml`: the subbie's details, `tick` the reason, the description (location, what went wrong, what was done to fix it, earlier warnings with dates), the four cost `row`s, and AMOUNT, AMOUNT_GST and AMOUNT_TOTAL from the receipt's `fields`.
4. Tell the user: attach photos and invoices. Record the deduction in the Subbie Payment Schedule. If the subbie's claim falls under security-of-payment law, the withheld amount and the reasons must be in the payment schedule sent to them on time (see the claims skill).

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

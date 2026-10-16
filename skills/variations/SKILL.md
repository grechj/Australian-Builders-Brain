---
name: variations
description: Draft, price and track building variations for Australian residential and commercial jobs. Produces Client Change Requests, Builder Initiated Variations, Priced Variation Notices, Variation Approval Forms and Variation Explanation Letters as filled Word documents, and updates the Variation Register. Use when a builder or tradie mentions a variation, change request, extra work, latent conditions, "var", a client wanting something changed, or needs to price or get sign-off on a change.
---

# Variations

You help an Australian builder turn a change on site into a signed, priced
variation that will get paid.

## Where things are

The repository root is two levels up from this skill's folder. All paths
below are relative to it, and all commands run from it.

- Knowledge: `brain/contracts/variations.md` (read it first), `brain/contracts/hia_mba_clause_map.md`, `brain/states/overview.md`
- Document pages: `brain/documents/<name>.md` (fields and purpose of each template)
- Templates: `templates/word/` and `templates/excel/`
- Tools: `tools/compute.py`, `tools/fill_template.py`, `brain/references/attesters/check_receipt.py`
- Example inputs: `examples/project_example.yaml`, `examples/var_001_spec.yaml`

If `python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r requirements.txt` first.

## Pick the document

| The user says | Document | Template |
|---|---|---|
| The client wants to change something | Client Change Request, then a Priced Variation Notice | `Client_Change_Request_TEMPLATE.docx` |
| I found rock / asbestos / the engineer changed it / council wants... | Builder Initiated Variation | `Builder_Initiated_Variation_TEMPLATE.docx` |
| Price this variation / send the client a var | Priced Variation Notice | `Priced_Variation_Notice_TEMPLATE.docx` |
| They've agreed / need it signed | Variation Approval Form | `Variation_Approval_Form_TEMPLATE.docx` |
| The client is pushing back or confused | Variation Explanation Letter | `Variation_Explanation_Letter_TEMPLATE.docx` |
| Where are we at with variations? | Variation Register | `Variation_Register.xlsx` |

## Steps

### 1. Get the project facts

Ask for the project file (`my_project.yaml` or similar). If there isn't
one, create it by copying `examples/project_example.yaml` and asking for the
values. Ask in one short message, not field by field.

Don't go on without these:
- `state`, because variation rules differ by state
- `contract_type` and `contract_edition`
- `builders_margin_pct`, the margin on variations from the contract schedule

### 2. Get the variation facts

- What is added, changed or omitted, and exactly where
- Why: client request, latent conditions, regulatory compliance, design change, other
- The drawing, spec or instruction it changes
- Cost lines ex GST: labour, materials, subcontractor, plant, other. Ask for supplier or subbie quotes if they have them.
- Time impact in days, plus the current completion date
- How long the price is valid: 7, 14 or 30 days
- The next VAR number (check the register or ask)

If the user gives prices inc GST, confirm before converting. Never invent a
cost line.

### 3. Price it, then check the price

```bash
python3 tools/compute.py variation_price --param labour=... --param materials=... \
    --param subcontractor=... --param plant=... --param other=... \
    --param margin_pct=... > out/VAR-00N_receipt.json
python3 brain/references/attesters/check_receipt.py out/VAR-00N_receipt.json
```

If the attester fails, stop and tell the user. Take every figure from the
receipt's `display` block exactly as written; never round or add figures
yourself.

Map the receipt to the Priced Variation Notice:

| Template row | Client page (sell, ex GST) | Internal page: actual, quoted, margin |
|---|---|---|
| Labour | `labour_sell_ex_gst` | `labour_cost_ex_gst`, `labour_sell_ex_gst`, `labour_margin_ex_gst` |
| Materials | `materials_sell_ex_gst` | same pattern |
| Subcontractor Costs | `subcontractor_sell_ex_gst` | same pattern (row `Subcontractor Costs#2`) |
| Equipment / Plant | `plant_sell_ex_gst` | same pattern (row `Equipment / Plant#2`) |
| Other | `other_sell_ex_gst` | same pattern (row `Other#2`) |
| Subtotal (excl. GST) | `amount_ex_gst` | `cost_ex_gst`, `amount_ex_gst`, `margin_ex_gst` (row `Subtotal (excl. GST)#2`) |
| GST (10%) | `gst` | |
| TOTAL (incl. GST) | `amount_inc_gst` | cost × 1.1 from a `gst` computation, `amount_inc_gst`, the difference |

For the internal margin percentage, run the `margin` computation
(`quoted_ex_gst` = `amount_ex_gst`, `actual_cost_ex_gst` = `cost_ex_gst`).
Report both margin on sell and markup on cost.

### 4. Write the spec and fill the template

Write `out/VAR-00N_spec.yaml`, using `examples/var_001_spec.yaml` as the
pattern:
- `set`: VAR_NUMBER, CONTRACT_CLAUSE, and `DD/MM/YYYY` for the date raised
- `replace`: each `[SELECT: ...]` choice and the contract reference line
- `cell`: the variation description and internal notes
- `row`: the cost lines from step 3, and the time impact rows (current and revised completion dates)

```bash
python3 tools/fill_template.py templates/word/Priced_Variation_Notice_TEMPLATE.docx \
    --project my_project.yaml --spec out/VAR-00N_spec.yaml \
    --out out/VAR-00N_Priced_Variation_Notice.docx
```

Read the JSON report. Anything in `remaining` (other than `[LOGO]`),
`instructions_left` or `unmatched` needs fixing in the spec. Re-run until
those lists are clean.

### 5. Clause reference

Take the clause from `brain/contracts/hia_mba_clause_map.md`. That map is
unverified, so always write "(check against the signed contract)" after the
clause, unless the user has confirmed the clause from their own contract.

### 6. Hand over

Tell the user:
- Where the file is, and that page 2 is internal and must not go to the client
- The price ex GST, the GST and the total inc GST, plus the time impact
- That no work should start until the client signs, and to log it in the Variation Register (status "Priced")
- Anything you assumed or couldn't verify

## Variation Register

Keep one row per variation from row 5 (VAR numbers fill themselves), as in
`examples/variation_register_spec.yaml`:
- B date raised, C description, D reason (Client Request, Latent Conditions, Compliance, Design Change, Other)
- E status (Requested, Priced, Approved, Rejected, Invoiced, Paid)
- F quoted and G actual cost, both ex GST; J days
- K approved date, L invoice number

Move the status along as things happen. The Summary sheet's revised
contract sum counts only Approved, Invoiced and Paid variations, ex GST.

## Allowances and selections

PC items and provisional sums are allowances in the contract.

- **Allowances Register**: one row per PC or PS item with the allowance and, once known, the actual cost (ex GST). Status runs Provisional, Selected, Ordered, Installed, Finalised. A negative variance (actual over allowance) is an adjustment to claim. Depending on the contract, it may go through as a variation or as a PC/PS adjustment, plus the builder's margin if the contract allows it.
- **Client Selections Register**: what the client still has to choose, by room, with the allowance, the chosen product, supplier and price, and the status (Pending, Selected, Ordered, Installed). Chase pending selections with a date in the weekly progress update (site skill); late selections cause delays.

Both feed the final account (handover skill) as PC/PS adjustments.

## Writing the description

Builders and clients both read this, so write it plainly. Say what, where
and why in two to four sentences. Name the drawing, spec or instruction. For
latent conditions, say what was found, where, and when, and that it wasn't
reasonably detectable at tender. Keep the conversation's site slang out of
the client-facing text: "sparky" becomes "electrician".

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.

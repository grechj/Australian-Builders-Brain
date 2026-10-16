---
name: estimating
description: Estimate and quote building jobs for Australian builders and trades. Builds the Trade Based Estimate Workbook, prices it with contingency and markup, compares subcontractor quotes, tests margin sensitivity, logs pre-contract clarifications, and produces the Quote Acceptance Form. Use when someone wants to price a job, do an estimate or take-off, put a quote together, compare subbie or supplier quotes, work out markup or margin, check if a job is worth taking, or get a client to accept a quote.
---

# Estimating

You help a builder price a job properly, quote it clearly, and win it
without leaving money or risk on the table.

## Where things are

The repository root is two levels up from this skill's folder. Run commands
from there.

- Knowledge: `brain/contracts/estimating_and_quoting.md` (read it first), `brain/contracts/variations.md` (PC and provisional sums), `brain/states/overview.md`
- Maths: `brain/computations/estimate_price.md`, `margin.md`, `gst.md`
- Templates: `templates/excel/Trade_Based_Estimate_Workbook.xlsx`, `Estimate_to_Quote_Converter_TEMPLATE.xlsx`, `Quote_Comparison_TEMPLATE.xlsx`, `Margin_Sensitivity_Calculator_TEMPLATE.xlsx`, `Pre_Contract_Clarifications_TEMPLATE.xlsx`; `templates/word/Quote_Acceptance_Form_TEMPLATE.docx`
- Examples: `examples/estimate_spec.yaml`, `examples/quote_acceptance_spec.yaml`

If `python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r requirements.txt`.

## Steps

### 1. Scope first

Get the drawings or a clear description, the site address, the state, and
whether it is residential work for an owner. Residential work changes the
contract and deposit rules. List what is unclear as clarifications
(RFI-001 ...) in the Pre-Contract Clarifications register, rather than
guessing.

### 2. Build the estimate

Work trade by trade into the Trade Based Estimate Workbook, using `cell`
entries as in `examples/estimate_spec.yaml`:

- Labour, rows 9 to 28: trade, description, qty, unit, rate. Column E defaults to the Setup rate and can be overridden.
- Materials, rows 33 to 57: item, description, qty, unit, unit cost
- Subcontractors, rows 62 to 76: trade, subcontractor, quote ref, quote date, amount
- Setup: default markup (B16) and contingency (B17) as fractions (0.2 and 0.05), or leave the defaults

For the materials lines, the materials skill can take off quantities and price them (Bunnings as a retail guide); replace those with trade prices before quoting. Prompt for the commonly missed items listed in the brain page. Never invent
quantities or prices. Mark anything the user hasn't given as an allowance
and say so.

### 3. Compare subbie quotes

For each trade with several quotes, fill the Quote Comparison. Check each
quote's licence and insurance are current, and that its inclusions match
the scope. The cheapest quote with exclusions is often not the cheapest
job.

### 4. Price it, then check the price

```bash
python3 tools/compute.py estimate_price --param labour=<labour subtotal> --param materials=<materials subtotal> \
    --param subcontract=<subcontract subtotal> --param contingency_pct=5 --param markup_pct=20 \
    > out/estimate_receipt.json
python3 brain/references/attesters/check_receipt.py out/estimate_receipt.json
```

The workbook's totals must match the receipt. Tell the user both the markup
and `margin_on_price_pct` ("20% markup, which is a 16.7% margin"). If the
user has a target margin, compare them. For risky jobs, fill the Margin
Sensitivity Calculator (Setup: estimated cost, target markup) and show what
a 5% or 10% overrun does to profit.

### 5. The quote

- The workbook's Quote Output sheet is the client-facing summary, with markup built into each line.
- Its standard terms say any deposit stays within the state's legal limit. Set the actual deposit in the contract, within the cap for the state (`brain/states/overview.md`).
- Put a validity period on it, and list inclusions, exclusions and allowances.

### 6. Acceptance

Fill the Quote Acceptance Form as in `examples/quote_acceptance_spec.yaml`:
quote number and dates (`row` for the quote date and valid-until), amounts
from the receipt, a scope summary (`cell`), the deposit (within the state
cap) and the payment method (`replace` "[  ] EFT" with "☒ EFT").

```bash
python3 tools/fill_template.py templates/word/Quote_Acceptance_Form_TEMPLATE.docx \
    --project my_project.yaml --spec out/quote_acceptance_spec.yaml --out out/Q-00N_Acceptance.docx
```

The fill must come back with nothing left over except `[LOGO]`.

For residential work, remind the user that acceptance is not the contract.
They need the state-compliant written contract and, above the threshold,
home warranty insurance before taking the deposit. The contracts skill
covers that.

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.

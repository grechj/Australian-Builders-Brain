---
name: financials
description: Track job costs and profit for Australian builders. Updates the Budget vs Actual Tracker with committed and spent costs and status, prepares the Job Profit and Loss Summary with gross margin, and runs a lessons-learned review at job close. Use when someone asks how a job is tracking, whether they're over budget, what they've committed or spent, what a job made, their margin or profit, or wants a job wrap-up or post-mortem.
---

# Financials

You help a builder see whether a job is making money while there's still
time to act, and learn from it when it's done.

## Where things are

The repository root is two levels up from this skill's folder. Run commands
from there.

- Knowledge: `brain/contracts/job_financials.md` (read it first), `brain/contracts/variations.md`, `brain/contracts/estimating_and_quoting.md` (markup vs margin)
- Maths: `brain/computations/budget_status.md`, `margin.md`, `estimate_price.md`
- Templates: `templates/excel/Budget_vs_Actual_Tracker_TEMPLATE.xlsx`, `Job_Profit_Loss_Summary_TEMPLATE.xlsx`, `Lessons_Learned_Register_TEMPLATE.xlsx`
- Examples: `examples/budget_spec.yaml`, `job_pnl_spec.yaml`, `lessons_spec.yaml`

If `python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r requirements.txt`.

Everything here is ex GST. If the user gives inc-GST invoice totals,
convert them with `python3 tools/compute.py ex_gst --param amount_inc_gst=...`.

## How's the job tracking?

1. Get each trade's budget (from the estimate), committed (orders and subcontracts let) and spent (invoices), and whether it's finished.
2. Work out the status:

   ```bash
   python3 tools/compute.py budget_status --param 'lines=[{"item": "Framing", "budget": ..., "committed": ..., "spent": ..., "complete": false}, ...]' \
       > out/budget_receipt.json
   python3 brain/references/attesters/check_receipt.py out/budget_receipt.json
   ```

3. Write the lines into the tracker (`examples/budget_spec.yaml`). The rows are fixed trades (5 Preliminaries to 23 Other; the example lists the row numbers). Columns: B budget, C committed, D spent, H status (from the receipt), I notes.
4. Tell the user in plain terms: the total forecast variance, which lines are Over Budget or At Risk, and for each the likely cause and fix (variation to recover, back charge, or absorb and record a lesson).

## What did the job make?

1. Collect budget and actual revenue (contract sum, approved variations, extras) and costs by category. Include supervision and the builder's own time.
2. Fill the Job P&L (`examples/job_pnl_spec.yaml`): rows 6 to 8 revenue, 11 to 21 costs; B budget, C actual.
3. Check the margin: `python3 tools/compute.py margin --param quoted_ex_gst=<total revenue> --param actual_cost_ex_gst=<total costs>`. It must match the workbook's Gross Margin. Give both margin and markup, and compare with the margin the job was priced at.

## Lessons learned

At job close, ask about each area: estimating, scheduling, subbies,
materials, client, safety, quality and commercial. For each lesson, record
what happened, the impact, what worked, what to do differently, one action
for the next job, and an owner (`examples/lessons_spec.yaml`). The category
must be from the dropdown. Prompt with what the records show: the
variation register, delay notices, incidents and budget overruns.

## Checks

`tools/fill_template.py` must report no `unmatched` entries.

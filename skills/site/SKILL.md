---
name: site
description: Keep day-to-day site records for Australian builders. Fills the Site Diary (weather, trades, work, delays, instructions, visitors), writes the weekly client Progress Update, tracks material orders and trade bookings, and walks quality hold points. Use when someone gives a daily update ("sparky and chippie on today, rain arvo"), wants to log the diary, update the client, chase a delivery, book or confirm trades, check what's next on the job, or sign off a stage before covering up.
---

# Site

You turn a builder's quick site updates into proper records, and keep the
client and the trades lined up.

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

- Knowledge: `brain/contracts/site_management.md` (read it first), `brain/playbooks/quality_hold_points.md`, `brain/phases/` (the phase for the job's type and stage: readiness checks, inspections, materials, weather risk, next trades), `brain/phases/trade_sequence.md`, `brain/glossary/site_slang.md`
- Maths: `brain/computations/site_week.md`, `progress_claim.md` (for % complete)
- Templates: `templates/excel/Site_Diary_TEMPLATE.xlsx`, `Material_Order_Tracker_TEMPLATE.xlsx`, `Trade_Booking_Lead_Time_Tracker_TEMPLATE.xlsx`; `templates/word/Progress_Update_Email_TEMPLATE.docx`; `templates/pdf/Quality_Hold_Point_Checklist.pdf`
- Examples: `examples/site_diary_spec.yaml`, `progress_update_spec.yaml`, `material_order_spec.yaml`, `trade_booking_spec.yaml`

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

## Daily diary

Builders talk in slang ("sparky", "chippie", "arvo"). Read
`brain/glossary/site_slang.md`, and write the diary in plain terms.

From the update, pull out: the date, weather morning and afternoon (only
these values: Fine, Overcast, Light Rain, Heavy Rain, Storm, Hot >35,
Cold <10, Windy), trades on site, work completed, delays and their causes,
instructions given, visitors and notes. Ask only for what's missing that
matters, usually the weather or the cause of a delay.

Write one row per day from row 5 (`Site Diary!A5`; column B, the day, is
calculated), as in `examples/site_diary_spec.yaml`. When updating an
existing diary, pass it as the template so earlier days are kept, and write
to the next empty row.

Then act on what the entry shows:
- A delay with a cause outside the builder's control: offer the delay notice (notices skill), and note the contract's notice deadline
- An instruction given verbally: offer a site instruction (notices skill)
- A change to scope: offer a variation (variations skill)
- A safety issue: offer an incident report (safety skill)
- Tomorrow's readiness: give 2 or 3 readiness checks for the current phase from `brain/phases/`

## Weekly progress update

1. Week number: `python3 $ABB/tools/compute.py site_week --param start_date=<site start> --param on_date=<today>`
2. % complete from the latest progress claim receipt (claimed to date ÷ schedule total), or ask
3. From the diary: work done, delays and rain days. From the program: next week's work.
4. Client actions with dates, pending variations, and when the next claim is due
5. Fill it following `examples/progress_update_spec.yaml`. Everything in `[SELECT: ...]` and `[__]%` must be replaced.

Keep it factual, positive and in plain English for the client.

## Materials and trades

- **Orders**: one row each from row 5 (`material_order_spec.yaml`). Delivered is Yes, No or Partial. Flag long-lead items not yet ordered for upcoming phases (the phase pages list key materials).
- **Bookings**: one row per trade (`trade_booking_spec.yaml`). Status is Booked, Confirmed, On Site, Complete, Delayed or Cancelled. Expected finish calculates from the actual start, or the expected start until there is one. Before confirming a trade, check what it waits for in `brain/phases/trade_sequence.md`.

## Hold points

Before covering up work (slab pour, lining, waterproofing, PC), walk the
relevant section of `brain/playbooks/quality_hold_points.md`. A failed hold
point means the next trade waits. Record each sign-off (date and who) in the
diary.

## Checks

`tools/fill_template.py` must report nothing left over (except `[LOGO]`)
and no `unmatched` entries.

## Your own format

The templates are references, not a straitjacket. If the user wants the
document on their own letterhead, as an email, as a PDF, or can't run
Python (for example in Claude.ai):

- Write it from the **Structure** section of `brain/documents/<name>.md`, which lists every section, field, table and prompt in order. Keep every section, and keep the money exactly as the computation receipt gives it.
- If they have their own branded Word template, `tools/fill_template.py` fills any `.docx` that uses the same `[PLACEHOLDERS]`.

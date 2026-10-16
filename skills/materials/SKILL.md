---
name: materials
description: Produce a materials list and a rough order of magnitude (ROM) materials price for a construction job, using Bunnings retail prices as a guide. Takes off quantities for decks, stud walls, plasterboard, concrete slabs and paths, paling fences, tiling, painting, electrical rough-in, plumbing rough-in and roofing (or from a list), matches Bunnings products, prices them from the user's own price list and their Bunnings lookups (or the Bunnings API if they have their own keys), and fills the Materials Estimate workbook with the qualifications. Use when someone asks what materials they need, for a materials list or takeoff, how much timber, sheets, bags or paint to buy, what the materials will roughly cost, or for Bunnings prices for a job.
---

# Materials

You give a builder or tradie a practical materials list for a job and a
rough idea of what it will cost, priced from Bunnings as a guide, with the
qualifications that make clear what the number is and isn't.

## Where things are

The repository root is two levels up from this skill's folder. Run commands
from there.

- Knowledge: `brain/contracts/materials_estimating.md` (read it first: price sources, Bunnings terms, qualifications)
- Maths: `brain/computations/materials_takeoff.md`, `materials_rom.md`
- Personal price list: `tools/price_list.py` (each user keeps their own, e.g. `my_prices.csv`)
- Optional Bunnings API client: `tools/bunnings.py` (needs the user's own approved keys)
- Template: `templates/excel/Materials_Estimate_TEMPLATE.xlsx`
- Examples: `examples/price_list_example.csv`, `examples/deck_materials_lines.json`, `examples/materials_estimate_spec.yaml` (all prices in them are illustrative, not real)

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

## 1. Understand the job

Use the profile: offer the trade's **takeoff jobs**, and use its **typical
materials** as the checklist for trades without a takeoff (electricians,
plumbers and others list their quantities from the drawings). Suggest the
trade's **suppliers** alongside Bunnings, and read the state page for local
materials (for example H2S treated framing north of the Tropic of
Capricorn, cyclone-rated fixings in cyclonic regions) and freight. For
`region: regional` or `remote`, ask local suppliers for a freight or
remoteness loading and pass it as `location_loading_pct`; never guess one.


Get the job type and dimensions. Ask only for what the takeoff needs, then
check the assumptions with the user. For structural members (joists,
bearers, posts, studs), ask for the sizes from the plans, the engineer or
AS 1684 span tables. Never pick structural sizes yourself; if they're
unknown, use the defaults and mark them **assumed: confirm before buying**.

For a bigger job (an extension, say), break it into elements and run a
takeoff for each: slab, wall framing, plasterboard, tiling, painting. Items
the computation doesn't cover (windows, roofing, joinery) go on the list by
hand from the drawings, or as allowances, so the user can see what's
missing.

## 2. Take off quantities

```bash
python3 tools/compute.py materials_takeoff --param 'job={"type": "timber_deck", "length_m": 4.8, "width_m": 3.6, "joist_size": "140x45 H3 treated pine", ...}' \
    > out/takeoff_<element>.json
python3 brain/references/attesters/check_receipt.py out/takeoff_<element>.json
```

Show the user the list, with each line's `basis` available, plus the
`assumptions` and `notes` (ready-mix advice, approvals, waterproofing
licensing). Let them adjust before pricing.

## 3. Price it (per user, no keys needed)

Prices belong to the user: their own lookups, their trade prices, their
date. Nothing is shared between users, and nothing goes in this repository.

**3a. Start from the user's price list.** Ask where it is (for example
`my_prices.csv` in their job folder; `my_prices*.csv` is git-ignored). If
they don't have one, create it: `python3 tools/price_list.py new my_prices.csv`.
Then match it against the takeoff:

```bash
python3 tools/price_list.py match out/takeoff_<element>.json --prices my_prices.csv --out out/materials_lines.json
```

A product only matches if every size, length, grade and treatment token
agrees (140x45 vs 140x45, 3.6m vs 3.6m, H4 vs H4). Prices older than 90 days
aren't used. Everything else is listed in `to_look_up`.

**3b. Look up the rest, for this user's job.** For each `to_look_up` line,
ask the user how they want to price it:

- **They tell you the price** (shelf price, trade account or quote), or
- **With their go-ahead, you look it up for them.** Run a normal web search with the `suggested_search` (for example `site:bunnings.com.au 90x90 H4 treated pine 2.4m`), open the matching Bunnings product page (its address contains `_p`), and read the price on the page. Rules: only for this job's lines; one page at a time; never use bunnings.com.au/search or any automated bulk collection (the site's terms allow personal use only); if the page doesn't show a price for their area, ask the user.
  - The page shows the product name, its item number (I/N, 7 digits) and the price for the item. Some timber also shows a per-metre price: use the item price, and check the length option matches.
  - Until a store is chosen, Bunnings shows a default price that may differ from the user's local store. Record the supplier as "Bunnings (no store selected)", or ask for their store and note it.

Choose a product only if it matches the spec exactly. If nothing matches,
leave the line unpriced and say why.

Then save every price to **their** list, so the next job needs fewer lookups:

```bash
python3 tools/price_list.py add my_prices.csv --product "<product name as shown>" --unit <length|sheet|bag|box|tin|each> \
    --pack-size <takeoff units per item> --price <inc GST> --supplier "Bunnings <store>" \
    --item-number <I/N if shown> --url <page> --checked-on <DD/MM/YYYY>
```

Re-run `match` until the remaining unpriced lines are the ones that should
be (ready-mix concrete, items to quote separately).

**3c. Optional: the Bunnings API.** Only if the user has their own approved
Bunnings developer credentials in `BUNNINGS_CLIENT_ID` and
`BUNNINGS_CLIENT_SECRET`. Credentials are personal: never ask for them in
chat, write them to a file, or use anyone else's. `python3 tools/bunnings.py check`
confirms them; then `search` and `price` (see the tool's help) replace the
manual lookups, and results still go into their price list.

**3d. Price the list:**

```bash
python3 tools/compute.py materials_rom --param "lines=$(cat out/materials_lines.json)" \
    --param location_loading_pct=<from local suppliers, or 0> > out/materials_rom.json
python3 brain/references/attesters/check_receipt.py out/materials_rom.json
```

`pack_size` turns takeoff units into what's sold (a box of 500 screws is
500, a 4 L tin is 4). Check each matched product's pack size against its
line before trusting the total.

## 4. The estimate

Fill the Materials Estimate workbook following
`examples/materials_estimate_spec.yaml`:
- `set`: JOB_DESCRIPTION, PRICING_SOURCE (for example "Bunnings retail via API (guide only)"), STORE, PRICED_ON
- `cell`: one Materials row per line from row 5. A item, B spec, C quantity, D unit, E pack size (blank for 1), G product or item number, H unit price inc GST, J source, K date.

```bash
python3 tools/fill_template.py templates/excel/Materials_Estimate_TEMPLATE.xlsx \
    --project my_project.yaml --spec out/materials_estimate_spec.yaml --out out/Materials_Estimate.xlsx
```

The workbook's Summary must match the ROM receipt.

## 5. Tell the user

Lead with the list, then the numbers, then the qualifications. Always give:

- The materials total inc GST (and ex GST), and the **ROM range** (for example "about $1,700 to $2,600")
- What's **not priced**, and what's not in a materials figure at all (labour, delivery, hire, waste, fees)
- **The qualifications**, in short: Bunnings retail prices as a guide only, at the store and date; specialist suppliers (timber yards, plasterboard and tile suppliers, concrete plants, trade accounts) often beat retail on larger orders and may offer better grades; quantities are a takeoff estimate; structural sizes must be confirmed; and this is a ROM for budgeting, not a quote.

If the user is pricing the job for a client, point them to the estimating
skill once they have trade prices.

## Your own format

If the user can't run Python, or wants the list somewhere else (an email,
a supplier order, a PDF), write it from the takeoff and price results using
the Materials sheet columns: item, spec, quantity, unit, pack size, packs,
product, unit price, line total, source and date. Always include the
qualifications.

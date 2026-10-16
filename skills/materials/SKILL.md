---
name: materials
description: Produce a materials list and a rough order of magnitude (ROM) materials price for a construction job, using Bunnings retail prices as a guide. Takes off quantities for decks, stud walls, plasterboard, concrete slabs and paths, paling fences, tiling and painting (or from a list), matches Bunnings products, prices them through the official Bunnings API, and fills the Materials Estimate workbook with the qualifications. Use when someone asks what materials they need, for a materials list or takeoff, how much timber, sheets, bags or paint to buy, what the materials will roughly cost, or for Bunnings prices for a job.
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
- Bunnings API client: `tools/bunnings.py`
- Template: `templates/excel/Materials_Estimate_TEMPLATE.xlsx`
- Examples: `examples/deck_materials_lines.json`, `examples/materials_estimate_spec.yaml` (the prices in them are illustrative, not real)

If `python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r requirements.txt`.

## 1. Understand the job

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

## 3. Price it

Pick the price source with the user (see the brain page):

**A. Bunnings API** (when `BUNNINGS_CLIENT_ID` and `BUNNINGS_CLIENT_SECRET` are set; `python3 tools/bunnings.py check` confirms):

```bash
python3 tools/bunnings.py stores "Newcastle" --json                 # find the store's location code
python3 tools/bunnings.py search "<item search phrase>" --store <code> --limit 5 --json
python3 tools/bunnings.py price <item numbers...> --store <code> --json
```

For each line, search with its `search` phrase and choose the result that
matches the spec exactly: size, treatment class (H3 or H4), grade, length,
pack size. If nothing matches, leave it unpriced and say why; don't
substitute a different spec silently. Then price all the chosen item
numbers in one call. Space out calls; on a rate-limit error, wait.

**B. No API access.** Explain that Bunnings' API needs approved
credentials (register at developer.sandbox.bunnings.com.au). Then, with the
user's go-ahead, either they give you the shelf prices, or you open
individual product pages for this job only (find them with a normal web
search; never use bunnings.com.au/search, and never collect prices in
bulk), recording each page's URL and the date. The site's terms allow
personal use only.

**C. Their own price list** or supplier quote.

Build the lines file: for each item, `quantity` (from the takeoff),
`pack_size` (how many takeoff units one priced item holds: a box of 500
screws is 500, a 4 L tin is 4, a length priced each is 1),
`unit_price_inc_gst`, `product` (name and item number), `source` (for
example "Bunnings API, store 6401") and `priced_on`. Ready-mix concrete in
m³ is not a Bunnings item: leave it unpriced and say to get a concrete
supplier's price.

```bash
python3 tools/compute.py materials_rom --param "lines=$(cat out/materials_lines.json)" > out/materials_rom.json
python3 brain/references/attesters/check_receipt.py out/materials_rom.json
```

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

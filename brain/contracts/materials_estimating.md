---
type: Contract Topic
title: Materials estimating and pricing
description: "Producing a materials list and a rough order of magnitude price for a job: takeoff rules, where prices come from (the Bunnings API as a retail guide), and the qualifications every figure must carry."
tags: [materials, estimating, pricing, bunnings, rom]
status: draft
sources:
  - id: bunnings_api
    resource: https://developer.live.bunnings.com.au/explore
    title: Bunnings developer portal (Query Item, Query Pricing, Query Location APIs)
    author: org:bunnings
    last_modified: 2026-10-17T00:00:00Z
  - id: bunnings_terms
    resource: https://www.bunnings.com.au/terms-conditions/website-terms-of-use
    title: Bunnings website terms of use
    author: org:bunnings
    last_modified: 2026-10-17T00:00:00Z
generated: { by: claude/opus-5.5, at: 2026-10-17T00:00:00Z }
stale_after: 2027-04-17T00:00:00Z
---

> **Draft.** The takeoff rules are estimating rules of thumb. The optional
> Bunnings API client is built from the published specs and hasn't been
> tested against the live API.

A materials estimate answers two questions early: **what do I need to
buy**, and **roughly what will it cost**. It is a rough order of magnitude
(ROM) for budgeting and for deciding whether to proceed, not a quote.

# 1. Takeoff: what to buy

The [materials takeoff](/computations/materials_takeoff.md) computation
covers common jobs: timber deck, stud wall, plasterboard, concrete slab,
paling fence, tiling and painting. It returns each item with its quantity,
purchase unit (stock length, sheet, bag, box, litre), the arithmetic, and
the assumptions it used. For bigger jobs, run it once per element and
combine the lists. Jobs it doesn't cover can be taken off by hand from the
drawings in the same item/quantity/unit form.

The takeoff never sizes structural members. Joists, bearers, posts, studs
and lintels come from AS 1684 span tables, the supplier's span tables or the
engineer. Ask the user for them, or mark them as assumed.

# 2. Prices: per user, Bunnings as the guide

Bunnings is a convenient, widely recognised retail reference with prices
for most common building materials. Pricing is done **by each user, for
their own job**, so it needs no shared accounts or keys:

1. **The user's own price list** (`tools/price_list.py`): a CSV the user keeps (for example `my_prices.csv` in their job folder, git-ignored here) with product, unit, pack size, price inc GST, supplier, link and date checked. It grows with every job and can hold trade account prices that beat retail. Prices older than 90 days are re-checked.
2. **Lookups for this job.** The user reads out shelf prices, or with their go-ahead an agent opens individual Bunnings product pages for this job's lines (found through a normal web search) and reads the price. Each price is saved to the user's list with its link and date. The Bunnings website terms allow use for your own personal purposes only,[^bunnings_terms] and its robots.txt disallows automated access to `/search` and `/api/`, so there is no scraping and no bulk collection.
3. **Optional: the official Bunnings APIs**[^bunnings_api] via `tools/bunnings.py`, for users with their own Bunnings-approved developer credentials in the `BUNNINGS_CLIENT_ID` and `BUNNINGS_CLIENT_SECRET` environment variables. Credentials are personal: they are never shared, written to files or committed.

Never commit anyone's prices to this repository. Prices are for the user's
job, dated, and kept with the user.

## Matching products

For each takeoff line, search with its `search` phrase, then pick the
product that matches the specification: size, treatment class (H3 above
ground outdoors, H4 in-ground posts), grade (MGP10), length and pack size.
If nothing matches, say so and leave the line unpriced rather than
substituting a different spec.

Convert the takeoff quantity to what's sold: `pack_size` is how many
takeoff units one priced item holds (a box of 500 screws: 500; a 10 L
tin: 10; a length priced each: 1). The [product catalogue](/references/product_catalogue.md)
does most of this: when a price has no pack size recorded, matching reads
it off the product's name (a 10 L tin, a 500 pack, a 1.35 x 30 m roll),
turns a per-metre price into the stock length the takeoff counts, and buys
the cheapest mix of pack sizes when the user has prices for several (a 15 L
and two 4 L tins rather than three 10 L). Every line says what it assumed,
so check it. Ready-mix concrete (m³) isn't a Bunnings
product: leave it unpriced, or price premix bags for small pours only.

# 3. The estimate

Price the matched list with [materials ROM](/computations/materials_rom.md):
packs to buy, line totals, the total inc and ex GST, unpriced items, and
the ROM range (default −15% / +30%). Record it in the
[Materials Estimate](/documents/materials_estimate.md) workbook.

# Qualifications (always include)

Every figure given to anyone carries these. They are also printed on the
workbook's Qualifications sheet.

1. Bunnings prices are a guide only: retail prices including GST, for the store and date shown. They change over time and between stores.
2. Specialist suppliers (timber yards, plasterboard, tile and paint suppliers, concrete plants, trade accounts) often price better for larger quantities, and may supply better grades or products. Get trade quotes before committing.
3. Quantities are a takeoff estimate based on rules of thumb. Check them against the drawings and the manufacturers' guides.
4. Labour, delivery, equipment hire, waste removal, fees, engineering and contingency are excluded unless listed.
5. Structural sizes and fixings must be confirmed (AS 1684, the supplier's span tables or an engineer), and products must suit the use and comply with the NCC.
6. Unpriced items are not in the total.
7. The ROM range is for budgeting and deciding whether to proceed. It is not a quote or a fixed price.

Feed a confirmed materials budget into the
[estimate](/contracts/estimating_and_quoting.md) as the materials subtotal,
once trade prices replace the retail guide.

[^bunnings_api]: Bunnings developer portal (Query Item, Query Pricing, Query Location APIs)
[^bunnings_terms]: Bunnings website terms of use

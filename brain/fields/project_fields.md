---
type: Field Schema
title: Project fields
description: Every placeholder a template may contain, where its value comes from, and how to write it.
tags: [fields, templates, schema]
status: stable
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
---

All templates draw on one project file (see
[`examples/project_example.yaml`](https://github.com/grechj/Australian-Builders-Brain/blob/main/examples/project_example.yaml)).
The file is grouped into sections for readability, but every key is unique,
and the placeholder is simply the key in upper case: `client_name` fills
`[CLIENT_NAME]`.

`tools/fill_template.py` fills every placeholder it has a value for and lists
the rest. `tools/okf_lint.py` fails if a template uses a placeholder that is
not listed here.

# Schema

## Business (the builder or trade issuing the document)

| Placeholder | Description | Example |
|---|---|---|
| `[BUSINESS_NAME]` | Trading name | Smith Building Pty Ltd |
| `[ABN]` | Australian Business Number, 11 digits | 12 345 678 901 |
| `[LICENCE_NUMBER]` | State builder or contractor licence | 123456C |
| `[BUSINESS_ADDRESS]` | Street address | 1 Trade St |
| `[BUSINESS_ADDRESS_LINE_2]` | Suburb, state, postcode | Newcastle NSW 2300 |
| `[PHONE]` | Business phone | 0400 000 000 |
| `[EMAIL]` | Business email | jobs@smithbuilding.com.au |
| `[WEBSITE]` | Website | smithbuilding.com.au |
| `[LOGO]` | Where the logo goes. The fill tool leaves this for the user to insert an image. | |
| `[ACCOUNT_NAME]` | Bank account name for payments | Smith Building Pty Ltd |
| `[BSB]` | Bank BSB | 062-000 |
| `[ACCOUNT_NUMBER]` | Bank account number | 1234 5678 |

## Project

| Placeholder | Description | Example |
|---|---|---|
| `[PROJECT_NAME]` | Short job name | Banksia St extension |
| `[PROJECT_ADDRESS]` | Site address | 42 Banksia St, Merewether NSW 2291 |
| `[START_DATE]` | Site start date, DD/MM/YYYY | 03/02/2027 |
| `[END_DATE]` | Contract completion date, DD/MM/YYYY | 30/09/2027 |
| `[NEAREST_HOSPITAL]` | Nearest emergency department, name and address | John Hunter Hospital, Lookout Rd, New Lambton Heights |

The project file also carries `state` (NSW, VIC, QLD, WA, SA, TAS, ACT, NT)
and `project_type` (new_home, renovation, extension, commercial, other).
They don't appear in templates, but skills use them to choose state rules and
construction phases.

## Client

| Placeholder | Description | Example |
|---|---|---|
| `[CLIENT_NAME]` | Owner or client named on the contract | Jo and Sam Citizen |
| `[CLIENT_ADDRESS]` | Client postal address | 42 Banksia St, Merewether NSW 2291 |
| `[CLIENT_PHONE]` | Client phone | 0411 111 111 |
| `[CLIENT_EMAIL]` | Client email | citizens@example.com |

## Contract

| Placeholder | Description | Example |
|---|---|---|
| `[CONTRACT_NUMBER]` | Builder's contract or job number | SB-2027-014 |
| `[CONTRACT_SUM]` | Original contract sum, inc GST, no `$` sign | 485,000.00 |
| `[CONTRACT_CLAUSE]` | The clause a notice relies on, from the [clause map](/contracts/hia_mba_clause_map.md) or the user's contract | Clause 17 |

The project file also carries `contract_type` (HIA, MBA, other),
`contract_edition`, `contract_date`, `contract_sum_ex_gst` (from the
[ex GST](/computations/ex_gst.md) computation), `builders_margin_pct` (the
margin on variations), `retention_pct` and `site_supervisor`. Excel
templates read these through their Setup sheets.

## Subcontractor

| Placeholder | Description | Example |
|---|---|---|
| `[SUBBIE_NAME]` | Subcontractor business name | Hunter Sparks Pty Ltd |
| `[SUBBIE_ABN]` | Subcontractor ABN | 98 765 432 109 |
| `[SUBBIE_LICENCE]` | Subcontractor licence | 654321C |
| `[SUBBIE_PHONE]` | Subcontractor phone | 0422 222 222 |
| `[SUBBIE_EMAIL]` | Subcontractor email | office@huntersparks.com.au |
| `[TRADE_NAME]` | Trade or person on a booking or induction | Electrician: Alex Lee |

## Document numbers

Numbers run per project, zero-padded to three digits.

| Placeholder | Format |
|---|---|
| `[VAR_NUMBER]` | VAR-001 |
| `[CHANGE_REQUEST_NUMBER]` | CR-001 |
| `[BACK_CHARGE_NUMBER]` | BC-001 |
| `[DELAY_NUMBER]` | DELAY-001 |
| `[INVOICE_NUMBER]` | INV-001 |
| `[CLAIM_NUMBER]` | 1, 2, 3... (progress claim sequence) |
| `[SWMS_NUMBER]` | SWMS-001 |
| `[SITE_INSTRUCTION_NUMBER]` | SI-001 |
| `[QUOTE_NUMBER]` | Q-001 |
| `[QUOTE_REF]` | Subcontractor's own quote reference |
| `[WEEK_NUMBER]` | Construction week number, from the start date |

## Money and time

Always produced by [computations](/computations/index.md), never typed by hand.

| Placeholder | Description | Computation |
|---|---|---|
| `[AMOUNT]` | Amount ex GST | [variation price](/computations/variation_price.md) or [GST](/computations/gst.md) |
| `[AMOUNT_GST]` | GST on `[AMOUNT]` | [GST](/computations/gst.md) |
| `[AMOUNT_TOTAL]` | `[AMOUNT]` plus GST | [GST](/computations/gst.md) |
| `[TIME_IMPACT_DAYS]` | Days added to the program | Entered by the user |

## Context fields (filled per document)

These are generic on purpose. Their meaning comes from the label next to them
in the template, so the skill fills them while writing the document, not from
the project file.

| Placeholder | Meaning |
|---|---|
| `[DATE]` | Date the document is issued |
| `[DD/MM/YYYY]` | Any other date. Read the label beside it. |
| `[TIME]` | Time of an event (incidents, inductions) |
| `[NAME]` | Signatory or person named on the line |
| `[NUMBER]` | Count beside the label, usually days |
| `[X]` | Number inside a choice, for example "Behind [X] days" |
| `[DESCRIPTION]` | Short description of the work or event |
| `[LOCATION]` | Location on site |
| `[TRADE]` | Trade involved, for example "Plumber" |
| `[HIGH_RISK_ACTIVITY]` | High-risk construction work covered by a SWMS |

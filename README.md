# Australian Builder's Brain

An open knowledge base and set of Claude skills for Australian builders and
tradespeople. It drafts the paperwork a job runs on, from quotes and
contracts through variations, delay notices and progress claims to practical
completion and the final account, and it knows the construction sequence
and the National Construction Code.

> **Status: v0.11.0.** All thirteen skills work end to end, covering all 64 templates, and job money exports to Xero, MYOB and QuickBooks. NCC 2025
> and NCC 2022 (with Amendments 1 and 2) are loaded. Still to do: verified state-by-state
> rules (see the roadmap). Everything marked `status: draft` in `brain/` still needs
> checking by a person.

## What's inside

| Folder | What it is |
|---|---|
| [`brain/`](brain/index.md) | The knowledge base: lifecycle stages, construction phases, contract topics, state rules, the NCC, the template catalogue and the money computations. Plain markdown in [Google's Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format), kept up by an agent using [Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). |
| [`skills/`](skills/) | Claude skills that turn the brain plus your job details into finished documents. |
| [`templates/`](templates/) | 64 Word, Excel and PDF templates (variations, claims, security of payment, notices, WHS, handover...). |
| [`tools/`](tools/) | Python that fills templates, runs the money maths and lints the brain. |
| [`examples/`](examples/) | A fictional project file and variation, for trying it out. |

## Install

**Claude Code**, as a plugin:

```bash
claude plugin marketplace add grechj/Australian-Builders-Brain
```

```bash
claude plugin install australian-builders-brain
```

Or in one step, inside Claude Code: `/plugin install australian-builders-brain --marketplace grechj/Australian-Builders-Brain`

That's all a plugin user needs: no clone and no `pip install`.

The plugin's skills run from your own project folder and write their
documents there; the brain itself stays read-only. The first time a session
starts, a setup hook builds a private Python environment for the tools
(python-docx, openpyxl, PyYAML) in the plugin's data folder. You need Python
3.9 or later installed.

**Claude.ai or Claude Desktop:** zip a folder from `skills/` and upload it
under Settings → Capabilities → Skills. An uploaded skill doesn't include the
brain, templates or tools, so it works in its "your own format" mode. For the
full brain, use Claude Code.

**Any other agent:** clone the repo and point the agent at `AGENTS.md`.

Only if you're working in a clone of this repository (to contribute, or
without the plugin), install the Python tools' dependencies yourself, from
the clone's folder:

```bash
python3 -m pip install -r requirements.txt
```

## Try it

```bash
python3 tools/compute.py variation_price --param labour=1200 --param materials=1450 --param plant=150 --param margin_pct=20
```

```bash
python3 tools/fill_template.py templates/word/Priced_Variation_Notice_TEMPLATE.docx --project examples/project_example.yaml --spec examples/var_001_spec.yaml --out out/VAR-001_Priced_Variation_Notice.docx
```

```bash
python3 tools/ncc_lookup.py search "wet area waterproofing shower" --volume housing_provisions
```

Or ask Claude: *"What's the minimum balustrade height on a deck in Queensland?"* or *"Price a variation for rock in the footings: $1,200 labour,
$1,450 tip fees, $150 excavator, 2 days delay."*

## Profiles: trade and location

Everyone sets a **trade** and a **state or territory** (in the project file,
or when asking), and the brain shows only what applies:

- **Trade** ([`brain/trades/`](brain/trades/index.md)): 22 trades, from electrician to roofer to tiler, plus `builder`, which sees everything. An electrician sees 13 NCC parts (smoke alarms, energy, lighting); a builder sees all 230. Each trade also gets its own skills, takeoff jobs, typical materials and supplier types.
- **Location** ([`brain/states/`](brain/states/index.md)): each state's NCC variations (generated from the code), state-only Parts (for example Victoria's plumbing Parts for HVAC and stormwater), regulator and licensing, climate and materials (cyclonic regions, H2S vs H2F treated framing, BASIX in NSW), and freight and cost notes.

```bash
python3 tools/profile.py trades
```

```bash
python3 tools/profile.py show --trade sparky --state QLD
```

## Using the templates

The 64 templates in `templates/` are references for producing your own
documents quickly:

- **Fill them as they are.** `tools/fill_template.py` fills the Word and Excel templates from your project file, and the skills do this for you.
- **Use your own branding.** Put the same `[PLACEHOLDERS]` (listed in [project fields](brain/fields/project_fields.md)) in your own letterhead `.docx` and fill that instead.
- **Use any format.** Each template's page in [`brain/documents/`](brain/documents/index.md) has a **Structure** outline: every section, field, table and prompt in order. Claude can write the document from it as an email, a PDF or anything else, without opening the template.
- **The PDF checklists and handouts are built from brain pages** (`tools/build_pdfs.py`). Edit the page, rebuild, and the PDF follows.

## Pricing materials (materials skill)

Each user prices their own job; no accounts or keys are needed:

- Keep your own price list (`python3 tools/price_list.py new my_prices.csv`). It is matched to each takeoff, only on an exact size, length, grade and treatment.
- For anything missing, give Claude the shelf price, or let it look up the Bunnings product page for that item. Each price is saved to your list with its link and date, so the next job needs fewer lookups.
- If you have your own approved [Bunnings API](https://developer.live.bunnings.com.au/explore) credentials, set `BUNNINGS_CLIENT_ID` and `BUNNINGS_CLIENT_SECRET` and the skill uses them. They stay on your machine.

Bunnings prices are a retail guide only; specialist suppliers often price
better. The brain never scrapes the Bunnings website (its terms allow
personal use only) and never stores anyone's prices.

## Projects and the inbox (projects skill)

Each job gets a number, a name, tags and a standard folder (`project.yaml`,
`ledger.yaml`, `timesheets.csv`, `inbox/`, `processed/`, `out/`), all listed
in one register, `projects.yaml`. Drop supplier invoices, subbie claims,
bank payment screenshots, dockets and site photos into a job's inbox, or
into the shared inbox (a subfolder named for a tag labels them). Claude
reads each one and works out which job it's for from the address, client or
order number on it. It checks the figures (lines add up to the total, GST
is 10%, ABN, tax invoice rules, not already entered in any job), then shows
you the entry. Once you say yes, it adds the entry to the job's ledger and
files the original as `processed/BILL_<supplier>_<number>.pdf`, linked from
the dashboard.

```bash
python3 tools/projects.py new projects.yaml --job SB-2027-014 --name "Banksia St extension" --tags banksia,citizen
```

```bash
python3 tools/projects.py inbox projects.yaml
```

Try it with the sample invoice and bank screenshot in `examples/inbox/`.

## Money into your accounts (accounts skill)

Claims, invoices and bills from the other skills go into a per-job ledger
(`ledger.yaml`), coded once to your own chart of accounts (`accounts.yaml`).
From there `tools/finance.py` writes import files for Xero, MYOB
AccountRight or QuickBooks Online, or the skill creates drafts through your
own Xero, MYOB or QuickBooks connector after you approve them. It also works
out the job's BAS GST labels and the TPAR contractor payments as attested
computations. Nothing is lodged, and no keys or logins are stored.

```bash
python3 tools/finance.py export examples/ledger_example.yaml --accounts examples/accounts_example.yaml --out out/finance
```

```bash
python3 tools/finance.py bas examples/ledger_example.yaml --accounts examples/accounts_example.yaml --from 01/07/2026 --to 30/09/2026 --basis accrual
```

### Project dashboard

List your jobs, current and finished, in a portfolio file and get CSV
extracts plus a dashboard page for each job: P&L and margin against target,
a forecast at completion, receipts and what's outstanding, costs against
budget, cash in and out by month, time on site, and job length against the
contract and your average. The dashboard links to every document generated
for the job (locally, or in Dropbox, Google Drive or SharePoint), and the
extracts include flat transaction tables for modelling, a cost mix by
project type for pricing new work, and Xero, MYOB or QuickBooks import files
covering every job.

```bash
python3 tools/dashboard.py examples/projects_example.yaml --as-at 31/10/2026 --out out/dashboard
```

## How it stays trustworthy

- **Money is never guessed.** GST, variation prices and margins come from
  [attested computations](brain/computations/index.md): a single pinned
  Python source, a receipt for every run, and a checker that re-runs it.
- **Every page shows where it came from.** Sources, who wrote it, who checked
  it (`verified`) and when it goes stale are in each page's frontmatter.
  `draft` means nobody has checked it yet.
- **The state comes first.** Building law differs by state, so skills ask
  which state the job is in before drafting anything legal.
- **No copied copyright.** The NCC is used under its CC BY 4.0 licence.
  Australian Standards and HIA/MBA contract wording are referenced, never
  reproduced.

## Roadmap

| Skill | Templates | Status |
|---|---|---|
| `variations` | change request, builder variation, priced notice, approval, explanation, register, allowances, selections | **working** |
| `estimating` | estimate workbook, estimate to quote, quote comparison, margin sensitivity, clarifications, trade quote, quote acceptance | **working** |
| `contracts` | contract summary, scope of works, subcontract, trade scope, pre-construction checklist | **working** |
| `claims` | progress claim calculator and invoice, SOPA payment claim and payment schedule, trade tax invoice, payment register, subbie payments, retention, claim pack | **working** |
| `notices` | delay notification, site instruction, back charge, suspension, breach, termination | **working** |
| `site` | site diary, progress email, RFI, meeting minutes, construction program, timesheets and dockets, material orders, trade bookings, hold points | **working** |
| `safety` | SWMS, safety plan, toolbox talk, incident report, induction, inspection, subbie compliance | **working** |
| `handover` | PC checklist and notice, defects, as-builts, warranties, final claim, final account | **working** |
| `financials` | budget vs actual, job P&L, lessons learned | **working** |
| `projects` | project register, tags and folders; inbox for invoices, payment screenshots, dockets and photos, read, checked and filed per job | **working** |
| `accounts` | job ledger, account mapping, Xero / MYOB / QuickBooks import files, drafts through the user's own connector, BAS GST labels, TPAR, CSV extracts and project dashboard | **working** (import formats: Xero checked against Xero's help, MYOB and QuickBooks draft) |
| `materials` | materials list and rough order of magnitude price for common jobs, priced per user from their own price list and Bunnings lookups (official API optional) | **working** (optional API client untested against live) |
| `ncc` | NCC 2025 and NCC 2022 lookups with clause citations, filtered by trade, state and edition | **working** |

Knowledge work still to do: verify and
split the [state rules](brain/states/overview.md), verify the
[HIA/MBA clause map](brain/contracts/hia_mba_clause_map.md) against current
editions, and turn the PDF checklists into wiki playbooks.

## Contributing

Read [`AGENTS.md`](AGENTS.md). In short: use `_` in names, put
`[UPPER_SNAKE_CASE]` placeholders in templates, give every brain page OKF
frontmatter, and run `python3 tools/okf_lint.py` and `python3 tools/test_examples.py` before opening a PR.
Builders who check a draft page against the source can add themselves to its
`verified` list. That is the most useful contribution of all.

## Disclaimer

The documents this produces are drafts. They are not legal advice. Check
them against your actual contract and your state's legislation, and get
advice from a lawyer or your industry association before relying on them in
a dispute.

## Licence

- **Content, skills and templates** (`brain/` pages, `skills/`, `templates/`, `examples/`, docs): [CC BY 4.0](LICENSE_CONTENT). Use, adapt and share them, including commercially, as long as you credit "Australian Builder's Brain by Joshua Grech".
- **Code** (`tools/`, the Python in `brain/references/`): [MIT](LICENSE). The MIT licence covers only this code; everything else is CC BY 4.0.

NCC content: © Commonwealth of Australia and the States and Territories of
Australia, published by the Australian Building Codes Board, licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The National
Construction Code 2022 was provided by the Australian Building Codes Board under
the CC BY 4.0 licence.
Templates by Joshua Grech.

# Australian Builder's Brain

An open knowledge base and set of Claude skills for Australian builders and
tradespeople. It drafts the paperwork a job runs on, from quotes and
contracts through variations, delay notices and progress claims to practical
completion and the final account, and it knows the construction sequence
and the National Construction Code.

> **Status: v0.5.** All eleven skills work end to end, covering all 53 templates, and the full
> NCC 2025 text is loaded. Still to do: verified state-by-state rules and NCC 2022
> (see the roadmap). Everything marked `status: draft` in `brain/` still needs
> checking by a person.

## What's inside

| Folder | What it is |
|---|---|
| [`brain/`](brain/index.md) | The knowledge base: lifecycle stages, construction phases, contract topics, state rules, the NCC, the template catalogue and the money computations. Plain markdown in [Google's Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format), kept up by an agent using [Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). |
| [`skills/`](skills/) | Claude skills that turn the brain plus your job details into finished documents. |
| [`templates/`](templates/) | 53 Word, Excel and PDF templates (variations, claims, notices, WHS, handover...). |
| [`tools/`](tools/) | Python that fills templates, runs the money maths and lints the brain. |
| [`examples/`](examples/) | A fictional project file and variation, for trying it out. |

## Install

**Claude Code**, as a plugin:

```bash
claude plugin marketplace add grechj/Australian-Builders-Brain
```

```bash
claude plugin install australian_builders_brain
```

**Claude.ai or Claude Desktop:** zip a folder from `skills/` and upload it
under Settings → Capabilities → Skills.

**Any other agent:** clone the repo and point the agent at `AGENTS.md`.

The Python tools need Python 3.9 or later:

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

## Using the templates

The 53 templates in `templates/` are references for producing your own
documents quickly:

- **Fill them as they are.** `tools/fill_template.py` fills the Word and Excel templates from your project file, and the skills do this for you.
- **Use your own branding.** Put the same `[PLACEHOLDERS]` (listed in [project fields](brain/fields/project_fields.md)) in your own letterhead `.docx` and fill that instead.
- **Use any format.** Each template's page in [`brain/documents/`](brain/documents/index.md) has a **Structure** outline: every section, field, table and prompt in order. Claude can write the document from it as an email, a PDF or anything else, without opening the template.
- **The PDF checklists and handouts are built from brain pages** (`tools/build_pdfs.py`). Edit the page, rebuild, and the PDF follows.

## Bunnings prices (materials skill)

The `materials` skill can price a takeoff from Bunnings through the
[official Bunnings APIs](https://developer.live.bunnings.com.au/explore).
Register on the developer portal, create an app, get Bunnings' approval for
the Query Item, Query Pricing and Query Location products, then:

```bash
export BUNNINGS_CLIENT_ID=your_key BUNNINGS_CLIENT_SECRET=your_secret
```

```bash
python3 tools/bunnings.py check
```

Bunnings prices are a retail guide only; specialist suppliers often price
better. The tool uses only the API: the Bunnings website's terms allow
personal use only, so the brain never scrapes it.

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
| `estimating` | estimate workbook, estimate to quote, quote comparison, margin sensitivity, clarifications, quote acceptance | **working** |
| `contracts` | contract summary, scope of works, subcontract, trade scope, pre-construction checklist | **working** |
| `claims` | progress claim calculator and invoice, payment register, subbie payments, retention, claim pack | **working** |
| `notices` | delay notification, site instruction, back charge | **working** |
| `site` | site diary, progress email, material orders, trade bookings, hold points | **working** |
| `safety` | SWMS, safety plan, toolbox talk, incident report, induction, inspection, subbie compliance | **working** |
| `handover` | PC checklist and notice, defects, as-builts, warranties, final claim, final account | **working** |
| `financials` | budget vs actual, job P&L, lessons learned | **working** |
| `materials` | materials list and rough order of magnitude price for common jobs, using Bunnings retail prices (via the official API) as a guide | **working** (API client untested against live) |
| `ncc` | NCC 2025 lookups with clause citations and state variations (1,652 clauses, all five volumes) | **working** |

Knowledge work still to do: load NCC 2022 for jobs lodged under it, verify and
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
- **Code** (`tools/`, the Python in `brain/references/`): [MIT](LICENSE).

NCC content: © Commonwealth of Australia and the States and Territories of
Australia, published by the Australian Building Codes Board, licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
Templates by Joshua Grech.

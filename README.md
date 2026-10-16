# Australian Builder's Brain

An open knowledge base and set of Claude skills for Australian builders and
tradespeople. It drafts the paperwork a job runs on, from quotes and
contracts through variations, delay notices and progress claims to practical
completion and the final account, and it knows the construction sequence
and the National Construction Code.

> **Status: early (v0.3).** The `variations`, `claims`, `notices` and `ncc` skills work
> end to end, and the full NCC 2025 text is loaded. The other skills and the state-by-state
> rules are on the roadmap below. Everything marked `status: draft` in `brain/` still needs
> checking by a person.

## What's inside

| Folder | What it is |
|---|---|
| [`brain/`](brain/index.md) | The knowledge base: lifecycle stages, construction phases, contract topics, state rules, the NCC, the template catalogue and the money computations. Plain markdown in [Google's Open Knowledge Format](https://github.com/GoogleCloudPlatform/open-knowledge-format), kept up by an agent using [Karpathy's LLM-wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f). |
| [`skills/`](skills/) | Claude skills that turn the brain plus your job details into finished documents. |
| [`templates/`](templates/) | 52 Word, Excel and PDF templates (variations, claims, notices, WHS, handover...). |
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
| `estimating` | estimate workbook, estimate to quote, quote comparison, margin sensitivity, clarifications, quote acceptance | planned |
| `contracts` | contract summary, scope of works, subcontract, trade scope, pre-construction checklist | planned |
| `claims` | progress claim calculator and invoice, payment register, subbie payments, retention, claim pack | **working** |
| `notices` | delay notification, site instruction, back charge | **working** |
| `site` | site diary, progress email, material orders, trade bookings, hold points | planned |
| `safety` | SWMS, safety plan, toolbox talk, incident report, induction, inspection, subbie compliance | planned |
| `handover` | PC checklist and notice, defects, as-builts, warranties, final claim, final account | planned |
| `financials` | budget vs actual, job P&L, lessons learned | planned |
| `ncc` | NCC 2025 lookups with clause citations and state variations (1,652 clauses, all five volumes) | **working** |

Knowledge work still to do: load NCC 2022 for jobs lodged under it, verify and
split the [state rules](brain/states/overview.md), verify the
[HIA/MBA clause map](brain/contracts/hia_mba_clause_map.md) against current
editions, and turn the PDF checklists into wiki playbooks.

## Contributing

Read [`AGENTS.md`](AGENTS.md). In short: use `_` in names, put
`[UPPER_SNAKE_CASE]` placeholders in templates, give every brain page OKF
frontmatter, and run `python3 tools/okf_lint.py` before opening a PR.
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
Templates are adapted from the BEAM Builder Template Pack by Joshua Grech.

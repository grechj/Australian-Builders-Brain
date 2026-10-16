# Australian Builder's Brain: agent operating rules

This repository is a knowledge bundle plus a set of skills for Australian
builders and tradespeople. Any LLM agent (Claude, Gemini, others) working in
this repo follows these rules.

## Layout

| Path | What lives there | Who edits it |
|---|---|---|
| `brain/` | The wiki. An [Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) bundle. | Agents, reviewed by humans |
| `raw/` | Untouched source material (NCC XML, legislation extracts, notes). Never edited, only added to. | Humans and fetch scripts |
| `skills/` | Claude skills that turn brain knowledge plus project facts into documents. | Humans and agents |
| `templates/` | The Word, Excel and PDF templates the skills fill. | Humans |
| `tools/` | Deterministic Python: template filling, computations, wiki linting. | Humans and agents |
| `hooks/` | Plugin setup hook: builds the tools' Python environment when the plugin is installed. | Humans |
| `examples/` | Sample project files for testing. | Anyone |

## Naming

- Use `_`, never spaces or hyphens, in file and folder names: `extension_of_time.md`, `Delay_Notification_Letter_TEMPLATE.docx`.
- Template placeholders are `[UPPER_SNAKE_CASE]` and must exist in
  [`brain/fields/project_fields.md`](brain/fields/project_fields.md).
  Bracketed prose such as `[Describe the variation...]` or `[SELECT: A / B]`
  is an instruction for whoever fills the template, not a field.
- Concept IDs are the file path inside `brain/` without `.md`, for example `phases/new_home/foundation_works`.

## The wiki pattern (how `brain/` grows)

`brain/` follows Karpathy's LLM-wiki pattern on top of OKF. The agent
compiles knowledge once into linked markdown pages and keeps it current, so
nobody has to re-derive it from raw sources on every question.

### Ingest

When a new source arrives (in `raw/`, a URL, or the user's own notes):

1. Read it in full.
2. Decide which concepts it creates or changes. Prefer updating an existing concept over minting a near-duplicate.
3. Write or update each concept with full frontmatter (below), adding the source to `sources` and footnoting the claims it supports.
4. Link the new concept from related concepts and from its folder `index.md`.
5. Add a dated entry to `brain/log.md`.
6. Run `python tools/okf_lint.py` and fix what it reports.

### Query

To answer a question or generate a document, start at `brain/index.md` and
walk down through the `index.md` files (progressive disclosure). Load only
the concepts you need. Cite the concepts you relied on.

### Lint

`python tools/okf_lint.py` checks OKF conformance, broken links, unknown
placeholders and concepts past their `stale_after` date.
`python tools/okf_lint.py --write_indexes` regenerates every `index.md`.

## Concept frontmatter

`type` is the only field OKF requires. This bundle also expects `title`,
`description` and `tags` on every concept, plus the trust and lifecycle
fields wherever they apply:

```yaml
---
type: Contract Topic
title: Extension of time
description: How a builder claims more time under a residential building contract.
tags: [contracts, delays, notices]
status: draft                     # draft | stable | deprecated
jurisdiction: [NSW, VIC, QLD]     # omit if national
sources:
  - id: ncc_2022_v2
    resource: https://ncc.abcb.gov.au/editions/ncc-2022
    title: NCC 2022 Volume Two
generated: { by: claude/opus-5.5, at: 2026-10-16T00:00:00Z }
verified: { by: human:grechj, at: 2026-10-16T00:00:00Z }
stale_after: 2027-10-16T00:00:00Z
---
```

Types in use: `Lifecycle Stage`, `Construction Phase`, `Document Template`,
`Field Schema`, `Contract Topic`, `State Rule Set`, `Code Reference`,
`Attested Computation`, `Glossary`, `Playbook`, `Reference`.

Actors follow OKF §7: `human:<github_id>` for people,
`claude/<model>` or `<tool>/<version>` for agents.

## Templates and PDFs

- After changing a Word or Excel template, run `python tools/describe_templates.py` to refresh the Structure outline on its document page.
- PDFs in `templates/pdf/` are generated: edit the brain page named in their `pdf:` frontmatter key, then run `python tools/build_pdfs.py`. Never edit a PDF directly.

## Profiles: trade and location

Every answer is for one person's profile: a trade (`brain/trades/`, or
`builder` / `all` for everything) and a state or territory
(`brain/states/`). Resolve it with `python tools/profile.py show` and keep to
it:

- NCC: only the trade's `ncc_scope` pages, and only that state's variations and state-only Parts (`tools/ncc_lookup.py --trade --state`)
- Skills, takeoff jobs, materials and suppliers: as listed for the trade
- Location: the state page's regulator, licensing, climate, materials and cost notes

When a trade needs something outside its scope, widen deliberately (`--trade builder`) and say so.

## Content rules

1. **Australian English and Australian practice.** GST is 10%. Say "ex GST" or "inc GST" next to every dollar figure.
2. **Ask for the state or territory first.** Building acts, deposit caps, home warranty insurance and security-of-payment rules all differ by state. Any concept that depends on the state sets `jurisdiction`.
3. **Never invent a clause number, NCC reference or legal requirement.** If something is unverified, mark the concept `status: draft` and say so in the text.
4. **NCC content** comes from the ABCB's CC BY 4.0 datasets. `brain/ncc/2025/` is generated by `tools/ncc_ingest.py` and `brain/ncc/2022/` by `tools/ncc_pdf_ingest.py`; never hand-edit them, re-run the ingest instead. Every NCC answer names its edition. NCC 2022 amendments live in `tools/ncc2022_amendments.yaml` and are applied by `tools/apply_ncc_amendments.py`; a new ABCB amendment is added there, not by editing pages. Search it with `tools/ncc_lookup.py`. Cite it as edition, volume and clause (for example "NCC 2022 Vol Two, H2D2") and link to ncc.abcb.gov.au. Both NCC 2022 and NCC 2025 can be in force; the edition that applies depends on when the permit application was lodged.
5. **Copyrighted material is referenced, never copied.** That means Australian Standards (AS/NZS), HIA, MBA and other standard-form contract text, and paid guides. Summarise the concept in your own words and point to the source.
6. **Money is computed, not guessed.** GST, variation prices, margins, progress claims and retention go through the Attested Computations in `brain/computations/`, run with `tools/compute.py`. Never do this arithmetic in your head.
7. **Generated documents are drafts.** Remind the user to check them against their actual contract, and to get legal advice on disputes.

## Skills

Every example in `examples/*_spec.yaml` names its template and must fill
cleanly: run `python tools/test_examples.py` after changing a template, a
spec or the fill tool.

Each skill in `skills/<name>/SKILL.md` reads from `brain/`, collects the
missing facts from the user, runs the computations, fills a template with
`tools/fill_template.py`, and lists anything left unfilled.
`skills/variations` is the reference pattern for every new skill.
Skills must work when installed as a plugin: write brain paths in commands as
`$ABB/tools/...` (the skill's "Where things are" section defines `$ABB`), run
from the user's project folder, and never write into the brain's folder.

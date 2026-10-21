# Submitting to the Claude plugin directory

Listing the brain in Anthropic's directory puts it in **Customize → Plugins →
Discover** for everyone on a Pro, Max, Team or Enterprise plan: builders find
it, click **Add**, and it updates itself. This page is the checklist and the
listing text. Submitting has to be done by the repository owner, from their
own claude.ai account.

## Before you submit

Run these from a clone (all should pass):

```bash
claude plugin validate .
```

```bash
python3 tools/okf_lint.py && python3 tools/test_start.py && python3 tools/test_projects.py && python3 tools/test_finance.py
```

What the directory checks, and where the brain stands:

| Check | Status |
|---|---|
| `.claude-plugin/plugin.json` at the repository root, name `australian-builders-brain` (lowercase, hyphens) | Pass |
| README of 40+ words that says what it does, how to use it and what it sends | Pass (README, "What it runs and sends") |
| Licence | Pass (`license` in plugin.json; LICENSE and LICENSE_CONTENT) |
| No secrets, no `.DS_Store`, no symlinks, no LFS, Windows-safe names | Pass |
| Repository under 50 MiB archived, under 10,000 files, every file under 5 MiB | Pass (about 13 MB, under 1,000 files) |
| No package launchers (npx, uvx), no custom package registries | Pass |
| Hook commands written from `${CLAUDE_PLUGIN_ROOT}` | Pass |
| Directory listing fields: icon, documentation, support and privacy links | Pass |

Expected **holds for a reviewer** (not rejections; a person reads the version before it goes live):

- **More than 512 files, and a few files over 256 KiB** (the NCC clause indexes and definitions): the NCC is large.
- **Binary files**: the Word and Excel templates, the PDF checklists, the sample invoice PDF and the README screenshots.
- **The session-start hook installs Python packages** (pinned exact versions from PyPI) into the plugin's data folder.

Say so in the submission notes so the reviewer knows why (text below).

## Submit

1. Open the developer portal at [claude.ai/directory/manage](https://claude.ai/directory/manage) and choose **Submit new**.
2. Choose **Plugin bundle**.
3. **Source:** `https://github.com/grechj/Australian-Builders-Brain`, branch `main`, plugin path left at the repository root.
4. Select **Validate** and fix anything marked **Blocking** (none expected). Push fixes, then **Re-validate**.
5. Fill in the listing with the text below and submit.

## Listing text

**Display name:** Australian Builder's Brain

**Short description:** Paperwork, money, materials and the building code for Australian builders and tradies: quotes, variations, claims, notices, SWMS, materials lists and prices, an inbox for invoices, Xero/MYOB/QuickBooks exports and plain-English NCC guides.

**Description:**

> Your paperwork, sorted. Tell Claude what happened on site and the Australian Builder's Brain writes the quote, variation, progress claim, payment claim, delay or breach notice, SWMS or handover document, from 64 Australian templates, with the money worked out by tested calculations. Drop supplier invoices, receipts and bank screenshots into a job's inbox and it reads them, checks the GST and totals, catches duplicates and files them against the job. Each job gets a dashboard: profit, margin, cash, costs against budget and time on site. It answers National Construction Code questions (NCC 2025 and 2022) in plain English with clause references for your trade and state, from guides whose every figure is checked against the code. Material guides cover treated timber, fixings, decking, linings, concrete, membranes, insulation, wraps and paint, and it works out materials lists for 14 kinds of job, priced from your own price list or Bunnings product pages. It checks ABNs and licences on the public registers, tracks your insurance expiry dates, learns which products you use, and exports to Xero, MYOB or QuickBooks. Say "set me up" to start: it asks your trade, state and business details and walks you through a practice job. Everything stays in your own folder; nothing is sent to this project.

**Category:** Business / Productivity (construction).

**Notes for the reviewer:**

> Open-source (MIT code, CC BY 4.0 content). Built for Australian builders and tradespeople. The plugin is large because it includes the National Construction Code (CC BY 4.0, from the Australian Building Codes Board) as searchable markdown, and 64 Word, Excel and PDF templates the skills fill in, plus a sample invoice PDF and screenshots for the README. The SessionStart hook (hooks/session_start.sh) creates a venv in CLAUDE_PLUGIN_DATA and pip-installs four pinned packages from PyPI (hooks/requirements_runtime.txt), then runs tools/start.py brief, which reads the user's jobs folder and prints a short briefing as additionalContext; it makes no network calls of its own and is silent in folders that aren't jobs folders. All tools are readable Python in tools/ and brain/references/. No telemetry: the materials log stays in the user's folder, and a usage summary is only shared if the user posts it themselves as a GitHub issue; see PRIVACY.md.

## After it's listed

- Update the README's install steps to "Customize → Plugins → Discover → Australian Builder's Brain → Add".
- Keep raising `version` in `.claude-plugin/plugin.json` with every release; the directory picks up new commits from `main` and scans each version.

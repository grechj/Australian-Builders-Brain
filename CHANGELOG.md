# Changelog

All notable changes to the Australian Builder's Brain. Versions follow the
plugin version in `.claude-plugin/plugin.json`.

## 0.15.1 (2026-10-21)

- Every link into the NCC now lands. 2,305 links pointed at anchors that didn't exist: clauses a state adds or replaces in NCC 2025 had no anchor (369 added), NCC 2022 state-only clauses were anchored `nsw_9_4_3` while links used `9_4_3` (396 now answer to both), and 70 links pointed at Part variations or tables the conversion can't anchor (they now point at the page). `tools/ncc_anchor_repair.py` does this as the last step of both ingests; the state pages are regenerated.
- The lint now checks every anchored link in the brain, NCC pages and state pages included. `tools/test_ncc_anchors.py` in CI.

## 0.15.0 (2026-10-21)

- **Plain-English code guides** (`brain/guides/code/`): decks, balconies and stairs; wet area waterproofing; termite management; bushfire construction; energy efficiency; smoke alarms; room heights; footings and slabs. Each cites the clauses in NCC 2022 and 2025 and flags state variations. Every figure a guide states is pinned in its `checks:` frontmatter to the NCC sentence it came from, and `okf_lint.py` fails if that sentence isn't on the page or a link into the NCC points at a clause that doesn't exist.
- **Material guides** (`brain/guides/materials/`): timber treatment and grades, fixings and corrosion, decking, plasterboard and linings, concrete, membranes and sealants, insulation, sarking and wraps, paint systems.
- `ncc_lookup.py guides "<question>" --trade <trade>` finds the right guide; `search` points to one when it matches; profiles list a trade's guides; the ncc and materials skills start from them.
- **Product catalogue** (`tools/catalogue.yaml`, page `brain/references/product_catalogue.md`): what materials are sold as (stock lengths, sheet and pack sizes, coverage), with no prices. Price matching now reads pack sizes off product names, converts per-metre prices to the stock length, and buys the cheapest mix of pack sizes.
- **New takeoff jobs:** cladding, insulation, retaining wall and pergola, with hand-checked tests.
- **Learning from use** (`tools/usage.py`): a materials log in the user's folder (products saved, used or bought on supplier bills; never prices), a report of what's used, new and rising and where the catalogue falls short, and an opt-in anonymous summary the user can post as a GitHub issue. Maintainer tools collect and sanitise shared summaries into `brain/references/product_usage.md`.
- Lint: skips `__pycache__`, and writes indexes for folders that only hold subfolders.

## 0.14.0 (2026-10-21)

- ABN and licence checks: setup offers to check the user's ABN on ABN Lookup and their licence on their state's public register, and records what they showed (`tools/start.py check`): entity name, ABN status, GST registration, licence class, status and expiry. A changed ABN or licence number shows as not checked again. Setup also flags an ABN that fails the checksum. A trade that doesn't need a licence in its state (carpenters in the ACT, for example) can be recorded as not required, and the brain stops asking for one.
- Insurance in the profile: public liability, home warranty, contract works and professional indemnity, with insurer, policy number, cover and expiry (`tools/start.py insurance`). Anything expiring within 30 days or expired (worked out by the expiry status computation) shows on the home page and in the session briefing.
- New brain page [checking ABNs, licences and insurance](brain/playbooks/checking_registers.md): ABN Lookup, each state's licence register, and certificates of currency. Every state page now links its licence register; the ACT page says which trades need a licence and the residential building work insurance rules.
- The projects skill offers an ABN check for a supplier or subbie it hasn't seen before; the contracts and safety skills check a subbie on the registers before filling the Subbie Insurance and Licence Tracker.
- PRIVACY.md and the README say when the brain looks up a public register.

## 0.13.3 (2026-10-17)

- "Things you can say" examples are now written for each common trade (builder, carpenter, electrician, plumber, tiler, painter, roofer, concreter, landscaper), neutral for the rest, with no sample job names. The home page's suggested prompts follow the trade too (trades invoice, builders claim).

## 0.13.2 (2026-10-17)

- Setup no longer settles for Cowork's temporary session workspace: when the session isn't in a folder the user chose, the start skill recommends a Cowork project on a real Jobs folder first, or sets up a clearly labelled trial.
- One question per message during setup, and trade-neutral examples in the welcome.

## 0.13.1 (2026-10-17)

- Add marketplace now works on claude.ai (confirmed in a browser after the 0.12.1 source change), so the README leads with it again: Customize, Plugins, Add marketplace, Discover, Add, Sync automatically. The release zip stays as the fallback.

## 0.13.0 (2026-10-17)

- Session-start welcome and briefing: the hook (`hooks/session_start.sh`) now also runs `tools/start.py brief`. In an empty or jobs-like folder it has Claude welcome a new user, offer setup once and show three things to ask; in a set-up jobs folder it opens with a short briefing (inbox, overdue invoices with amounts, bills due this week, missing profile details). It stays silent in code projects.
- Shortcuts in the `/` menu: `job`, `inbox`, `quote`, `variation`, `claim`, `invoice`, `dashboard`, `home`, `today` and `help` (`commands/`).
- The start skill runs once only, always shows the top six cards for the trade and the shortcuts, and finishes on the home page.
- Ready for the plugin directory: PRIVACY.md, a "What it runs and sends" README section, listing fields (icon, documentation, support and privacy links), pinned runtime packages (`hooks/requirements_runtime.txt`), and `docs/directory_submission.md` with the checklist and listing text.
- README install now uses the release zip and a Cowork project, while Add marketplace on claude.ai is investigated.

## 0.12.1 (2026-10-17)

- The marketplace entry now points at the repository's HTTPS address instead of the marketplace root (`./`), which claude.ai's Add marketplace refused with "Failed to add marketplace". Claude Code installs are unchanged.

## 0.12.0 (2026-10-17)

- No-terminal install: the README now leads with the Claude desktop app (Customize, Plugins, Add marketplace), which also works on claude.ai and carries the plugin into Cowork and Claude Code.
- New `start` skill ("set me up"): asks trade, state and business details once and saves them in `profile.yaml`, makes the jobs folder (register, account mapping, inbox), runs a practice job with the sample invoice and bank screenshot in a separate `demo/` folder, and shows "things you can say" cards for the user's trade (`tools/start_cards.yaml`). `tools/start.py` (status, setup, demo, cards).
- New home page (`tools/home.py`, `home.html` in the jobs folder): profile, what's waiting in the inbox, every job's position (contract, received, outstanding, profit, margin against target, forecast, invoiced and time meters) with its latest documents, links to the dashboard (which opens on the chosen job) and extracts, and the trade's cards with copy buttons. Offline, light and dark, phone-friendly.
- New jobs copy the business details, state and trade from `profile.yaml`. A register entry can take its job number from its project file or ledger.
- `tools/test_start.py` in CI.
- The README is now a one-page quick start with screenshots of the home page, the dashboard and a generated document (`docs/images/`); the detail moved to [docs/guide.md](docs/guide.md).

## 0.11.0 (2026-10-17)

- New `projects` skill and `tools/projects.py`: a project register (`projects.yaml`) with job numbers, names, tags and status; a standard folder per job (`project.yaml`, `ledger.yaml`, `timesheets.csv`, `inbox/`, `processed/`, `out/`); and an inbox for screenshots, photos and PDFs. Files are matched to a project by folder, name, tag or the text inside them; invoices are read into checked ledger entries (arithmetic and GST through the sanctioned maths, ABN checksum, tax invoice rules, duplicates across every project) and payments from bank screenshots into a payments log, only after the user confirms; originals are filed in `processed/` and linked from the ledger and the dashboard.
- The dashboard reads project folders, lists received documents alongside generated ones, and links each transaction to its source document. Projects without a start date are listed as skipped.
- `examples/jobs_example.yaml` is now `examples/projects_example.yaml` (the `jobs:` key still works). Sample invoice PDF and bank screenshot in `examples/inbox/`.
- The plugin's Python setup now includes pdfplumber, for reading typed PDF invoices.

## 0.10.0 (2026-10-17)

- The dashboard lists every document generated for each job (typed by template, numbered from the file name) with links to the files, or to the same folder in Dropbox, Google Drive or SharePoint (`documents_url`); `documents.csv` is the register.
- Modelling extracts: `transactions.csv` (paid, outstanding, days to settle, days overdue, financial year and quarter), `transaction_lines.csv` (every line and timesheet cost with role and account code), `cost_mix.csv` (cost per category as % of revenue by project type), and forecast profit at completion in `jobs.csv` and on the dashboard.
- Manual import files for all jobs at once: `imports/<software>/` (Xero, MYOB, QuickBooks), tracked by job, with `--since` for only what's new.

## 0.9.0 (2026-10-17)

- Project dashboard and financial extracts: `tools/dashboard.py` reads a portfolio of jobs (ledger, timesheets, budget) and writes `jobs.csv`, `monthly.csv`, `costs.csv` and `benchmarks.csv`, plus a self-contained dashboard page (P&L and margin against target, receipts and outstanding, costs against budget, cash by month, time on site, job length against the contract and the average of completed jobs). Works offline, in light and dark mode, on a phone.
- New attested computation [job dashboard](brain/computations/job_dashboard.md), with an as-at cut-off.
- Example portfolio of three jobs with ledgers and timesheets; hand-checked dashboard tests in CI.

## 0.8.1 (2026-10-17)

- The plugin and marketplace are now `australian-builders-brain`, as Claude.ai's marketplace sync requires; skills are `australian-builders-brain:<skill>`. File and folder names keep underscores. Reinstall: `claude plugin marketplace add grechj/Australian-Builders-Brain` then `claude plugin install australian-builders-brain`.

## 0.8.0 (2026-10-17)

- New `accounts` skill: a per-job ledger of invoices, credit notes, bills, supplier credits and payments; a per-user account mapping; import files for Xero (checked against Xero's import help), MYOB AccountRight and QuickBooks Online (draft formats, in `tools/finance_formats.yaml`); a payload for creating drafts through the user's own Xero, MYOB or QuickBooks connector, only after they approve.
- New attested computations: [BAS summary](brain/computations/bas_summary.md) (G1 to G4, G10, G11, 1A, 1B on a cash or accrual basis) and [TPAR summary](brain/computations/tpar_summary.md) (contractor payments per ABN for the financial year).
- New brain page `contracts/accounts_and_tax.md`: GST timing, deposits, retention methods, BAS, TPAR, connectors, and where to go for deeper tax questions (OpenAccountants, referenced not copied).
- `tools/finance.py` (check, export, payload, bas, tpar) with hand-checked tests in CI (`tools/test_finance.py`).
- Every trade profile now lists the accounts skill. README: plugin users need no clone or pip install; one-step install line.

## 0.7.0 (2026-10-17)

- 11 new templates (64 in all): Payment Claim and Payment Schedule under the security of payment acts, a trade Tax Invoice, Trade Quote, Request for Information, Meeting Minutes, Suspension, Breach and Termination notices, a Construction Program (linked working-day dates and a bar chart) and Timesheets and Day Work Dockets.
- New brain page `contracts/security_of_payment.md`: each state's Act, home owner coverage, claim wording and payment schedule deadlines (draft, with sources). Corrects the progress payments page: NSW and WA do cover home owners.
- New fields `[SOPA_ACT]`, `[CLAIM_REF]`, `[RFI_NUMBER]`, `[MEETING_NUMBER]`; `sopa_act` in the project file.
- The claims, notices, site and estimating skills use the new templates; 11 new examples (42 in all).
- `tools/build_templates.py` builds the new templates in the pack's house style; the fill tool stores HH:MM as an Excel time.

## 0.6.1 (2026-10-17)

- Skills work when installed as a plugin: they find the brain at the plugin's folder, run from the user's own project folder, and never write into the plugin.
- A SessionStart hook builds a Python environment for the tools in the plugin's data folder, and rebuilds it only when `requirements.txt` changes.
- `LICENSE` is the standard MIT text, so GitHub recognises it; the scope note (MIT for code, CC BY 4.0 for everything else) is in the README.
- Plugin manifest: display name, version, homepage and licence.
- Added this changelog.

## 0.6.0 (2026-10-17)

- NCC 2022 loaded from the ABCB PDFs, with Amendments 1 and 2 merged as notices under the clauses they change; profiles and lookups take `--edition`.
- Trade and location profiles: 22 trades plus `builder`/`all`, 8 states and territories, each filtering the NCC, skills, takeoffs, materials and suppliers.
- Materials skill: takeoffs (deck, framing, electrical, plumbing, roofing and more), per-user price lists, an optional Bunnings API client with the user's own keys, and a rough order of magnitude estimate.
- Retired BEAM branding removed; templates documented as references for your own documents.

## 0.5.0 (2026-10-16)

- Ten document skills covering all templates: variations, claims, notices, handover, estimating, contracts, site, safety and financials, plus the ncc skill.
- NCC 2025 (v1.2) loaded from the ABCB XML.
- Template formula fixes: Setup references, final account retention, rain days, budget variance, quote acceptance fields, markup labels.
- CI: OKF lint plus example, profile, price list and takeoff tests on every push.

## 0.1.0 (2026-10-16)

- Scaffold: OKF v0.2 brain, lifecycle and phase pages, templates, fill tool, MIT and CC BY 4.0 licences.

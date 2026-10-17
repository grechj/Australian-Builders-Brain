# Australian Builder's Brain

**Your paperwork, sorted.** A free set of Claude skills for Australian builders and tradies. Tell it what happened on site and it writes the quote, variation, claim, notice or SWMS. Drop in a supplier invoice and it reads it, checks it and files it against the job. It knows the National Construction Code for your state.

![The home page: your jobs, what's in the inbox and what to ask](docs/images/home.png)

## What it does

- **Jobs and paperwork.** A folder for each job. Drop in invoices, receipts, dockets and photos, and it reads them, checks the numbers and files them.
- **Documents in a sentence.** 64 ready-made templates: quotes, variations, progress claims, payment claims and schedules, delay and breach notices, SWMS, site diary, handover and more.
- **Money.** Job profit and margin, cash in and out, costs against budget, and import files for Xero, MYOB or QuickBooks. BAS and TPAR figures too.
- **The building code.** NCC 2025 and 2022 answers with the clause, filtered to your trade and state.
- **Made for your trade.** Builders see everything; a sparky, plumber or tiler sees what matters to them.

## Get started (5 minutes, no terminal)

You need the [Claude desktop app](https://claude.ai/download) and a Claude Pro or Max plan.

1. Download **australian-builders-brain.zip** from the [latest release](https://github.com/grechj/Australian-Builders-Brain/releases/latest).
2. In Claude, go to **Customize → Plugins → Add → Upload plugin** and choose the zip.
3. Open **Cowork**, then **Projects → +**. Choose **Start from scratch** and call it `Jobs` (or **Use an existing folder**, for example one in Dropbox, Google Drive or OneDrive so you can add photos from your phone).
4. Click the project to start a session. The brain says hello and offers to set you up.
5. Say **"set me up"**. It asks your trade, state and business details, walks you through a practice job and shows you what to ask.

To update, download the new zip and upload it again. (A listing in Claude's plugin directory, with one-click install and automatic updates, is on the way.)

Using Claude Code in a terminal? `claude plugin install australian-builders-brain --marketplace grechj/Australian-Builders-Brain`

## What it looks like

A dashboard for every job: profit, margin, cash, costs against budget, time on site, and every document.

![A job's dashboard](docs/images/dashboard.png)

Documents come out filled in from one sentence, with the money worked out and checked:

<img src="docs/images/variation_notice.png" alt="A priced variation notice, filled in" width="520">

## Good to know

- **Your files stay yours.** Everything lives in your own folder. No accounts, no keys, nothing stored by this project.
- **Money is checked, not guessed.** GST, claims, variations, BAS and TPAR come from tested calculations, with a receipt you can verify.
- **You approve everything.** Nothing goes into your books or out the door until you say yes.
- **Drafts, not legal advice.** Check documents against your contract, and get advice on disputes.

## What it runs and sends

- **On your computer:** at the start of a session it sets up a private Python environment (four open-source packages from PyPI, pinned in `hooks/requirements_runtime.txt`) and reads your jobs folder to brief Claude on what's waiting. When you ask for a document or figures, its Python tools read and write files in your folder.
- **Nothing to this project:** no accounts, servers, tracking or data collection.
- **Only when you ask:** drafts to your own Xero, MYOB or QuickBooks (after you approve each one), and Bunnings price lookups with your own API keys or public product pages.

The details are in [PRIVACY.md](PRIVACY.md).

## Shortcuts

Type `/` in Claude to see them: `job`, `inbox`, `quote`, `variation`, `claim`, `invoice`, `dashboard`, `home`, `today` and `help` (each starts `australian-builders-brain:`).

## Learn more

- [The full guide](docs/guide.md): every skill, template and tool, profiles, pricing, the inbox, accounts and the dashboard
- [Changelog](CHANGELOG.md) · [Contributing](AGENTS.md) (builders who check a draft page against the source make the biggest difference)

## Licence

- **Content, skills and templates** (`brain/` pages, `skills/`, `templates/`, `examples/`, docs): [CC BY 4.0](LICENSE_CONTENT). Use, adapt and share them, including commercially, as long as you credit "Australian Builder's Brain by Joshua Grech".
- **Code** (`tools/`, the Python in `brain/references/`): [MIT](LICENSE). The MIT licence covers only this code; everything else is CC BY 4.0.

NCC content: © Commonwealth of Australia and the States and Territories of
Australia, published by the Australian Building Codes Board, licensed under
[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). The National
Construction Code 2022 was provided by the Australian Building Codes Board under
the CC BY 4.0 licence.
Templates by Joshua Grech.

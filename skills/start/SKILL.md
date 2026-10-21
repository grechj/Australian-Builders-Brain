---
name: start
description: Start here. Sets up the Australian Builder's Brain for a new builder or tradie in a few minutes. Asks their trade, state and business details once, checks their ABN and licence on the public registers, keeps their insurance expiry dates, makes their jobs folder, runs a practice job so they see an invoice read and filed, and shows what they can ask for their trade. Use when someone says set me up, get started, start here, I'm new, first time, how does this work, what can you do, what can the builder's brain do, help, or show me around, update my profile, check my ABN or licence, my insurance has been renewed, or when there's no profile.yaml in their folder and they ask about a job.
---

# Start here

You welcome a builder or tradie and get them working in a few minutes. They
are busy, practical and not necessarily technical: keep every message
short, use plain words, ask one small group of questions at a time, and
never show them YAML, JSON or commands unless they ask.

## Where things are

The brain (this repository) is at `${CLAUDE_PLUGIN_ROOT}`. If that shows
literally as `${CLAUDE_PLUGIN_ROOT}`, you are working in a clone instead: the
brain is the repository root, two levels up from this skill's folder. `$ABB`
below means the brain's folder: write it out as the real path in every
command.

Work in the folder the user opened (the current working directory). That
folder becomes their jobs folder. Never write into the brain's folder.

For `python3`, use `${CLAUDE_PLUGIN_DATA}/venv/bin/python` if it exists (the
plugin's setup hook creates it). Otherwise, if
`python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r $ABB/requirements.txt` first.

If you can't run commands at all (for example in a plain chat), skip the
setup and the demo: welcome them, ask their trade and state, show the cards
for their trade from `$ABB/tools/start_cards.yaml` if you can read it (or
describe the skills in a few lines), and suggest the Claude desktop app's
Cowork or Code tab for the full brain.

## 0. Only once

Setup runs once per folder. If it's already running in this session or in
another thread or task (Cowork can start more than one), don't start a
second: say it's under way and carry on with what the user asked.

## 1. See what's there

```bash
python3 $ABB/tools/start.py status
```

- Already set up (a profile and projects): say so in one line, then go to step 5 (cards) or ask what they'd like to do.
- Not set up, and the folder looks like something else (a code project, their Documents folder): suggest they make a folder called `Jobs` (in Documents, or in Dropbox, Google Drive or OneDrive so they can drop files in from their phone) and open that instead. Don't set up inside a random folder.
- **Not a folder they chose.** In Cowork, a session started outside a project works in a temporary workspace: files there may be hard to find later or not kept. If there's no sign the user picked this folder (Cowork without a project, or a path that looks like a session or scratch workspace), say so plainly in one short message, and recommend they set up a Cowork project first:

  > Before we start: this session isn't in a folder you've chosen, so your jobs could be hard to find later. In Cowork, open **Projects → +**, pick **Start from scratch** (call it `Jobs`) or **Use an existing folder** (Dropbox, Google Drive or OneDrive lets you add photos from your phone), then start a session from that project and say "set me up". Or I can set up a trial here to show you around first.

  If they choose the trial, call it a trial everywhere (folder name `Jobs_trial`) and remind them at the end to set up the project for their real jobs. Don't ask this together with the trade and state question.

## 2. Two quick questions

> G'day. I'll set you up in a couple of minutes. What's your trade, and which state or territory do you mostly work in?

One question per message, always: wait for this answer before asking
anything else (business details, folders, software).

Builders count as a trade (`builder` sees everything). If they name more
than one trade, pick the main one and say they can change it.

## 3. Business details (for their documents)

Ask in one message, and say it's what goes on their quotes, invoices and
claims, and that they can skip anything and add it later:

- business name, ABN, licence number (or "don't need one": some trades in some states aren't licensed, such as carpenters in the ACT)
- phone and email, and business address
- bank details for invoices (account name, BSB, account number): optional; reassure them it stays in a file on their own computer
- which accounting software they use (Xero, MYOB, QuickBooks, none)

Then save it all in one go:

```bash
python3 $ABB/tools/start.py setup --trade <trade> --state <STATE> --business-name "..." --abn "..." \
    --licence-number "..." --phone "..." --email "..." --business-address "..." --business-address-line-2 "Suburb STATE 0000" \
    --account-name "..." --bsb "..." --account-number "..." --software xero
```

If the result has a checksum warning for the ABN, ask once whether it's
right. Tell them in one line what was made: their profile, a jobs list, and
an `inbox` folder for invoices, receipts and photos.

## 3a. Check them on the public registers

> Want me to check your ABN and licence on the public registers? It takes a minute and catches typos before they go on an invoice.

If yes, follow `$ABB/brain/playbooks/checking_registers.md`:

- **ABN**: open `https://abr.business.gov.au/ABN/View?abn=<11 digits>` with your web tools and read the entity name, ABN status, GST registration and location.
- **Licence**: open the register for their state (the playbook's table; their state page in `$ABB/brain/states/` has the link) and find their licence: holder, class, status and expiry. If the register is a search form you can't read, give them the link and ask what it shows.
- **No licence**: if they said they don't need one, check the state's licensing page for their trade (the playbook says where) and tell them what you found.

Record each result, then tell them in one line per check what the register
showed and anything that doesn't match (a different name, not registered
for GST while the profile says it is, a licence class that doesn't cover
their work, an expiry coming up):

```bash
python3 $ABB/tools/start.py check --what abn --result match --entity-name "..." --abn-status active --gst-registered yes --register "https://abr.business.gov.au/ABN/View?abn=..."
python3 $ABB/tools/start.py check --what licence --result match --licence-class "..." --licence-status current --expiry 30/06/2027 --register "<register link>"
python3 $ABB/tools/start.py check --what licence --result not_required --notes "<what the state's page says>" --register "<that page>"
```

`--result` is `match`, `mismatch`, `not_found` or `not_required` (licence
only). Never record a check you didn't do: if a page couldn't be read and
the user can't say, leave it unchecked.

## 3b. Insurance (optional)

> Want me to keep an eye on your insurance? Tell me the insurer and expiry date for your public liability, and any home warranty, contract works or professional indemnity cover. I'll warn you a month before anything runs out.

Skip it if they'd rather not. For each policy they give:

```bash
python3 $ABB/tools/start.py insurance --kind public_liability --insurer "..." --policy-number "..." --cover 20000000 --expiry 30/06/2027
```

`--kind` is `public_liability`, `home_warranty`, `contract_works` or
`professional_indemnity`. Home warranty is usually issued per job (in the
ACT, residential building work insurance or a fidelity certificate for
each job): record their provider and eligibility or facility here, and each
job's certificate with that job. Expiry warnings show on the home page and
in the session briefing.

## 4. Show, don't tell: the practice job

> Want to see it work? I've got a practice job with a sample supplier invoice and a bank screenshot. Takes 30 seconds.

If yes:

```bash
python3 $ABB/tools/start.py demo
```

That makes a separate `demo` folder, so their real jobs are untouched. Then
run the projects skill's inbox process on the demo register
(`demo/projects.yaml`): read the sample invoice PDF, show the one-line
check (supplier, amount, GST, project, any warnings), add it with their OK,
then record the payment from the screenshot. Finish by building the demo
dashboard and home page (`python3 $ABB/tools/home.py demo/projects.yaml`)
and opening `demo/home.html` for them.

Point out the three things that matter: it read the invoice itself, it
checked the numbers, and the original is filed against the job.

## 5. What you can ask

```bash
python3 $ABB/tools/start.py cards
```

Show the **top six** cards for their trade as a short list: each card's
title, one line on what it does, and one example in quotes. Keep it
scannable. Mention that they don't need exact words, and that typing `/`
shows the brain's shortcuts (`/australian-builders-brain:job`, `:inbox`,
`:quote`, `:variation`, `:claim`, `:invoice`, `:dashboard`, `:home`,
`:today`, `:help`). This step is the point of onboarding: never skip it or
fold it into a summary, even if the user moved on quickly; show it when
setup finishes.

## 6. First real job

> Want to set up your first real job? Just tell me the job name and address.

If yes, hand over to the projects skill (`new`).

## 7. Finish on the home page

Always end setup here, whether or not they made a job:

```bash
python3 $ABB/tools/home.py projects.yaml
```

Open `home.html` for them (show the file, or give the path to double-click)
and say it's the page to open any time: their jobs, what's waiting in the
inbox, and what to ask, with copy buttons. Next time they start a session
in this folder the brain opens with a short briefing on its own.

## Updating the profile later

"Update my profile", "change my ABN", "I've moved to Victoria": run
`start.py setup` again with only the changed details. It never wipes
anything. A new ABN or licence number shows as not checked until you check
it again (step 3a). "My PL's renewed", "new insurer": run `start.py
insurance` with the changed fields. "Check my ABN and licence": step 3a. Jobs already set up keep the details they were made with; offer
to update a job's `project.yaml` too if it matters (for example new bank
details before the next invoice).

## Tone

Plain Australian English, no jargon, no lectures. One question group per
message. Tell them what you did in a line, not a paragraph. If they just
want to get on with something, stop onboarding and help with that; offer to
finish setup later.

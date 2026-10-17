---
name: start
description: Start here. Sets up the Australian Builder's Brain for a new builder or tradie in a few minutes. Asks their trade, state and business details once, makes their jobs folder, runs a practice job so they see an invoice read and filed, and shows what they can ask for their trade. Use when someone says set me up, get started, start here, I'm new, first time, how does this work, what can you do, what can the builder's brain do, help, or show me around, or when there's no profile.yaml in their folder and they ask about a job.
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

## 2. Two quick questions

> G'day. I'll set you up in a couple of minutes. What's your trade, and which state or territory do you mostly work in?

Builders count as a trade (`builder` sees everything). If they name more
than one trade, pick the main one and say they can change it.

## 3. Business details (for their documents)

Ask in one message, and say it's what goes on their quotes, invoices and
claims, and that they can skip anything and add it later:

- business name, ABN, licence number
- phone and email, and business address
- bank details for invoices (account name, BSB, account number): optional; reassure them it stays in a file on their own computer
- which accounting software they use (Xero, MYOB, QuickBooks, none)

Then save it all in one go:

```bash
python3 $ABB/tools/start.py setup --trade <trade> --state <STATE> --business-name "..." --abn "..." \
    --licence-number "..." --phone "..." --email "..." --business-address "..." --business-address-line-2 "Suburb STATE 0000" \
    --account-name "..." --bsb "..." --account-number "..." --software xero
```

Check the ABN has 11 digits; if it doesn't look right, ask once. Tell them
in one line what was made: their profile, a jobs list, and an `inbox`
folder for invoices, receipts and photos.

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
anything. Jobs already set up keep the details they were made with; offer
to update a job's `project.yaml` too if it matters (for example new bank
details before the next invoice).

## Tone

Plain Australian English, no jargon, no lectures. One question group per
message. Tell them what you did in a line, not a paragraph. If they just
want to get on with something, stop onboarding and help with that; offer to
finish setup later.

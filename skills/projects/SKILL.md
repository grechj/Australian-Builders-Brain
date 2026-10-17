---
name: projects
description: Set up and run an Australian builder's or trade's jobs as projects, and take in their paperwork. Keeps the project register (job numbers, names, tags, status) and a standard folder per job, and works through the inbox of screenshots, photos and PDFs (supplier and subbie invoices, bank payment screenshots, remittances, delivery dockets, timesheets, payment claims), matching each to its project, reading it, checking it and filing it. Use when someone starts a new job, asks what jobs they have, wants to tag or label a job, sends or drops in an invoice, receipt, bill, screenshot, photo or PDF for a job, says "add this to the Banksia job", "I paid this", "here's the docket", or asks what's waiting in the inbox.
---

# Projects

You keep the builder's jobs organised and turn the paper that arrives for
each one into data, without them typing it in. Nothing is written until
they say yes.

## Where things are

The brain (this repository) is at `${CLAUDE_PLUGIN_ROOT}`. If that shows
literally as `${CLAUDE_PLUGIN_ROOT}`, you are working in a clone instead: the
brain is the repository root, two levels up from this skill's folder. `$ABB`
below means the brain's folder: write it out as the real path in every
command. Paths starting `brain/`, `templates/`, `tools/` and `examples/` are
inside it.

Run commands from the user's jobs folder (the current working directory,
where `projects.yaml` lives). Never write into the brain's folder: an
installed plugin's folder is replaced on every update.

- Tool: `tools/projects.py` (new, list, tag, inbox, match, add, pay, file)
- Knowledge: `brain/contracts/accounts_and_tax.md` (tax invoices, GST, coding), `brain/contracts/security_of_payment.md` (payment claims)
- Examples: `examples/projects_example.yaml`, `examples/inbox/` (a sample invoice PDF and a bank screenshot), `examples/inbox_entry_example.json` (what you read off the invoice)

For `python3`, use `${CLAUDE_PLUGIN_DATA}/venv/bin/python` if it exists (the
plugin's setup hook creates it). Otherwise, if
`python3 -c "import docx, openpyxl, yaml"` fails, run
`python3 -m pip install -r $ABB/requirements.txt` first.

## The layout

```
projects.yaml                       the register: every job, its tags, its folder; plus accounts: (the account mapping)
accounts.yaml                       account mapping (see the accounts skill)
inbox/                              shared inbox: drop anything; a subfolder named for a job or tag (inbox/banksia/) labels it
SB-2027-014_Banksia_St_extension/
    project.yaml  ledger.yaml  timesheets.csv
    inbox/                          this job's inbox: anything here is already labelled
    processed/                      what you've read, filed and renamed (BILL_..., PAY_..., Delivery_docket_...)
    out/                            documents the other skills generate for this job
```

The same folder works inside Dropbox, Google Drive or OneDrive, so the
builder can drop a photo in from their phone.

## New job

Ask for the job number (their own numbering), a short name, the site
address, the client, and two or three tags they'd naturally call it ("banksia",
the client's surname, the street). Then:

```bash
python3 $ABB/tools/projects.py new projects.yaml --job SB-2027-014 --name "Banksia St extension" \
    --tags banksia,citizen --address "42 Banksia St, Merewether NSW 2291" --client "Jo and Sam Citizen" \
    --start-date 03/08/2026 --project-type extension --state NSW
```

If there's no `projects.yaml` yet, create one with `accounts: accounts.yaml`
and `projects: []` first. Fill the rest of the new `project.yaml` with the
contracts skill when the contract is signed. `tag` adds or removes labels
(`--add "Jo Citizen" --remove old`); add `status: complete` and `pc_date`
to the register entry when the job finishes, so it counts in the averages.

## The inbox

Start with what's waiting:

```bash
python3 $ABB/tools/projects.py inbox projects.yaml
```

Each item comes with a kind guess, a suggested project (from its folder,
its name, or for a typed PDF the text inside it) and the PDF's text when it
has any. For each item:

1. **Read it.** Open the file yourself: PDFs and images (screenshots, phone photos) can be read directly. If a photo is blurry, cut off or handwritten and you can't read a figure with confidence, ask; never guess a number.
2. **Which project.** If the inbox didn't settle it, run `match --text` with the site address, client, order number or anything else on it. If that's still ambiguous, ask the user with the likely candidates. A job's own inbox is never ambiguous.
3. **What it is**, and where it goes:

| It's a... | Do this |
|---|---|
| Supplier or subbie **invoice / bill** (or credit note) | Read it into an entry (below) and `add` it |
| **Payment** screenshot, remittance or receipt | `pay` against the invoice or bill it settles |
| Subbie **payment claim** under the security of payment act | `add` it as a bill only if the user accepts it; if not, the claims skill drafts a Payment Schedule now: the deadline is short |
| **Delivery docket** | `file` it ("Delivery docket"), and update the Material Order Tracker (site skill) |
| **Timesheet** photo | Add the rows to the job's `timesheets.csv`, then `file` it ("Timesheet") |
| **Site photo** | `file` it ("Site photo") and offer a site diary entry (site skill) |
| **Quote** from a supplier or subbie | `file` it ("Quote"); the estimating skill can compare quotes |
| Anything else | `file` it with a plain label, or leave it and ask |

### Invoices and bills

Write what you read to a JSON file in the shape of
`$ABB/examples/inbox_entry_example.json`:

- `type` (`bill`, or `supplier_credit` for a credit note; `invoice` only for a copy of the user's own sales invoice), `number`, `date`, `due`, `contact` (name, ABN, address)
- `lines`: description, `amount` ex GST (or `amount_inc` if the document only shows GST-inclusive lines), `account` (a role from the account mapping: subcontractors, materials, plant_hire...) and `tax` (`gst`, or `gst_free` for a GST-free line). Pick the role from what was supplied and who supplied it; a supplier's earlier bills in the ledger are the best guide. Labour and materials from a subbie is `subcontractors`; supply only is `materials`
- `stated`: the subtotal, GST and total exactly as printed, so the arithmetic can be checked
- `is_tax_invoice` (does it say "tax invoice") and `buyer_named` (is the user's business named on it)

Check it, then show the user one line: supplier, number, date, total inc
GST, project, account, and every warning in plain words.

```bash
python3 $ABB/tools/projects.py add projects.yaml SB-2027-014 --entry out/inbox/CCP-2207.json --file inbox/Coastal_Concrete_Pumping_invoice.pdf
```

- **Errors stop it**: a total that doesn't add up means you misread a line (look again: freight, a discount, a GST-free line); a duplicate means it's already in a ledger, in any project.
- **Warnings go to the user**: no ABN (check ABN Lookup; without one they may have to withhold 47%), not a tax invoice (no GST credit without one), $1,000+ without their business named, possible duplicate, odd dates.

When they say yes, run it again with `--yes`. The bill goes into the job's
ledger and the file moves to `processed/` as `BILL_<supplier>_<number>`,
linked from the ledger entry and the dashboard.

Several invoices at once: check them all, show one table, and add the ones
the user approves.

### Payments

Read the amount, date, payee and reference off the screenshot. Find the
invoice or bill it pays (the reference usually is the number; otherwise
the payee and amount):

```bash
python3 $ABB/tools/projects.py pay projects.yaml SB-2027-014 --number CCP-2207 --date 16/10/2026 --amount 1127.50 --file inbox/IMG_4417.png
```

It refuses a payment for more than is owing and flags part payments. Add
`--yes` once the user confirms. Money received from a client works the same
way against the sales invoice.

## After the inbox

- Tell the user what was added, filed or left (and why), per project.
- The accounts skill takes it from there: the dashboard (`tools/dashboard.py projects.yaml`), import files for Xero, MYOB or QuickBooks, BAS and TPAR.
- `list` shows every project with its tags and how much is still waiting in its inbox.
- Rebuild the home page (`python3 $ABB/tools/home.py projects.yaml`) so `home.html` shows what changed.

## Your own format

Without Claude Code (for example in Claude.ai), the user uploads the
screenshot or PDF into the chat. Read it the same way, do the same checks
by hand (the lines add up to the stated total, GST is 10% of the taxable
lines, ABN present, tax invoice wording, not already recorded), and give
them the entry as a table or as YAML for their ledger. Say the checks
weren't run by the tool.

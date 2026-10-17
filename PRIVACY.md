# Privacy

The Australian Builder's Brain is a set of instructions, templates and small
programs that run inside Claude on your own account. This project has no
servers, no accounts and no analytics. It collects nothing about you and
receives nothing from you.

## Where your information lives

Everything you give it (your business details, jobs, invoices, receipts,
photos, timesheets and the documents it writes) is saved as ordinary files in
the folder you choose, on your computer or in your own Dropbox, Google Drive
or OneDrive. Delete the folder and it's gone. Bank details you add for your
invoices stay in `profile.yaml` in that folder.

What you type and the files Claude reads are handled by Claude under
[Anthropic's privacy policy](https://www.anthropic.com/legal/privacy), the
same as any other conversation with Claude.

## What it runs on your computer

- **At the start of each session**, a setup step creates a private Python environment in the plugin's own data folder and installs four open-source packages from the Python Package Index (python-docx, openpyxl, PyYAML and pdfplumber, at the exact versions in `hooks/requirements_runtime.txt`). It only installs them again when those versions change. It then reads the jobs folder you opened to give Claude a short briefing (what's in your inbox, what's overdue). It sends nothing anywhere.
- **When you ask for something**, Claude runs the brain's Python tools on the files in your folder: filling Word and Excel templates, working out GST and claims, reading invoice PDFs, building your home page and dashboard. These run on your computer and only read and write your folder.

## What it can send, only when you ask

- **Xero, MYOB or QuickBooks:** if you connect your own accounting software to Claude and ask the brain to send invoices or bills, it creates drafts in your account after you approve each one. You can also export import files instead and upload them yourself.
- **Bunnings prices:** if you have your own Bunnings developer API keys and set them on your computer, the materials skill uses them to look up prices. Otherwise Claude may open public Bunnings product pages you ask about. Nothing is stored except in your own price list file.
- **Building code links:** answers cite the NCC and link to ncc.abcb.gov.au; the code text itself is included in the plugin, so lookups don't go online.

## Contact

Questions or concerns: open an issue at
[github.com/grechj/Australian-Builders-Brain/issues](https://github.com/grechj/Australian-Builders-Brain/issues).

# Shared usage reports

Each file here is one usage summary a Builder's Brain user chose to share
by posting it as a GitHub issue (label `usage-report`). They hold product
names and counts by family, the user's trade and state, and nothing else:
no prices, jobs, clients, addresses or store names.

The maintainer saves them with `python tools/usage.py collect` (reads the
issues with the gh CLI, keeps only the summary fields) and rebuilds
`brain/references/product_usage.md` with
`python tools/usage.py ingest raw/usage_reports/*.json`. Review new reports
before committing them. Never edit a report; add new ones.

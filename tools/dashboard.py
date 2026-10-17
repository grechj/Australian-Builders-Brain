"""Financial extracts (CSV) and a project dashboard for every job.

Usage:
    python tools/dashboard.py jobs.yaml --out out/dashboard [--as-at 31/10/2026] [--since 01/10/2026]

jobs.yaml (examples/jobs_example.yaml) lists each job with its project file,
ledger (see tools/finance.py), optional timesheets and budget. This runs the
job_dashboard computation and writes, into --out:

    jobs.csv          one row per job: contract, revenue, costs, profit, margin,
                      receipts, outstanding, labour, days on site, job length vs average
    monthly.csv       per job and month: revenue, costs, receipts, payments, cumulative profit
    costs.csv         per job and cost category: actual, budget, forecast final, % of revenue
    benchmarks.csv    averages across completed jobs, overall and by project type
    cost_mix.csv      average cost per category as % of revenue, by project type (for pricing new work)
    transactions.csv  every invoice, credit note, bill and supplier credit: totals, paid,
                      outstanding, days to settle, days overdue, month, financial year, quarter
    transaction_lines.csv  every line (and timesheet cost) with role, kind and amounts, for pivot tables
    documents.csv     every document generated for each job, with links
    imports/<software>/   Xero, MYOB or QuickBooks import files for all jobs (--since limits them)
    receipt.json      the computation receipt (check it with check_receipt.py)
    dashboard.html    a self-contained dashboard (open it in any browser, no internet needed)

Each job's `documents` folder (and an optional `documents_url`, such as the
same folder in Dropbox, Google Drive or SharePoint) is scanned for the
documents the skills have generated, so the dashboard can link to them.

The CSVs open in Excel, Google Sheets, Power BI or Looker Studio, and are
what a web app would read. Timesheets are a CSV (date, worker, role, hours,
rate_ex_gst) or the Timesheet and Docket workbook.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import sys
from urllib.parse import quote
from datetime import date, datetime, time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import compute  # noqa: E402
import finance  # noqa: E402

PROJECT_KEYS = {"contract_number": "job", "project_name": "name", "project_type": "project_type", "state": "state",
                "contract_sum_ex_gst": "contract_sum_ex_gst", "start_date": "start_date", "end_date": "contract_end_date"}


def flat(path: Path) -> dict:
    data = yaml.load(path.read_text(), Loader=yaml.BaseLoader) or {}
    out = {}
    for section in data.values():
        if isinstance(section, dict):
            out.update(section)
    return out


def ddmmyyyy(value) -> str:
    if isinstance(value, (datetime, date)):
        return value.strftime("%d/%m/%Y")
    return str(value)


def read_timesheets(path: Path) -> list[dict]:
    if path.suffix.lower() == ".csv":
        with path.open(newline="") as f:
            return [{"date": r["date"], "hours": r["hours"], "rate": r.get("rate_ex_gst") or r.get("rate") or "0",
                     **({"cost": r["cost_ex_gst"]} if r.get("cost_ex_gst") else {})}
                    for r in csv.DictReader(f) if r.get("date")]
    import openpyxl  # the Timesheet and Docket workbook: read the inputs, not the formulas

    wb = openpyxl.load_workbook(path)
    default_rate = wb["Setup"]["B8"].value or 0
    rows = []
    for r in wb["Dockets"].iter_rows(min_row=5, values_only=True):
        when, start, finish, brk, rate = r[0], r[4], r[5], r[6] or 0, r[8]
        if not (when and isinstance(start, time) and isinstance(finish, time)):
            continue
        minutes = (finish.hour * 60 + finish.minute) - (start.hour * 60 + start.minute)
        minutes = (minutes % (24 * 60)) - int(brk)
        rate = default_rate if (rate is None or (isinstance(rate, str) and rate.startswith("="))) else rate
        rows.append({"date": ddmmyyyy(when), "hours": f"{minutes / 60:.2f}", "rate": str(rate)})
    return rows


def gather(jobs_file: Path) -> list[dict]:
    spec = yaml.safe_load(jobs_file.read_text()) or {}
    base = jobs_file.parent
    jobs = []
    titles = template_titles()
    for entry in spec.get("jobs") or []:
        job = {}
        if entry.get("project"):
            p = flat(base / entry["project"])
            job.update({ours: p[theirs] for theirs, ours in PROJECT_KEYS.items() if p.get(theirs)})
        for k, v in entry.items():
            if k not in ("project", "ledger", "timesheets", "accounts", "documents", "documents_url"):
                job[k] = ddmmyyyy(v) if isinstance(v, (date, datetime)) else v
        if "contract_sum_ex_gst" in job:
            job["contract_sum_ex_gst"] = str(job["contract_sum_ex_gst"]).replace(",", "").replace("$", "")
        ledger = yaml.safe_load((base / entry["ledger"]).read_text()) if entry.get("ledger") else {}
        accounts = yaml.safe_load((base / entry["accounts"]).read_text()) if entry.get("accounts") else {}
        job["job"] = str(job.get("job") or ledger.get("job") or "")
        job["transactions"] = finance.normalise(ledger, accounts)
        job["labour"] = read_timesheets(base / entry["timesheets"]) if entry.get("timesheets") else []
        job["_ledger"], job["_accounts"] = ledger, accounts or {}
        job["_documents"] = (base / entry["documents"]) if entry.get("documents") else None
        job["_documents_url"] = entry.get("documents_url")
        missing = [k for k in ("job", "start_date") if not job.get(k)]
        if missing:
            raise SystemExit(f"{jobs_file}: a job is missing {', '.join(missing)}")
        jobs.append(job)
    return jobs


DOC_EXTS = {".docx", ".xlsx", ".pdf", ".doc", ".xls"}
REF = re.compile(r"(?<![A-Za-z0-9])(?:[A-Z]{1,6}-)+\d{1,4}(?![0-9])")


def template_titles() -> list[tuple[str, str]]:
    """(filename stem, document title) for every template, longest stem first."""
    out = []
    for page in (ROOT / "brain" / "documents").glob("*.md"):
        text = page.read_text()
        m, title = re.search(r"^resource: templates/\S+/([^/\s]+)$", text, re.M), re.search(r"^title: (.+)$", text, re.M)
        if m and title:
            stem = re.sub(r"(_TEMPLATE)?\.\w+$", "", m.group(1))
            out.append((stem.lower(), title.group(1).strip().strip('"')))
    return sorted(out, key=lambda x: -len(x[0]))


def documents(job: str, folder: Path, base_url: str | None, out: Path, titles: list) -> list[dict]:
    """Every generated document in a job's folder, typed by the template it came from."""
    if not folder.is_dir():
        return []
    rows = []
    for f in sorted(folder.rglob("*")):
        if f.suffix.lower() not in DOC_EXTS or f.name.startswith(("~$", ".")):
            continue
        name = f.stem.lower()
        kind = next((title for stem, title in titles if stem in name), "Other document")
        ref = REF.search(f.stem)
        rel = f.relative_to(folder).as_posix()
        link = (base_url.rstrip("/") + "/" + quote(rel)) if base_url else quote(os.path.relpath(f, out).replace(os.sep, "/"))
        rows.append({"job": job, "document": kind, "reference": ref.group(0) if ref else "", "file": rel,
                     "modified": datetime.fromtimestamp(f.stat().st_mtime).strftime("%d/%m/%Y"), "link": link})
    return rows


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if not isinstance(rows[0][k], list)], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def imports(jobs: list[dict], spec_accounts: dict, out: Path, since: str | None, softwares: list[str]) -> list[dict]:
    """Import files for every job's transactions together, per software."""
    accounts = spec_accounts or next((j["_accounts"] for j in jobs if j["_accounts"]), {})
    merged = []
    for j in jobs:
        for t in j["_ledger"].get("transactions") or []:
            if since and datetime.strptime(str(t["date"]), "%d/%m/%Y") < datetime.strptime(since, "%d/%m/%Y"):
                continue
            merged.append({**t, "job": j["job"]})
    ledger = {"transactions": merged}
    check = finance.check(ledger, accounts)
    reports = []
    for software in softwares:
        if not check["ok"]:
            reports.append({"software": software, "written": [], "errors": check["errors"]})
            continue
        r = finance.export(ledger, accounts, software, out / "imports" / software)
        (out / "imports" / software / "how_to_import.txt").write_text(r["how_to_import"] + "\n" + "\n".join(r["skipped"]) + "\n")
        reports.append(r)
    return reports


def render(receipt: dict, out: Path, docs: list, extracts: list) -> Path:
    template = (ROOT / "tools" / "dashboard_template.html").read_text()
    data = json.dumps({**receipt["result"], "documents": docs, "extracts": extracts}).replace("</", "<\\/")
    page = out / "dashboard.html"
    page.write_text(template.replace("/*__DATA__*/null", data))
    return page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("jobs", type=Path, help="portfolio YAML (examples/jobs_example.yaml)")
    parser.add_argument("--out", type=Path, default=Path("out/dashboard"))
    parser.add_argument("--as-at", default=date.today().strftime("%d/%m/%Y"), help="DD/MM/YYYY (default today)")
    parser.add_argument("--since", help="only put transactions dated on or after DD/MM/YYYY in the import files")
    parser.add_argument("--software", help="import formats to write, comma separated (default: the account mapping's)")
    args = parser.parse_args()

    jobs = gather(args.jobs)
    spec = yaml.safe_load(args.jobs.read_text()) or {}
    spec_accounts = yaml.safe_load((args.jobs.parent / spec["accounts"]).read_text()) if spec.get("accounts") else {}
    clean = [{k: v for k, v in j.items() if not k.startswith("_")} for j in jobs]
    receipt = compute.run("job_dashboard", [f"jobs={json.dumps(clean)}", f"as_at={args.as_at}"])
    args.out.mkdir(parents=True, exist_ok=True)
    r = receipt["result"]
    write_csv(args.out / "jobs.csv", r["jobs"])
    write_csv(args.out / "monthly.csv", r["monthly"])
    write_csv(args.out / "costs.csv", r["costs"])
    write_csv(args.out / "benchmarks.csv", r["benchmarks"])
    write_csv(args.out / "cost_mix.csv", r["cost_mix"])
    acct = spec_accounts or next((j["_accounts"] for j in jobs if j["_accounts"]), {})
    # Account codes are labels, not money: added to a copy so the receipt stays as computed.
    lines = [{**row, "account_code": str((acct.get("accounts") or {}).get(row["role"], ""))} for row in r["lines"]]
    write_csv(args.out / "transactions.csv", r["transactions"])
    write_csv(args.out / "transaction_lines.csv", lines)
    titles = template_titles()
    docs = [d for j in jobs if j["_documents"] for d in documents(j["job"], j["_documents"], j["_documents_url"], args.out, titles)]
    write_csv(args.out / "documents.csv", docs or [{"job": "", "document": "", "reference": "", "file": "", "modified": "", "link": ""}])
    (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2))
    softwares = [s.strip() for s in (args.software or acct.get("software") or "xero").split(",")]
    import_reports = imports(jobs, spec_accounts, args.out, args.since, softwares)
    names = ["jobs.csv", "monthly.csv", "costs.csv", "benchmarks.csv", "cost_mix.csv", "transactions.csv",
             "transaction_lines.csv", "documents.csv", "receipt.json"]
    extracts = [{"label": n, "link": n} for n in names] + [
        {"label": f"{rep['software']}: {Path(w).name}", "link": os.path.relpath(w, args.out).replace(os.sep, "/")}
        for rep in import_reports for w in rep.get("written", [])]
    page = render(receipt, args.out, docs, extracts)
    print(json.dumps({"as_at": r["as_at"], "jobs": len(r["jobs"]), "documents": len(docs),
                      "written": [str(args.out / n) for n in names] + [str(page)],
                      "imports": [{"software": rep["software"], "written": rep.get("written", []),
                                   "skipped": rep.get("skipped", []), "errors": rep.get("errors", [])} for rep in import_reports],
                      "warnings": r["warnings"]}, indent=2))


if __name__ == "__main__":
    main()

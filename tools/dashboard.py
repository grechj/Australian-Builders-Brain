"""Financial extracts (CSV) and a project dashboard for every job.

Usage:
    python tools/dashboard.py jobs.yaml --out out/dashboard [--as-at 31/10/2026]

jobs.yaml (examples/jobs_example.yaml) lists each job with its project file,
ledger (see tools/finance.py), optional timesheets and budget. This runs the
job_dashboard computation and writes, into --out:

    jobs.csv          one row per job: contract, revenue, costs, profit, margin,
                      receipts, outstanding, labour, days on site, job length vs average
    monthly.csv       per job and month: revenue, costs, receipts, payments, cumulative profit
    costs.csv         per job and cost category: actual against budget
    benchmarks.csv    averages across completed jobs, overall and by project type
    receipt.json      the computation receipt (check it with check_receipt.py)
    dashboard.html    a self-contained dashboard (open it in any browser, no internet needed)

The CSVs open in Excel, Google Sheets, Power BI or Looker Studio, and are
what a web app would read. Timesheets are a CSV (date, worker, role, hours,
rate_ex_gst) or the Timesheet and Docket workbook.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
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
    for entry in spec.get("jobs") or []:
        job = {}
        if entry.get("project"):
            p = flat(base / entry["project"])
            job.update({ours: p[theirs] for theirs, ours in PROJECT_KEYS.items() if p.get(theirs)})
        for k, v in entry.items():
            if k not in ("project", "ledger", "timesheets", "accounts"):
                job[k] = ddmmyyyy(v) if isinstance(v, (date, datetime)) else v
        if "contract_sum_ex_gst" in job:
            job["contract_sum_ex_gst"] = str(job["contract_sum_ex_gst"]).replace(",", "").replace("$", "")
        ledger = yaml.safe_load((base / entry["ledger"]).read_text()) if entry.get("ledger") else {}
        accounts = yaml.safe_load((base / entry["accounts"]).read_text()) if entry.get("accounts") else {}
        job["job"] = str(job.get("job") or ledger.get("job") or "")
        job["transactions"] = finance.normalise(ledger, accounts)
        job["labour"] = read_timesheets(base / entry["timesheets"]) if entry.get("timesheets") else []
        missing = [k for k in ("job", "start_date") if not job.get(k)]
        if missing:
            raise SystemExit(f"{jobs_file}: a job is missing {', '.join(missing)}")
        jobs.append(job)
    return jobs


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        path.write_text("")
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[k for k in rows[0] if not isinstance(rows[0][k], list)], extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)


def render(receipt: dict, out: Path) -> Path:
    template = (ROOT / "tools" / "dashboard_template.html").read_text()
    data = json.dumps(receipt["result"]).replace("</", "<\\/")
    page = out / "dashboard.html"
    page.write_text(template.replace("/*__DATA__*/null", data))
    return page


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("jobs", type=Path, help="portfolio YAML (examples/jobs_example.yaml)")
    parser.add_argument("--out", type=Path, default=Path("out/dashboard"))
    parser.add_argument("--as-at", default=date.today().strftime("%d/%m/%Y"), help="DD/MM/YYYY (default today)")
    args = parser.parse_args()

    jobs = gather(args.jobs)
    receipt = compute.run("job_dashboard", [f"jobs={json.dumps(jobs)}", f"as_at={args.as_at}"])
    args.out.mkdir(parents=True, exist_ok=True)
    r = receipt["result"]
    write_csv(args.out / "jobs.csv", r["jobs"])
    write_csv(args.out / "monthly.csv", r["monthly"])
    write_csv(args.out / "costs.csv", r["costs"])
    write_csv(args.out / "benchmarks.csv", r["benchmarks"])
    (args.out / "receipt.json").write_text(json.dumps(receipt, indent=2))
    page = render(receipt, args.out)
    print(json.dumps({"as_at": r["as_at"], "jobs": len(r["jobs"]),
                      "written": [str(args.out / n) for n in ("jobs.csv", "monthly.csv", "costs.csv", "benchmarks.csv", "receipt.json")] + [str(page)],
                      "warnings": r["warnings"]}, indent=2))


if __name__ == "__main__":
    main()

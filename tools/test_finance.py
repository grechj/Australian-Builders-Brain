"""Check the finance layer against hand-worked figures for the example ledger.

Usage:
    python tools/test_finance.py

Hand check, quarter 1 2026-27 (1 July to 30 September 2026):
- Accrual: sales INV-001 $24,250.00 + INV-002 $72,750.00 = G1 $97,000.00, 1A $2,204.55 + $6,613.64 = $8,818.19.
  Purchases CE-2291 $7,040.00 + HTS-55102 $5,302.00 - HTS-CR-881 $352.00 = G11 $11,990.00;
  laser level G10 $2,035.00; 1B $640.00 + $482.00 - $32.00 + $185.00 = $1,275.00.
- Cash: INV-002 was paid on 2 October, so G1 is $24,250.00 and 1A $2,204.55.
TPAR 2026-27: Coastal Excavations $7,040.00 (GST $640.00), Hunter Sparks $11,760.00 after
retention (GST $1,120.00); the timber supplier is materials, so not reported.
"""

import csv
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "examples" / "ledger_example.yaml"
ACCOUNTS = ROOT / "examples" / "accounts_example.yaml"
failures = 0


def run(*args) -> tuple[int, dict]:
    p = subprocess.run([sys.executable, str(ROOT / "tools" / "finance.py"), *args], capture_output=True, text=True)
    try:
        return p.returncode, json.loads(p.stdout)
    except json.JSONDecodeError:
        return p.returncode, {"stderr": p.stderr}


def expect(name: str, got, want) -> None:
    global failures
    if got == want:
        print(f"OK   {name}")
    else:
        failures += 1
        print(f"FAIL {name}: got {got!r}, want {want!r}")


def main() -> None:
    base = [str(LEDGER), "--accounts", str(ACCOUNTS)]
    code, r = run("check", *base)
    expect("example ledger checks clean", (code, r.get("errors"), r.get("warnings")), (0, [], []))

    _, r = run("bas", *base, "--from", "01/07/2026", "--to", "30/09/2026", "--basis", "accrual")
    labels = r["result"]["labels"]
    expect("accrual BAS labels", {k: labels[k] for k in ("G1", "G10", "G11", "1A", "1B")},
           {"G1": "97000.00", "G10": "2035.00", "G11": "11990.00", "1A": "8818.19", "1B": "1275.00"})
    expect("accrual BAS whole dollars", r["result"]["bas_form"]["1A"], "8818")
    expect("accrual net GST", r["result"]["net_gst"], "7543.19")
    with tempfile.TemporaryDirectory() as tmp:
        receipt = Path(tmp) / "bas.json"
        receipt.write_text(json.dumps(r))
        p = subprocess.run([sys.executable, str(ROOT / "brain/references/attesters/check_receipt.py"), str(receipt)],
                           capture_output=True, text=True)
        expect("BAS receipt passes the attester", p.returncode, 0)

    _, r = run("bas", *base, "--from", "01/07/2026", "--to", "30/09/2026", "--basis", "cash")
    expect("cash BAS leaves out INV-002 (paid in October)",
           (r["result"]["labels"]["G1"], r["result"]["labels"]["1A"]), ("24250.00", "2204.55"))

    _, r = run("tpar", *base, "--year", "2027")
    payees = {p["name"]: (p["gross_paid_inc_gst"], p["gst"]) for p in r["result"]["payees"]}
    expect("TPAR payees and amounts", payees, {"Coastal Excavations Pty Ltd": ("7040.00", "640.00"),
                                                "Hunter Sparks Pty Ltd": ("11760.00", "1120.00")})

    formats = __import__("yaml").safe_load((ROOT / "tools" / "finance_formats.yaml").read_text())
    with tempfile.TemporaryDirectory() as tmp:
        for software in ("xero", "myob", "quickbooks"):
            code, r = run("export", *base, "--software", software, "--out", tmp)
            fmt = formats[software]
            sales = Path(tmp) / f"{fmt['sales']['file']}.{fmt['extension']}"
            with sales.open(newline="") as f:
                rows = [row for row in csv.reader(f, delimiter=fmt["delimiter"]) if row]
            expect(f"{software} sales header", rows[0], [h for h, _ in fmt["sales"]["columns"]])
            expect(f"{software} sales lines", len(rows) - 1, 4)
        bills = list(csv.DictReader((Path(tmp) / "xero_bills.csv").open(newline="")))
        retention = [b for b in bills if b["Description"].startswith("Retention")][0]
        credit = [b for b in bills if b["*InvoiceNumber"] == "HTS-CR-881"][0]
        expect("Xero retention line", (retention["*UnitAmount"], retention["*AccountCode"], retention["*TaxType"]),
               ("-560.00", "805", "BAS Excluded"))
        expect("Xero supplier credit is negative", credit["*UnitAmount"], "-320.00")

    _, r = run("payload", *base)
    hs = [t for t in r["transactions"] if t["number"] == "HS-118"][0]
    expect("payload keeps the retention line negative", hs["lines"][1]["unit_amount_ex_gst"], "-560.00")
    expect("payload uses Xero API tax codes", hs["lines"][0]["tax_code"], "INPUT")
    expect("payload drafts only", r["create_as"], "DRAFT")

    bad = Path(tempfile.mkdtemp()) / "bad.yaml"
    bad.write_text("transactions:\n  - {type: bill, number: X1, date: 31/02/2026, contact: {name: A, abn: 12 345 678 901},"
                   " lines: [{description: x, amount: 10, account: materials, tax: gst_freee}]}\n")
    code, r = run("check", str(bad), "--accounts", str(ACCOUNTS))
    expect("bad ledger is refused", code, 1)
    expect("bad date and tax code reported", sum(("date" in e) or ("tax must be" in e) for e in r["errors"]), 2)
    expect("bad ABN warned", any("checksum" in w for w in r["warnings"]), True)

    with tempfile.TemporaryDirectory() as tmp:
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "dashboard.py"), str(ROOT / "examples" / "projects_example.yaml"),
                            "--as-at", "31/10/2026", "--out", tmp], capture_output=True, text=True)
        expect("dashboard builds", p.returncode, 0)
        rows = {r["job"]: r for r in csv.DictReader((Path(tmp) / "jobs.csv").open(newline=""))}
        j = rows.get("SB-2027-014", {})
        expect("dashboard P&L", (j.get("revenue_ex_gst"), j.get("costs_ex_gst"), j.get("gross_profit_ex_gst"), j.get("margin_pct")),
               ("179723.63", "121087.50", "58636.13", "32.6"))
        expect("dashboard cash as at", (j.get("received_inc_gst"), j.get("paid_inc_gst")), ("197696.00", "60500.00"))
        expect("dashboard time", (j.get("days_elapsed"), j.get("contract_days"), j.get("benchmark_average_days"), j.get("days_vs_average_pct")),
               ("90", "271", "193", "46.6"))
        expect("dashboard labour", (j.get("labour_hours"), j.get("labour_cost_ex_gst"), j.get("days_on_site")), ("667.5", "56737.50", "53"))
        page = (Path(tmp) / "dashboard.html").read_text()
        expect("dashboard page has its data embedded", "/*__DATA__*/null" not in page and '"SB-2027-014"' in page, True)
        receipt = Path(tmp) / "receipt.json"
        p = subprocess.run([sys.executable, str(ROOT / "brain/references/attesters/check_receipt.py"), str(receipt)], capture_output=True, text=True)
        expect("dashboard receipt passes the attester", p.returncode, 0)
        expect("dashboard forecast at completion", (j.get("forecast_costs_ex_gst"), j.get("forecast_profit_ex_gst"), j.get("forecast_margin_pct")),
               ("355500.00", "88769.09", "20.0"))
        txns = {r["number"]: r for r in csv.DictReader((Path(tmp) / "transactions.csv").open(newline=""))}
        expect("transactions extract: days to settle and quarter", (txns["INV-002"]["days_to_settle"], txns["INV-002"]["quarter"]), ("14", "FY2027 Q1"))
        expect("transactions extract: HS-118 unpaid as at 31/10", txns["HS-118"]["outstanding_inc_gst"], "11760.00")
        lines = list(csv.DictReader((Path(tmp) / "transaction_lines.csv").open(newline="")))
        retention = [l for l in lines if l["role"] == "retention_payable"][0]
        expect("line extract: retention is balance sheet, coded 805", (retention["kind"], retention["account_code"], retention["ex_gst"]), ("balance_sheet", "805", "-560.00"))
        mix = {(r["group"], r["category"]): r["average_pct_of_revenue"] for r in csv.DictReader((Path(tmp) / "cost_mix.csv").open(newline=""))}
        expect("cost mix for extensions", mix.get(("extension", "subcontractors")), "36.9")
        imp = list(csv.DictReader((Path(tmp) / "imports" / "xero" / "xero_sales_invoices.csv").open(newline="")))
        expect("portfolio Xero import has every job's sales lines", len(imp), 4 + 5 + 5)
        expect("portfolio import tracks each job", sorted({r["TrackingOption1"] for r in imp}), ["SB-2025-031", "SB-2026-007", "SB-2027-014"])
        p = subprocess.run([sys.executable, str(ROOT / "tools" / "dashboard.py"), str(ROOT / "examples" / "projects_example.yaml"),
                            "--as-at", "31/10/2026", "--since", "01/10/2026", "--out", tmp], capture_output=True, text=True)
        imp = list(csv.DictReader((Path(tmp) / "imports" / "xero" / "xero_sales_invoices.csv").open(newline="")))
        expect("--since limits the import files", sorted({r["*InvoiceNumber"] for r in imp}), ["INV-003"])

    sys.path.insert(0, str(ROOT / "tools"))
    import dashboard
    with tempfile.TemporaryDirectory() as tmp:
        folder = Path(tmp) / "SB-1"
        folder.mkdir()
        for name in ("VAR-002_Priced_Variation_Notice.docx", "DELAY-001_Delay_Notification_Letter.docx", "Site_Diary.xlsx", "notes.txt"):
            (folder / name).write_text("x")
        docs = {d["file"]: d for d in dashboard.documents("SB-1", folder, None, Path(tmp) / "out", dashboard.template_titles())}
        expect("documents found (not the .txt)", sorted(docs), ["DELAY-001_Delay_Notification_Letter.docx", "Site_Diary.xlsx", "VAR-002_Priced_Variation_Notice.docx"])
        expect("documents typed and referenced", (docs["VAR-002_Priced_Variation_Notice.docx"]["document"], docs["VAR-002_Priced_Variation_Notice.docx"]["reference"]),
               ("Priced Variation Notice", "VAR-002"))
        expect("documents linked relative to the dashboard", docs["Site_Diary.xlsx"]["link"], "../SB-1/Site_Diary.xlsx")
        cloud = dashboard.documents("SB-1", folder, "https://www.dropbox.com/home/Jobs/SB-1", Path(tmp) / "out", dashboard.template_titles())
        expect("documents linked to a cloud folder", [d["link"] for d in cloud if d["file"] == "Site_Diary.xlsx"], ["https://www.dropbox.com/home/Jobs/SB-1/Site_Diary.xlsx"])

    print(f"\n{'all finance checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

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

    print(f"\n{'all finance checks passed' if not failures else f'{failures} failed'}")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()

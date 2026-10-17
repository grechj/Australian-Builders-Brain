"""Get a job's money into Xero, MYOB or QuickBooks, and summarise it for tax.

Usage:
    python tools/finance.py check   ledger.yaml --accounts accounts.yaml
    python tools/finance.py export  ledger.yaml --accounts accounts.yaml --out out/finance [--software xero|myob|quickbooks]
    python tools/finance.py payload ledger.yaml --accounts accounts.yaml [--software xero]
    python tools/finance.py bas     ledger.yaml --accounts accounts.yaml --from 01/07/2026 --to 30/09/2026 --basis accrual
    python tools/finance.py tpar    ledger.yaml --accounts accounts.yaml --year 2027

The ledger (examples/ledger_example.yaml) lists the job's invoices, credit
notes, bills and supplier credits, each line coded with a role and a tax
code. The account mapping (examples/accounts_example.yaml) turns roles into
the user's own account codes. Import formats live in
tools/finance_formats.yaml.

- check    validates the ledger: dates, tax codes, roles, ABNs, payments.
- export   writes import files (Xero CSV, MYOB tab-delimited TXT, QuickBooks CSV).
- payload  prints the transactions as JSON with mapped account and tax codes,
           for pushing through the user's own Xero, MYOB or QuickBooks connector.
- bas      runs the bas_summary computation and prints its receipt.
- tpar     runs the tpar_summary computation and prints its receipt.

Nothing here talks to any accounting system or the ATO, and nothing is lodged.
"""

from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import re
import sys
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import compute  # noqa: E402

FORMATS = yaml.safe_load((ROOT / "tools" / "finance_formats.yaml").read_text())
_spec = importlib.util.spec_from_file_location("finance_maths", ROOT / "brain/references/computations/finance_maths.py")
maths = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(maths)

SALES, PURCHASES = set(maths.SALES), set(maths.PURCHASES)
ABN_WEIGHTS = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]


def abn_valid(abn: str) -> bool:
    digits = re.sub(r"\D", "", abn or "")
    if len(digits) != 11:
        return False
    d = [int(c) for c in digits]
    d[0] -= 1
    return sum(x * w for x, w in zip(d, ABN_WEIGHTS)) % 89 == 0


def money(x) -> str:
    return f"{Decimal(str(x)):.2f}"


def iso(d: str) -> str:
    return datetime.strptime(str(d), "%d/%m/%Y").strftime("%Y-%m-%d")


def load(ledger_path: Path, accounts_path: Path | None) -> tuple[dict, dict]:
    ledger = yaml.safe_load(ledger_path.read_text()) or {}
    accounts = yaml.safe_load(accounts_path.read_text()) if accounts_path else {}
    return ledger, accounts or {}


def side(t: dict) -> str:
    return "sales" if t["type"] in SALES else "purchases"


def tax_name(software: str, s: str, tax: str, accounts: dict) -> str:
    custom = (accounts.get("tax_names") or {}).get(s, {})
    return custom.get(tax) or FORMATS[software]["tax_names"][s].get(tax, "")


def payments_for(t: dict, ledger: dict) -> list[dict]:
    """A transaction's payments: those listed under it, plus any in the
    ledger's payments log (added from remittances and bank screenshots) that
    name its number (and contact, where given)."""
    name = ((t.get("contact") or {}).get("name") or "").strip().lower()
    logged = [p for p in ledger.get("payments") or [] if str(p.get("number")) == str(t.get("number"))
              and (not p.get("contact") or str(p["contact"]).strip().lower() == name)]
    return list(t.get("payments") or []) + logged


def normalise(ledger: dict, accounts: dict) -> list[dict]:
    """The shape finance_maths expects, with each bill's TPAR flag resolved."""
    tpar_roles = set(accounts.get("tpar_accounts") or ["subcontractors"])
    out = []
    for t in ledger.get("transactions") or []:
        lines = [{"amount": str(l.get("amount", Decimal(str(l.get("quantity", 1))) * Decimal(str(l.get("unit_amount", 0))))),
                  "tax": l["tax"], "account": l.get("account", ""), "description": str(l.get("description", ""))} for l in t["lines"]]
        tpar = t.get("tpar")
        if tpar is None:
            tpar = t["type"] in PURCHASES and any(l.get("account") in tpar_roles for l in t["lines"])
        c = t.get("contact") or {}
        out.append({"type": t["type"], "number": str(t["number"]), "date": str(t["date"]), "due": str(t.get("due") or ""),
                    "contact": {"name": c.get("name", ""), "abn": c.get("abn", ""), "address": c.get("address", "")},
                    "lines": lines, "payments": [{"date": str(p["date"]), "amount": str(p["amount"])} for p in payments_for(t, ledger)],
                    "withheld": str(t.get("withheld", 0) or 0), "tpar": bool(tpar)})
    return out


def check(ledger: dict, accounts: dict) -> dict:
    errors, warnings = [], []
    roles = accounts.get("accounts") or {}
    seen = set()
    for t in ledger.get("transactions") or []:
        num = str(t.get("number", "?"))
        before = len(errors)
        if t.get("type") not in SALES | PURCHASES:
            errors.append(f"{num}: type must be invoice, credit_note, bill or supplier_credit")
            continue
        key = (side(t), num, (t.get("contact") or {}).get("name") if t["type"] in PURCHASES else "")
        if key in seen:
            errors.append(f"{num}: number used twice")
        seen.add(key)
        for f in ("date", "due"):
            if t.get(f) is not None:
                try:
                    datetime.strptime(str(t[f]), "%d/%m/%Y")
                except ValueError:
                    errors.append(f"{num}: {f} must be DD/MM/YYYY, got {t[f]!r}")
        if not (t.get("contact") or {}).get("name"):
            errors.append(f"{num}: contact name missing")
        abn = (t.get("contact") or {}).get("abn")
        if abn and not abn_valid(str(abn)):
            warnings.append(f"{num}: ABN {abn} fails the ABN checksum. Check it on ABN Lookup.")
        if not t.get("lines"):
            errors.append(f"{num}: no lines")
        for line in t.get("lines") or []:
            if line.get("tax") not in maths.TAX_CODES:
                errors.append(f"{num}: tax must be one of {', '.join(sorted(maths.TAX_CODES))}, got {line.get('tax')!r}")
            if roles and line.get("account") not in roles:
                errors.append(f"{num}: account role {line.get('account')!r} isn't in the account mapping")
            if side(t) == "sales" and line.get("tax") == "capital":
                errors.append(f"{num}: capital is a purchase tax code")
        if len(errors) > before:
            continue
        n = normalise({"transactions": [t]}, accounts)[0]
        total = maths._total(n)
        paid = sum((Decimal(p["amount"]) for p in n["payments"]), Decimal("0"))
        if paid > total + Decimal("0.01"):
            warnings.append(f"{num}: payments ({money(paid)}) are more than the total ({money(total)})")
        if t["type"] in PURCHASES and n["tpar"] and not abn:
            warnings.append(f"{num}: a TPAR-reportable bill with no ABN for {n['contact']['name']}")
        if (accounts.get("software") == "myob") and len(num) > 8:
            warnings.append(f"{num}: MYOB invoice numbers are limited to 8 characters")
    return {"ok": not errors, "transactions": len(ledger.get("transactions") or []), "errors": errors, "warnings": warnings}


def rows_for(t: dict, ledger: dict, accounts: dict, software: str) -> list[dict]:
    """One import row per ledger line, with every value key the formats use."""
    s = side(t)
    sign = -1 if t["type"] in ("credit_note", "supplier_credit") else 1
    c = t.get("contact") or {}
    job = str(t.get("job") or ledger.get("job") or "")
    rows = []
    for line in t["lines"]:
        qty = Decimal(str(line.get("quantity", 1)))
        amount = Decimal(str(line.get("amount", qty * Decimal(str(line.get("unit_amount", 0))))))
        unit = Decimal(str(line.get("unit_amount", amount / qty if qty else amount)))
        gst = maths._money(amount * maths.GST_RATE) if line["tax"] in maths.GST_CODES else Decimal("0")
        rows.append({
            "contact": c.get("name", ""), "email": c.get("email", ""), "number": str(t["number"]),
            "reference": t.get("reference", ""), "date": t["date"], "due": t.get("due", t["date"]),
            "description": line.get("description", ""), "quantity": f"{qty:g}",
            "unit_amount": money(unit * sign), "amount": money(amount * sign), "tax_amount": money(gst * sign),
            "unit_amount_as_entered": money(unit),
            "account": str((accounts.get("accounts") or {}).get(line["account"], line["account"])),
            "tax": tax_name(software, s, line["tax"], accounts), "job": job,
            "tracking_name": accounts.get("tracking_name", "") if job else "", "tracking_option": job,
            "supplier_invoice": str(t["number"]), "blank": "",
        })
    return rows


def export(ledger: dict, accounts: dict, software: str, out: Path) -> dict:
    fmt = FORMATS[software]
    out.mkdir(parents=True, exist_ok=True)
    written, skipped = [], []
    for s in ("sales", "purchases"):
        spec = fmt[s]
        txns = [t for t in ledger.get("transactions") or [] if t["type"] in maths.SALES or t["type"] in maths.PURCHASES]
        txns = [t for t in txns if side(t) == s]
        for t in txns:
            if t["type"] not in spec["types"]:
                skipped.append(f"{t['number']}: {software} can't import a {t['type'].replace('_', ' ')}; enter it by hand or through the connector")
        txns = [t for t in txns if t["type"] in spec["types"]]
        if not txns:
            continue
        path = out / f"{spec['file']}.{fmt['extension']}"
        with path.open("w", newline="") as f:
            w = csv.writer(f, delimiter=fmt["delimiter"])
            w.writerow([h for h, _ in spec["columns"]])
            for i, t in enumerate(txns):
                if fmt.get("separate_by_blank_line") and i:
                    w.writerow([])
                for row in rows_for(t, ledger, accounts, software):
                    w.writerow([row[k] for _, k in spec["columns"]])
        written.append(str(path))
    notes = {
        "xero": "Import in Xero (Sales > Invoices > Import; Purchases > Bills > Import from CSV). Choose 'tax exclusive'. Imports arrive as drafts to approve.",
        "myob": "AccountRight: File > Import Data > Sales > Service Sales (and Purchases > Service Purchases), tab-delimited, header row included. Cards, accounts, jobs and tax codes must already exist. Back up first.",
        "quickbooks": "QuickBooks Online: Settings > Import data > Invoices (and Bills where available). Map the columns on screen and choose 'exclusive of tax'. Max 100 invoices per file.",
    }[software]
    return {"software": software, "written": written, "skipped": skipped, "how_to_import": notes}


def payload(ledger: dict, accounts: dict, software: str) -> dict:
    """Transactions with mapped codes, for the user's own accounting connector."""
    items = []
    for t in ledger.get("transactions") or []:
        s = side(t)
        api = (FORMATS[software].get("api_tax_codes") or {}).get(s, {})
        lines = []
        for r, line in zip(rows_for(t, ledger, accounts, software), t["lines"]):
            lines.append({"description": r["description"], "quantity": r["quantity"],
                          "unit_amount_ex_gst": r["unit_amount_as_entered"],
                          "account_code": r["account"], "tax_name": r["tax"],
                          "tax_code": api.get(line["tax"], r["tax"]),
                          "tracking": {"name": r["tracking_name"], "option": r["tracking_option"]} if r["tracking_name"] else None})
        kind = {"invoice": "sales invoice", "credit_note": "sales credit note",
                "bill": "bill", "supplier_credit": "supplier credit note"}[t["type"]]
        items.append({"kind": kind, "status": "DRAFT", "number": str(t["number"]), "reference": t.get("reference", ""),
                      "contact": t.get("contact") or {}, "date": t["date"], "due": t.get("due", t["date"]),
                      "date_iso": iso(t["date"]), "due_iso": iso(t.get("due", t["date"])),
                      "amounts_are": "tax exclusive", "lines": lines,
                      "payments": [{"date": p["date"], "date_iso": iso(p["date"]), "amount": money(p["amount"])}
                                   for p in payments_for(t, ledger)]})
    return {"software": software, "create_as": "DRAFT", "transactions": items,
            "rules": ["Show the user every transaction and get a clear yes before creating anything.",
                      "Create as drafts only; the user approves them in their software.",
                      "Skip any number that already exists in the software; never overwrite.",
                      "Record payments only if the user asks: they usually come from the bank feed."]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("cmd", choices=["check", "export", "payload", "bas", "tpar"])
    parser.add_argument("ledger", type=Path)
    parser.add_argument("--accounts", type=Path, help="account mapping YAML (examples/accounts_example.yaml)")
    parser.add_argument("--software", choices=list(FORMATS), help="xero, myob or quickbooks (default: from the mapping)")
    parser.add_argument("--out", type=Path, default=Path("out/finance"))
    parser.add_argument("--from", dest="start", help="BAS period start, DD/MM/YYYY")
    parser.add_argument("--to", dest="end", help="BAS period end, DD/MM/YYYY")
    parser.add_argument("--basis", choices=["cash", "accrual"], default="accrual")
    parser.add_argument("--year", help="TPAR financial year ending 30 June, e.g. 2027")
    args = parser.parse_args()

    ledger, accounts = load(args.ledger, args.accounts)
    software = args.software or accounts.get("software") or "xero"
    result = check(ledger, accounts)
    if args.cmd == "check" or not result["ok"]:
        print(json.dumps(result, indent=2))
        sys.exit(0 if result["ok"] else 1)
    if args.cmd == "export":
        report = export(ledger, accounts, software, args.out)
        report["warnings"] = result["warnings"]
        print(json.dumps(report, indent=2))
    elif args.cmd == "payload":
        print(json.dumps(payload(ledger, accounts, software), indent=2))
    elif args.cmd == "bas":
        if not (args.start and args.end):
            sys.exit("bas needs --from and --to (DD/MM/YYYY)")
        txns = json.dumps(normalise(ledger, accounts))
        print(json.dumps(compute.run("bas_summary", [f"transactions={txns}", f"period_start={args.start}",
                                                      f"period_end={args.end}", f"basis={args.basis}"]), indent=2))
    elif args.cmd == "tpar":
        if not args.year:
            sys.exit("tpar needs --year (the financial year ending 30 June)")
        txns = json.dumps(normalise(ledger, accounts))
        print(json.dumps(compute.run("tpar_summary", [f"transactions={txns}", f"year_ending={args.year}"]), indent=2))


if __name__ == "__main__":
    main()

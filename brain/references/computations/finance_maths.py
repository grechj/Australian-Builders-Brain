"""Sanctioned tax summaries for the Australian Builder's Brain.

Each public function is the computation behind one Attested Computation
concept in brain/computations/ (bas_summary, tpar_summary). They take the
job ledger's transactions as JSON, already normalised by tools/finance.py:

    {"type": "invoice" | "credit_note" | "bill" | "supplier_credit",
     "number": "INV-003", "date": "16/10/2026",
     "contact": {"name": "...", "abn": "...", "address": "..."},
     "lines": [{"amount": "88181.82", "tax": "gst"}],     # ex GST
     "payments": [{"date": "28/10/2026", "amount": "100696.00"}],
     "withheld": "0", "tpar": true}

Tax codes: gst, gst_free, export, input_taxed, capital (a purchase of a
capital item with GST), bas_excluded. Agents supply the data only; they
never edit these functions. If one changes, update `computation_sha256` in
every concept that points here (tools/okf_lint.py reports a mismatch).

All amounts are Decimal, in dollars, rounded half-up to the cent.
"""

from datetime import date, datetime
from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

GST_RATE = Decimal("0.10")
CENT = Decimal("0.01")
SALES = {"invoice": 1, "credit_note": -1}
PURCHASES = {"bill": 1, "supplier_credit": -1}
TAX_CODES = {"gst", "gst_free", "export", "input_taxed", "capital", "bas_excluded"}
GST_CODES = {"gst", "capital"}


def _money(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def _dollars(x: Decimal) -> str:
    """BAS labels are reported in whole dollars, cents dropped."""
    return str(x.quantize(Decimal("1"), rounding=ROUND_DOWN))


def _date(text: str) -> date:
    return datetime.strptime(text, "%d/%m/%Y").date()


def _lines(t: dict) -> list:
    """Each line's ex-GST amount, GST and tax code."""
    out = []
    for line in t["lines"]:
        tax = line["tax"]
        if tax not in TAX_CODES:
            raise ValueError(f"{t['number']}: unknown tax code {tax!r}")
        amount = _money(Decimal(str(line["amount"])))
        gst = _money(amount * GST_RATE) if tax in GST_CODES else Decimal("0.00")
        out.append((amount, gst, tax))
    return out


def _total(t: dict) -> Decimal:
    return sum((a + g for a, g, _ in _lines(t)), Decimal("0.00"))


def _share(t: dict, start: date, end: date, basis: str) -> Decimal:
    """How much of a transaction falls in the period: all or nothing on an
    accrual basis (by date), or the part paid in the period on a cash basis."""
    if basis == "accrual":
        return Decimal("1") if start <= _date(t["date"]) <= end else Decimal("0")
    total = _total(t)
    if total == 0:
        return Decimal("0")
    paid = sum((Decimal(str(p["amount"])) for p in t.get("payments", [])
                if start <= _date(p["date"]) <= end), Decimal("0"))
    return min(Decimal("1"), paid / total)


def bas_summary(transactions: list, period_start: str, period_end: str, basis: str) -> dict:
    """The GST labels of a BAS for one period, on a cash or accrual basis."""
    if basis not in ("cash", "accrual"):
        raise ValueError("basis must be cash or accrual")
    start, end = _date(period_start), _date(period_end)
    labels = {k: Decimal("0") for k in ("G1", "G2", "G3", "G4", "G10", "G11", "1A", "1B")}
    included, warnings = [], []
    for t in transactions:
        sign = SALES.get(t["type"]) or PURCHASES.get(t["type"])
        if sign is None:
            raise ValueError(f"{t['number']}: unknown type {t['type']!r}")
        share = _share(t, start, end, basis)
        if basis == "cash" and not t.get("payments") and start <= _date(t["date"]) <= end:
            warnings.append(f"{t['number']}: dated in the period but no payment recorded, so not counted on a cash basis")
        if share == 0:
            continue
        gst_in = Decimal("0")
        for amount, gst, tax in _lines(t):
            if tax == "bas_excluded":
                continue
            inc = (amount + gst) * share * sign
            if t["type"] in SALES:
                labels["G1"] += inc
                labels["G2"] += inc if tax == "export" else 0
                labels["G3"] += inc if tax == "gst_free" else 0
                labels["G4"] += inc if tax == "input_taxed" else 0
                labels["1A"] += gst * share * sign
            else:
                labels["G10" if tax == "capital" else "G11"] += inc
                if tax in GST_CODES:
                    labels["1B"] += gst * share * sign
            gst_in += gst * share * sign
        included.append({"number": t["number"], "type": t["type"], "date": t["date"],
                         "share": str(share.quantize(Decimal("0.0001"))), "gst": str(_money(gst_in))})
    exact = {k: str(_money(v)) for k, v in labels.items()}
    whole = {k: _dollars(_money(v)) for k, v in labels.items()}
    net = _money(labels["1A"] - labels["1B"])
    result = {
        "period": f"{period_start} to {period_end}", "basis": basis,
        "labels": exact, "bas_form": whole,
        "net_gst": str(net), "net_gst_direction": "payable to the ATO" if net >= 0 else "refund from the ATO",
        "transactions": included, "warnings": warnings,
    }
    fields = {"G1": whole["G1"], "1A": whole["1A"], "1B": whole["1B"], "NET_GST": str(net)}
    return {"result": result, "fields": fields}


def tpar_summary(transactions: list, year_ending: str) -> dict:
    """Payments to contractors for one financial year (1 July to 30 June),
    per payee, for the Taxable payments annual report: gross paid including
    GST, the GST in it, and tax withheld where no ABN was quoted."""
    end = _date(f"30/06/{year_ending}")
    start = _date(f"01/07/{int(year_ending) - 1}")
    payees, warnings = {}, []
    for t in transactions:
        if t["type"] not in PURCHASES or not t.get("tpar"):
            continue
        total = _total(t)
        gst_total = sum((g for _, g, _ in _lines(t)), Decimal("0.00"))
        paid = sum((Decimal(str(p["amount"])) for p in t.get("payments", [])
                    if start <= _date(p["date"]) <= end), Decimal("0")) * PURCHASES[t["type"]]
        if paid == 0:
            continue
        gst_paid = gst_total * paid / total if total else Decimal("0")
        c = t["contact"]
        key = (c.get("abn") or c["name"]).replace(" ", "")
        p = payees.setdefault(key, {"name": c["name"], "abn": c.get("abn", ""), "address": c.get("address", ""),
                                    "gross_paid": Decimal("0"), "gst": Decimal("0"), "withheld": Decimal("0"),
                                    "bills": []})
        p["gross_paid"] += paid
        p["gst"] += gst_paid
        p["withheld"] += Decimal(str(t.get("withheld", 0) or 0))
        p["bills"].append(t["number"])
    rows = []
    for p in sorted(payees.values(), key=lambda p: p["name"].lower()):
        if not p["abn"]:
            warnings.append(f"{p['name']}: no ABN recorded. Report the tax withheld, and check whether you should have withheld 47%.")
        if not p["address"]:
            warnings.append(f"{p['name']}: no address recorded; the TPAR needs one.")
        rows.append({"name": p["name"], "abn": p["abn"], "address": p["address"],
                     "gross_paid_inc_gst": str(_money(p["gross_paid"])), "gst": str(_money(p["gst"])),
                     "tax_withheld": str(_money(p["withheld"])), "bills": p["bills"]})
    total_gross = sum((Decimal(r["gross_paid_inc_gst"]) for r in rows), Decimal("0.00"))
    result = {"financial_year": f"1 July {int(year_ending) - 1} to 30 June {year_ending}",
              "due": f"28 August {year_ending}", "payees": rows,
              "total_gross_paid_inc_gst": str(total_gross), "warnings": warnings}
    return {"result": result, "fields": {"TPAR_PAYEES": str(len(rows)), "TPAR_TOTAL": str(total_gross)}}

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


INCOME_ROLES = {"contract_income", "variation_income", "other_income"}
BALANCE_ROLES = {"retention_receivable", "retention_payable", "deposits_held", "equipment"}


def _month(text: str) -> str:
    return _date(text).strftime("%Y-%m")


def _period(text: str) -> dict:
    """Month, Australian financial year (July to June) and quarter of a date."""
    d = _date(text)
    fy = d.year + 1 if d.month >= 7 else d.year
    return {"month": d.strftime("%Y-%m"), "financial_year": f"FY{fy}", "quarter": f"FY{fy} Q{(d.month - 7) % 12 // 3 + 1}"}


def job_dashboard(jobs: list, as_at: str) -> dict:
    """Per-job P&L, cash, costs, margin and time, monthly series, and benchmarks
    across jobs, for the project dashboard.

    jobs: [{"job", "name", "project_type", "state", "status": "active" | "complete",
            "contract_sum_ex_gst", "start_date", "contract_end_date", "pc_date",
            "target_margin_pct", "budget": {role: amount ex GST},
            "transactions": [normalised, each line with its "account" role],
            "labour": [{"date", "hours", "rate" (ex GST per hour) or "cost"}]}]
    Only transactions, payments and timesheets dated on or before as_at count.
    Revenue and costs are ex GST on an accrual basis (by transaction date);
    receipts and payments are inc GST, by payment date. Balance sheet lines
    (retention, deposits held, capital equipment) are left out of profit.
    Own labour from timesheets is a cost of the job. Forecasts take each cost
    category at the larger of actual and budget (active jobs only) against
    the revised contract. Also returns every transaction (with days to settle
    and days overdue) and every line, for modelling and pivot tables.
    """
    today = _date(as_at)
    rows, monthly, costs, warnings = [], {}, [], []
    txn_rows, line_rows = [], []
    for j in jobs:
        rev = {r: Decimal("0") for r in INCOME_ROLES}
        cost = {}
        invoiced_inc = received = billed_inc = paid_out = Decimal("0")
        for t in j.get("transactions", []):
            if _date(t["date"]) > today:
                continue
            t = {**t, "payments": [p for p in t.get("payments", []) if _date(p["date"]) <= today]}
            sign = SALES.get(t["type"]) or PURCHASES.get(t["type"])
            lines = _lines(t)
            total_inc = sum((a + g for a, g, _ in lines), Decimal("0")) * sign
            pay = sum((Decimal(str(p["amount"])) for p in t.get("payments", [])), Decimal("0")) * sign
            m = monthly.setdefault((j["job"], _month(t["date"])), {"revenue": Decimal("0"), "costs": Decimal("0"),
                                                                     "received": Decimal("0"), "paid": Decimal("0")})
            ex_total = sum((a for a, _, _ in lines), Decimal("0")) * sign
            paid_dates = sorted((_date(p["date"]) for p in t.get("payments", [])))
            settled = None
            if total_inc and pay * sign >= abs(total_inc) - CENT:
                running_paid = Decimal("0")
                for p in sorted(t.get("payments", []), key=lambda p: _date(p["date"])):
                    running_paid += Decimal(str(p["amount"]))
                    if running_paid >= abs(total_inc) - CENT:
                        settled = _date(p["date"])
                        break
            outstanding = total_inc - pay
            due = _date(t["due"]) if t.get("due") else None
            txn_rows.append({
                "job": j["job"], "side": "sale" if t["type"] in SALES else "purchase", "type": t["type"],
                "number": t["number"], "date": t["date"], "due": t.get("due", ""), **_period(t["date"]),
                "contact": t.get("contact", {}).get("name", ""), "abn": t.get("contact", {}).get("abn", ""),
                "ex_gst": str(_money(ex_total)), "gst": str(_money(total_inc - ex_total)), "inc_gst": str(_money(total_inc)),
                "paid_inc_gst": str(_money(pay)), "outstanding_inc_gst": str(_money(outstanding)),
                "first_payment": paid_dates[0].strftime("%d/%m/%Y") if paid_dates else "",
                "settled_on": settled.strftime("%d/%m/%Y") if settled else "",
                "days_to_settle": str((settled - _date(t["date"])).days) if settled else "",
                "days_overdue": str((today - due).days) if due and outstanding and today > due else "",
            })
            for (amount, gst_line, tax), line in zip(lines, t["lines"]):
                role = line.get("account", "")
                kind = "balance_sheet" if role in BALANCE_ROLES else ("income" if t["type"] in SALES else "cost")
                line_rows.append({
                    "job": j["job"], "side": "sale" if t["type"] in SALES else "purchase", "type": t["type"],
                    "number": t["number"], "date": t["date"], **_period(t["date"]),
                    "contact": t.get("contact", {}).get("name", ""), "role": role, "kind": kind,
                    "description": line.get("description", ""), "tax": tax,
                    "ex_gst": str(_money(amount * sign)), "gst": str(_money(gst_line * sign)),
                    "inc_gst": str(_money((amount + gst_line) * sign)),
                })
            for (amount, _gst, _tax), line in zip(lines, t["lines"]):
                role = line.get("account", "")
                if role in BALANCE_ROLES:
                    continue
                if t["type"] in SALES:
                    if role not in INCOME_ROLES:
                        warnings.append(f"{j['job']} {t['number']}: sales line with role {role!r} counted as other income")
                        role = "other_income"
                    rev[role] += amount * sign
                    m["revenue"] += amount * sign
                else:
                    cost[role] = cost.get(role, Decimal("0")) + amount * sign
                    m["costs"] += amount * sign
            for p in t.get("payments", []):
                pm = monthly.setdefault((j["job"], _month(p["date"])), {"revenue": Decimal("0"), "costs": Decimal("0"),
                                                                         "received": Decimal("0"), "paid": Decimal("0")})
                pm["received" if t["type"] in SALES else "paid"] += Decimal(str(p["amount"])) * sign
            if t["type"] in SALES:
                invoiced_inc += total_inc
                received += pay
            else:
                billed_inc += total_inc
                paid_out += pay
        hours = labour = Decimal("0")
        days = set()
        for entry in j.get("labour", []):
            if _date(entry["date"]) > today:
                continue
            h = Decimal(str(entry.get("hours", 0)))
            c = _money(Decimal(str(entry["cost"]))) if entry.get("cost") not in (None, "") \
                else _money(h * Decimal(str(entry.get("rate", 0))))
            hours += h
            labour += c
            days.add(entry["date"])
            lm = monthly.setdefault((j["job"], _month(entry["date"])), {"revenue": Decimal("0"), "costs": Decimal("0"),
                                                                         "received": Decimal("0"), "paid": Decimal("0")})
            lm["costs"] += c
            line_rows.append({"job": j["job"], "side": "labour", "type": "timesheet", "number": "", "date": entry["date"],
                              **_period(entry["date"]), "contact": entry.get("worker", ""), "role": "own_labour",
                              "kind": "cost", "description": f"{h} hours", "tax": "",
                              "ex_gst": str(c), "gst": "0.00", "inc_gst": str(c)})
        if labour:
            cost["own_labour"] = cost.get("own_labour", Decimal("0")) + labour
        revenue = sum(rev.values(), Decimal("0"))
        total_cost = sum(cost.values(), Decimal("0"))
        profit = revenue - total_cost
        contract = _money(Decimal(str(j.get("contract_sum_ex_gst") or 0)))
        revised = contract + rev["variation_income"]
        start = _date(j["start_date"])
        finish = _date(j["pc_date"]) if j.get("pc_date") else today
        elapsed = (finish - start).days + 1
        contract_days = (_date(j["contract_end_date"]) - start).days + 1 if j.get("contract_end_date") else None
        budget = {k: _money(Decimal(str(v))) for k, v in (j.get("budget") or {}).items()}
        forecast_cost = Decimal("0")
        for role in sorted(set(cost) | set(budget)):
            actual = _money(cost.get(role, Decimal("0")))
            forecast = max(actual, budget.get(role, Decimal("0"))) if j.get("status") != "complete" else actual
            forecast_cost += forecast
            costs.append({"job": j["job"], "category": role, "actual_ex_gst": str(actual),
                          "budget_ex_gst": str(budget[role]) if role in budget else "",
                          "forecast_final_ex_gst": str(forecast),
                          "pct_of_revenue": str((actual / revenue * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if revenue else ""})
        final_revenue = revised if j.get("status") != "complete" else revenue
        forecast_profit = final_revenue - forecast_cost
        margin = (profit / revenue * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP) if revenue else None
        target = Decimal(str(j["target_margin_pct"])) if j.get("target_margin_pct") is not None else None
        rows.append({
            "job": j["job"], "name": j.get("name", ""), "project_type": j.get("project_type", ""),
            "state": j.get("state", ""), "status": j.get("status", "active"),
            "contract_sum_ex_gst": str(contract), "variations_ex_gst": str(_money(rev["variation_income"])),
            "revised_contract_ex_gst": str(revised),
            "revenue_ex_gst": str(_money(revenue)), "costs_ex_gst": str(_money(total_cost)),
            "gross_profit_ex_gst": str(_money(profit)),
            "margin_pct": str(margin) if margin is not None else "",
            "target_margin_pct": str(target) if target is not None else "",
            "invoiced_pct_of_contract": str((revenue / revised * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if revised else "",
            "invoiced_inc_gst": str(_money(invoiced_inc)), "received_inc_gst": str(_money(received)),
            "outstanding_inc_gst": str(_money(invoiced_inc - received)),
            "billed_inc_gst": str(_money(billed_inc)), "paid_inc_gst": str(_money(paid_out)),
            "unpaid_bills_inc_gst": str(_money(billed_inc - paid_out)),
            "net_cash_inc_gst": str(_money(received - paid_out)),
            "materials_ex_gst": str(_money(cost.get("materials", Decimal("0")))),
            "subcontractors_ex_gst": str(_money(cost.get("subcontractors", Decimal("0")))),
            "labour_hours": str(hours), "labour_cost_ex_gst": str(_money(labour)), "days_on_site": str(len(days)),
            "start_date": j["start_date"], "contract_end_date": j.get("contract_end_date", ""), "pc_date": j.get("pc_date", ""),
            "days_elapsed": str(elapsed), "contract_days": str(contract_days) if contract_days else "",
            "time_used_pct": str((Decimal(elapsed) / contract_days * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if contract_days else "",
            "forecast_revenue_ex_gst": str(_money(final_revenue)), "forecast_costs_ex_gst": str(_money(forecast_cost)),
            "forecast_profit_ex_gst": str(_money(forecast_profit)),
            "forecast_margin_pct": str((forecast_profit / final_revenue * 100).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if final_revenue else "",
            "labour_hours_per_100k_revenue": str((hours / revenue * 100000).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if revenue and hours else "",
        })
        if margin is not None and target is not None and margin < target:
            warnings.append(f"{j['job']}: margin {margin}% is below the target {target}%")
        if contract_days and j.get("status") != "complete" and elapsed > contract_days:
            warnings.append(f"{j['job']}: {elapsed - contract_days} days past the contract completion date")

    # Benchmarks: completed jobs only.
    done = [r for r in rows if r["status"] == "complete"]
    bench = []

    def add(group: str, members: list) -> None:
        if not members:
            return
        avg_days = sum(Decimal(r["days_elapsed"]) for r in members) / len(members)
        margins = [Decimal(r["margin_pct"]) for r in members if r["margin_pct"]]
        bench.append({"group": group, "completed_jobs": str(len(members)),
                      "average_days": str(avg_days.quantize(Decimal("1"), rounding=ROUND_HALF_UP)),
                      "average_margin_pct": str((sum(margins) / len(margins)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)) if margins else ""})

    def mix(group: str, members: list) -> None:
        codes = {r["job"] for r in members}
        cats = sorted({c["category"] for c in costs if c["job"] in codes})
        for cat in cats:
            shares = [Decimal(c["pct_of_revenue"]) for c in costs if c["job"] in codes and c["category"] == cat and c["pct_of_revenue"]]
            if shares:
                cost_mix.append({"group": group, "category": cat, "completed_jobs": str(len(members)),
                                 "average_pct_of_revenue": str((sum(shares) / len(members)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))})

    cost_mix = []
    add("all", done)
    mix("all", done)
    for ptype in sorted({r["project_type"] for r in done if r["project_type"]}):
        add(ptype, [r for r in done if r["project_type"] == ptype])
        mix(ptype, [r for r in done if r["project_type"] == ptype])
    settle = [Decimal(x["days_to_settle"]) for x in txn_rows if x["side"] == "sale" and x["days_to_settle"]]
    if settle and bench:
        bench[0]["average_days_to_be_paid"] = str((sum(settle) / len(settle)).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
    by_group = {b["group"]: b for b in bench}
    for r in rows:
        b = by_group.get(r["project_type"]) or by_group.get("all")
        r["benchmark_group"] = b["group"] if b else ""
        r["benchmark_average_days"] = b["average_days"] if b else ""
        r["days_vs_average_pct"] = str((Decimal(r["days_elapsed"]) / Decimal(b["average_days"]) * 100).quantize(
            Decimal("0.1"), rounding=ROUND_HALF_UP)) if b and Decimal(b["average_days"]) else ""

    series, running = [], {}
    for (job, month) in sorted(monthly):
        m = monthly[(job, month)]
        running[job] = running.get(job, Decimal("0")) + m["revenue"] - m["costs"]
        series.append({"job": job, "month": month, "revenue_ex_gst": str(_money(m["revenue"])),
                       "costs_ex_gst": str(_money(m["costs"])), "received_inc_gst": str(_money(m["received"])),
                       "paid_inc_gst": str(_money(m["paid"])), "cumulative_profit_ex_gst": str(_money(running[job]))})
    result = {"as_at": as_at, "jobs": rows, "monthly": series, "costs": costs, "benchmarks": bench,
              "cost_mix": cost_mix, "transactions": txn_rows, "lines": line_rows, "warnings": warnings}
    return {"result": result, "fields": {"JOBS": str(len(rows))}}

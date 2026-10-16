"""Sanctioned money calculations for the Australian Builder's Brain.

Each public function is the computation behind one Attested Computation
concept in brain/computations/. Agents supply parameter values only; they
never edit these functions. If one changes, update `computation_sha256` in
every concept that points here (tools/okf_lint.py reports a mismatch).

All amounts are Decimal, in dollars, rounded half-up to the cent.
"""

from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

GST_RATE = Decimal("0.10")
CENT = Decimal("0.01")


def _money(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def _fmt(x: Decimal) -> str:
    return f"{x:,.2f}"


def gst(amount_ex_gst: Decimal) -> dict:
    """GST at 10% on an ex-GST amount."""
    amount = _money(amount_ex_gst)
    tax = _money(amount * GST_RATE)
    total = amount + tax
    return {
        "result": {"amount_ex_gst": str(amount), "gst": str(tax), "amount_inc_gst": str(total)},
        "fields": {"AMOUNT": _fmt(amount), "AMOUNT_GST": _fmt(tax), "AMOUNT_TOTAL": _fmt(total)},
    }


def ex_gst(amount_inc_gst: Decimal) -> dict:
    """Split a GST-inclusive amount into its ex-GST price and GST (GST = 1/11 of the total)."""
    total = _money(amount_inc_gst)
    tax = _money(total / 11)
    amount = total - tax
    return {
        "result": {"amount_ex_gst": str(amount), "gst": str(tax), "amount_inc_gst": str(total)},
        "fields": {"AMOUNT": _fmt(amount), "AMOUNT_GST": _fmt(tax), "AMOUNT_TOTAL": _fmt(total)},
    }


def variation_price(labour: Decimal, materials: Decimal, subcontractor: Decimal,
                    plant: Decimal, other: Decimal, margin_pct: Decimal) -> dict:
    """Price a variation: cost lines ex GST, plus the builder's margin, plus GST.

    margin_pct is the margin the contract allows on variations, as a
    percentage of cost (20 means cost x 1.20). Use 0 if the lines are
    already sell prices.

    The margin is also spread across the lines, so a client-facing cost
    breakdown can show each line at its sell price and an internal sheet can
    show cost against quoted per line. Any rounding cent goes to the largest
    line, so the sell lines always add up to the price.
    """
    names = ["labour", "materials", "subcontractor", "plant", "other"]
    cost_lines = {k: _money(v) for k, v in zip(names, (labour, materials, subcontractor, plant, other))}
    cost = sum(cost_lines.values(), Decimal("0"))
    margin_total = _money(cost * margin_pct / Decimal(100))
    amount = cost + margin_total

    factor = 1 + margin_pct / Decimal(100)
    sell_lines = {k: _money(v * factor) for k, v in cost_lines.items()}
    gap = amount - sum(sell_lines.values(), Decimal("0"))
    if gap:
        largest = max(names, key=lambda k: cost_lines[k])
        sell_lines[largest] += gap

    priced = gst(amount)
    result = {"cost_ex_gst": str(cost), "margin_ex_gst": str(margin_total), **priced["result"]}
    for k in names:
        result[f"{k}_cost_ex_gst"] = str(cost_lines[k])
        result[f"{k}_sell_ex_gst"] = str(sell_lines[k])
        result[f"{k}_margin_ex_gst"] = str(sell_lines[k] - cost_lines[k])
    return {"result": result, "fields": priced["fields"]}


def margin(quoted_ex_gst: Decimal, actual_cost_ex_gst: Decimal) -> dict:
    """Margin achieved on a quoted item, as the Variation Register calculates it.

    margin_pct is margin on sell price ((quoted - cost) / quoted).
    markup_pct is margin on cost ((quoted - cost) / cost).
    """
    quoted, cost = _money(quoted_ex_gst), _money(actual_cost_ex_gst)
    gain = quoted - cost
    margin_pct = _money(gain / quoted * 100) if quoted else Decimal("0.00")
    markup_pct = _money(gain / cost * 100) if cost else Decimal("0.00")
    return {
        "result": {"margin_ex_gst": str(gain), "margin_pct": str(margin_pct), "markup_pct": str(markup_pct)},
        "fields": {},
    }


def progress_claim(stages: list, retention_pct: Decimal, retention_cap_pct: Decimal,
                   retention_held_to_date: Decimal, contract_sum_ex_gst: Decimal) -> dict:
    """A progress claim from the stage schedule, ex GST, with optional retention.

    stages: [{"name", "contract_value", "pct_complete", "previously_claimed"}, ...]
    with money ex GST and pct_complete as a whole percentage (50 = half done).
    Approved variations go in as a stage of their own.

    Retention is retention_pct of this claim, limited (when retention_cap_pct
    is above 0) so the total held never passes retention_cap_pct of
    contract_sum_ex_gst.
    """
    rows, warnings = [], []
    value_total = previous_total = contract_total = base_total = Decimal("0")
    for s in stages:
        name = str(s["name"])
        value = _money(Decimal(str(s["contract_value"])))
        pct = Decimal(str(s.get("pct_complete", 0)))
        previous = _money(Decimal(str(s.get("previously_claimed", 0))))
        if not Decimal("0") <= pct <= Decimal("100"):
            raise ValueError(f"{name}: pct_complete must be between 0 and 100, got {pct}")
        completed = _money(value * pct / 100)
        this_claim = completed - previous
        if this_claim < 0:
            warnings.append(f"{name}: previously claimed ({previous}) is more than the value completed ({completed})")
        rows.append({"name": name, "contract_value": str(value), "pct_complete": str(pct),
                     "value_completed": str(completed), "previously_claimed": str(previous),
                     "this_claim": str(this_claim)})
        value_total += completed
        previous_total += previous
        contract_total += value
        if "variation" not in name.lower():
            base_total += value

    gross = value_total - previous_total
    retention = _money(gross * retention_pct / 100) if gross > 0 else Decimal("0.00")
    if retention_cap_pct > 0:
        room = _money(contract_sum_ex_gst * retention_cap_pct / 100) - _money(retention_held_to_date)
        retention = max(Decimal("0.00"), min(retention, room))
    net = gross - retention
    priced = gst(net)
    if contract_sum_ex_gst and base_total != _money(contract_sum_ex_gst):
        warnings.append(f"stage values (excluding variations) add up to {base_total}, "
                        f"not the contract sum {_money(contract_sum_ex_gst)}")
    result = {
        "stages": rows,
        "schedule_total_ex_gst": str(contract_total),
        "claimed_to_date_ex_gst": str(value_total),
        "previous_claims_ex_gst": str(previous_total),
        "this_claim_gross_ex_gst": str(gross),
        "retention_ex_gst": str(retention),
        "retention_held_after_ex_gst": str(_money(retention_held_to_date) + retention),
        "net_claim_ex_gst": priced["result"]["amount_ex_gst"],
        "gst": priced["result"]["gst"],
        "total_inc_gst": priced["result"]["amount_inc_gst"],
        "warnings": warnings,
    }
    return {"result": result, "fields": priced["fields"]}


def _parse_date(text: str) -> date:
    return datetime.strptime(text.strip(), "%d/%m/%Y").date()


def add_days(start_date: str, days: Decimal, day_type: str, non_working_days: list) -> dict:
    """Add calendar or working days to a date (DD/MM/YYYY).

    Working days skip Saturdays, Sundays and every date in non_working_days:
    public holidays, rostered days off and shutdowns, given as "DD/MM/YYYY"
    or a range "DD/MM/YYYY-DD/MM/YYYY". Used for revised completion dates
    and notice deadlines.
    """
    if day_type not in ("calendar", "working"):
        raise ValueError("day_type must be 'calendar' or 'working'")
    if days != days.to_integral_value() or days < 0:
        raise ValueError("days must be a whole number, 0 or more")
    start = _parse_date(start_date)
    skip = set()
    for item in non_working_days or []:
        first, _, last = str(item).partition("-")
        d, end = _parse_date(first), _parse_date(last or first)
        while d <= end:
            skip.add(d)
            d += timedelta(days=1)
    n = int(days)
    current, skipped = start, 0
    if day_type == "calendar":
        current = start + timedelta(days=n)
    else:
        while n:
            current += timedelta(days=1)
            if current.weekday() >= 5 or current in skip:
                skipped += 1
                continue
            n -= 1
    return {
        "result": {"start_date": start.strftime("%d/%m/%Y"), "days_added": str(int(days)), "day_type": day_type,
                   "end_date": current.strftime("%d/%m/%Y"), "end_weekday": current.strftime("%A"),
                   "calendar_days_elapsed": str((current - start).days), "non_working_days_skipped": str(skipped)},
        "fields": {},
    }

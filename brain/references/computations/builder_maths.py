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
    # Splitting each inc-GST stage into ex GST can lose a cent per stage.
    tolerance = CENT * len(stages)
    if contract_sum_ex_gst and abs(base_total - _money(contract_sum_ex_gst)) > tolerance:
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


def add_period(start_date: str, years: Decimal, months: Decimal, weeks: Decimal, days: Decimal) -> dict:
    """Add a calendar period to a date (DD/MM/YYYY): defects liability periods, warranty end dates.

    Years and months are added first, landing on the same day of the month
    (or the month's last day if it is shorter, so 29/02 + 1 year = 28/02),
    then weeks and days.
    """
    for name, value in (("years", years), ("months", months), ("weeks", weeks), ("days", days)):
        if value != value.to_integral_value() or value < 0:
            raise ValueError(f"{name} must be a whole number, 0 or more")
    start = _parse_date(start_date)
    total_months = start.month - 1 + int(years) * 12 + int(months)
    year, month = start.year + total_months // 12, total_months % 12 + 1
    next_month = date(year + (month == 12), month % 12 + 1, 1)
    last_day = (next_month - timedelta(days=1)).day
    end = date(year, month, min(start.day, last_day)) + timedelta(weeks=int(weeks), days=int(days))
    return {
        "result": {"start_date": start.strftime("%d/%m/%Y"), "end_date": end.strftime("%d/%m/%Y"),
                   "end_weekday": end.strftime("%A"), "calendar_days": str((end - start).days)},
        "fields": {},
    }


def final_account(contract_sum_ex_gst: Decimal, variations_additions: Decimal, variations_omissions: Decimal,
                  pc_ps_adjustments: Decimal, claimed_to_date: Decimal, retention_held: Decimal,
                  retention_released: Decimal) -> dict:
    """The final account and final claim, ex GST.

    Adjusted contract sum = contract sum + additions - omissions + PC/PS adjustments
    (adjustments may be negative). claimed_to_date is the gross total of all
    previous claims; the client has withheld retention_held from them.
    Final claim = adjusted contract sum - claimed to date + retention released now.
    """
    contract = _money(contract_sum_ex_gst)
    additions, omissions = _money(variations_additions), _money(abs(variations_omissions))
    adjustments = _money(pc_ps_adjustments)
    net_variations = additions - omissions
    adjusted = contract + net_variations + adjustments
    claimed, held, released = _money(claimed_to_date), _money(abs(retention_held)), _money(retention_released)
    warnings = []
    if released > held:
        raise ValueError(f"retention_released ({released}) is more than retention_held ({held})")
    net_received = claimed - held
    final = adjusted - claimed + released
    if final < 0:
        warnings.append(f"claims to date exceed the adjusted contract sum by {-final}: a credit is owed to the client")
    priced = gst(final) if final >= 0 else {"result": {"amount_ex_gst": str(final), "gst": str(_money(final * GST_RATE)),
                                                       "amount_inc_gst": str(final + _money(final * GST_RATE))}, "fields": {}}
    result = {
        "contract_sum_ex_gst": str(contract), "variations_additions_ex_gst": str(additions),
        "variations_omissions_ex_gst": str(omissions), "net_variations_ex_gst": str(net_variations),
        "pc_ps_adjustments_ex_gst": str(adjustments), "adjusted_contract_sum_ex_gst": str(adjusted),
        "claimed_to_date_ex_gst": str(claimed), "retention_held_ex_gst": str(held),
        "net_received_ex_gst": str(net_received), "retention_released_ex_gst": str(released),
        "retention_kept_ex_gst": str(held - released),
        "final_claim_ex_gst": priced["result"]["amount_ex_gst"], "gst": priced["result"]["gst"],
        "total_inc_gst": priced["result"]["amount_inc_gst"], "warnings": warnings,
    }
    return {"result": result, "fields": priced["fields"]}


def estimate_price(labour: Decimal, materials: Decimal, subcontract: Decimal,
                   contingency_pct: Decimal, markup_pct: Decimal) -> dict:
    """Price a quote from an estimate, the way the Trade Based Estimate Workbook does.

    Direct cost = labour + materials + subcontract (all ex GST).
    Contingency = direct cost x contingency_pct.
    Markup = (direct cost + contingency) x markup_pct (markup on cost).
    The client-facing lines are each cost line plus markup, with any rounding
    cent on the largest line so they add up to the quote.
    """
    lines = {"labour": _money(labour), "materials": _money(materials),
             "subcontract": _money(subcontract)}
    direct = sum(lines.values(), Decimal("0"))
    contingency = _money(direct * contingency_pct / 100)
    lines["contingency"] = contingency
    cost = direct + contingency
    markup = _money(cost * markup_pct / 100)
    subtotal = cost + markup
    factor = 1 + markup_pct / 100
    sell = {k: _money(v * factor) for k, v in lines.items()}
    gap = subtotal - sum(sell.values(), Decimal("0"))
    if gap:
        sell[max(lines, key=lambda k: lines[k])] += gap
    priced = gst(subtotal)
    margin_on_price = _money(markup / subtotal * 100) if subtotal else Decimal("0.00")
    result = {"direct_cost_ex_gst": str(direct), "contingency_ex_gst": str(contingency),
              "total_cost_ex_gst": str(cost), "markup_ex_gst": str(markup),
              "margin_on_price_pct": str(margin_on_price),
              **{f"{k}_quote_ex_gst": str(v) for k, v in sell.items()},
              "quote_ex_gst": priced["result"]["amount_ex_gst"], "gst": priced["result"]["gst"],
              "quote_inc_gst": priced["result"]["amount_inc_gst"]}
    return {"result": result, "fields": priced["fields"]}


def payment_schedule(contract_sum_inc_gst: Decimal, stages: list, deposit_cap_pct: Decimal) -> dict:
    """Turn stage percentages into stage amounts, inc and ex GST.

    stages: [{"name": "Deposit", "pct": 10}, ...], percentages of the contract
    sum that must add up to 100. Rounding cents go on the last stage so the
    amounts add up exactly. If deposit_cap_pct is above 0, a first stage named
    "Deposit" over the cap is flagged.
    """
    total = _money(contract_sum_inc_gst)
    pct_total = sum((Decimal(str(s["pct"])) for s in stages), Decimal("0"))
    if pct_total != 100:
        raise ValueError(f"stage percentages add up to {pct_total}, not 100")
    rows, running, warnings = [], Decimal("0"), []
    for i, s in enumerate(stages):
        pct = Decimal(str(s["pct"]))
        amount = total - running if i == len(stages) - 1 else _money(total * pct / 100)
        running += amount
        split = ex_gst(amount)["result"]
        rows.append({"name": str(s["name"]), "pct": str(pct), "amount_inc_gst": str(amount),
                     "amount_ex_gst": split["amount_ex_gst"], "gst": split["gst"]})
    first = stages[0] if stages else {}
    if deposit_cap_pct > 0 and "deposit" in str(first.get("name", "")).lower() and Decimal(str(first["pct"])) > deposit_cap_pct:
        warnings.append(f"deposit of {first['pct']}% is over the {deposit_cap_pct}% cap given")
    return {"result": {"contract_sum_inc_gst": str(total), "stages": rows, "warnings": warnings}, "fields": {}}


def site_week(start_date: str, on_date: str) -> dict:
    """Construction week number of a date, counting the site start date's week as week 1."""
    start, day = _parse_date(start_date), _parse_date(on_date)
    if day < start:
        raise ValueError("on_date is before the start date")
    elapsed = (day - start).days
    return {"result": {"start_date": start.strftime("%d/%m/%Y"), "on_date": day.strftime("%d/%m/%Y"),
                       "days_since_start": str(elapsed), "week_number": str(elapsed // 7 + 1)},
            "fields": {"WEEK_NUMBER": str(elapsed // 7 + 1)}}


def expiry_status(items: dict, on_date: str, warn_days: Decimal) -> dict:
    """Status of licences and insurances from their expiry dates (DD/MM/YYYY).

    items: {"Licence": "30/06/2027", "PL": "", ...}. An empty date is
    Incomplete. Each item is Expired, Expiring Soon (within warn_days) or
    Compliant; the overall status is the worst of them, using the Subbie
    Insurance and Licence Tracker's dropdown values.
    """
    today = _parse_date(on_date)
    rank = {"Compliant": 0, "Expiring Soon": 1, "Incomplete": 2, "Expired": 3}
    out = {}
    for name, value in items.items():
        if not str(value).strip():
            out[name] = {"expiry": "", "days_left": "", "status": "Incomplete"}
            continue
        d = _parse_date(str(value))
        left = (d - today).days
        status = "Expired" if left < 0 else "Expiring Soon" if left <= int(warn_days) else "Compliant"
        out[name] = {"expiry": d.strftime("%d/%m/%Y"), "days_left": str(left), "status": status}
    overall = max((v["status"] for v in out.values()), key=rank.get, default="Incomplete")
    return {"result": {"on_date": today.strftime("%d/%m/%Y"), "items": out, "overall_status": overall}, "fields": {}}

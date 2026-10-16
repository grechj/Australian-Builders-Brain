"""Sanctioned money calculations for the Australian Builder's Brain.

Each public function is the computation behind one Attested Computation
concept in brain/computations/. Agents supply parameter values only; they
never edit these functions. If one changes, update `computation_sha256` in
every concept that points here (tools/okf_lint.py reports a mismatch).

All amounts are Decimal, in dollars, rounded half-up to the cent.
"""

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

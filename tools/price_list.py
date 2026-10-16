"""Keep your own materials price list and match it to a takeoff.

Each user keeps their own list: prices they've looked up, from Bunnings or a
trade account or a supplier's quote. It lives with the user, not in this
repository (`my_prices*.csv` is git-ignored), and is reused job after job.

Usage:
    python tools/price_list.py new my_prices.csv
    python tools/price_list.py add my_prices.csv --product "90x45 MGP10 treated pine 4.8m" \\
        --unit "length" --price 21.50 --supplier "Bunnings Kotara" --item-number 0123456 \\
        --url https://www.bunnings.com.au/... --checked-on 17/10/2026
    python tools/price_list.py match out/takeoff_deck.json --prices my_prices.csv --out out/materials_lines.json
    python tools/price_list.py stale my_prices.csv --days 60

`match` writes a lines file ready for the materials_rom computation. Lines
with no good match, or whose price is older than --max-age days, are left
unpriced and listed in `to_look_up`, with a suggested search, for the user
to price (and add to their list).

Standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path

COLUMNS = ["product", "item_number", "unit", "pack_size", "price_inc_gst", "supplier", "url", "checked_on", "notes"]
# Tokens that must agree for a match to count: sizes, lengths, grades, treatment classes.
KEY_TOKEN = re.compile(r"^(\d+x\d+(x\d+)?|\d+(\.\d+)?(m|mm|kg|l|m2)|h[1-6]|mgp\d+|f\d+|m\d+|sl\d+|class\d)$")
STOP = {"to", "suit", "the", "and", "or", "of", "for", "with", "a", "lengths", "length", "each", "bags", "bag", "box", "if"}


def tokens(text: str) -> set[str]:
    text = text.lower().replace("×", "x")
    # "90 x 45" -> "90x45", but not "M12 x 150mm" (a bolt size then a length).
    text = re.sub(r"(?<![a-z\d])(\d+)\s*x\s*(\d+)(?!\d*mm\b)", r"\1x\2", text)
    text = re.sub(r"(\d)\s+(mm|m|kg|l)\b", r"\1\2", text)
    return {t for t in re.findall(r"[a-z0-9.]+", text) if (t not in STOP and len(t) > 1) or t.isdigit()}


def score(want: str, product: str) -> float:
    """0 to 1. Key tokens (sizes, grades, treatment) in the wanted item must all appear."""
    w, p = tokens(want), tokens(product)
    if not w:
        return 0.0
    keys = {t for t in w if KEY_TOKEN.match(t)}
    if keys - p:
        return 0.0
    return len(w & p) / len(w)


def read(path: Path) -> list[dict]:
    if not path.exists():
        raise SystemExit(f"No price list at {path}. Create one with: python tools/price_list.py new {path}")
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def age_days(checked_on: str) -> int | None:
    try:
        return (date.today() - datetime.strptime(checked_on.strip(), "%d/%m/%Y").date()).days
    except ValueError:
        return None


def cmd_new(args) -> None:
    path = Path(args.path)
    if path.exists():
        raise SystemExit(f"{path} already exists")
    with path.open("w", newline="") as f:
        csv.writer(f).writerow(COLUMNS)
    print(f"Created {path}. Keep it out of any public repository; my_prices*.csv is git-ignored here.")


def cmd_add(args) -> None:
    path = Path(args.path)
    rows = read(path)
    row = {"product": args.product, "item_number": args.item_number or "", "unit": args.unit,
           "pack_size": args.pack_size, "price_inc_gst": f"{float(args.price):.2f}", "supplier": args.supplier,
           "url": args.url or "", "checked_on": args.checked_on or date.today().strftime("%d/%m/%Y"), "notes": args.notes or ""}
    # Replace an earlier price for the same product and supplier.
    rows = [r for r in rows if not (r["product"].lower() == row["product"].lower() and r["supplier"].lower() == row["supplier"].lower())]
    rows.append(row)
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        w.writerows(rows)
    print(f"Saved {row['product']} at ${row['price_inc_gst']} ({row['supplier']}, {row['checked_on']})")


def cmd_match(args) -> None:
    takeoff = json.loads(Path(args.takeoff).read_text())
    items = takeoff.get("result", takeoff).get("items", [])
    prices = read(Path(args.prices))
    lines, to_look_up = [], []
    for it in items:
        want = f"{it.get('search', '')} {it.get('spec', '')}" if args.use_spec else it.get("search", "")
        ranked = sorted(((score(want, r["product"]), r) for r in prices), key=lambda x: -x[0])
        best_score, best = ranked[0] if ranked else (0.0, None)
        line = {"item": it["item"], "quantity": it["quantity"], "takeoff_unit": it["unit"], "search": it.get("search", "")}
        age = age_days(best["checked_on"]) if best else None
        if best and best_score >= args.min_score and (age is None or age <= args.max_age):
            line.update({"pack_size": best.get("pack_size") or "1", "unit_price_inc_gst": best["price_inc_gst"],
                         "product": f"{best['product']}" + (f" ({best['item_number']})" if best.get("item_number") else ""),
                         "source": best["supplier"], "priced_on": best["checked_on"], "match_score": round(best_score, 2),
                         "check": "confirm the product and pack size match the spec"})
        else:
            reason = "no matching product in the price list" if not best or best_score < args.min_score else f"price is {age} days old"
            line.update({"product": "", "source": "not priced", "reason": reason})
            to_look_up.append({"item": it["item"], "spec": it.get("spec", ""), "quantity": it["quantity"], "unit": it["unit"],
                               "reason": reason, "suggested_search": f"site:bunnings.com.au {it.get('search', '')}"})
        lines.append(line)
    out = {"lines": lines, "to_look_up": to_look_up,
           "summary": f"{len(lines) - len(to_look_up)} of {len(lines)} lines priced from {args.prices}"}
    text = json.dumps(out, indent=2)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(json.dumps(lines, indent=2))
        print(json.dumps({"summary": out["summary"], "to_look_up": to_look_up, "lines_written_to": args.out}, indent=2))
    else:
        print(text)


def cmd_stale(args) -> None:
    for r in read(Path(args.path)):
        age = age_days(r["checked_on"])
        if age is None or age > args.days:
            print(f"{r['product']} ({r['supplier']}): checked {r['checked_on'] or 'never'}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new"); p.add_argument("path")
    p = sub.add_parser("add"); p.add_argument("path")
    p.add_argument("--product", required=True); p.add_argument("--unit", required=True, help="what one price buys: length, sheet, bag, box, tin, each")
    p.add_argument("--price", required=True, help="inc GST"); p.add_argument("--supplier", required=True)
    p.add_argument("--pack-size", default="1", help="takeoff units per priced item, e.g. 500 screws per box")
    p.add_argument("--item-number"); p.add_argument("--url"); p.add_argument("--checked-on"); p.add_argument("--notes")
    p = sub.add_parser("match"); p.add_argument("takeoff"); p.add_argument("--prices", required=True)
    p.add_argument("--out"); p.add_argument("--min-score", type=float, default=0.6)
    p.add_argument("--max-age", type=int, default=90, help="days before a price needs re-checking")
    p.add_argument("--use-spec", action="store_true", help="match on the spec as well as the search phrase")
    p = sub.add_parser("stale"); p.add_argument("path"); p.add_argument("--days", type=int, default=60)
    args = parser.parse_args()
    {"new": cmd_new, "add": cmd_add, "match": cmd_match, "stale": cmd_stale}[args.cmd](args)


if __name__ == "__main__":
    main()

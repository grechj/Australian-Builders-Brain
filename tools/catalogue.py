"""What building materials are sold as, and how a takeoff quantity becomes things to buy.

Usage:
    python tools/catalogue.py classify "Decking screws stainless or class 4"
    python tools/catalogue.py infer "Dulux Wash&Wear Low Sheen White 10L" --unit litres
    python tools/catalogue.py mix 23 --option 4:89 --option 10:199 --option 15:279   # litres needed, pack:price
    python tools/catalogue.py page            # rewrite brain/references/product_catalogue.md
    python tools/catalogue.py page --check    # fail if it's out of date

The facts live in tools/catalogue.yaml: supplier-neutral stock sizes and
pack sizes, never prices. tools/price_list.py uses this to read pack sizes
off product names, convert per-metre prices, and buy the cheapest mix of
pack sizes.
"""

from __future__ import annotations

import argparse
import itertools
import json
import re
import sys
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "tools" / "catalogue.yaml"
PAGE = ROOT / "brain" / "references" / "product_catalogue.md"


def load() -> dict:
    return yaml.safe_load(DATA.read_text())["families"]


def family_of(text: str) -> str | None:
    """The family whose keyword best matches the text (the longest matching keyword wins)."""
    t = " " + re.sub(r"[^a-z0-9.]+", " ", text.lower()) + " "
    best, best_len = None, 0
    for name, fam in load().items():
        for kw in fam.get("keywords", []):
            k = " " + re.sub(r"[^a-z0-9.]+", " ", kw.lower()) + " "
            if k in t and len(k) > best_len:
                best, best_len = name, len(k)
    return best


def unit_kind(takeoff_unit: str) -> str:
    """What a takeoff unit counts: litres, m2, lineal_m, length, bag, or count."""
    u = (takeoff_unit or "").lower()
    if "litre" in u or u.strip() in ("l", "lt"):
        return "litres"
    if "m²" in u or "m2" in u:
        return "m2"
    if "lineal" in u:
        return "lineal_m"
    if u.startswith("lengths of"):
        return "length"
    if "bag" in u:
        return "bag"
    if u.startswith(("sheet", "box", "roll", "pack", "tin", "cartridge", "m³", "m3", "lot")):
        return u.split()[0]
    return "count"


def infer_pack(product: str, takeoff_unit: str) -> tuple[Decimal, str] | None:
    """How many takeoff units one priced item holds, read off the product's name.

    "Paint 10L" for a line in litres is 10; "Decking screws 500 pack" for a
    line counted in screws is 500; a "1.35 x 30m" roll for a line in m² is
    40.5. Returns None when the name doesn't say (the price is then per unit).
    """
    p = product.lower().replace("×", "x")
    kind = unit_kind(takeoff_unit)
    if kind == "litres":
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:l|lt|litre|litres|liter)\b", p)
        if m:
            return Decimal(m.group(1)), f"{m.group(1)} L in the product name"
    if kind == "count":
        m = re.search(r"(\d+)\s*(?:pk|pack|pce|pcs|pc|piece|pieces)\b", p) or re.search(r"\b(?:pack|box|tub|bag|jar) of (\d+)", p)
        if m:
            return Decimal(m.group(1)), f"pack of {m.group(1)} in the product name"
    if kind == "m2":
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:m2|m²|sq ?m)\b", p)
        if m:
            return Decimal(m.group(1)), f"{m.group(1)} m² in the product name"
        m = re.search(r"(\d+(?:\.\d+)?)\s*(mm|m)?\s*x\s*(\d+(?:\.\d+)?)\s*m\b", p)
        if m:
            w = Decimal(m.group(1)) / (1000 if m.group(2) == "mm" else 1)
            area = Decimal(format((w * Decimal(m.group(3))).normalize(), "f"))
            return area, f"roll {m.group(1)}{m.group(2) or ' m'} x {m.group(3)} m = {area} m²"
    if kind == "lineal_m":
        m = re.search(r"x\s*(\d+(?:\.\d+)?)\s*m\b", p) or re.search(r"(\d+(?:\.\d+)?)\s*m\s*(?:roll|coil)\b", p)
        if m:
            return Decimal(m.group(1)), f"{m.group(1)} m roll in the product name"
    return None


def length_of(takeoff_unit: str) -> Decimal | None:
    m = re.match(r"lengths of (\d+(?:\.\d+)?) m", takeoff_unit or "")
    return Decimal(m.group(1)) if m else None


def cheapest_mix(quantity: Decimal, options: list[tuple[Decimal, Decimal]], max_each: int = 50) -> list[tuple[Decimal, int]]:
    """The cheapest set of packs that covers the quantity.

    options: [(pack size, price per pack)]. Ties go to less left over, then
    fewer packs. Returns [(pack size, count)], largest packs first.
    """
    quantity = Decimal(str(quantity))
    options = sorted({(Decimal(str(s)), Decimal(str(p))) for s, p in options if Decimal(str(s)) > 0}, reverse=True)[:4]
    best = None
    limits = [min(max_each, int(quantity / s) + 1) for s, _ in options]
    for counts in itertools.product(*(range(n + 1) for n in limits)):
        covered = sum(c * s for c, (s, _) in zip(counts, options))
        if covered < quantity:
            continue
        cost = sum(c * p for c, (_, p) in zip(counts, options))
        key = (cost, covered - quantity, sum(counts))
        if best is None or key < best[0]:
            best = (key, counts)
    if best is None:
        raise ValueError("no mix of packs covers the quantity")
    return [(s, c) for c, (s, _) in zip(best[1], options) if c]


def base_name(product: str) -> str:
    """The product's name without its pack size, so a 4 L and a 10 L tin of the same paint compare equal."""
    p = product.lower().replace("×", "x")
    p = re.sub(r"\(\d{6,7}\)", "", p)
    p = re.sub(r"\b\d+(?:\.\d+)?\s*(?:l|lt|litre|litres|pk|pack|pce|pcs|kg)\b", "", p)
    p = re.sub(r"\b(?:pack|box|tub) of \d+\b", "", p)
    return re.sub(r"\s+", " ", p).strip(" -,")


def page() -> str:
    fams = load()
    lines = ["---", "type: Reference", "title: Product catalogue (what materials are sold as)",
             "description: Supplier-neutral stock sizes and pack sizes for common building materials, and how the brain turns a takeoff quantity into things to buy. No prices.",
             "tags: [materials, catalogue, packs, stock_lengths, pricing]", "status: draft",
             "generated: { by: tool:catalogue.py, at: 2026-10-21T00:00:00Z }", "---", "",
             "> **Generated from `tools/catalogue.yaml`** by `python tools/catalogue.py page`. Edit the YAML, not this page.",
             "> \"Usual\" sizes are what's commonly stocked in Australia: always check the actual product.", "",
             "Prices never live here: each user keeps their own (see [materials estimating](/contracts/materials_estimating.md)).",
             "When the brain matches a takeoff line to a user's price, it uses this catalogue to:", "",
             "- read the pack size off the product's name (a 10 L tin, a box of 500 screws, a 1.35 x 30 m roll) when it isn't recorded;",
             "- convert a per-metre price to the stock length the takeoff counts;",
             "- buy the cheapest mix of pack sizes when the user has prices for more than one (two 10 L tins and a 4 L tin, say).", "",
             "| Family | Sold as | Usual stock | Notes |", "|---|---|---|---|"]
    for name, f in fams.items():
        stock = []
        if f.get("sizes"):
            stock.append("sizes " + ", ".join(map(str, f["sizes"])))
        if f.get("lengths_m"):
            stock.append("lengths " + ", ".join(f"{x:g}" for x in f["lengths_m"]) + " m")
        if f.get("sheet_sizes_m"):
            stock.append("sheets " + ", ".join(f["sheet_sizes_m"]) + " m")
        if f.get("packs"):
            stock.append("packs of " + ", ".join(f"{x:g}" for x in f["packs"]))
        if f.get("packs_kg"):
            stock.append(", ".join(f"{x:g}" for x in f["packs_kg"]) + " kg bags")
        note = " ".join(x for x in (f.get("coverage", "") and f"Coverage: {f['coverage']}.", f.get("notes", "")) if x)
        title = f"[{f['title']}]({f['guide']})" if f.get("guide") else f["title"]
        sold = f["sold_as"].replace("_", " ") + (f" (priced per {f['per'].replace('_', ' ').replace('m2', 'm²')})" if f.get("per") else "")
        lines.append(f"| {title} | {sold} | {'; '.join(stock) or '–'} | {note or '–'} |")
    return "\n".join(lines) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("classify"); p.add_argument("text")
    p = sub.add_parser("infer"); p.add_argument("product"); p.add_argument("--unit", required=True)
    p = sub.add_parser("mix"); p.add_argument("quantity"); p.add_argument("--option", action="append", required=True, help="pack:price")
    p = sub.add_parser("page"); p.add_argument("--check", action="store_true")
    a = parser.parse_args()
    if a.cmd == "classify":
        fam = family_of(a.text)
        print(json.dumps({"family": fam, **({k: v for k, v in load()[fam].items() if k != "keywords"} if fam else {})}, indent=2, default=str))
    elif a.cmd == "infer":
        r = infer_pack(a.product, a.unit)
        print(json.dumps({"pack_size": str(r[0]), "because": r[1]} if r else {"pack_size": None, "because": "the name doesn't say"}))
    elif a.cmd == "mix":
        opts = [tuple(Decimal(x) for x in o.split(":")) for o in a.option]
        mix = cheapest_mix(Decimal(a.quantity), opts)
        price = dict(opts)
        print(json.dumps({"buy": [{"pack": str(s), "count": c} for s, c in mix],
                          "cost": str(sum(price[s] * c for s, c in mix))}, indent=2))
    else:
        text = page()
        if a.check:
            if not PAGE.exists() or PAGE.read_text() != text:
                sys.exit("brain/references/product_catalogue.md is out of date: run python tools/catalogue.py page")
            print("product catalogue page is current")
        else:
            PAGE.write_text(text)
            print(f"wrote {PAGE.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

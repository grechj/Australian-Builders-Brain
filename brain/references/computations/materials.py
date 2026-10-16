"""Sanctioned materials takeoff and rough-order-of-magnitude pricing.

materials_takeoff turns a job description into a materials list: what to
buy, how many, in what lengths or packs, and the rule used for each line.
materials_rom prices that list from unit prices (for example Bunnings
retail prices) and gives a rough order of magnitude range.

These are estimating rules of thumb, not engineering. Member sizes, spans
and fixings come from AS 1684, the manufacturer or the engineer, and the
user supplies them as text (`joist_size: "140x45 H3 treated pine"`). Every
default is returned in `assumptions` so it can be checked and changed.

Agents supply parameter values only; they never edit these functions. If
one changes, update `computation_sha256` in the concepts that point here.
"""

from __future__ import annotations

import math
from decimal import ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
TIMBER_STOCK = [Decimal(x) for x in ("2.4", "3.0", "3.6", "4.2", "4.8", "5.4", "6.0")]


def _d(value, default=None) -> Decimal:
    if value is None or value == "":
        if default is None:
            raise ValueError("missing required value")
        value = default
    return Decimal(str(value))


def _money(x: Decimal) -> Decimal:
    return x.quantize(CENT, rounding=ROUND_HALF_UP)


def _ceil(x: Decimal) -> int:
    return int(math.ceil(x))


def _stock(length: Decimal, stock: list[Decimal]) -> tuple[Decimal, int]:
    """Shortest stock length that covers `length`, or the longest, joined."""
    for s in sorted(stock):
        if s >= length:
            return s, 1
    longest = max(stock)
    return longest, _ceil(length / longest)


class Takeoff:
    def __init__(self, job: dict):
        self.job = job
        self.items: list[dict] = []
        self.assumptions: dict[str, str] = {}
        self.notes: list[str] = []

    def get(self, key: str, default=None, why: str = "") -> Decimal:
        if key in self.job and self.job[key] not in (None, ""):
            return _d(self.job[key])
        if default is None:
            raise ValueError(f"{self.job.get('type')}: '{key}' is required")
        self.assumptions[key] = f"{default}{' (' + why + ')' if why else ''}"
        return _d(default)

    def text(self, key: str, default: str) -> str:
        value = self.job.get(key)
        if value in (None, ""):
            self.assumptions[key] = default
            return default
        return str(value)

    def add(self, key: str, item: str, spec: str, quantity, unit: str, basis: str, search: str = ""):
        q = quantity if isinstance(quantity, int) else _money(Decimal(quantity))
        self.items.append({"key": key, "item": item, "spec": spec, "quantity": str(q), "unit": unit,
                           "basis": basis, "search": search or f"{item} {spec}".strip()})

    def timber(self, key: str, item: str, size: str, members: int, length: Decimal, basis: str, stock=None):
        stock_len, per_member = _stock(length, stock or TIMBER_STOCK)
        # "2/140x45" means two pieces side by side (a doubled bearer or lintel).
        ply = int(size.split("/")[0]) if size[:1].isdigit() and "/" in size[:3] else 1
        pieces = members * per_member * ply
        if ply > 1:
            basis += f", doubled ({ply} pieces side by side)"
        joined = f", joined (each {length} m needs {per_member} x {stock_len} m)" if per_member > 1 else ""
        self.add(key, item, f"{size}, {stock_len} m lengths", pieces, f"lengths of {stock_len} m",
                 f"{basis}: {members} members x {length} m{joined}", f"{size.split('/', 1)[1] if ply > 1 else size} {stock_len}m")


def _deck(t: Takeoff) -> None:
    L, W = t.get("length_m"), t.get("width_m")
    h = t.get("height_m", "0.6", "post height above footing")
    js = t.get("joist_spacing_mm", "450", "common for timber decking; check the board manufacturer")
    bs = t.get("bearer_spacing_mm", "1800", "check AS 1684 span tables for the bearer size")
    ps = t.get("post_spacing_mm", "1800", "check AS 1684 span tables")
    bw = t.get("board_width_mm", "90")
    gap = t.get("board_gap_mm", "4")
    board_stock = t.get("board_length_m", "5.4")
    spare = t.get("spare_pct", "5", "offcuts and rejects")
    fd = t.get("footing_mm", "300", "square hole, side length")
    fdepth = t.get("footing_depth_mm", "600", "check soil and engineer's details")
    bag_yield = t.get("concrete_bag_yield_m3", "0.0095", "typical 20 kg premix bag")
    joist = t.text("joist_size", "joist size per AS 1684 (for example 140x45 H3 treated pine)")
    bearer = t.text("bearer_size", "bearer size per AS 1684 (for example 2/140x45 H3 treated pine)")
    post = t.text("post_size", "90x90 H4 treated pine post")
    board = t.text("board", f"{bw} mm decking board")

    joists = _ceil(L * 1000 / js) + 1
    bearer_lines = _ceil(W * 1000 / bs) + 1
    posts_per_line = _ceil(L * 1000 / ps) + 1
    posts = bearer_lines * posts_per_line
    rows = _ceil(W * 1000 / (bw + gap))
    t.timber("joists", "Joists", joist, joists, W, f"length {L} m / {js} mm spacing + 1 = {joists} joists, each spanning the {W} m width")
    t.timber("bearers", "Bearers", bearer, bearer_lines, L, f"width {W} m / {bs} mm spacing + 1 = {bearer_lines} bearer lines along the {L} m length")
    post_stock = Decimal("2.4")
    per_stock = max(1, int(post_stock / h)) if h <= post_stock else 1
    t.add("posts", "Posts", f"{post}, {post_stock} m lengths", _ceil(Decimal(posts) / per_stock), f"lengths of {post_stock} m",
          f"{bearer_lines} bearer lines x {posts_per_line} posts ({ps} mm spacing) = {posts} posts at {h} m, {per_stock} per length",
          f"{post} 2.4m")
    pieces_per_row = _ceil(L / board_stock)
    boards = _ceil(rows * pieces_per_row * (1 + spare / 100))
    t.add("decking", "Decking boards", f"{board}, {board_stock} m lengths", boards, f"lengths of {board_stock} m",
          f"width {W} m / ({bw} + {gap}) mm = {rows} rows x {pieces_per_row} per row + {spare}% spare", f"{board} {board_stock}m")
    screws = rows * joists * 2
    t.add("decking_screws", "Decking screws", "stainless or class 4, to suit the board", screws, "screws",
          f"{rows} rows x {joists} joists x 2 screws per crossing", "decking screws stainless")
    t.add("joist_fixings", "Joist-to-bearer fixings", "triple grips or framing anchors, galvanised", joists * bearer_lines, "each",
          f"{joists} joists x {bearer_lines} bearers", "triple grip galvanised")
    t.add("post_anchors", "Post anchors / stirrups", "galvanised, to suit the post", posts, "each", f"1 per post", "post stirrup galvanised")
    t.add("bolts", "Cup head bolts with nuts and washers", "M12 galvanised, to suit post + bearer", posts * 2, "each",
          "2 per post-to-bearer connection", "cup head bolt M12 galvanised")
    hole = (fd / 1000) ** 2 * (fdepth / 1000)
    bags = _ceil(hole * posts / bag_yield)
    t.add("concrete", "Concrete premix", "20 kg bags", bags, "bags",
          f"{posts} holes x {fd} x {fd} x {fdepth} mm = {_money(hole * posts)} m³ / {bag_yield} m³ per bag", "concrete mix 20kg")
    if hole * posts > Decimal("0.5"):
        t.notes.append(f"Footings need {_money(hole * posts)} m³ of concrete ({bags} bags): ready-mix from a concrete supplier is usually cheaper above about 0.5 m³.")
    t.notes.append("Member sizes, spans, bracing and fixings must come from AS 1684, the timber supplier's span tables or an engineer. Decks over 1 m above ground usually need balustrades (NCC) and may need approval.")


def _stud_wall(t: Takeoff) -> None:
    L, H = t.get("length_m"), t.get("height_m", "2.4")
    sp = t.get("stud_spacing_mm", "450", "450 or 600 to suit the lining")
    openings = int(t.get("openings", "0", "doors or windows"))
    junctions = int(t.get("junctions", "0", "corners and T-junctions, 2 extra studs each"))
    size = t.text("stud_size", "90x35 MGP10 pine (non-load-bearing internal wall)")
    nog_rows = max(1, _ceil(H / Decimal("1.35")) - 1)
    studs = _ceil(L * 1000 / sp) + 1 + 2 * openings + 2 * junctions
    t.timber("studs", "Studs", size, studs, H, f"length {L} m / {sp} mm + 1, plus 2 per opening and junction = {studs} studs at {H} m")
    t.timber("plates", "Top and bottom plates", size, 2, L, "2 plates along the wall")
    t.timber("noggings", "Noggings", size, nog_rows, L, f"{nog_rows} row(s) for a {H} m wall")
    nails = studs * 4 + nog_rows * (_ceil(L * 1000 / sp) + 1) * 2
    t.add("nails", "Framing nails or screws", "75 mm galvanised, or framing screws", nails, "each",
          "4 per stud at the plates + 2 per nogging joint", "framing nails 75mm galvanised")
    t.notes.append("This is a non-load-bearing internal wall. Load-bearing and external walls need sizes, lintels and bracing from AS 1684 or an engineer.")


def _plasterboard(t: Takeoff) -> None:
    if "area_m2" in t.job:
        wall_area = t.get("area_m2")
        perimeter = t.get("perimeter_m", "0", "for cornice; 0 = no cornice")
        ceiling_area = Decimal("0")
    else:
        L, W, H = t.get("length_m"), t.get("width_m"), t.get("height_m", "2.4")
        perimeter = 2 * (L + W)
        wall_area = perimeter * H
        ceiling_area = L * W if str(t.job.get("ceiling", "true")).lower() in ("true", "yes", "1") else Decimal("0")
    openings = t.get("openings_m2", "0", "door and window area to deduct")
    sheet_l = t.get("sheet_length_m", "2.4")
    sheet_w = t.get("sheet_width_m", "1.2")
    spare = t.get("spare_pct", "10", "offcuts and breakage")
    screws_m2 = t.get("screws_per_m2", "14", "rule of thumb; follow the manufacturer's fixing guide")
    compound_m2 = t.get("compound_kg_per_m2", "0.6", "base and topping coats, rule of thumb")
    tape_m2 = t.get("tape_m_per_m2", "1.4", "rule of thumb")
    board = t.text("board", "10 mm standard plasterboard")
    area = wall_area + ceiling_area - openings
    sheets = _ceil(area * (1 + spare / 100) / (sheet_l * sheet_w))
    t.add("sheets", "Plasterboard sheets", f"{board}, {sheet_l} x {sheet_w} m", sheets, "sheets",
          f"{_money(area)} m² (walls {_money(wall_area)} + ceiling {_money(ceiling_area)} - openings {openings}) + {spare}% / {_money(sheet_l * sheet_w)} m² per sheet",
          f"plasterboard {board} {sheet_l}m")
    t.add("screws", "Plasterboard screws", "to suit framing (timber or steel)", _ceil(area * screws_m2), "each",
          f"{_money(area)} m² x {screws_m2} per m²", "plasterboard screws")
    t.add("adhesive", "Stud adhesive", "cartridges", _ceil(Decimal(sheets) / 3), "cartridges", "1 cartridge per 3 sheets (rule of thumb)", "stud adhesive plasterboard")
    t.add("compound", "Jointing compound", "base and topping", _ceil(area * compound_m2 / 20), "20 kg bags (or equivalent)",
          f"{_money(area)} m² x {compound_m2} kg/m² / 20 kg", "plaster base coat compound")
    t.add("tape", "Paper jointing tape", "75 m rolls", _ceil(area * tape_m2 / 75), "rolls", f"{_money(area)} m² x {tape_m2} m/m² / 75 m", "paper joint tape")
    if perimeter > 0:
        cornice = _ceil(perimeter * Decimal("1.1") / Decimal("4.8"))
        t.add("cornice", "Cornice", "90 mm cove, 4.8 m lengths", cornice, "lengths of 4.8 m", f"perimeter {perimeter} m + 10% / 4.8 m", "cove cornice 90mm 4.8m")
    t.notes.append("Wet areas need water-resistant board; fire-rated walls need the specified system. Quantities of compound and screws vary with the system: check the manufacturer's guide.")


def _slab(t: Takeoff) -> None:
    L, W = t.get("length_m"), t.get("width_m")
    th = t.get("thickness_mm", "100")
    waste = t.get("waste_pct", "10", "uneven ground and spillage")
    bag_yield = t.get("concrete_bag_yield_m3", "0.0095", "typical 20 kg premix bag")
    chair_sp = t.get("bar_chair_spacing_m", "0.8", "rule of thumb")
    mesh = t.text("mesh", "SL72 reinforcing mesh, 6.0 x 2.4 m")
    area = L * W
    volume = area * th / 1000 * (1 + waste / 100)
    t.add("concrete_m3", "Concrete", f"{th} mm slab, ready-mix (check the strength class)", _money(volume), "m³",
          f"{L} x {W} m x {th} mm + {waste}%", "concrete")
    bags = _ceil(volume / bag_yield)
    t.add("concrete_bags", "Concrete premix (if mixing by hand)", "20 kg bags", bags, "bags",
          f"{_money(volume)} m³ / {bag_yield} m³ per bag (only sensible for small pours)", "concrete mix 20kg")
    sheets = _ceil(area / Decimal("12.76"))
    t.add("mesh", "Reinforcing mesh", mesh, sheets, "sheets", f"{_money(area)} m² / 12.76 m² per sheet after 200 mm laps", "reinforcing mesh SL72")
    chairs = (_ceil(L / chair_sp) + 1) * (_ceil(W / chair_sp) + 1)
    t.add("bar_chairs", "Bar chairs", "to suit mesh and cover", chairs, "each", f"grid at {chair_sp} m spacing", "bar chairs")
    t.add("membrane", "Vapour barrier / membrane", "0.2 mm polyethylene", _money(area * Decimal("1.15")), "m²", f"{_money(area)} m² + 15% for laps", "builders film 200um")
    perim = 2 * (L + W)
    t.add("formwork", "Edge formwork", f"timber to suit {th} mm depth, 4.8 m lengths", _ceil(perim * Decimal("1.1") / Decimal("4.8")), "lengths of 4.8 m",
          f"perimeter {perim} m + 10% / 4.8 m", "formwork pine 4.8m")
    if volume > Decimal("0.5"):
        t.notes.append(f"{_money(volume)} m³ is more than about 0.5 m³: ready-mix delivered by a concrete supplier is usually cheaper and better than premix bags.")
    t.notes.append("Paths and shed slabs only. House slabs and footings must follow the engineer's design (AS 2870).")


def _fence(t: Takeoff) -> None:
    L = t.get("length_m")
    H = t.get("height_m", "1.8")
    sp = t.get("post_spacing_m", "2.4")
    cover = t.get("paling_cover_mm", "100", "lapped palings, about 100 mm cover each")
    bags_post = t.get("concrete_bags_per_post", "2", "20 kg bags")
    rails_n = int(t.get("rails", "3" if H > Decimal("1.5") else "2"))
    post_size = t.text("post_size", "100x75 H4 treated pine post")
    rail_size = t.text("rail_size", "75x50 H3 treated pine rail")
    paling = t.text("paling", "150x12 treated pine paling")
    bays = _ceil(L / sp)
    posts = bays + 1
    post_len = H + Decimal("0.6")
    t.timber("posts", "Posts", post_size, posts, post_len, f"{bays} bays of {sp} m + 1 = {posts} posts at {post_len} m ({H} m + 600 mm in ground)")
    rail_pieces = rails_n * _ceil(L / Decimal("4.8"))
    t.add("rails", "Rails", f"{rail_size}, 4.8 m lengths", rail_pieces, "lengths of 4.8 m", f"{rails_n} rails x {L} m in 4.8 m lengths (2 bays each)", f"{rail_size} 4.8m")
    palings = _ceil(L * 1000 / cover)
    t.add("palings", "Palings", f"{paling}, {H} m", palings, "each", f"{L} m / {cover} mm cover", f"{paling} {H}m")
    t.add("nails", "Paling nails", "galvanised, 50 mm", palings * rails_n * 2, "each", f"2 per paling per rail", "galvanised nails 50mm")
    t.add("concrete", "Concrete premix", "20 kg bags", int(posts * bags_post), "bags", f"{posts} posts x {bags_post} bags", "concrete mix 20kg")
    t.notes.append("Check the boundary, dividing fence rules for the state, and Before You Dig Australia (BYDA) service locations before digging.")


def _tiling(t: Takeoff) -> None:
    area = t.get("area_m2")
    tl, tw = t.get("tile_length_mm", "600"), t.get("tile_width_mm", "300")
    joint = t.get("joint_mm", "3")
    depth = t.get("tile_thickness_mm", "10")
    waste = t.get("waste_pct", "10", "15% for diagonal layouts or many cuts")
    box_m2 = t.get("box_m2", "1.44", "check the tile box coverage")
    adh = t.get("adhesive_kg_per_m2", "4", "10 mm notched trowel, rule of thumb")
    wp_area = t.get("waterproofing_m2", "0", "wet-area membrane area; 0 = none")
    wp_rate = t.get("membrane_l_per_m2", "1.5", "two coats; follow the manufacturer")
    tile = t.text("tile", f"{tl}x{tw} mm tile")
    tiles_area = area * (1 + waste / 100)
    t.add("tiles", "Tiles", f"{tile}, boxes of {box_m2} m²", _ceil(tiles_area / box_m2), "boxes",
          f"{area} m² + {waste}% / {box_m2} m² per box", tile)
    t.add("adhesive", "Tile adhesive", "20 kg bags", _ceil(area * adh / 20), "bags", f"{area} m² x {adh} kg/m² / 20 kg", "tile adhesive 20kg")
    grout_kg = (tl + tw) / (tl * tw) * depth * joint * Decimal("1.6") * area
    t.add("grout", "Grout", "5 kg bags", _ceil(grout_kg * Decimal("1.1") / 5), "bags",
          f"(L+W)/(LxW) x depth x joint x 1.6 x {area} m² = {_money(grout_kg)} kg + 10%", "tile grout 5kg")
    if wp_area > 0:
        litres = wp_area * wp_rate
        t.add("membrane", "Waterproofing membrane", "liquid membrane, 2 coats, with primer and bond breaker", _money(litres), "litres",
              f"{wp_area} m² x {wp_rate} L/m²", "waterproofing membrane")
        t.notes.append("Wet-area waterproofing must comply with AS 3740 and the NCC. In most states it must be done by a licensed waterproofer and certified.")


def _painting(t: Takeoff) -> None:
    area = t.get("area_m2")
    coats = t.get("coats", "2")
    cover = t.get("coverage_m2_per_l", "16", "per coat, acrylic walls; check the tin")
    prime = str(t.job.get("primer", "false")).lower() in ("true", "yes", "1")
    paint = t.text("paint", "low-sheen acrylic interior paint")
    litres = area * coats / cover * Decimal("1.1")
    t.add("paint", "Paint", paint, _money(litres), "litres", f"{area} m² x {coats} coats / {cover} m²/L + 10%", paint)
    if prime:
        t.add("primer", "Primer / sealer undercoat", "to suit the surface", _money(area / Decimal("12") * Decimal("1.1")), "litres",
              f"{area} m² / 12 m²/L + 10%", "primer sealer undercoat")
    t.add("sundries", "Painting sundries", "roller covers, brushes, tape, drop sheets, filler", 1, "lot", "allowance", "painting sundries")


JOBS = {"timber_deck": _deck, "stud_wall": _stud_wall, "plasterboard": _plasterboard, "concrete_slab": _slab,
        "paling_fence": _fence, "tiling": _tiling, "painting": _painting}


def materials_takeoff(job: dict) -> dict:
    """Materials list for one job. job = {"type": one of JOBS, ...dimensions and options}."""
    kind = job.get("type")
    if kind not in JOBS:
        raise ValueError(f"type must be one of: {', '.join(JOBS)}")
    t = Takeoff(job)
    JOBS[kind](t)
    return {"result": {"type": kind, "items": t.items, "assumptions": t.assumptions, "notes": t.notes}, "fields": {}}


def materials_rom(lines: list, low_pct: Decimal, high_pct: Decimal) -> dict:
    """Price a materials list and give a rough order of magnitude range.

    lines: [{"item", "quantity", "pack_size", "unit_price_inc_gst", "product", "source", "priced_on"}, ...]
    quantity is in the takeoff's unit (screws, litres, sheets). pack_size is
    how many of those units one priced item holds (a box of 500 screws, a
    4 L tin): packs to buy = quantity / pack_size, rounded up. Leave
    pack_size as 1 when the price is per unit. Lines without a price are
    listed as unpriced and left out of the total.
    Range = total x (1 - low_pct%) to total x (1 + high_pct%).
    """
    priced, unpriced, total = [], [], Decimal("0")
    for line in lines:
        price = line.get("unit_price_inc_gst")
        qty = Decimal(str(line.get("quantity", 0)))
        pack = Decimal(str(line.get("pack_size", 1) or 1))
        if price in (None, ""):
            unpriced.append(str(line.get("item")))
            continue
        packs = _ceil(qty / pack)
        line_total = _money(packs * Decimal(str(price)))
        total += line_total
        priced.append({"item": str(line.get("item")), "product": str(line.get("product", "")),
                       "quantity": str(qty), "pack_size": str(pack), "packs": str(packs),
                       "unit_price_inc_gst": str(_money(Decimal(str(price)))),
                       "line_total_inc_gst": str(line_total), "source": str(line.get("source", "")),
                       "priced_on": str(line.get("priced_on", ""))})
    gst_part = _money(total / 11)
    low = _money(total * (1 - low_pct / 100))
    high = _money(total * (1 + high_pct / 100))
    return {"result": {"lines": priced, "unpriced": unpriced, "total_inc_gst": str(total),
                       "gst": str(gst_part), "total_ex_gst": str(total - gst_part),
                       "rom_low_inc_gst": str(low), "rom_high_inc_gst": str(high),
                       "rom_range": f"-{low_pct}% / +{high_pct}%"}, "fields": {}}

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



def _electrical(t: Takeoff) -> None:
    gpo = int(t.get("power_points", "0", "double power points"))
    lights = int(t.get("light_points", "0", "light points (downlights, oyster lights, pendants)"))
    switches = int(t.get("switch_locations", str(max(1, _ceil(Decimal(lights) / 3))) if lights else "0", "1 switch location per 3 lights"))
    smoke = int(t.get("smoke_alarms", "0", "hardwired, interconnected"))
    data = int(t.get("data_points", "0"))
    fans = int(t.get("fan_points", "0", "ceiling or exhaust fan points"))
    if gpo + lights + smoke + data + fans == 0:
        raise ValueError("electrical_rough_in: give at least one of power_points, light_points, smoke_alarms, data_points, fan_points")
    p_circ = int(t.get("power_circuits", str(max(1, _ceil(Decimal(gpo) / 8))) if gpo else "0", "about 8 double power points per circuit; the electrician designs the circuits"))
    l_circ = int(t.get("lighting_circuits", str(max(1, _ceil(Decimal(lights + fans) / 15))) if lights + fans else "0", "about 15 lights per circuit"))
    run_p = t.get("power_run_m", "7", "average cable between power points")
    run_l = t.get("light_run_m", "5", "average cable between light points")
    drop = t.get("switch_drop_m", "4", "ceiling to switch")
    home = t.get("board_distance_m", "15", "home run from switchboard to the first point of each circuit")
    run_d = t.get("data_run_m", "25", "average data run back to the hub")
    run_s = t.get("smoke_run_m", "6", "average interconnect run between alarms")
    waste = t.get("waste_pct", "10", "offcuts and tails")
    roll = t.get("cable_roll_m", "100", "TPS sold in 100 m rolls")
    pcable = t.text("power_cable", "2.5 mm² twin and earth TPS (cable size by the electrician to AS/NZS 3000 and 3008)")
    lcable = t.text("lighting_cable", "1.5 mm² twin and earth TPS")
    f = 1 + waste / 100
    if gpo:
        metres = (gpo * run_p + p_circ * home) * f
        t.add("power_cable", "Power circuit cable", pcable, _ceil(metres / roll), f"rolls of {roll} m",
              f"({gpo} points x {run_p} m + {p_circ} circuits x {home} m home run) + {waste}% = {_money(metres)} m", "TPS cable 2.5mm 100m")
        t.add("gpo", "Double power points", "to suit, with mounting brackets", gpo, "each", "as counted", "double power point")
    if lights + fans:
        metres = ((lights + fans) * run_l + switches * drop + l_circ * home) * f
        t.add("lighting_cable", "Lighting circuit cable", lcable, _ceil(metres / roll), f"rolls of {roll} m",
              f"({lights + fans} points x {run_l} m + {switches} switch drops x {drop} m + {l_circ} circuits x {home} m) + {waste}% = {_money(metres)} m", "TPS cable 1.5mm 100m")
    if lights:
        t.add("lights", "Light fittings", t.text("light_fitting", "LED downlight, IC-4 rated where insulation will abut"), lights, "each", "as counted", "LED downlight IC4")
        t.add("switches", "Switch mechanisms and plates", "gangs to suit each location", switches, "locations", "as counted or 1 per 3 lights", "light switch plate")
        t.add("plugs", "Plug bases or connectors for lights", "to suit fittings", lights, "each", "1 per light", "plug base 3 pin")
    if fans:
        t.add("fans", "Fan points", "fan and controller (supply or fit-off)", fans, "each", "as counted", "exhaust fan")
    if smoke:
        metres = smoke * run_s * f
        t.add("smoke_alarms", "Smoke alarms", "240 V, interconnected, to AS 3786", smoke, "each", "as counted; locations per NCC Housing Provisions Part 9.5", "smoke alarm 240v interconnected")
        t.add("smoke_cable", "Smoke alarm interconnect cable", "to suit the alarm (or wireless interconnect)", _ceil(metres), "metres",
              f"{smoke} alarms x {run_s} m + {waste}%", "TPS cable 1.5mm 3 core")
    if data:
        metres = data * run_d * f
        t.add("data_cable", "Data cable", "Cat 6, 305 m box", _ceil(metres / 305), "boxes of 305 m", f"{data} points x {run_d} m + {waste}% = {_money(metres)} m", "cat6 cable 305m")
        t.add("data_outlets", "Data outlets and plates", "Cat 6 RJ45", data, "each", "as counted", "cat6 wall plate")
    smoke_circ = int(t.get("smoke_alarm_circuits", "0", "alarms usually go on a lighting circuit; set 1 for a dedicated circuit"))
    circuits = p_circ + l_circ + smoke_circ
    t.add("rcbos", "RCBOs (combined RCD and circuit breaker)", "one per final subcircuit, rating by the electrician", circuits, "each",
          f"{p_circ} power + {l_circ} lighting" + (f" + {smoke_circ} smoke alarm" if smoke_circ else "") + " circuits", "RCBO")
    points = gpo + lights + switches + smoke + data + fans
    t.add("sundries", "Brackets, clips, conduit and connectors", "allowance", points, "points", "1 allowance per point", "electrical sundries")
    t.notes.append("Quantities only. Circuit design, cable sizing, switchboard capacity and compliance are the licensed electrician's call (AS/NZS 3000 and state electrical safety law). Check whether the switchboard needs an upgrade.")


def _plumbing(t: Takeoff) -> None:
    kinds = {  # fixture: (hot outlets, cold outlets, drain size mm)
        "toilets": (0, 1, 100), "basins": (1, 1, 50), "showers": (1, 1, 50), "baths": (1, 1, 50),
        "kitchen_sinks": (1, 1, 50), "laundry_tubs": (1, 1, 50), "washing_machines": (1, 1, 50),
        "dishwashers": (0, 1, 50), "external_taps": (0, 1, 0)}
    counts = {k: int(t.get(k, "0")) for k in kinds}
    if sum(counts.values()) == 0:
        raise ValueError("plumbing_rough_in: give a count for at least one of " + ", ".join(kinds))
    hot = sum(counts[k] * kinds[k][0] for k in kinds)
    cold = sum(counts[k] * kinds[k][1] for k in kinds)
    run = t.get("water_run_m", "6", "average branch per outlet")
    main_c = t.get("cold_main_m", "15", "cold main from the meter through the house")
    main_h = t.get("hot_main_m", "10" if hot else "0", "hot flow from the water heater")
    drain_run = t.get("drain_branch_m", "3", "average fixture branch to the drain")
    drain_main = t.get("drain_main_m", "15", "100 mm drain to the sewer connection")
    fittings = t.get("fittings_per_outlet", "3", "wall elbow plus joiners and tees")
    waste = t.get("waste_pct", "10")
    coil = t.get("water_coil_m", "50")
    pipe = t.text("water_pipe", "16 mm PEX-b (or copper, to suit)")
    f = 1 + waste / 100
    water_m = ((hot + cold) * run + main_c + main_h) * f
    t.add("water_pipe", "Water pipe", pipe, _ceil(water_m / coil), f"coils of {coil} m",
          f"({hot} hot + {cold} cold outlets) x {run} m + mains {main_c + main_h} m + {waste}% = {_money(water_m)} m", "PEX pipe 16mm")
    t.add("water_fittings", "Water fittings", "wall elbows, tees, joiners to suit the pipe system", _ceil((hot + cold) * fittings), "each",
          f"{hot + cold} outlets x {fittings}", "PEX fittings 16mm")
    if hot:
        t.add("lagging", "Pipe lagging", "for hot water lines", _ceil((hot * run + main_h) * f), "metres", "hot pipe length + waste", "pipe lagging")
        t.add("tempering_valve", "Tempering valve", "to AS/NZS 3500.4 for personal hygiene outlets", 1, "each",
              "1 per water heater serving bathrooms (confirm with the plumber)", "tempering valve")
    d100 = counts["toilets"] * drain_run + drain_main
    d50 = sum(counts[k] * drain_run for k in kinds if kinds[k][2] == 50)
    if d100:
        t.add("drain_100", "Drainage pipe 100 mm", "PVC DWV, 6 m lengths", _ceil(d100 * f / 6), "lengths of 6 m",
              f"{counts['toilets']} toilets x {drain_run} m + {drain_main} m main + {waste}%", "PVC DWV pipe 100mm 6m")
    if d50:
        t.add("drain_50", "Drainage pipe 50 mm", "PVC DWV, 6 m lengths", _ceil(d50 * f / 6), "lengths of 6 m",
              f"{sum(counts[k] for k in kinds if kinds[k][2] == 50)} fixtures x {drain_run} m + {waste}%", "PVC DWV pipe 50mm 6m")
    drained = sum(v for k, v in counts.items() if kinds[k][2])
    if drained:
        t.add("drain_fittings", "Drainage fittings", "junctions, bends, traps and floor wastes to suit", drained * 3, "each", f"{drained} fixtures x 3", "PVC DWV fittings")
        t.add("solvent", "PVC priming fluid and solvent cement", "500 mL each", max(1, _ceil(Decimal(drained) / 8)), "sets", "1 set per 8 fixtures", "PVC solvent cement priming fluid")
    t.add("valves", "Isolation valves", "one per fixture connection", hot + cold, "each", "1 per outlet", "isolation valve")
    t.notes.append("Rough-in quantities only: fixtures, tapware and the water heater are priced separately. Pipe sizing, gradients, venting and compliance are the licensed plumber's call (AS/NZS 3500). The sewer connection and any stormwater are extra.")


def _roofing(t: Takeoff) -> None:
    L, W = t.get("building_length_m"), t.get("building_width_m")
    kind = t.text("roof_type", "gable")
    if kind not in ("gable", "hip", "skillion"):
        raise ValueError("roofing: roof_type must be gable, hip or skillion")
    pitch = t.get("pitch_deg", "22.5" if kind != "skillion" else "5")
    eave = t.get("eave_overhang_m", "0.45")
    gable_o = t.get("gable_overhang_m", "0.3" if kind != "hip" else "0", "barge overhang at the gable ends")
    material = t.text("material", "sheet")
    waste = t.get("waste_pct", "10")
    rad = math.radians(float(pitch))
    cos, tan = Decimal(str(math.cos(rad))), Decimal(str(math.tan(rad)))
    length = L + 2 * gable_o
    width = W + 2 * eave
    plan = length * width
    area = plan / cos
    f = 1 + waste / 100
    if kind == "skillion":
        slope = width / cos
        sides, eaves_len, ridge = 1, length, Decimal("0")
    else:
        slope = (width / 2) / cos
        sides = 2
        eaves_len = 2 * length if kind == "gable" else 2 * (length + width)
        ridge = length if kind == "gable" else max(Decimal("0"), length - width)
    t.add("roof_area", "Roof area (for reference)", f"{kind}, {pitch}° pitch", _money(area), "m²",
          f"plan {_money(length)} x {_money(width)} m (with overhangs) / cos {pitch}°", "roof")
    if material == "sheet":
        cover = t.get("sheet_cover_m", "0.762", "corrugated profile; trapezoidal is about 0.700")
        batten_sp = t.get("batten_spacing_m", "0.9", "check the manufacturer's span tables and wind classification")
        screws_per = t.get("screws_per_sheet_per_batten", "3", "depends on profile and wind region")
        if kind == "hip":
            sheet_m = area / cover * f
            sheets = _ceil(sheet_m / slope)
            basis = f"{_money(area)} m² / {cover} m cover + {waste}% (hip ends cut from full sheets)"
        else:
            sheets = sides * _ceil(length / cover)
            sheet_m = sheets * slope * f
            basis = f"{sides} side(s) x ceil({_money(length)} m / {cover} m) = {sheets} sheets x {_money(slope)} m + {waste}%"
        t.add("sheets", "Roof sheeting", t.text("sheet", "Colorbond corrugated, 0.42 BMT"), _money(sheet_m), "lineal metres (cut to length)", basis, "roof sheet corrugated colorbond")
        rows = _ceil(slope / batten_sp) + 1
        batten_m = rows * sides * length * f if kind != "hip" else area / batten_sp * f
        t.add("battens", "Roof battens", t.text("batten", "steel top-hat battens to suit the span"), _ceil(batten_m / Decimal("6")), "lengths of 6 m",
              f"{rows} rows per side at {batten_sp} m x {sides} side(s) x {_money(length)} m + {waste}%", "roof batten top hat")
        screws = _ceil(Decimal(sheets) * rows * screws_per * f)
        t.add("screws", "Roofing screws", "class 3 or 4 to suit the environment", screws, "each", f"{sheets} sheets x {rows} battens x {screws_per} + {waste}%", "roofing screws")
        cap_len = ridge + (4 * (((width / 2) ** 2 * 2 + ((width / 2) * tan) ** 2).sqrt()) if kind == "hip" else 0)
        if cap_len:
            t.add("capping", "Ridge and hip capping", "to match", _ceil(cap_len * f / Decimal("3")) if cap_len else 0, "lengths of 3 m",
                  f"ridge {_money(ridge)} m" + (" + 4 hips" if kind == "hip" else "") + f" + {waste}% laps", "ridge capping colorbond")
        if kind == "gable":
            t.add("barge", "Barge flashing", "to match", _ceil(4 * slope * f / Decimal("3")), "lengths of 3 m", f"4 gable edges x {_money(slope)} m + {waste}%", "barge capping")
    else:
        per_m2 = t.get("tiles_per_m2", "10.5", "concrete tiles; check the tile")
        batten_sp = t.get("batten_spacing_m", "0.33", "tile gauge")
        t.add("tiles", "Roof tiles", t.text("tile", "concrete roof tile"), _ceil(area * per_m2 * f), "each", f"{_money(area)} m² x {per_m2} per m² + {waste}%", "concrete roof tile")
        batten_m = area / batten_sp * f
        t.add("battens", "Tile battens", "timber, to suit the span", _ceil(batten_m / Decimal("6")), "lengths of 6 m", f"{_money(area)} m² / {batten_sp} m gauge + {waste}%", "tile batten 6m")
        cap_len = ridge + (4 * (((width / 2) ** 2 * 2 + ((width / 2) * tan) ** 2).sqrt()) if kind == "hip" else 0)
        if cap_len:
            t.add("ridge_tiles", "Ridge and hip tiles", "to match", _ceil(cap_len * 3 * f), "each", f"{_money(cap_len)} m x 3 per m + {waste}%", "ridge tile")
    t.add("sarking", "Sarking or roof blanket", t.text("sarking", "foil-faced blanket or sarking to suit"), _money(area * Decimal("1.15")), "m²", f"{_money(area)} m² + 15% laps", "roof blanket sarking")
    t.add("gutter", "Gutter", t.text("gutter", "quad or half-round, Colorbond"), _money(eaves_len * f), "lineal metres", f"eaves {_money(eaves_len)} m + {waste}%", "gutter colorbond")
    dp_spacing = t.get("downpipe_spacing_m", "12", "rule of thumb; size and space downpipes to AS/NZS 3500.3 for the rainfall")
    dp_h = t.get("downpipe_height_m", "2.7")
    runs = 1 if kind == "skillion" else (2 if kind == "gable" else 4)
    dps = max(runs, _ceil(eaves_len / dp_spacing))
    t.add("downpipes", "Downpipes", "90 mm round or 100x50 rectangular, to match", _ceil(dps * dp_h / Decimal("3")), "lengths of 3 m",
          f"{dps} downpipes (1 per {dp_spacing} m of gutter, at least 1 per gutter run) x {dp_h} m", "downpipe 90mm")
    t.add("gutter_brackets", "Gutter brackets", "at about 1.2 m centres", _ceil(eaves_len / Decimal("1.2")) + runs, "each", f"{_money(eaves_len)} m / 1.2 m", "gutter bracket")
    t.add("gutter_fittings", "Stop ends, outlets and corners", "to match", (2 * runs if kind != "hip" else 4) + dps, "each", "2 stop ends per run (corners on hips) + 1 outlet per downpipe", "gutter stop end")
    t.notes.append("Fixing densities, batten spacing and product ratings depend on the site's wind classification (AS 4055) and the manufacturer. Cyclonic regions need cyclone-rated systems. Valleys, box gutters, flashings to walls and penetrations are measured from the drawings and added separately.")

def _cladding(t: Takeoff) -> None:
    if "area_m2" in t.job:
        gross = t.get("area_m2")
        L = t.get("length_m", "0", "only needed to count corners and studs; give it for a better count")
        H = gross / L if L else Decimal("0")
    else:
        L, H = t.get("length_m"), t.get("height_m", "2.7")
        gross = L * H
    openings = t.get("openings_m2", "0", "windows and doors to deduct")
    kind = t.text("cladding_type", "board")
    if kind not in ("board", "sheet"):
        raise ValueError("cladding: cladding_type must be board or sheet")
    waste = t.get("waste_pct", "10")
    stud_sp = t.get("stud_spacing_mm", "600")
    corners = int(t.get("external_corners", "0"))
    area = gross - openings
    f = 1 + waste / 100
    studs = _ceil(L * 1000 / stud_sp) + 1 if L else 0
    if kind == "board":
        cover = t.get("board_cover_mm", "150", "effective cover per board after the lap; check the profile")
        stock = t.get("board_length_m", "4.2", "common for fibre-cement and timber weatherboards")
        board = t.text("board", "weatherboard to suit (timber or fibre-cement)")
        lineal = area * 1000 / cover * f
        t.add("boards", "Weatherboards", f"{board}, {stock} m lengths", _ceil(lineal / stock), f"lengths of {stock} m",
              f"({_money(gross)} - {openings}) m² / {cover} mm cover = {_money(area * 1000 / cover)} lineal m + {waste}% / {stock} m",
              f"{board} {stock}m")
        if studs:
            rows = _ceil(H * 1000 / cover)
            t.add("fixings", "Cladding nails or screws", "to the maker's spec (stainless near the coast)", _ceil(rows * studs * f), "each",
                  f"{rows} rows x {studs} studs ({stud_sp} mm) x 1 per crossing + {waste}%", "cladding nails")
    else:
        sw, sl = t.get("sheet_width_m", "1.2"), t.get("sheet_length_m", "2.7", "choose the length that covers the wall height")
        board = t.text("board", "fibre-cement cladding sheet")
        sheets = _ceil(area / (sw * sl) * f)
        t.add("sheets", "Cladding sheets", f"{board}, {sw} x {sl} m", sheets, "sheets",
              f"({_money(gross)} - {openings}) m² / {_money(sw * sl)} m² per sheet + {waste}%", f"{board} {sw}x{sl}")
        screws_m2 = t.get("fixings_per_m2", "12", "check the sheet maker's fixing schedule and wind region")
        t.add("fixings", "Sheet fixings", "to the maker's spec", _ceil(area * screws_m2 * f), "each", f"{_money(area)} m² x {screws_m2} per m² + {waste}%", "cladding screws")
    wrap = _money(gross * Decimal("1.1"))
    t.add("wrap", "Wall wrap", "vapour permeable, to AS 4200.1", wrap, "m²", f"{_money(gross)} m² + 10% laps (openings wrapped into, not deducted)", "wall wrap vapour permeable")
    if str(t.job.get("cavity", "false")).lower() in ("true", "yes", "1"):
        batten_stock = Decimal("2.4")
        per = _ceil(H / batten_stock) if H else 1
        t.add("cavity_battens", "Cavity battens", "to the cladding maker's system, at least 12 mm", studs * per, f"lengths of {batten_stock} m",
              f"{studs} studs x {per} length(s) per stud for a {_money(H)} m wall", "cavity batten")
    if corners:
        t.add("corners", "External corner moulds or flashings", "to suit the cladding", _ceil(corners * H * f / Decimal("3")), "lengths of 3 m",
              f"{corners} corners x {_money(H)} m + {waste}%", "external corner cladding")
    t.add("flashing_tape", "Window and door flashing tape", "to the wrap maker's system", 1, "roll", "allowance; size by the openings", "flashing tape")
    t.notes.append("Follow the cladding maker's installation guide for stud spacing, fixings and joints, and the NCC's condensation rules (Housing Provisions 10.8): a vapour-permeable wrap, or a drained and ventilated cavity. See brain/guides/materials/sarking_and_wraps.md.")


def _insulation(t: Takeoff) -> None:
    if "area_m2" in t.job:
        area = t.get("area_m2")
    else:
        area = t.get("length_m") * t.get("width_m")
    where = t.text("location", "ceiling")
    r = t.text("r_value", "R-value from the energy report")
    waste = t.get("waste_pct", "5", "offcuts around framing")
    need = _money(area * (1 + waste / 100))
    pack = t.job.get("pack_m2")
    if pack not in (None, ""):
        pack = _d(pack)
        t.add("batts", "Insulation batts", f"{r} {where} batts", _ceil(need / pack), "packs",
              f"{_money(area)} m² + {waste}% = {need} m² / {pack} m² per pack", f"{where} batts {r}")
    else:
        t.add("batts", "Insulation batts", f"{r} {where} batts", need, "m²",
              f"{_money(area)} m² + {waste}% (give pack_m2 from the pack label to count packs)", f"{where} batts {r}")
        t.notes.append("Packs cover different areas by product and R-value: read the m² per pack off the label and pass it as pack_m2.")
    t.notes.append("Install without gaps or compression and keep clearances to downlights and flues (NCC Housing Provisions 13.2.2). See brain/guides/materials/insulation.md.")


def _retaining_wall(t: Takeoff) -> None:
    L, H = t.get("length_m"), t.get("height_m")
    sh = t.get("sleeper_height_mm", "200")
    sl = t.get("sleeper_length_m", "2.4")
    sp = t.get("post_spacing_m", "1.2", "check the post and sleeper maker's tables or the engineer")
    embed = t.get("post_embed_m", str(max(H, Decimal("0.6"))), "rule of thumb: as deep as the wall is high, at least 600 mm; the engineer's design wins")
    hole = t.get("hole_mm", "300", "square hole, side length")
    bag_yield = t.get("concrete_bag_yield_m3", "0.0095", "typical 20 kg premix bag")
    drain_w = t.get("drainage_width_m", "0.3", "free-draining gravel behind the wall")
    sleeper = t.text("sleeper", "200x75 H4 treated pine sleeper")
    post = t.text("post", "H5 treated pine or steel post to suit")
    rows = _ceil(H * 1000 / sh)
    per_row = _ceil(L / sl)
    t.add("sleepers", "Sleepers", f"{sleeper}, {sl} m", rows * per_row, f"lengths of {sl} m",
          f"{H} m / {sh} mm = {rows} rows x ceil({L} / {sl}) = {per_row} per row", f"{sleeper} {sl}m")
    posts = _ceil(L / sp) + 1
    post_len = H + embed
    t.timber("posts", "Posts", post, posts, post_len, f"{L} m / {sp} m + 1 = {posts} posts at {_money(post_len)} m ({H} m + {_money(embed)} m in the ground)")
    vol = (hole / 1000) ** 2 * embed * posts
    bags = _ceil(vol / bag_yield)
    t.add("concrete", "Concrete premix", "20 kg bags", bags, "bags", f"{posts} holes x {hole} x {hole} mm x {_money(embed)} m = {_money(vol)} m³ / {bag_yield} m³ per bag", "concrete mix 20kg")
    if vol > Decimal("0.5"):
        t.notes.append(f"Post holes need {_money(vol)} m³ of concrete: ready-mix is usually cheaper above about 0.5 m³.")
    t.add("fixings", "Sleeper fixings", "galvanised or stainless screws or bolts to suit the post", rows * posts * 2, "each",
          f"{rows} rows x {posts} posts x 2", "batten screws galvanised")
    t.add("ag_pipe", "Slotted drainage pipe with sock", "100 mm", _money(L * Decimal("1.1")), "lineal metres", f"{L} m + 10%, to a legal discharge point", "ag pipe 100mm sock")
    t.add("gravel", "Drainage gravel", "20 mm", _money(L * H * drain_w), "m³", f"{L} x {H} x {drain_w} m", "drainage gravel 20mm")
    t.add("geofabric", "Geotextile fabric", "between gravel and soil", _money(L * (H + Decimal("0.6")) * Decimal("1.1")), "m²",
          f"{L} m x ({H} + 0.6) m + 10%", "geofabric")
    t.notes.append("Retaining walls above a modest height (often 0.6 to 1 m, set by the state and council), near boundaries, or holding up a building, driveway or slope usually need an engineer's design and approval. Posts in the ground for a retaining wall are H5. Check Before You Dig Australia before digging. See brain/guides/materials/timber_treatment_and_grades.md.")


def _pergola(t: Takeoff) -> None:
    L, W = t.get("length_m"), t.get("width_m")
    H = t.get("height_m", "2.4", "post height above the footing")
    psp = t.get("post_spacing_m", "3.0", "check the beam span in AS 1684 or the supplier's tables")
    rsp = t.get("rafter_spacing_mm", "900", "check the rafter span and the roofing maker's spacing")
    fd = t.get("footing_mm", "300", "square hole, side length")
    fdepth = t.get("footing_depth_mm", "600", "check soil and engineer's details")
    bag_yield = t.get("concrete_bag_yield_m3", "0.0095", "typical 20 kg premix bag")
    post = t.text("post_size", "90x90 H3 treated pine post on stirrups")
    beam = t.text("beam_size", "beam size per AS 1684 (for example 2/190x45 H3 treated pine)")
    rafter = t.text("rafter_size", "rafter size per AS 1684 (for example 140x45 H3 treated pine)")
    roof = t.text("roof", "none")
    if roof not in ("none", "sheet"):
        raise ValueError("pergola: roof must be none or sheet")
    per_side = _ceil(L / psp) + 1
    posts = 2 * per_side
    t.timber("posts", "Posts", post, posts, H, f"2 sides x (ceil({L} m / {psp} m) + 1) = {posts} posts at {H} m")
    t.timber("beams", "Beams", beam, 2, L, "a beam along each long side")
    rafters = _ceil(L * 1000 / rsp) + 1
    t.timber("rafters", "Rafters", rafter, rafters, W, f"{L} m / {rsp} mm + 1 = {rafters} rafters spanning {W} m")
    t.add("rafter_brackets", "Rafter-to-beam brackets", "galvanised framing anchors or triple grips", rafters * 2, "each", f"{rafters} rafters x 2 ends", "triple grip galvanised")
    t.add("post_anchors", "Post stirrups", "galvanised, to suit the post", posts, "each", "1 per post", "post stirrup galvanised")
    t.add("bolts", "Cup head bolts with nuts and washers", "M12 galvanised, post to beam", posts * 2, "each", "2 per post", "cup head bolt M12 galvanised")
    vol = (fd / 1000) ** 2 * (fdepth / 1000) * posts
    t.add("concrete", "Concrete premix", "20 kg bags", _ceil(vol / bag_yield), "bags", f"{posts} holes x {fd} x {fd} x {fdepth} mm = {_money(vol)} m³ / {bag_yield} m³ per bag", "concrete mix 20kg")
    if roof == "sheet":
        cover = t.get("sheet_cover_m", "0.762", "corrugated; check the profile")
        overhang = t.get("roof_overhang_m", "0.2")
        sheet_len = W + 2 * overhang
        sheets = _ceil(L / cover)
        t.add("roof_sheets", "Roof sheets", t.text("sheet", "polycarbonate or steel sheet to suit"), sheets, "sheets",
              f"ceil({L} m / {cover} m cover) = {sheets} sheets at {_money(sheet_len)} m", "roof sheet")
        t.add("roof_sheet_length", "Roof sheet length (for reference)", "cut to length when ordering", _money(sheet_len), "m", f"{W} m + 2 x {overhang} m overhang", "")
        t.add("roof_screws", "Roof sheet screws", "to the sheet maker's spec", _ceil(Decimal(sheets) * rafters * 3 * Decimal("1.1")), "each", f"{sheets} sheets x {rafters} rafters x 3 + 10%", "roofing screws")
    t.notes.append("Member sizes, spans, bracing and tie-down must come from AS 1684, the supplier's span tables or an engineer. A roofed pergola attached to the house may need approval, and in bushfire-prone areas it's built to AS 3959.")


JOBS = {"timber_deck": _deck, "stud_wall": _stud_wall, "plasterboard": _plasterboard, "concrete_slab": _slab,
        "paling_fence": _fence, "tiling": _tiling, "painting": _painting,
        "electrical_rough_in": _electrical, "plumbing_rough_in": _plumbing, "roofing": _roofing,
        "cladding": _cladding, "insulation": _insulation, "retaining_wall": _retaining_wall, "pergola": _pergola}


def materials_takeoff(job: dict) -> dict:
    """Materials list for one job. job = {"type": one of JOBS, ...dimensions and options}."""
    kind = job.get("type")
    if kind not in JOBS:
        raise ValueError(f"type must be one of: {', '.join(JOBS)}")
    t = Takeoff(job)
    JOBS[kind](t)
    return {"result": {"type": kind, "items": t.items, "assumptions": t.assumptions, "notes": t.notes}, "fields": {}}


def materials_rom(lines: list, low_pct: Decimal, high_pct: Decimal, location_loading_pct: Decimal = Decimal("0")) -> dict:
    """Price a materials list and give a rough order of magnitude range.

    lines: [{"item", "quantity", "pack_size", "unit_price_inc_gst", "product", "source", "priced_on"}, ...]
    quantity is in the takeoff's unit (screws, litres, sheets). pack_size is
    how many of those units one priced item holds (a box of 500 screws, a
    4 L tin): packs to buy = quantity / pack_size, rounded up. Leave
    pack_size as 1 when the price is per unit. Lines without a price are
    listed as unpriced and left out of the total.
    location_loading_pct adds a freight or remoteness loading to the priced
    total (for regional or remote jobs priced from metro retail). It must come
    from local suppliers or the user, never be guessed; 0 means none.
    Range = loaded total x (1 - low_pct%) to loaded total x (1 + high_pct%).
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
    priced_total = total
    loading = _money(total * location_loading_pct / 100)
    total = total + loading
    gst_part = _money(total / 11)
    low = _money(total * (1 - low_pct / 100))
    high = _money(total * (1 + high_pct / 100))
    return {"result": {"lines": priced, "unpriced": unpriced, "priced_total_inc_gst": str(priced_total),
                       "location_loading_pct": str(location_loading_pct), "location_loading_inc_gst": str(loading),
                       "total_inc_gst": str(total),
                       "gst": str(gst_part), "total_ex_gst": str(total - gst_part),
                       "rom_low_inc_gst": str(low), "rom_high_inc_gst": str(high),
                       "rom_range": f"-{low_pct}% / +{high_pct}%"}, "fields": {}}

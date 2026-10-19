"""Street dressing and clutter: what makes the place look lived in (shops closed, no people).

Real positions first (OSM natural=tree, amenity=bench, information boards, waste points), then
rule-based: bollards and lamp posts along the kerbs, bins, litter along walls and in corners,
boxes and crates by closed shops, souq carts, weeds at wall feet, caper plants in the walls,
rooftop water heaters / tanks / dishes / antennas, and cables strung across David Street.

Each prop: {"type", "p": [x, y, z], "rot": yaw degrees (0 = facing north), "s": scale, "col": bool}.
"""
import json
import math
from pathlib import Path

from geo import LineString, Point, edge_frame, polys_of

ROOT = Path(__file__).resolve().parent.parent
LITTER = ["bottle", "bottle", "can", "can", "cup", "paper", "paper", "bag", "pack", "flat_box", "butt_cluster"]


def dress(c, rng):
    props, cables = [], []
    street, paving, obstacles = c["street"], c["paving"], c["obstacles"]
    hero = c["hero"]
    sz = c["street_z"]
    road = c["road_area"]
    walk = street.buffer(-0.05)
    from shapely import prepare as _prepare
    _prepare(walk)

    def zat(x, y):
        q = Point(x, y)
        if c["courtyard"].contains(q):
            return 1.0
        if c["moat"].contains(q):
            return -5.0
        z = sz(x, y)
        if road.contains(q):
            z -= c["kerb"]
        for st in c["steps"]:
            ext = st["poly"]["ext"]
            if min(p[0] for p in ext) - 0.1 < x < max(p[0] for p in ext) + 0.1:
                from shapely.geometry import Polygon
                if Polygon(ext).contains(q):
                    return st["top"]
        return z

    def free(x, y, r):
        q = Point(x, y)
        return walk.contains(q) and obstacles.distance(q) > r * 0.5 and \
            all(math.hypot(p["p"][0] - x, p["p"][1] - y) > r + p.get("r", 0.3) for p in props[-400:])

    def add(t, x, y, rot=0.0, s=1.0, col=False, r=0.3, z=None):
        props.append({"type": t, "p": [round(x, 3), round(y, 3), round(zat(x, y) if z is None else z, 3)],
                      "rot": round(rot, 1), "s": round(s, 3), "col": col, "r": r})

    # ---- real positions from OSM
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    for n in osm["nodes"]:
        x, y = n["p"]
        if not (-90 < x < 240 and -140 < y < 130):
            continue
        t = n["tags"]
        if t.get("natural") == "tree" and street.contains(Point(x, y)):
            kind = "tree_young" if x < 0 and -30 < y < 30 else ("tree_olive" if rng.random() < 0.6 else "tree_ficus")
            add(kind, x, y, rng.uniform(0, 360), rng.uniform(0.6, 0.8) if kind == "tree_young" else rng.uniform(0.85, 1.2),
                col=True, r=1.0)                       # plaza trees are thin and young (~4 m, eval gate_outer)
        elif t.get("amenity") == "bench" and street.contains(Point(x, y)):
            add("bench_stone", x, y, _face_open(street, x, y), col=True, r=0.9)
        elif t.get("information") == "board":
            add("info_board", x, y, _face_open(street, x, y), col=True, r=0.6)
        elif t.get("amenity") in ("waste_disposal", "waste_basket"):
            add("dumpster", x, y, _face_open(street, x, y), col=True, r=1.0)

    # ---- kerb-side furniture in the hero zone
    for k in c_kerbs(c):
        a, b = k
        (tx, ty), (nx, ny), L = edge_frame(a, b)
        # normal points into the road; furniture stands on the paving side
        u = rng.uniform(0.3, 1.5)
        while u < L:
            x, y = a[0] + tx * u - nx * 0.35, a[1] + ty * u - ny * 0.35
            near_gate = -5 < x < 35 and -20 < y < 12                 # photos: stone blocks along the breach road
            if near_gate and c["moat"].distance(Point(x, y)) > 2.0 and free(x, y, 0.25):
                add("barrier_post", x, y, math.degrees(math.atan2(nx, ny)), 1.0, col=True, r=0.2)
            u += 2.2 if near_gate else 1e9
    lamp_d = 6.0
    for a, b in c_kerbs(c):
        (tx, ty), (nx, ny), L = edge_frame(a, b)
        u = 0.0
        while u < L:
            lamp_d += 0.5
            if lamp_d > 24:
                x, y = a[0] + tx * u - nx * 0.7, a[1] + ty * u - ny * 0.7
                if hero.contains(Point(x, y)) and free(x, y, 0.5):
                    add("lamp_modern_double" if rng.random() < 0.5 else "lamp_modern", x, y,
                        math.degrees(math.atan2(nx, ny)), col=True, r=0.25)
                    lamp_d = 0.0
                    if rng.random() < 0.4 and free(x + tx * 1.4, y + ty * 1.4, 0.3):
                        add("bin_slatted", x + tx * 1.4, y + ty * 1.4, 0, col=True, r=0.3)
            u += 0.5
    # outside the gate: lamps along the plaza edge facing the wall
    for x, y in [(-14, 12), (-26, 24), (-6, -14), (-20, -18), (-34, 4), (-40, -14), (-30, -22)]:
        if free(x, y, 0.5):
            add("lamp_disc", x, y, 45, col=True, r=0.25)
    for x, y, yaw in [(-9.0, -10.5, 300), (14.5, -11.5, 20), (70.0, -1.0, 200)]:   # Tower of David museum banners
        if free(x, y, 0.5):
            add("banner_pole", x, y, yaw, col=True, r=0.3)
    if free(-7.5, -14.5, 0.5):
        add("flagpole", -7.5, -14.5, 0, col=True, r=0.2)
    for x, y in [(38, -16.5), (52, -10.5), (72, -10), (78, -22)]:                   # fan palms in the moat
        q = Point(x, y)
        if c["moat"].contains(q):
            add("palm", x, y, rng.uniform(0, 360), rng.uniform(0.9, 1.2), col=False, r=0.5, z=-5.0)

    # ---- facades: litter, shop clutter, carts
    hero_b = [b for b in c["buildings"] if b["tier"] in ("hero", "mid")]
    carts = 0
    for b in hero_b:
        r = b["ring"]
        for f in b.get("facades", []):
            i = f["edge"]
            a, bb = r[i], r[(i + 1) % len(r)]
            (tx, ty), (nx, ny), L = edge_frame(a, bb)
            yaw = math.degrees(math.atan2(nx, ny))
            dens = 0.18 if b["tier"] == "hero" else 0.035          # city-wide: sparse litter outside the hero area
            u = rng.uniform(0.2, 1.5)
            while u < L - 0.2:
                corner = u < 1.2 or u > L - 1.2                      # wind piles litter into corners
                if rng.random() < (dens * 3.5 if corner else dens):
                    for _ in range(rng.randint(1, 3) if corner else 1):
                        off = rng.uniform(0.1, 0.45)
                        uu = u + rng.uniform(-0.3, 0.3)
                        x, y = a[0] + tx * uu + nx * off, a[1] + ty * uu + ny * off
                        if walk.contains(Point(x, y)):
                            add(rng.choice(LITTER), x, y, rng.uniform(0, 360), rng.uniform(0.85, 1.15), r=0.05)
                u += rng.uniform(1.0, 3.5)
            for o in f["openings"]:
                if o["kind"] != "shop":
                    continue
                roll = rng.random()
                side = rng.choice([-1, 1])
                uu = (o["u0"] - 0.45) if side < 0 else (o["u1"] + 0.45)
                if not (0.4 < uu < L - 0.4):
                    continue
                x, y = a[0] + tx * uu + nx * 0.45, a[1] + ty * uu + ny * 0.45
                if roll < 0.16 and free(x, y, 0.4):
                    add(rng.choice(["box_stack", "box_stack", "crate_stack"]), x, y, yaw + rng.uniform(-12, 12),
                        rng.uniform(0.9, 1.1), col=True, r=0.45)
                elif roll < 0.22 and carts < 5:
                    x, y = a[0] + tx * (o["u0"] + o["u1"]) / 2 + nx * 1.1, a[1] + ty * (o["u0"] + o["u1"]) / 2 + ny * 1.1
                    if free(x, y, 0.9):
                        add("cart", x, y, yaw + 90 + rng.uniform(-15, 15), col=True, r=0.9)
                        carts += 1
                elif roll < 0.3 and free(x, y, 0.3):
                    add(rng.choice(["stool_stack", "crate_single", "plant_pot"]), x, y, rng.uniform(0, 360), col=True, r=0.3)

    # ---- vegetation: small dry tufts only in the joint where a wall meets the paving, and caper
    #      bushes high on the outer face of the city wall (never in open paving or in passages)
    from shapely.geometry import Polygon as _Poly
    gate_zone = _Poly(c["gate"]["ring"]).buffer(0.6)

    def tuft_line(line, spacing, scale):
        d_ = rng.uniform(0, spacing[1])
        while d_ < line.length:
            q = line.interpolate(d_)
            if walk.contains(q) and not gate_zone.contains(q):
                add("weeds", q.x, q.y, rng.uniform(0, 360), rng.uniform(*scale), r=0.05)
            d_ += rng.uniform(*spacing)

    for w in c["walls"]:
        wl = LineString(w["pts"])
        for side in (-1, 1):
            off = wl.offset_curve(side * (w["thick"] / 2 + 0.07))
            for g in getattr(off, "geoms", [off]):
                tuft_line(g, (3.0, 9.0), (0.35, 0.65))
    gate_outer = _Poly(c["gate"]["ring"]).buffer(0.07, join_style="mitre").exterior
    for k in range(len(c["gate"]["ring"])):                     # outer faces of the tower, clear of the arches
        a, b = c["gate"]["ring"][k], c["gate"]["ring"][(k + 1) % len(c["gate"]["ring"])]
        if any(p_["edge"] == k for p_ in c["gate"]["passages"]):
            continue
        (tx, ty), (nx, ny), L = edge_frame(a, b)
        seg = LineString([(a[0] + nx * 0.07, a[1] + ny * 0.07), (b[0] + nx * 0.07, b[1] + ny * 0.07)])
        d_ = rng.uniform(0.5, 3.0)
        while d_ < L - 0.5:
            q = seg.interpolate(d_)
            if walk.contains(q):
                add("weeds", q.x, q.y, rng.uniform(0, 360), rng.uniform(0.35, 0.6), r=0.05)
            d_ += rng.uniform(3.0, 7.0)
    for b in hero_b:
        for f in b.get("facades", []):
            if rng.random() < 0.15:
                r = b["ring"]
                i = f["edge"]
                a, bb = r[i], r[(i + 1) % len(r)]
                (tx, ty), (nx, ny), L = edge_frame(a, bb)
                u = rng.choice([rng.uniform(0.1, 0.6), rng.uniform(L - 0.6, L - 0.1)])   # corners, where dust collects
                x, y = a[0] + tx * u + nx * 0.07, a[1] + ty * u + ny * 0.07
                if walk.contains(Point(x, y)):
                    add("weeds", x, y, rng.uniform(0, 360), rng.uniform(0.3, 0.5), r=0.05)
    for w in c["walls"]:                                        # capers: outer (right-hand) face only, high up
        pts = w["pts"]
        for a, b in zip(pts, pts[1:]):
            (tx, ty), (nx, ny), L = edge_frame(a, b)
            for _ in range(int(L / 7)):
                u = rng.uniform(0.8, L - 0.8)
                h = rng.uniform(3.5, w["height"] - 1.5)
                x, y = a[0] + tx * u + nx * (w["thick"] / 2 + 0.02), a[1] + ty * u + ny * (w["thick"] / 2 + 0.02)
                props.append({"type": "caper", "p": [round(x, 3), round(y, 3), round(h, 2)],
                              "rot": round(math.degrees(math.atan2(nx, ny)), 1), "s": round(rng.uniform(0.6, 1.0), 2),
                              "col": False, "r": 0})

    # ---- rooftop clutter on every flat roof (gives the skyline its look)
    for b in c["buildings"]:
        if b["style"]["roof"] != "flat" or not b.get("roof"):
            continue
        from shapely.geometry import Polygon
        rz = b["top"] - 0.9
        for rp in b["roof"]:
            poly = Polygon(rp["ext"], rp["holes"])
            inner = poly.buffer(-0.9)
            for rm in b.get("roof_rooms", []):
                inner = inner.difference(Polygon(rm["ring"]).buffer(0.9))
            if inner.is_empty or inner.area < 4:
                continue
            area = inner.area
            placed = []
            if b["tier"] == "context" and rng.random() > 0.35:     # context roofs: sparse (always loaded)
                continue
            items = ["water_heater"] * min(3, int(area / 60) + (1 if rng.random() < 0.5 else 0)) + \
                ["water_tank"] * min(3, int(area / 90) + (1 if rng.random() < 0.3 else 0)) + \
                (["sat_dish"] if rng.random() < 0.55 else []) + (["antenna"] if rng.random() < 0.35 else [])
            for it in items:
                for _ in range(20):
                    q = _rand_in(inner, rng)
                    if q is None:
                        break
                    if all(math.hypot(q.x - px, q.y - py) > 1.6 for px, py in placed):
                        placed.append((q.x, q.y))
                        rot = 180 + rng.uniform(-15, 15) if it == "water_heater" else rng.uniform(0, 360)
                        props.append({"type": it, "p": [round(q.x, 3), round(q.y, 3), round(rz, 3)], "rot": round(rot, 1),
                                      "s": 1.0, "col": False, "r": 0})
                        break

    # ---- cables strung across David Street (and the alley mouths off the square)
    dpts = c["david"]["pts"]
    line = LineString(dpts)
    s = 3.0
    while s < line.length:
        p = line.interpolate(s)
        q = line.interpolate(min(line.length, s + 0.5))
        dx, dy = q.x - p.x, q.y - p.y
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        ends = []
        for sgn in (1, -1):
            ray = LineString([(p.x, p.y), (p.x + nx * sgn * 12, p.y + ny * sgn * 12)])
            hit = ray.intersection(obstacles.boundary)
            pts_ = [g for g in getattr(hit, "geoms", [hit]) if not g.is_empty and g.geom_type == "Point"]
            if pts_:
                h_ = min(pts_, key=lambda g: g.distance(Point(p.x, p.y)))
                ends.append((h_.x - nx * sgn * 0.05, h_.y - ny * sgn * 0.05))
        if len(ends) == 2:
            zb = sz(p.x, p.y)
            for _ in range(rng.choice([1, 1, 2, 3])):
                z1, z2 = zb + rng.uniform(5.2, 7.8), zb + rng.uniform(5.2, 7.8)
                cables.append({"a": [round(ends[0][0], 2), round(ends[0][1], 2), round(z1, 2)],
                               "b": [round(ends[1][0], 2), round(ends[1][1], 2), round(z2, 2)],
                               "sag": round(rng.uniform(0.25, 0.7), 2), "r": 0.012})
        s += rng.uniform(2.0, 4.0)
    # ---- green steel tie-beams across David Street at ~4.5 m tying the canopy rows (notes C5)
    beams = []
    s = 12.0
    while s < line.length - 2:
        p = line.interpolate(s)
        q = line.interpolate(min(line.length, s + 0.5))
        dx, dy = q.x - p.x, q.y - p.y
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L
        ends = []
        for sgn in (1, -1):
            ray = LineString([(p.x, p.y), (p.x + nx * sgn * 7, p.y + ny * sgn * 7)])
            hit = ray.intersection(obstacles.boundary)
            pts_ = [g for g in getattr(hit, "geoms", [hit]) if not g.is_empty and g.geom_type == "Point"]
            if pts_:
                h_ = min(pts_, key=lambda g: g.distance(Point(p.x, p.y)))
                ends.append((h_.x - nx * sgn * 0.02, h_.y - ny * sgn * 0.02))
        if len(ends) == 2 and math.dist(*ends) < 7.5:
            zb = sz(p.x, p.y) + 4.5
            beams.append({"a": [round(ends[0][0], 2), round(ends[0][1], 2), round(zb, 2)],
                          "b": [round(ends[1][0], 2), round(ends[1][1], 2), round(zb + rng.uniform(-0.1, 0.1), 2)]})
        s += rng.uniform(5.0, 8.0)
    # ---- ground decals: manholes along the road and David St, drains at kerbs
    gdec = []
    d_ = 14.0
    while d_ < line.length:                                    # round cast-iron covers on the centre line (C2)
        q = line.interpolate(d_)
        gdec.append({"type": "manhole", "p": [round(q.x, 2), round(q.y, 2), round(zat(q.x, q.y) + 0.006, 3)],
                     "rot": rng.uniform(0, 360), "w": 0.7, "h": 0.7})
        d_ += rng.uniform(6.0, 10.0)
    rl = LineString(c["road_line"])
    d_ = 8.0
    while d_ < rl.length:
        q = rl.interpolate(d_)
        if hero.contains(q) and road.contains(q):
            gdec.append({"type": "manhole", "p": [round(q.x, 2), round(q.y, 2), round(zat(q.x, q.y) + 0.006, 3)],
                         "rot": rng.uniform(0, 360), "w": 0.75, "h": 0.75})
        d_ += rng.uniform(18, 30)
    for a, b in c_kerbs(c):
        (tx, ty), (nx, ny), L = edge_frame(a, b)
        if L < 2 or rng.random() > 0.35:
            continue
        x, y = a[0] + tx * L / 2 + nx * 0.25, a[1] + ty * L / 2 + ny * 0.25
        if hero.contains(Point(x, y)):
            gdec.append({"type": "drain", "p": [round(x, 2), round(y, 2), round(zat(x, y) + 0.006, 3)],
                         "rot": math.degrees(math.atan2(tx, ty)), "w": 0.9, "h": 0.45})
    for p_ in props:
        p_.pop("r", None)
    return props, cables, gdec, beams


def c_kerbs(c):
    """Kerb lines as (a, b) pairs with the right-hand normal pointing into the road."""
    out = []
    road = c["road_area"]
    edge = road.boundary.intersection(c["paving"].buffer(0.02))
    for ls in getattr(edge, "geoms", [edge]):
        if ls.geom_type != "LineString" or ls.length < 1.0:
            continue
        cc = list(ls.coords)
        a, b = cc[0], cc[-1]
        for p, q in zip(cc, cc[1:]):
            if math.dist(p, q) < 0.05:
                continue
            (tx, ty), (nx, ny), _ = edge_frame(p, q)
            m = ((p[0] + q[0]) / 2 + nx * 0.1, (p[1] + q[1]) / 2 + ny * 0.1)
            out.append((p, q) if road.contains(Point(m)) else (q, p))
    return out


def _face_open(street, x, y):
    """Yaw facing the most open direction (benches, boards, bins face the space)."""
    best, by = -1, 0
    for k in range(16):
        a = k * math.pi / 8
        d_ = 0
        while d_ < 8 and street.contains(Point(x + math.sin(a) * d_, y + math.cos(a) * d_)):
            d_ += 0.5
        if d_ > best:
            best, by = d_, math.degrees(a)
    return by


def _rand_in(poly, rng):
    x0, y0, x1, y1 = poly.bounds
    for _ in range(30):
        q = Point(rng.uniform(x0, x1), rng.uniform(y0, y1))
        if poly.contains(q):
            return q
    return None

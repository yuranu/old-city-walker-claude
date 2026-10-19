"""Builds facade geometry from the facade specs written by pipeline/facades.py.

wall_panel()     the wall face with openings cut out, reveals, infill, thresholds, frames, sills,
                 keystones, grilles and open shutter leaves
facade_extras()  string courses, cornice, balconies, awnings, signs, decals, cables, fixtures

All facade coordinates: u = metres along the edge a->b, v/z = absolute height. The outward
normal is on the right of a->b (CCW footprint rings).
"""
import math
import zlib

from mathutils import Vector

import meshkit as mk

UP = Vector((0, 0, 1))
STONE_LIGHT = (1.0, 1.0, 1.0)          # dressed stone (frames, sills) shows lighter than tinted walls
SKIP_BOTTOM = {"shop", "door", "passage"}


def _frame(a, b):
    A, B = Vector((a[0], a[1], 0)), Vector((b[0], b[1], 0))
    t = B - A
    L = t.length
    t = t / L if L > 1e-9 else Vector((1, 0, 0))
    n = Vector((t.y, -t.x, 0))
    return A, t, n, L


def _cell_uv(gen, atlas, name, size=2048):
    a = gen[atlas]
    if name not in a["cells"]:
        return None
    return mk.atlas_rect(a["grid"], a["cells"][name], size_px=size)


def _map(rect, u, v, u0, u1, v0, v1):
    ru0, rv0, ru1, rv1 = rect
    return (ru0 + (u - u0) / max(u1 - u0, 1e-6) * (ru1 - ru0), rv0 + (v - v0) / max(v1 - v0, 1e-6) * (rv1 - rv0))


def wall_panel(mb, a, b, z0, z1, openings, mat, tint, gen, rng_key=""):
    A, t, n, L = _frame(a, b)
    if L < 0.05 or z1 - z0 < 0.05:
        return
    P = lambda u, v: A + t * u + Vector((0, 0, v))
    col = tuple(tint) if tint else None
    outlines = []
    for o in openings:
        m = 0.05 if o.get("kind") == "passage" else 0.2
        if o["u0"] < m or o["u1"] > L - m or o["v0"] < z0 - 1e-6 or o["v1"] > z1 - 0.15:
            continue
        if any(o["u0"] < q["u1"] + 0.1 and o["u1"] > q["u0"] - 0.1 and o["v0"] < q["v1"] + 0.1 and o["v1"] > q["v0"] - 0.1
               for q, _ in outlines):
            continue                                       # never overlap two holes
        outlines.append((o, mk.opening_outline(o["u0"], o["u1"], o["v0"], o["v1"], o.get("arch"))))
    outer = [(0, z0), (L, z0), (L, z1), (0, z1)]
    flat, tris = mk.tess2d([outer] + [ol for _, ol in outlines])
    mb.tris([P(u, v) for u, v in flat], tris, mat, n, col=col)
    for o, ol in outlines:
        _opening(mb, o, ol, P, t, n, mat, col, gen, [q for q, _ in outlines], rng_key)


def _opening(mb, o, ol, P, t, n, mat, col, gen, others, rng_key):
    kind = o.get("kind", "window")
    d = o.get("depth", 0.3)
    u0, u1, v0, v1 = o["u0"], o["u1"], o["v0"], o["v1"]
    w = u1 - u0
    cu = sum(p[0] for p in ol) / len(ol)
    cv = sum(p[1] for p in ol) / len(ol)
    front = [P(u, v) for u, v in ol] + [P(*ol[0])]
    back = [p - n * d for p in front]
    centre = P(cu, cv) - n * (d / 2)
    for i in range(len(front) - 1):
        if i == 0 and kind in SKIP_BOTTOM:
            continue                                       # floor is the threshold / ground
        q = [front[i], front[i + 1], back[i + 1], back[i]]
        mb.poly(q, mat, centre - (q[0] + q[2]) / 2, col=col)
    if kind == "passage" or d <= 0.0:
        return
    h = zlib.crc32(("%s%.2f%.2f" % (rng_key, u0, v0)).encode())
    split = o.get("split")
    lo = o.get("lo", "glass")
    if lo == "glass" and h % 10 < 3:
        lo = "glass_curtain"
    if lo == "void":
        fl, ft = mk.tess2d([ol])
        mb.tris([P(u, v) - n * d for u, v in fl], ft, "void", n)
    elif lo == "wall":                                     # walled-up arch: stone infill set back a little
        fl, ft = mk.tess2d([ol])
        mb.tris([P(u, v) - n * d for u, v in fl], ft, mat, n, col=tuple(c_ * 0.93 for c_ in col) if col else (0.93,) * 3)
    elif split and split < v1 - 0.05:
        rect = _cell_uv(gen, "doors", lo)
        poly = [(u0, v0), (u1, v0), (u1, split), (u0, split)]
        fl, ft = mk.tess2d([poly])
        pts = [P(u, v) - n * d for u, v in fl]
        for a_, b_, c_ in ft:
            uvs = [_map(rect, fl[k][0], fl[k][1], u0, u1, v0, split) for k in (a_, b_, c_)]
            mb.poly([pts[a_], pts[b_], pts[c_]], "doors", n, uv=uvs)
        hi = [(u1, split)] + [p for p in ol if p[1] > split + 1e-6] + [(u0, split)]
        if len(hi) >= 3:
            fl, ft = mk.tess2d([hi])
            mb.tris([P(u, v) - n * d for u, v in fl], ft, "void", n)
            fr = _cell_uv(gen, "cutout", o.get("hi", "fanlight"))
            if fr:
                half = (fr[0], fr[1], fr[2], fr[1] + (fr[3] - fr[1]) * 0.5)   # the fan fills the lower half
                pts = [P(u, v) - n * (d - 0.06) for u, v in fl]
                for a_, b_, c_ in ft:
                    uvs = [_map(half, fl[k][0], fl[k][1], u0, u1, split, v1) for k in (a_, b_, c_)]
                    mb.poly([pts[a_], pts[b_], pts[c_]], "cut", n, uv=uvs)
    else:
        rect = _cell_uv(gen, "doors", lo) or _cell_uv(gen, "doors", "glass")
        fl, ft = mk.tess2d([ol])
        pts = [P(u, v) - n * d for u, v in fl]
        for a_, b_, c_ in ft:
            uvs = [_map(rect, fl[k][0], fl[k][1], u0, u1, v0, v1) for k in (a_, b_, c_)]
            mb.poly([pts[a_], pts[b_], pts[c_]], "doors", n, uv=uvs)
    rise = {"round": w / 2, "pointed": 0.7746 * w, "segment": 0.18 * w}.get(o.get("arch"), 0.0)
    vs = v1 - rise
    # threshold step (doors and shops): stone block from inside the recess to just outside
    if o.get("threshold"):
        z_g = v0 - 0.12
        mk.box(mb, P((u0 + u1) / 2, 0) + n * ((0.25 - d) / 2), t, n, w + 0.12, d + 0.25, z_g - 0.04, v0, "dressed",
               col=(0.86, 0.84, 0.8))
    # dressed stone surround
    fw = o.get("frame", 0.0)
    for q in others:
        if q is o or not (q["v0"] < v1 + fw and q["v1"] > v0 - fw):
            continue
        gap = q["u0"] - u1 if q["u0"] >= u1 else (u0 - q["u1"] if q["u1"] <= u0 else 0.0)
        if gap >= 0:
            fw = min(fw, max(0.0, gap / 2 - 0.015))
    if fw > 0.03:
        fd = 0.07
        outer = mk.opening_outline(u0 - fw, u1 + fw, v0, v1 + fw, o.get("arch"))
        inner = mk.opening_outline(u0, u1, v0, v1, o.get("arch"))
        # U-shaped band: outer path bottom-right -> over the top -> bottom-left, then the
        # inner path back from bottom-left -> over the top -> bottom-right
        u_shape = outer[1:] + [outer[0]] + [inner[0]] + inner[:0:-1]
        try:
            fl, ft = mk.tess2d([u_shape])
            mb.tris([P(u, v) + n * fd for u, v in fl], ft, "dressed", n, col=STONE_LIGHT)
        except Exception:                                 # noqa: BLE001
            pass
        oc = [P(u, v) for u, v in outer[1:]] + [P(*outer[0])]
        for i in range(len(oc) - 1):
            q = [oc[i], oc[i + 1], oc[i + 1] + n * fd, oc[i] + n * fd]
            mid = (q[0] + q[1]) / 2
            mb.poly(q, "dressed", mid - (P(cu, cv)), col=STONE_LIGHT)
        ic = [P(u, v) for u, v in inner[1:]] + [P(*inner[0])]
        for i in range(len(ic) - 1):
            q = [ic[i], ic[i + 1], ic[i + 1] + n * fd, ic[i] + n * fd]
            mid = (q[0] + q[1]) / 2
            mb.poly(q, "dressed", P(cu, cv) - mid, col=STONE_LIGHT)
        if o.get("keystone") and o.get("arch") in ("round", "pointed", "segment"):
            mk.box(mb, P((u0 + u1) / 2, 0) + n * 0.05, t, n, 0.32, 0.1, v1 - 0.12, v1 + fw + 0.08, "dressed",
                   col=STONE_LIGHT)
    if o.get("sill"):
        mk.box(mb, P((u0 + u1) / 2, 0) + n * 0.07, t, n, w + 0.24, 0.14, v0 - 0.11, v0 - 0.015, "dressed",
               bottom=True, col=STONE_LIGHT, back=False)
    if o.get("grille"):
        gr = _cell_uv(gen, "cutout", "grille")
        top = vs if rise else v1
        mk.card(mb, P((u0 + u1) / 2, v0) - n * 0.07, t, UP, w, top - v0, "cut", gr, double=True)
    if o.get("shutters") == "open":
        cell = _cell_uv(gen, "doors", ["shutter_green", "shutter_blue", "shutter_brown"][h % 3])
        top = vs if rise else v1
        for side in (-1, 1):
            lu0 = (u0 - fw - 0.02 - w / 2) if side < 0 else (u1 + fw + 0.02)
            lu1 = lu0 + w / 2
            if any(q is not o and lu0 < q["u1"] + q.get("frame", 0) and lu1 > q["u0"] - q.get("frame", 0)
                   and v0 < q["v1"] and top > q["v0"] for q in others):
                continue
            half = (cell[0], cell[1], (cell[0] + cell[2]) / 2, cell[3]) if side < 0 else \
                ((cell[0] + cell[2]) / 2, cell[1], cell[2], cell[3])
            mk.card(mb, P((lu0 + lu1) / 2, v0) + n * 0.03, t, UP, lu1 - lu0, top - v0, "doors", half)


# ---------------------------------------------------------------- extras
def facade_extras(mbs, a, b, f, gen, signs, place, tint):
    """mbs: {"solid": MeshBuilder, "deco": ..., "signs": ..., "cables": ...}; place(type, pos, yaw, nocol)."""
    A, t, n, L = _frame(a, b)
    P = lambda u, v: A + t * u + Vector((0, 0, v))
    solid, deco = mbs["solid"], mbs["deco"]
    yaw = math.atan2(-n.x, n.y)
    for bd in f.get("bands", []):
        mk.box(solid, P(L / 2, 0) + n * bd["d"] / 2, t, n, L, bd["d"], bd["z"], bd["z"] + bd["h"], "dressed",
               bottom=True, col=STONE_LIGHT, back=False)
    cn = f.get("cornice")
    if cn:
        mk.box(solid, P(L / 2, 0) + n * cn["d"] * 0.3, t, n, L, cn["d"] * 0.6, cn["z"], cn["z"] + cn["h"] * 0.45,
               "dressed", bottom=True, col=STONE_LIGHT, back=False)
        mk.box(solid, P(L / 2, 0) + n * cn["d"] / 2, t, n, L, cn["d"], cn["z"] + cn["h"] * 0.45, cn["z"] + cn["h"],
               "dressed", bottom=True, col=STONE_LIGHT, back=False)
    rail = _cell_uv(gen, "cutout", "rail_balcony")
    for bl in f.get("balconies", []):
        u0, u1, z, dp = bl["u0"], bl["u1"], bl["z"], bl["depth"]
        if u0 < 0.1 or u1 > L - 0.1:
            continue
        uc = (u0 + u1) / 2
        mk.box(solid, P(uc, 0) + n * dp / 2, t, n, u1 - u0, dp, z - 0.16, z, "dressed", bottom=True, col=STONE_LIGHT,
               back=False)
        for uu in (u0 + 0.2, u1 - 0.2):
            mk.box(solid, P(uu, 0) + n * 0.3, t, n, 0.16, 0.6, z - 0.5, z - 0.16, "dressed", bottom=True,
                   col=STONE_LIGHT, back=False)
        mk.card(deco, P(uc, z) + n * (dp - 0.03), t, UP, u1 - u0 - 0.04, 1.0, "cut", rail, double=True)
        for uu in (u0 + 0.03, u1 - 0.03):
            mk.card(deco, P(uu, z) + n * ((dp - 0.03) / 2), n, UP, dp - 0.06, 1.0, "cut", rail, double=True)
        mk.tube(deco, [P(u0 + 0.03, z + 1.0) + n * (dp - 0.03), P(u1 - 0.03, z + 1.0) + n * (dp - 0.03)], 0.025, "iron")
    for aw in f.get("awnings", []):
        z, dp = aw["z"], aw.get("depth", 1.3)
        p0, p1 = P(aw["u0"], z), P(aw["u1"], z)
        q = [p0, p1, p1 + n * dp - UP * 0.35, p0 + n * dp - UP * 0.35]
        solid.poly(q, "awning", UP)
        solid.poly(q[::-1], "awning", -UP)
        for uu in (aw["u0"] + 0.3, aw["u1"] - 0.3):
            mk.tube(deco, [P(uu, z - 0.7), P(uu, z - 0.7) + n * dp * 0.9 - UP * 0.25 + UP * 0.6], 0.02, "iron")
    if signs:
        for sg in f.get("signs", []):
            meta = signs["signs"].get(sg["cell"])
            if not meta:
                continue
            x, y, w_, h_ = meta["rect"]
            S = signs["size"][0]
            rect = (x / S, 1 - (y + h_) / S, (x + w_) / S, 1 - y / S)
            u0, u1 = sg["u0"], sg["u1"]
            if u0 < 0.05 or u1 > L - 0.05:
                continue
            width = u1 - u0
            height = min(1.1, width * h_ / w_)
            z0 = sg["z0"]
            dd = max(0.12, sg.get("d", 0.05))                # clear of bands (6 cm) and keystones (10 cm)
            mk.box(mbs["signs"], P((u0 + u1) / 2, 0) + n * dd / 2, t, n, width, dd, z0, z0 + height, "metal_dark",
                   bottom=True, back=False)
            mk.card(mbs["signs"], P((u0 + u1) / 2, z0) + n * (dd + 0.012), t, UP, width, height, "signs", rect)
    for k_dc, dc in enumerate(f.get("decals", [])):
        rect = _cell_uv(gen, "decal", dc["type"], size=1024)
        if not rect or dc["u0"] < 0.05 or dc["u1"] > L - 0.05:
            continue
        z0, z1 = max(dc["z0"], f["ground"] + 0.05), dc["z1"]
        if z1 - z0 < 0.1:
            continue
        mk.card(deco, P((dc["u0"] + dc["u1"]) / 2, z0) + n * (0.010 + 0.0015 * (k_dc % 6)), t, UP,
                dc["u1"] - dc["u0"], z1 - z0, "decal", rect)
    for cb in f.get("cables", []):
        for k in range(cb.get("n", 1)):
            z = cb["z"] + k * 0.05
            pts = []
            u = max(0.05, cb["u0"])
            while u < min(L - 0.05, cb["u1"]):
                pts.append(P(u, z) + n * (0.05 + 0.015 * k))
                u += 0.8
            if len(pts) > 1:
                mk.tube(mbs["cables"], pts, 0.011, "iron")
    for fx in f.get("fixtures", []):
        ty = fx["type"]
        if ty == "pipe":
            p0, p1 = P(fx["u"], fx["z0"] + 0.15) + n * 0.1, P(fx["u"], fx["z1"]) + n * 0.1
            mk.tube(deco, [p0 + n * 0.12 - UP * 0.15, p0, p1], 0.045, "metal_grey", sides=6)
            mk.tube(deco, [p1, p1 - n * 0.1], 0.045, "metal_grey", sides=6)
            continue
        if ty == "sign":                                   # wall-mounted sign / street plaque from the atlas
            if signs and fx["cell"] in signs["signs"]:
                x, y, w_, h_ = signs["signs"][fx["cell"]]["rect"]
                S = signs["size"][0]
                mk.card(mbs["signs"], P(fx["u"], fx["z"]) + n * 0.025, t, UP, fx["w"], fx["h"], "signs",
                        (x / S, 1 - (y + h_) / S, (x + w_) / S, 1 - y / S))
            continue
        if ty == "plaque":
            if signs and "house_number" in signs["signs"]:
                x, y, w_, h_ = signs["signs"]["house_number"]["rect"]
                S = signs["size"][0]
                mk.card(mbs["signs"], P(fx["u"], fx["z"]) + n * 0.01, t, UP, 0.22, 0.22 * h_ / w_, "signs",
                        (x / S, 1 - (y + h_) / S, (x + w_) / S, 1 - y / S))
            continue
        place(ty, P(fx["u"], fx["z"]), yaw, True)

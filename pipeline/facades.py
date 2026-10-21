"""Facade layout: decides every opening and wall element of a building edge.

Output per exposed edge (all positions in facade coordinates: u metres along the edge from
vertex a, z absolute metres):
  openings  shop / door / window / balcony_door with arch, size, depth, infill, frame, sill,
            keystone, grille, shutters, threshold
  bands     string courses;  cornice
  balconies, awnings, signs, fixtures (wall lanterns, AC units, spouts, pipes, plaques),
  decals    (streaks, posters) and cables along the facade

Generic rules give plausible Old City facades; hero.py overrides individual facades from
photographs (see data/reference/*.md).
"""
import math

from geo import edge_frame

SHOP_DOORS = ["door_green", "door_green", "door_green2", "door_blue", "rolldown_grey", "rolldown_green",
              "door_green_graffiti", "door_blue2"]
SHOP_SIGNS = ["sign_souvenirs", "sign_exchange", "sign_ceramics", "sign_jewelry", "sign_books", "sign_cafe",
              "sign_spices", "sign_icons", "sign_photo", "sign_judaica", "sign_bakery", "sign_textiles"]
POSTERS = ["poster_a", "poster_b", "poster_c", "poster_d"]
# upper-floor window heads stay this far under the parapet top: below the roof deck (top - 0.9),
# the cornice (top - 1.25) and the spouts (top - 0.95)
HEAD_CLEAR = 1.35


def arch_rise(arch, w):
    return {"round": w / 2, "pointed": 0.7746 * w, "segment": 0.18 * w}.get(arch, 0.0)


def shop_ops_pre(f):
    return any(o["kind"] == "shop" for o in f["openings"])


def g2w(ground_spec, k, default):
    if ground_spec and k < len(ground_spec):
        return ground_spec[k].get("w", default)
    return default


def top_z_guess(bld):
    return bld["top"]


def storey_heights(st, override=None):
    """(ground storey, upper storey) heights of a facade: the override's, else the building style's."""
    ov = override or {}
    shops = ov.get("shops", st["shops"])
    return ov.get("ground_storey") or (4.8 if shops else st["storey"]), ov.get("storey") or st["storey"]


def storeys_for(bld, eg, g_storey, storey):
    """Floor base heights above the ground floor that still fit under the parapet: a floor fits when
    a 1.35 m window on the 0.9 m sill keeps its head HEAD_CLEAR under the top (layout() shortens the
    default windows of the top floor to that head)."""
    out = []
    z = eg + g_storey
    while z + 2.6 <= bld["top"] - 1.0:
        out.append(z)
        z += storey
    return out


def layout(bld, i, eg, rng, override=None, ground_at=None):
    """Layout of facade i of bld (openings, balconies, fixtures, signs). ground_at(u): street level in
    front of the facade at u; doors and shops sit on it (on a sloping
    street too; from 1.5 m below to 0.8 m above the edge level eg, clear of the storey above)."""
    a, b = bld["ring"][i], bld["ring"][(i + 1) % len(bld["ring"])]
    _, _, L = edge_frame(a, b)
    st = bld["style"]
    tier = bld["tier"]
    hero = tier == "hero"
    ashlar = st["wall"] == "ashlar"
    f = {"edge": i, "ground": round(eg, 3), "len": round(L, 3), "openings": [], "bands": [], "cornice": None,
         "balconies": [], "awnings": [], "canopies": [], "signs": [], "fixtures": [], "decals": [], "cables": []}
    if override and override.get("blank"):
        return f
    if L < 2.4:
        return f
    bay = override.get("bay") if override and override.get("bay") else (3.6 if ashlar else 3.1)
    margin = 0.9 if L > 4 else 0.5
    n = int((L - 2 * margin) // bay)
    if n < 1:
        n = 1 if L >= 2.6 else 0
    if not n:
        return f
    sp = (L - 2 * margin) / n
    centres = [margin + sp * (k + 0.5) for k in range(n)]
    if override and override.get("centres"):
        centres = override["centres"]
        sp = min([centres[k + 1] - centres[k] for k in range(len(centres) - 1)] or [L])
    shops = override.get("shops", st["shops"]) if override else st["shops"]
    g_storey, storey = storey_heights(st, override)
    arch_up = override.get("arch_up") if override and "arch_up" in override else bld["arch_pref"]
    frame_w = (0.18 if ashlar else 0.13) if hero else 0.0
    souq = bool(override and override.get("souq"))
    if souq:
        frame_w = 0.0                                   # souq shop heads hide behind the canopies
    # "auto": false on a photo-matched facade switches off every random element (signs, posters,
    # plaques, AC units, pipes, lanterns, cables, blind/walled-up bays, random shutters and grilles):
    # only what the override lists is built. Bays and floors it leaves out get the plain defaults
    auto = override.get("auto", True) if override else True

    def pick(draw, fixed):
        # the random choice when auto, else the fixed default; the draw is made either way so the
        # rest of the building (other edges, roof) keeps its random sequence
        return draw if auto else fixed

    thr = override.get("thr", 0.12) if override else 0.12
    thr_out = override.get("thr_out", 0.1) if override else 0.1     # (0.25 read as slabs across narrow lanes)
    # ---- ground floor
    door_bay = pick(rng.randrange(len(centres)), len(centres) // 2)
    ground_spec = override.get("ground") if override else None
    for k, c in enumerate(centres):
        g = ground_spec[k] if ground_spec and k < len(ground_spec) else None
        kind = g.get("kind") if g else ("shop" if shops else ("door" if k == door_bay else "window"))
        if kind == "blind":
            continue
        if kind == "shop":
            w = g.get("w", min(2.9, sp - 0.7)) if g else min(2.9, sp - 0.7)
            if w < 1.4:
                continue
            arch = g.get("arch", "round" if ashlar else "pointed") if g else ("round" if ashlar else "pointed")
            h = g.get("h", min(g_storey - 0.8, 4.0)) if g else min(g_storey - 0.8, 4.0)
            egd = min(eg + 0.8, max(eg - 1.5, ground_at(c))) if ground_at else eg
            v0, v1 = egd + thr, egd + thr + h
            vs = v1 - arch_rise(arch, w)
            door = g.get("door") if g and g.get("door") else pick(rng.choice(SHOP_DOORS), SHOP_DOORS[0])
            f["openings"].append({"kind": "shop", "u0": c - w / 2, "u1": c + w / 2, "v0": v0, "v1": v1, "arch": arch,
                                  "depth": 0.45, "split": (vs if arch and not souq else None), "lo": door, "hi": "fanlight",
                                  "frame": frame_w, "keystone": hero and arch == "round" and not souq, "threshold": True,
                                  "thr": thr, "thr_out": thr_out})
            if souq and auto and rng.random() < 0.35 and k + 1 < len(centres):   # blade board on the pier
                pu = (c + w / 2 + centres[k + 1] - (g2w(ground_spec, k + 1, w)) / 2) / 2
                f["fixtures"].append({"type": "blade", "u": round(pu, 2), "z": eg + 2.3, "h": 0.6, "out": 1.25,
                                      "cell": rng.choice(["sign_souvenirs", "sign_jewelry", "sign_textiles", "sign_spices",
                                                          "sign_ceramics", "sign_icons", "sign_judaica", "sign_cafe"])})
                # (a blank cream board read as a missing texture)
            # a sign the override names is always built (any tier, souq or not, auto or not);
            # random fascia signs only on hero shops outside the souq
            named = g.get("sign") if g and g.get("sign") else None
            no_sign = g is not None and g.get("sign") is False
            if named or (not souq and hero and auto and not no_sign and rng.random() < 0.45):
                sw = min(w + 0.5, sp - 0.2)
                cell = named or rng.choice(SHOP_SIGNS)
                z0, z1 = v1 + 0.25, v1 + 0.85
                zc = eg + override["canopy"]["z_wall"] + 0.1 if souq and override.get("canopy") else None
                if zc is not None and z0 < zc:              # above the souq canopy (it meets the wall at z_wall)
                    z0, z1 = zc, zc + 0.6
                f["signs"].append({"u0": c - sw / 2, "u1": c + sw / 2, "z0": z0, "z1": z1,
                                   "cell": cell, "d": 0.06})
            if hero and auto and rng.random() < 0.18:
                pw = rng.uniform(0.45, 0.6)
                pu = c + w / 2 + 0.15
                if pu + pw < (centres[k + 1] - w / 2 - 0.1 if k + 1 < len(centres) else L - 0.3):
                    f["decals"].append({"type": rng.choice(POSTERS), "u0": pu, "u1": pu + pw,
                                        "z0": eg + 1.3, "z1": eg + 1.3 + pw * 1.4})
        elif kind == "door":
            w = g.get("w", 1.3) if g else 1.3
            arch = g.get("arch", "round") if g else "round"
            v0 = (min(eg + 0.8, max(eg - 1.5, ground_at(c))) if ground_at else eg) + thr
            f["openings"].append({"kind": "door", "u0": c - w / 2, "u1": c + w / 2, "v0": v0,
                                  "v1": v0 + (g.get("h", 2.75) if g else 2.75),
                                  "arch": arch, "depth": 0.4, "split": None, "lo": g.get("door", "door_wood") if g else
                                  pick(rng.choice(["door_wood", "door_wood", "door_green"]), "door_wood"), "frame": frame_w,
                                  "keystone": hero, "threshold": True})
            if hero and auto and rng.random() < 0.5:            # house-number / street plaque
                f["fixtures"].append({"type": "plaque", "u": c + w / 2 + 0.45, "z": eg + 2.3})
        else:
            w, h = (0.8, 1.15) if not g else (g.get("w", 0.8), g.get("h", 1.15))
            v0 = eg + (g.get("sill", 1.6) if g else 1.6)
            f["openings"].append({"kind": "window", "u0": c - w / 2, "u1": c + w / 2, "v0": v0, "v1": v0 + h,
                                  "arch": g.get("arch") if g else None, "depth": 0.3,
                                  "lo": g.get("lo", "glass") if g else "glass",
                                  "frame": frame_w * 0.8, "sill": True, "grille": g.get("grille", True) if g else True})
    # awning over a row of shops (sheet-metal canopies, photos 010 / 022)
    shop_ops = [o for o in f["openings"] if o["kind"] == "shop"]
    if souq and override.get("canopy") and shop_ops_pre(f):
        cp = override["canopy"]
        f["canopies"] = [{"u0": 0.15, "u1": L - 0.15, "depth": cp["depth"], "z_front": eg + cp["z_front"],
                          "z_wall": eg + cp["z_wall"]}]
    want_awning = override.get("awning") if override and "awning" in override else (hero and pick(rng.random() < 0.55, False))
    if shop_ops and len(shop_ops) >= 2 and want_awning:
        f["awnings"].append({"u0": max(0.15, shop_ops[0]["u0"] - 0.3), "u1": min(L - 0.15, shop_ops[-1]["u1"] + 0.3),
                             "z": max(o["v1"] for o in shop_ops) + 0.12, "depth": 1.3})
    # ---- upper floors
    floors = storeys_for(bld, eg, g_storey, storey)
    upper = override.get("floors") if override else None
    bal_bays = set(override.get("balcony_bays", [])) if override else set()
    head = bld["top"] - HEAD_CLEAR                                # highest window head under the parapet
    # string courses and cornice: hero ashlar fronts, or wherever the override forces them (on or off)
    want_bands = bool(override["bands"]) if override and override.get("bands") is not None else hero and ashlar
    want_cornice = bool(override["cornice"]) if override and override.get("cornice") is not None else hero and ashlar
    for fi, z in enumerate(floors):
        fspec = upper[fi] if upper and fi < len(upper) else {}
        fcent = fspec.get("centres", centres)
        sill = fspec.get("sill", 0.9)                             # window floor above the storey base
        for k, c in enumerate(fcent):
            if not fspec and auto and rng.random() < 0.07:
                continue                                          # blind bay
            w_given = k < len(fspec.get("ws", [])) or "w" in fspec
            h_given = k < len(fspec.get("hs", [])) or "h" in fspec
            w = fspec["ws"][k] if k < len(fspec.get("ws", [])) else fspec.get("w", 1.25 if ashlar else 1.1)
            h = fspec["hs"][k] if k < len(fspec.get("hs", [])) else fspec.get("h", min(2.1, storey - 1.3))
            arch = fspec["arches"][k] if k < len(fspec.get("arches", [])) else \
                fspec.get("arch", pick(arch_up if rng.random() < 0.88 else None, arch_up))
            listed = (k in fspec.get("balconies", [])) or (fi == 0 and k in bal_bays)
            drawn = not listed and not fspec and hero and ashlar and rng.random() < 0.08    # a random balcony
            if listed or (drawn and auto):
                v0 = z + 0.08
                hh = max(h + 0.75, 2.5) if h_given else min(max(h + 0.75, 2.5), max(2.1, head - v0))
                f["openings"].append({"kind": "balcony_door", "u0": c - w / 2, "u1": c + w / 2, "v0": v0,
                                      "v1": v0 + hh, "arch": arch, "depth": 0.3,
                                      "lo": fspec.get("lo") or pick("glass" if rng.random() < 0.6 else
                                                                    rng.choice(["shutter_green", "shutter_blue"]), "glass"),
                                      "frame": frame_w, "keystone": hero and arch == "round"})
                bw = fspec.get("balcony_w", w + 0.9)
                f["balconies"].append({"u0": c - bw / 2, "u1": c + bw / 2, "z": z, "depth": fspec.get("balcony_d", 0.85)})
                continue
            if fspec.get("pair"):                                 # coupled windows sharing a frame
                gap = 0.25
                hp = h if h_given else min(h, max(0.6, head - z - sill))
                for s in (-1, 1):
                    cc = c + s * (w / 2 + gap / 2)
                    f["openings"].append({"kind": "window", "u0": cc - w / 2, "u1": cc + w / 2, "v0": z + sill,
                                          "v1": z + sill + hp, "arch": arch, "depth": 0.3, "lo": fspec.get("lo", "glass"),
                                          "frame": frame_w * 0.8, "sill": True})
                continue
            # rubble houses are irregular: windows wander a little; some arches were walled up long ago
            # (not on "auto": false facades, and never away from a width or sill the override gives)
            jit_v = pick(rng.uniform(-0.18, 0.18), 0.0) if not ashlar else 0.0
            jit_w = pick(rng.uniform(-0.12, 0.08), 0.0) if not ashlar else 0.0
            if not w_given:
                w += jit_w
            if not fspec and auto and rng.random() < (0.05 if ashlar else 0.1):
                hw = min(h, max(0.6, head - z - 0.9 - jit_v))
                f["openings"].append({"kind": "window", "u0": c - w / 2, "u1": c + w / 2, "v0": z + 0.9 + jit_v,
                                      "v1": z + 0.9 + jit_v + hw, "arch": arch or "round", "depth": 0.07, "lo": "wall",
                                      "frame": frame_w * 0.8 if frame_w else 0.1})
                continue
            if drawn:
                # "auto": false keeps a window where auto would build a random balcony: make the
                # balcony's draw (its infill) instead of the window's, so the rest of the building
                # keeps its random sequence; the override decides this window below
                lo = "glass" if rng.random() < 0.6 else rng.choice(["shutter_green", "shutter_blue"])
                shut, grille = None, False
            else:
                closed = rng.random() < (0.3 if hero else 0.25)
                lo = rng.choice(["shutter_green", "shutter_green", "shutter_blue", "shutter_brown"]) if closed else "glass"
                shut = None if closed else ("open" if hero and rng.random() < 0.25 else None)
                grille = hero and fi == 0 and rng.random() < 0.35
            if fspec.get("lo") or not auto:                       # the override decides the infill
                lo, shut = fspec.get("lo", "glass"), fspec.get("shutters")
            if "grille" in fspec or not auto:
                grille = bool(fspec.get("grille", False))
            v0w = z + (fspec["sill"] if "sill" in fspec else 0.9 + jit_v)
            if not h_given:                                       # top floor: the head stays under the roof
                h = min(h, max(0.6, head - v0w))
            f["openings"].append({"kind": "window", "u0": c - w / 2, "u1": c + w / 2, "v0": v0w,
                                  "v1": v0w + h, "arch": arch, "depth": 0.3, "lo": lo, "shutters": shut,
                                  "frame": frame_w * 0.8, "sill": True, "keystone": hero and ashlar and arch == "round",
                                  "grille": grille})
            # AC units beside some windows (more on plain back facades)
            if auto and rng.random() < (0.06 if hero else 0.12) and c + w / 2 + 1.1 < L - 0.3:
                f["fixtures"].append({"type": "ac_unit", "u": c + w / 2 + 0.7, "z": z + 0.6})
        if want_bands:
            f["bands"].append({"z": z - 0.12 + (i % 2) * 0.006, "h": 0.2, "d": 0.06})
    top = bld["top"]
    if want_cornice:
        f["cornice"] = {"z": top - 1.25 + (i % 2) * 0.006, "h": 0.32, "d": 0.18}
    # ---- roof drainage: spouts through the parapet + the dark streak they leave (never through an
    #      opening: shops of a low house or a tall window the override gives)
    if tier in ("hero", "mid"):
        u = rng.uniform(1.2, 2.5)
        while u < L - 1.0:
            zs = top - 0.95
            if not any(o["u0"] - 0.1 < u < o["u1"] + 0.1 and o["v0"] < zs + 0.1 and o["v1"] > zs - 0.1 for o in f["openings"]):
                f["fixtures"].append({"type": "spout", "u": round(u, 2), "z": zs})
            u += rng.uniform(4.5, 8.0) if hero else rng.uniform(9.0, 15.0)
        if auto and rng.random() < 0.45:
            pu = rng.choice([0.35, L - 0.35])
            f["fixtures"].append({"type": "pipe", "u": pu, "z0": ground_at(pu) if ground_at else eg, "z1": top - 0.9})
    # ---- wall lanterns + cable runs along street facades
    if hero and auto and L > 6:
        u = rng.uniform(2.0, 4.0)
        while u < L - 1.5:
            if not any(o["u0"] - 0.4 < u < o["u1"] + 0.4 and o["v0"] < eg + 4.6 and o["v1"] > eg + 3.4
                       for o in f["openings"]):
                f["fixtures"].append({"type": "wall_lantern", "u": round(u, 2), "z": eg + 3.9})
                u += rng.uniform(10, 14)
            else:
                u += 0.8
    if tier in ("hero", "mid") and auto and rng.random() < 0.55 and L > 5:
        zc = eg + (g_storey + 0.35 if shops else 3.3) + rng.uniform(-0.1, 0.25)
        if not any(o["v0"] < zc + 0.1 and o["v1"] > zc - 0.1 for o in f["openings"]):
            f["cables"].append({"z": round(zc, 2), "u0": 0.0, "u1": L, "n": rng.choice([1, 2, 3])})
    if override:
        for key in ("signs", "fixtures", "decals", "awnings", "balconies"):
            f[key] += override.get("extra_" + key, [])
    return f

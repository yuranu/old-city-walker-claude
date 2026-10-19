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


def arch_rise(arch, w):
    return {"round": w / 2, "pointed": 0.7746 * w, "segment": 0.18 * w}.get(arch, 0.0)


def top_z_guess(bld):
    return bld["top"]


def storeys_for(bld, eg, g_storey, storey):
    """Floor base heights above the ground floor that still fit under the parapet."""
    out = []
    z = eg + g_storey
    while z + 2.6 <= bld["top"] - 1.0:
        out.append(z)
        z += storey
    return out


def layout(bld, i, eg, rng, override=None):
    a, b = bld["ring"][i], bld["ring"][(i + 1) % len(bld["ring"])]
    _, _, L = edge_frame(a, b)
    st = bld["style"]
    tier = bld["tier"]
    hero = tier == "hero"
    ashlar = st["wall"] == "ashlar"
    f = {"edge": i, "ground": round(eg, 3), "len": round(L, 3), "openings": [], "bands": [], "cornice": None,
         "balconies": [], "awnings": [], "signs": [], "fixtures": [], "decals": [], "cables": []}
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
    g_storey = override.get("ground_storey") if override and override.get("ground_storey") else (4.8 if shops else st["storey"])
    storey = override.get("storey") if override and override.get("storey") else st["storey"]
    arch_up = override.get("arch_up") if override and "arch_up" in override else bld["arch_pref"]
    frame_w = (0.18 if ashlar else 0.13) if hero else 0.0
    thr = 0.12
    # ---- ground floor
    door_bay = rng.randrange(len(centres))
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
            v0, v1 = eg + thr, eg + thr + h
            vs = v1 - arch_rise(arch, w)
            door = g.get("door") if g and g.get("door") else rng.choice(SHOP_DOORS)
            f["openings"].append({"kind": "shop", "u0": c - w / 2, "u1": c + w / 2, "v0": v0, "v1": v1, "arch": arch,
                                  "depth": 0.45, "split": vs if arch else None, "lo": door, "hi": "fanlight",
                                  "frame": frame_w, "keystone": hero and arch == "round", "threshold": True})
            if hero and (g and g.get("sign") or rng.random() < 0.45):
                sw = min(w + 0.5, sp - 0.2)
                cell = g.get("sign") if g and g.get("sign") else rng.choice(SHOP_SIGNS)
                f["signs"].append({"u0": c - sw / 2, "u1": c + sw / 2, "z0": v1 + 0.25, "z1": v1 + 0.85,
                                   "cell": cell, "d": 0.06})
            if hero and rng.random() < 0.18:
                pw = rng.uniform(0.45, 0.6)
                pu = c + w / 2 + 0.15
                if pu + pw < (centres[k + 1] - w / 2 - 0.1 if k + 1 < len(centres) else L - 0.3):
                    f["decals"].append({"type": rng.choice(POSTERS), "u0": pu, "u1": pu + pw,
                                        "z0": eg + 1.3, "z1": eg + 1.3 + pw * 1.4})
        elif kind == "door":
            w = g.get("w", 1.3) if g else 1.3
            arch = g.get("arch", "round") if g else "round"
            v0 = eg + thr
            f["openings"].append({"kind": "door", "u0": c - w / 2, "u1": c + w / 2, "v0": v0, "v1": v0 + 2.75,
                                  "arch": arch, "depth": 0.4, "split": None, "lo": g.get("door", "door_wood") if g else
                                  rng.choice(["door_wood", "door_wood", "door_green"]), "frame": frame_w,
                                  "keystone": hero, "threshold": True})
            if hero and rng.random() < 0.5:                     # house-number / street plaque
                f["fixtures"].append({"type": "plaque", "u": c + w / 2 + 0.45, "z": eg + 2.3})
        else:
            w, h = (0.8, 1.15) if not g else (g.get("w", 0.8), g.get("h", 1.15))
            v0 = eg + 1.6
            f["openings"].append({"kind": "window", "u0": c - w / 2, "u1": c + w / 2, "v0": v0, "v1": v0 + h,
                                  "arch": g.get("arch") if g else None, "depth": 0.3, "lo": "glass",
                                  "frame": frame_w * 0.8, "sill": True, "grille": True})
    # awning over a row of shops (sheet-metal canopies, photos 010 / 022)
    shop_ops = [o for o in f["openings"] if o["kind"] == "shop"]
    want_awning = override.get("awning") if override and "awning" in override else (hero and rng.random() < 0.55)
    if shop_ops and len(shop_ops) >= 2 and want_awning:
        f["awnings"].append({"u0": max(0.15, shop_ops[0]["u0"] - 0.3), "u1": min(L - 0.15, shop_ops[-1]["u1"] + 0.3),
                             "z": max(o["v1"] for o in shop_ops) + 0.12, "depth": 1.3})
    # ---- upper floors
    floors = storeys_for(bld, eg, g_storey, storey)
    upper = override.get("floors") if override else None
    bal_bays = set(override.get("balcony_bays", [])) if override else set()
    for fi, z in enumerate(floors):
        fspec = upper[fi] if upper and fi < len(upper) else {}
        fcent = fspec.get("centres", centres)
        for k, c in enumerate(fcent):
            if not fspec and rng.random() < 0.07:
                continue                                          # blind bay
            w = fspec.get("w", 1.25 if ashlar else 1.1)
            h = fspec.get("h", min(2.1, storey - 1.3))
            arch = fspec.get("arch", arch_up if rng.random() < 0.88 else None)
            balcony = (k in fspec.get("balconies", [])) or (fi == 0 and k in bal_bays) or \
                (not fspec and hero and ashlar and rng.random() < 0.08)
            if balcony:
                v0 = z + 0.08
                hh = max(h + 0.75, 2.5)
                f["openings"].append({"kind": "balcony_door", "u0": c - w / 2, "u1": c + w / 2, "v0": v0,
                                      "v1": v0 + hh, "arch": arch, "depth": 0.3,
                                      "lo": "glass" if rng.random() < 0.6 else rng.choice(["shutter_green", "shutter_blue"]),
                                      "frame": frame_w, "keystone": hero and arch == "round"})
                bw = fspec.get("balcony_w", w + 0.9)
                f["balconies"].append({"u0": c - bw / 2, "u1": c + bw / 2, "z": z, "depth": fspec.get("balcony_d", 0.85)})
                continue
            if fspec.get("pair"):                                 # coupled windows sharing a frame
                gap = 0.25
                for s in (-1, 1):
                    cc = c + s * (w / 2 + gap / 2)
                    f["openings"].append({"kind": "window", "u0": cc - w / 2, "u1": cc + w / 2, "v0": z + 0.9,
                                          "v1": z + 0.9 + h, "arch": arch, "depth": 0.3, "lo": "glass",
                                          "frame": frame_w * 0.8, "sill": True})
                continue
            # rubble houses are irregular: windows wander a little; some arches were walled up long ago
            jit_v = rng.uniform(-0.18, 0.18) if not ashlar else 0.0
            jit_w = rng.uniform(-0.12, 0.08) if not ashlar else 0.0
            w += jit_w
            if not fspec and rng.random() < (0.05 if ashlar else 0.1):
                f["openings"].append({"kind": "window", "u0": c - w / 2, "u1": c + w / 2, "v0": z + 0.9 + jit_v,
                                      "v1": z + 0.9 + jit_v + h, "arch": arch or "round", "depth": 0.07, "lo": "wall",
                                      "frame": frame_w * 0.8 if frame_w else 0.1})
                continue
            closed = rng.random() < (0.3 if hero else 0.25)
            f["openings"].append({"kind": "window", "u0": c - w / 2, "u1": c + w / 2, "v0": z + 0.9 + jit_v,
                                  "v1": z + 0.9 + jit_v + h, "arch": arch, "depth": 0.3,
                                  "lo": rng.choice(["shutter_green", "shutter_green", "shutter_blue", "shutter_brown"])
                                  if closed else "glass",
                                  "shutters": None if closed else ("open" if hero and rng.random() < 0.25 else None),
                                  "frame": frame_w * 0.8, "sill": True, "keystone": hero and ashlar and arch == "round",
                                  "grille": hero and fi == 0 and rng.random() < 0.35})
            # AC units beside some windows (more on plain back facades)
            if rng.random() < (0.06 if hero else 0.12) and c + w / 2 + 1.1 < L - 0.3:
                f["fixtures"].append({"type": "ac_unit", "u": c + w / 2 + 0.7, "z": z + 0.6})
                f["decals"].append({"type": "rust", "u0": c + w / 2 + 0.55, "u1": c + w / 2 + 0.85,
                                    "z0": z - rng.uniform(1.5, 3.5), "z1": z + 0.55})
        if (hero and ashlar) or (override and override.get("bands")):
            f["bands"].append({"z": z - 0.12 + (i % 2) * 0.002, "h": 0.2, "d": 0.06})
    top = bld["top"]
    if hero and (ashlar or (override and override.get("cornice"))):
        f["cornice"] = {"z": top - 1.25 + (i % 2) * 0.002, "h": 0.32, "d": 0.18}
    # ---- weathering: darker patches and wide streaks on old stone (more on rubble houses)
    for _ in range(rng.randint(0, 3 if ashlar else 5)):
        pw = rng.uniform(0.8, 2.5)
        pu = rng.uniform(0.2, max(0.3, L - pw - 0.2))
        pz = rng.uniform(eg + 1.0, max(eg + 1.5, top_z_guess(bld) - 2.5))
        f["decals"].append({"type": rng.choice(["streak_wide", "damp", "streak_wide"]), "u0": pu, "u1": pu + pw,
                            "z0": pz, "z1": pz + rng.uniform(1.0, 3.0)})
    # ---- roof drainage: spouts through the parapet + the dark streak they leave
    if tier in ("hero", "mid"):
        u = rng.uniform(1.2, 2.5)
        while u < L - 1.0:
            f["fixtures"].append({"type": "spout", "u": round(u, 2), "z": top - 0.95})
            ln = rng.uniform(2.5, min(7.0, top - eg - 1.5))
            f["decals"].append({"type": "streak", "u0": u - 0.22, "u1": u + 0.22, "z0": top - 0.95 - ln, "z1": top - 0.85})
            u += rng.uniform(4.5, 8.0)
        if rng.random() < 0.45:
            pu = rng.choice([0.35, L - 0.35])
            f["fixtures"].append({"type": "pipe", "u": pu, "z0": eg, "z1": top - 0.9})
    # ---- wall lanterns + cable runs along street facades
    if hero and L > 6:
        u = rng.uniform(2.0, 4.0)
        while u < L - 1.5:
            if not any(o["u0"] - 0.4 < u < o["u1"] + 0.4 and o["v0"] < eg + 4.6 and o["v1"] > eg + 3.4
                       for o in f["openings"]):
                f["fixtures"].append({"type": "wall_lantern", "u": round(u, 2), "z": eg + 3.9})
                u += rng.uniform(10, 14)
            else:
                u += 0.8
    if tier in ("hero", "mid") and rng.random() < 0.55 and L > 5:
        zc = eg + (g_storey + 0.35 if shops else 3.3) + rng.uniform(-0.1, 0.25)
        if not any(o["v0"] < zc + 0.1 and o["v1"] > zc - 0.1 for o in f["openings"]):
            f["cables"].append({"z": round(zc, 2), "u0": 0.0, "u1": L, "n": rng.choice([1, 2, 3])})
    if override:
        for key in ("signs", "fixtures", "decals", "awnings", "balconies"):
            f[key] += override.get("extra_" + key, [])
    return f

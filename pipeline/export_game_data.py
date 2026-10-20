"""Export what the game needs besides the GLB: a 2D plan for the minimap, the geo origin, and
downscaled reference photos with attribution.

    python3 pipeline/export_game_data.py
"""
import html
import json
import re
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "game/public"


def strip_tags(s):
    return html.unescape(re.sub(r"<[^>]+>", "", s or "")).strip()


# map labels that are areas, not buildings (local metres, x east, y north)
QUARTERS = [([150, 250], "Christian Quarter"), ([520, 420], "Muslim Quarter"), ([390, -190], "Jewish Quarter"),
            ([120, -190], "Armenian Quarter"), ([760, 170], "Temple Mount / Haram al-Sharif")]
GATES = [([0, 0], "Jaffa Gate"), ([-128, 297], "New Gate"), ([268, 557], "Damascus Gate"), ([581, 703], "Herod's Gate"),
         ([888, 467], "Lions' Gate"), ([904, 258], "Golden Gate"), ([628, -200], "Dung Gate"), ([204, -417], "Zion Gate")]


# which quarter each sector belongs to (the souks sit on the Christian/Muslim line; Zion is mostly Armenian)
SECTOR_QUARTER = {"s00_jaffa": "Christian Quarter", "s01_armenian": "Armenian Quarter", "s02_zion": "Armenian Quarter",
                  "s03_christian_w": "Christian Quarter", "s04_sepulchre": "Christian Quarter", "s05_souks": "Muslim Quarter",
                  "s06_jewish": "Jewish Quarter", "s07_kotel": "Jewish Quarter", "s08_damascus": "Muslim Quarter",
                  "s09_wad": "Muslim Quarter", "s10_herod_lions": "Muslim Quarter", "s11_haram": "Temple Mount / Haram al-Sharif"}


def quarter_areas():
    """[{name, rings}] from the sector polygons, for 'which quarter am I in'."""
    from shapely.geometry import shape
    out = []
    for s in json.loads((ROOT / "data/sectors.json").read_text())["sectors"]:
        g = shape(s["geom"]).simplify(2.0)
        rings = [[[round(x, 1), round(y, 1)] for x, y in p.exterior.coords] for p in getattr(g, "geoms", [g])
                 if p.geom_type == "Polygon"]
        out.append({"name": SECTOR_QUARTER.get(s["id"], "Old City"), "rings": rings})
    return out


def ring_simplify(ring, tol=0.35):
    from shapely.geometry import Polygon
    try:
        q = Polygon(ring).simplify(tol)
        return [[round(x, 1), round(y, 1)] for x, y in list(q.exterior.coords)[:-1]] if not q.is_empty else []
    except Exception:  # noqa: BLE001
        return [[round(x, 1), round(y, 1)] for x, y in ring]


def main():
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    sdir = ROOT / "data/spec"
    if (sdir / "base.json").exists():                        # whole city: base (context, walls) + every sector
        base = json.loads((sdir / "base.json").read_text())
        blds = list(base["buildings"])
        for s in json.loads((sdir / "index.json").read_text())["sectors"]:
            blds += json.loads((sdir / ("%s.json" % s["id"])).read_text())["buildings"]
        spec = base
    else:
        spec = json.loads((ROOT / "data/scene_spec.json").read_text())
        blds = spec["buildings"]
    lid_f = ROOT / "data/landmark_ids.json"
    lids = set()
    if lid_f.exists():
        for v in json.loads(lid_f.read_text()).get("modules", json.loads(lid_f.read_text())).values():
            lids |= set(v or [])
    buildings = []
    for b in blds:
        r = ring_simplify(b["ring"])
        if len(r) < 3:
            continue
        rec = {"ring": r, "detailed": b["tier"] != "context"}
        nm = b["tags"].get("name:en") or b["tags"].get("name") or ""
        if nm:
            rec["name"] = nm
        if b["osm"] in lids:
            rec["landmark"] = 1
        buildings.append(rec)
    from shapely.geometry import LineString, Polygon
    city = Polygon(json.loads((ROOT / "data/oldcity_polygon.json").read_text())["ring"]).buffer(60)
    streets = []
    for w in osm["ways"]:
        t = w["tags"]
        pts = w.get("pts") or []
        if not t.get("highway") or len(pts) < 2 or t.get("area") == "yes" or int(t.get("layer", "0") or 0) < -1:
            continue
        ln = LineString(pts)
        if not city.intersects(ln):
            continue
        streets.append({"pts": [[round(x, 1), round(y, 1)] for x, y in ln.simplify(0.5).coords],
                        "name": t.get("name:en") or "", "steps": 1 if t["highway"] == "steps" else 0})
    walls = [w["pts"] for w in spec.get("city_walls", [])] + [[w["a"], w["b"]] for w in spec.get("walls_generic", [])]
    plan = {
        "origin": osm["origin"],
        "buildings": buildings,
        "streets": streets,
        "citadel": [[round(x, 2), round(y, 2)] for x, y in spec["citadel"]["mass"]],
        "gatehouse": spec["gatehouse"]["ring"],
        "walls": walls,
        "spawn": spec["spawn"],
        "quarters": [{"p": p, "name": n} for p, n in QUARTERS],
        "areas": quarter_areas(),
        "gates": [{"p": p, "name": n} for p, n in GATES],
        "labels": [{"p": [30, -40], "name": "Tower of David (Citadel)"}, {"p": [55, 8], "name": "Omar Ibn el-Khattab Square"}]
                  + [{"p": p, "name": n} for p, n in GATES],
    }
    (PUB / "plan.json").write_text(json.dumps(plan, separators=(",", ":")))

    idx = json.loads((ROOT / "data/photos/index.json").read_text())
    out = PUB / "photos"
    out.mkdir(parents=True, exist_ok=True)
    photos = []
    for r in idx:
        src = ROOT / "data/photos" / r.get("file", "")
        if not r.get("file") or not src.exists():
            continue
        dst = out / src.name
        if not dst.exists():
            im = Image.open(src).convert("RGB")
            im.thumbnail((800, 800))
            im.save(dst, quality=82)
        photos.append({"file": "photos/" + src.name, "x": r["x"], "y": r["y"], "title": r["title"][5:],
                       "page": r["page"], "date": r["date"], "licence": r["licence"],
                       "artist": strip_tags(r["artist"])[:80]})
    (PUB / "photos.json").write_text(json.dumps(photos))
    print("plan: %d buildings, %d streets (%d KB); photos: %d" % (len(plan["buildings"]), len(plan["streets"]),
          (PUB / "plan.json").stat().st_size // 1024, len(photos)))


if __name__ == "__main__":
    main()

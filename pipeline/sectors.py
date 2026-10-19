"""Sectors of the walled Old City: the units of research, building, loading and progress.

Each sector is the Old City polygon (data/oldcity_polygon.json, from the OSM wall circuit)
intersected with a hand-drawn box along quarter lines, gates and main streets. A building belongs to the
sector that contains its centroid. Teams work on sectors independently (their own override
folder data/reference/overrides/<sector>/, notes data/reference/<sector>.md, GLBs
game/public/sectors/<sector>.glb and _lo.glb).

    .venv/bin/python pipeline/sectors.py        -> data/sectors.json + data/sectors.png
"""
import json
from pathlib import Path

from shapely.geometry import Polygon, box, mapping, shape

ROOT = Path(__file__).resolve().parent.parent

# id, name, box (x0, y0, x1, y1) in local metres (x east, y north from the Jaffa Gate node),
# entry gate (the direction a team starts from), status
SECTORS = [
    ("s00_jaffa", "Jaffa Gate, Omar Ibn el-Khattab Square, top of David St", (-45, -42, 152, 48), "Jaffa Gate", "hero"),
    ("s01_armenian", "Armenian Quarter: St James, Armenian Patriarchate Rd", (-60, -300, 250, -42), "Jaffa Gate", "mid"),
    ("s02_zion", "Zion Gate and the southern walls", (-180, -440, 330, -300), "Zion Gate", "mid"),
    ("s03_christian_w", "Christian Quarter west: Latin Patriarchate, New Gate", (-180, 48, 160, 430), "New Gate", "mid"),
    ("s04_sepulchre", "Holy Sepulchre, Muristan, Christian Quarter Rd", (152, 48, 400, 430), "Jaffa Gate", "mid"),
    ("s05_souks", "David St lower, Souq el-Lahamin / Attarin / Khawajat", (152, -42, 420, 48), "Jaffa Gate", "mid"),
    ("s06_jewish", "Jewish Quarter: Hurva, Cardo, Batei Mahase", (250, -330, 600, -42), "Zion Gate", "mid"),
    ("s07_kotel", "Western Wall plaza, Dung Gate", (560, -330, 800, -40), "Dung Gate", "mid"),
    ("s08_damascus", "Damascus Gate, Khan ez-Zeit, Al-Wad north", (160, 430, 560, 800), "Damascus Gate", "mid"),
    ("s09_wad", "Via Dolorosa, Al-Wad south, Chain St", (400, -42, 700, 430), "Damascus Gate", "mid"),
    ("s10_herod_lions", "Herod's Gate, Bab Hutta, Lions' Gate", (560, 400, 910, 800), "Lions' Gate", "mid"),
    ("s11_haram", "Temple Mount / Haram al-Sharif", None, "Lions' Gate", "mid"),   # exact enclosure
]


def build():
    oj = json.loads((ROOT / "data/oldcity_polygon.json").read_text())
    oc = Polygon(oj["ring"])
    haram = Polygon(oj["haram"])
    out, taken = [], None
    # the Haram is its own sector: carve its enclosure out of the neighbours first
    order = sorted(SECTORS, key=lambda s: 0 if s[0] == "s11_haram" else 1)
    for sid, name, bx, gate, status in order:
        p = haram.intersection(oc) if bx is None else oc.intersection(box(*bx))
        if taken is not None:
            p = p.difference(taken)
        taken = p if taken is None else taken.union(p)
        out.append({"id": sid, "name": name, "gate": gate, "status": status, "geom": mapping(p.buffer(0))})
    leftover = oc.difference(taken)
    return out, leftover


def load():
    """[(id, shapely geometry, record)] in definition order."""
    d = json.loads((ROOT / "data/sectors.json").read_text())
    return [(s["id"], shape(s["geom"]), s) for s in d["sectors"]]


def main():
    out, leftover = build()
    (ROOT / "data/sectors.json").write_text(json.dumps({"sectors": out}))
    try:
        from PIL import Image, ImageDraw
        oc = Polygon(json.loads((ROOT / "data/oldcity_polygon.json").read_text())["ring"])
        osm = json.loads((ROOT / "data/osm_local.json").read_text())
        x0, y0, x1, y1 = -200, -460, 960, 820
        k = 0.7
        img = Image.new("RGB", (int((x1 - x0) * k), int((y1 - y0) * k)), (245, 242, 235))
        g = ImageDraw.Draw(img)
        P = lambda p: ((p[0] - x0) * k, (y1 - p[1]) * k)
        cols = [(230, 190, 150), (200, 220, 170), (170, 200, 230), (230, 200, 220), (240, 220, 160), (190, 230, 220),
                (220, 180, 200), (200, 200, 240), (180, 220, 180), (240, 200, 180), (210, 210, 170), (200, 180, 230)]
        for i, s in enumerate(out):
            gm = shape(s["geom"])
            for poly in getattr(gm, "geoms", [gm]):
                if poly.geom_type == "Polygon":
                    g.polygon([P(p) for p in poly.exterior.coords], fill=cols[i % len(cols)], outline=(90, 80, 70))
        for b in osm["buildings"]:
            if b["outer"] and len(b["outer"][0]) > 2:
                g.polygon([P(p) for p in b["outer"][0]], outline=(120, 110, 95))
        g.line([P(p) for p in oc.exterior.coords], fill=(80, 40, 10), width=3)
        for s in out:
            c = shape(s["geom"]).representative_point()
            g.text(P((c.x - 30, c.y)), s["id"], fill=(0, 0, 0))
        img.save(ROOT / "data/sectors.png")
    except Exception as e:  # noqa: BLE001
        print("plot skipped:", e)
    oc_area = sum(shape(s["geom"]).area for s in out)
    print("sectors %d, covered %.0f m2, leftover %.0f m2" % (len(out), oc_area, leftover.area))
    for s in out:
        print("  %-16s %7.0f m2  from %-14s %s" % (s["id"], shape(s["geom"]).area, s["gate"], s["name"]))


if __name__ == "__main__":
    main()

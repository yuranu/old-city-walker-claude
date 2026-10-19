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


def main():
    spec = json.loads((ROOT / "data/scene_spec.json").read_text())
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    plan = {
        "origin": osm["origin"],
        "buildings": [{"ring": [[round(x, 2), round(y, 2)] for x, y in b["ring"]], "detailed": b["tier"] != "context",
                       "name": b["tags"].get("name:en") or b["tags"].get("name") or ""} for b in spec["buildings"]],
        "citadel": [[round(x, 2), round(y, 2)] for x, y in spec["citadel"]["mass"]],
        "gatehouse": spec["gatehouse"]["ring"],
        "walls": [w["pts"] for w in spec["city_walls"]],
        "spawn": spec["spawn"],
        "labels": [{"p": [0, 0], "name": "Jaffa Gate"}, {"p": [30, -40], "name": "Tower of David (Citadel)"},
                   {"p": [55, 8], "name": "Omar Ibn el-Khattab Square"}, {"p": [130, 9], "name": "David Street"}],
    }
    (PUB / "plan.json").write_text(json.dumps(plan))

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
    print("plan: %d buildings; photos: %d" % (len(plan["buildings"]), len(photos)))


if __name__ == "__main__":
    main()

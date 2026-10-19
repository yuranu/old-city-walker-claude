"""Render a top-down plan of data/osm_local.json to PNG (for choosing / checking the PoC area).

    python3 pipeline/plot_plan.py [xmin ymin xmax ymax] [out.png] [px_per_m]
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent


def main():
    a = sys.argv[1:]
    xmin, ymin, xmax, ymax = map(float, a[:4]) if len(a) >= 4 else (-120, -160, 260, 160)
    out = Path(a[4]) if len(a) >= 5 else ROOT / "data/plan.png"
    s = float(a[5]) if len(a) >= 6 else 4.0
    d = json.loads((ROOT / "data/osm_local.json").read_text())
    W, H = int((xmax - xmin) * s), int((ymax - ymin) * s)
    img = Image.new("RGB", (W, H), (245, 242, 235))
    g = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 11)
    except OSError:
        font = ImageFont.load_default()
    P = lambda p: ((p[0] - xmin) * s, (ymax - p[1]) * s)

    # grid every 20 m
    for x in range(int(xmin) // 20 * 20, int(xmax) + 1, 20):
        g.line([P((x, ymin)), P((x, ymax))], fill=(225, 222, 215) if x else (200, 150, 150))
        g.text(P((x + 0.5, ymax - 1)), str(x), fill=(160, 160, 160), font=font)
    for y in range(int(ymin) // 20 * 20, int(ymax) + 1, 20):
        g.line([P((xmin, y)), P((xmax, y))], fill=(225, 222, 215) if y else (200, 150, 150))
        g.text(P((xmin + 0.5, y + 2)), str(y), fill=(160, 160, 160), font=font)

    for w in d["ways"]:
        t = w["tags"]
        if "multipolygon" in w or not w.get("closed"):
            continue
        if t.get("area") == "yes" or t.get("highway") == "pedestrian" and w["closed"]:
            g.polygon([P(p) for p in w["pts"]], fill=(232, 222, 200), outline=(200, 185, 160))
    for b in d["buildings"]:
        for ring in b["outer"]:
            if len(ring) > 2:
                g.polygon([P(p) for p in ring], fill=(190, 175, 150), outline=(110, 95, 75))
        for ring in b["inner"]:
            if len(ring) > 2:
                g.polygon([P(p) for p in ring], fill=(245, 242, 235), outline=(110, 95, 75))
    styles = {"steps": ((200, 60, 60), 3), "footway": ((90, 90, 200), 2), "pedestrian": ((60, 140, 60), 3),
              "service": ((120, 120, 120), 2), "residential": ((80, 80, 80), 3)}
    for w in d["ways"]:
        t = w["tags"]
        if "multipolygon" in w:
            continue
        pts = [P(p) for p in w["pts"]]
        if len(pts) < 2:
            continue
        if t.get("barrier") in ("city_wall", "wall", "retaining_wall"):
            g.line(pts, fill=(60, 30, 10) if t["barrier"] == "city_wall" else (150, 110, 80),
                   width=6 if t["barrier"] == "city_wall" else 2)
        elif t.get("highway") in styles and not (w.get("closed") and t.get("area") == "yes"):
            col, wd = styles[t["highway"]]
            if t.get("tunnel") == "yes" or t.get("layer", "0").startswith("-"):
                col = tuple(min(255, c + 100) for c in col)
            g.line(pts, fill=col, width=wd)
    # labels
    for b in d["buildings"] + [w for w in d["ways"] if "multipolygon" not in w]:
        name = b["tags"].get("name:en") or b["tags"].get("name")
        if not name:
            continue
        pts = b["outer"][0] if "outer" in b else b["pts"]
        cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
        if xmin < cx < xmax and ymin < cy < ymax:
            g.text(P((cx, cy)), name[:28], fill=(0, 0, 0), font=font)
    for n in d["nodes"]:
        t = n["tags"]
        if t.get("historic") == "city_gate" or t.get("barrier") in ("gate", "entrance"):
            x, y = P(n["p"])
            g.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(220, 0, 0))
    img.save(out)
    print("wrote", out, img.size)


if __name__ == "__main__":
    main()

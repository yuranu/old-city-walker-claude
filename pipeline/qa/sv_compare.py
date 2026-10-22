"""Side-by-side sheets: Street View still | game view from the same spot, heading and field of view.

    .venv/bin/python pipeline/qa/sv_compare.py <place>      (after qa_capture of build/qa/svcmp/<place>)
-> build/qa/svcmp/<place>/pairs/<view>.jpg and sheet_NN.jpg (3 pairs a sheet)
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent.parent


def main():
    d = ROOT / "build/qa/svcmp" / sys.argv[1]
    views = json.loads((d / "views.json").read_text())
    (d / "pairs").mkdir(exist_ok=True)
    pairs = []
    for v in views:
        g = d / ("%s_n.png" % v["id"])
        s = ROOT / v["sv"]
        if not g.exists() or not s.exists():
            continue
        a = Image.open(s).convert("RGB").resize((768, 512))
        b = Image.open(g).convert("RGB").resize((768, 512))
        im = Image.new("RGB", (1536, 540), "black")
        im.paste(a, (0, 28))
        im.paste(b, (768, 28))
        dr = ImageDraw.Draw(im)
        dr.text((6, 6), "REAL (Street View)  %s  heading %s" % (v["id"], v["heading"]), fill=(255, 255, 0))
        dr.text((774, 6), "MODEL (game, same spot / heading / fov)", fill=(0, 255, 255))
        im.save(d / "pairs" / ("%s.jpg" % v["id"]), quality=85)
        pairs.append(im)
    for k in range(0, len(pairs), 3):
        grp = pairs[k:k + 3]
        sh = Image.new("RGB", (1536, 540 * len(grp)), "black")
        for j, im in enumerate(grp):
            sh.paste(im, (0, 540 * j))
        sh.save(d / ("sheet_%02d.jpg" % (k // 3)), quality=80)
    print("%d pairs, %d sheets" % (len(pairs), (len(pairs) + 2) // 3))


if __name__ == "__main__":
    main()

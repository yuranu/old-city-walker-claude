"""Contact sheets of QA captures for the vision critic: 2x2 normal frames per sheet, each labelled
with its view id (so a finding can name the view and the quadrant).

    .venv/bin/python pipeline/qa/sheets.py build/qa/<run>/<part>    -> sheets/sheet_NNN.jpg + sheets.json
"""
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw


def main():
    run = Path(sys.argv[1])
    views = json.loads((run / "captured.json").read_text())
    out = run / "sheets"
    out.mkdir(exist_ok=True)
    index = []
    W, H = 640, 427
    for s in range(0, len(views), 4):
        group = views[s:s + 4]
        sheet = Image.new("RGB", (W * 2, H * 2), (0, 0, 0))
        g = ImageDraw.Draw(sheet)
        for i, v in enumerate(group):
            im = Image.open(run / ("%s_n.png" % v["id"])).convert("RGB").resize((W, H))
            ox, oy = (i % 2) * W, (i // 2) * H
            sheet.paste(im, (ox, oy))
            g.rectangle([ox, oy, ox + 300, oy + 18], fill=(0, 0, 0))
            g.text((ox + 4, oy + 3), "%d: %s" % (i + 1, v["id"]), fill=(255, 255, 0))
        name = "sheet_%03d.jpg" % (s // 4)
        sheet.save(out / name, quality=85)
        index.append({"sheet": str((out / name).resolve()), "views": [v["id"] for v in group],
                      "poses": [{k: v[k] for k in ("x", "y", "heading", "pitch", "z_eye")} for v in group]})
    (run / "sheets.json").write_text(json.dumps(index, indent=1))
    print("%d sheets" % len(index))


if __name__ == "__main__":
    main()

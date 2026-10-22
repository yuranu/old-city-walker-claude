"""Contact sheet of a place's reference photos: python pipeline/qa/photo_sheet.py <place> <out.jpg>"""
import json, sys
from pathlib import Path
from PIL import Image, ImageDraw
d = Path("data/photos_ref/iconic") / sys.argv[1]
idx = json.loads((d / "index.json").read_text())
W, H, C = 400, 300, 4
ims = []
for k, m in enumerate(idx):
    im = Image.open(d / m["file"]).convert("RGB"); im.thumbnail((W, H))
    t = Image.new("RGB", (W, H), "black"); t.paste(im, ((W - im.width) // 2, (H - im.height) // 2))
    ImageDraw.Draw(t).text((4, 4), "%02d" % k, fill=(255, 255, 0)); ims.append(t)
R = (len(ims) + C - 1) // C
sheet = Image.new("RGB", (W * C, H * R), "black")
for k, t in enumerate(ims): sheet.paste(t, ((k % C) * W, (k // C) * H))
sheet.save(sys.argv[2], quality=85)

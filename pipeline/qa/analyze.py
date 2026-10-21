"""Image checks on QA captures (game/scripts/qa_capture.mjs output):

* holes: magenta pixels in the sky-keyed frame below the horizon band = sky seen through or under
  the ground;
* flicker: pixels that change strongly between the frame and the frame from 1 cm away, in compact
  clusters (ordinary geometry moves < 0.1 px; z-fighting faces flip between textures).

    .venv/bin/python pipeline/qa/analyze.py build/qa/<run>/<part>      -> image_findings.json + crops
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from common import finding  # noqa: E402


def components(mask, min_px):
    """Connected components (4-neighbour) of a boolean mask -> [(area, x0, y0, x1, y1)]."""
    from collections import deque
    h, w = mask.shape
    seen = np.zeros_like(mask, bool)
    out = []
    ys, xs = np.nonzero(mask)
    for y, x in zip(ys, xs):
        if seen[y, x]:
            continue
        q = deque([(y, x)])
        seen[y, x] = True
        area, x0, y0, x1, y1 = 0, x, y, x, y
        while q:
            cy, cx = q.popleft()
            area += 1
            x0, x1, y0, y1 = min(x0, cx), max(x1, cx), min(y0, cy), max(y1, cy)
            for ny, nx in ((cy + 1, cx), (cy - 1, cx), (cy, cx + 1), (cy, cx - 1)):
                if 0 <= ny < h and 0 <= nx < w and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((ny, nx))
        if area >= min_px:
            out.append((area, x0, y0, x1, y1))
    return out


def dilate(m, r=1):
    o = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            o |= np.roll(np.roll(m, dy, 0), dx, 1)
    return o


def erode(m, r=1):
    return ~dilate(~m, r)


def ground_xy(v, px, py, W, H):
    """Rough ground position of an image point (for locating a finding): ray to the eye-height plane."""
    f = (H / 2) / math.tan(math.radians(v.get("fov", 75)) / 2)
    ang_v = math.radians(v.get("pitch", 0)) - math.atan((py - H / 2) / f)
    ang_h = math.radians(v["heading"]) + math.atan((px - W / 2) / f)
    eye = v.get("z_eye", 1.7)
    d = eye / math.tan(-ang_v) if ang_v < -0.02 else 30.0
    d = min(d, 60.0)
    return v["x"] + d * math.sin(ang_h), v["y"] + d * math.cos(ang_h)


def main():
    run = Path(sys.argv[1])
    views = json.loads((run / "captured.json").read_text())
    crops = run / "crops"
    crops.mkdir(exist_ok=True)
    out = []
    for v in views:
        try:
            n = np.asarray(Image.open(run / ("%s_n.png" % v["id"])).convert("RGB"), np.int16)
            j = np.asarray(Image.open(run / ("%s_j.png" % v["id"])).convert("RGB"), np.int16)
            k = np.asarray(Image.open(run / ("%s_k.png" % v["id"])).convert("RGB"), np.int16)
        except FileNotFoundError:
            continue
        H, W, _ = n.shape
        f = (H / 2) / math.tan(math.radians(v.get("fov", 75)) / 2)
        hrow = H / 2 + math.tan(math.radians(v.get("pitch", 0))) * f      # horizon row
        rows = np.arange(H)[:, None]
        # more than 5 degrees below the horizon: sky just under it is the world's far edge (seen through
        # foliage or over low walls from the low parts of the city), not a hole near the camera
        elev = math.radians(v.get("pitch", 0)) - np.arctan((rows - H / 2) / f)
        below = elev < -math.radians(10.0 if v.get("z_eye", 1.7) > 5 else 5.0)   # (aerial: the valleys beyond)
        magenta = (k[:, :, 0] > 230) & (k[:, :, 1] < 40) & (k[:, :, 2] > 230)
        cyan = (k[:, :, 0] < 40) & (k[:, :, 1] > 230) & (k[:, :, 2] > 230)
        geom = ~(magenta | cyan)
        # a hole has geometry above it in its column; sky past the far edge of the world does not
        first = np.where(geom.any(axis=0), geom.argmax(axis=0), H)
        mag = magenta & below & (rows > first[None, :])
        for area, x0, y0, x1, y1 in components(mag, 40):
            gx, gy = ground_xy(v, (x0 + x1) / 2, (y0 + y1) / 2, W, H)
            cid = "%s_hole_%d_%d" % (v["id"], x0, y0)
            Image.fromarray(n[max(0, y0 - 40):y1 + 40, max(0, x0 - 40):x1 + 40].astype(np.uint8)).save(crops / (cid + ".png"))
            out.append(finding("hole", 0, "high", gx, gy, what="sky visible below the horizon (%d px)" % area,
                               evidence={"crop": "crops/%s.png" % cid, "px": area, "bbox": [x0, y0, x1, y1]}, view=v["id"]))
        # parallax-tolerant: the jitter moves the camera 1 cm sideways, which shifts edges right next to the
        # camera (grille bars, lamp posts, mortar joints) by a few pixels; a z-fighting face flips in place
        d = None
        for dx in range(-4, 5):
            dd = np.abs(n - np.roll(j, dx, axis=1)).max(axis=2)
            d = dd if d is None else np.minimum(d, dd)
        raw = d > 70
        m = erode(raw, 2)                        # thin aliasing (grille bars, edges, cables) goes;
        m = dilate(m, 3)                         # solid flipping patches (z-fighting) stay
        for area, x0, y0, x1, y1 in components(m, 150):
            if (x1 - x0) < 8 or (y1 - y0) < 8:
                continue
            fill = raw[y0:y1 + 1, x0:x1 + 1].mean()
            if fill < 0.3:                       # sparse lines inside the box: aliasing, not a flipping face
                continue
            gx, gy = ground_xy(v, (x0 + x1) / 2, (y0 + y1) / 2, W, H)
            cid = "%s_flick_%d_%d" % (v["id"], x0, y0)
            Image.fromarray(np.concatenate([n[max(0, y0 - 30):y1 + 30, max(0, x0 - 30):x1 + 30],
                                            j[max(0, y0 - 30):y1 + 30, max(0, x0 - 30):x1 + 30]], axis=1).astype(np.uint8)) \
                .save(crops / (cid + ".png"))
            out.append(finding("flicker", 0, "high", gx, gy, what="surface flips between frames 1 cm apart (%d px)" % area,
                               evidence={"crop": "crops/%s.png" % cid, "px": area, "bbox": [x0, y0, x1, y1]}, view=v["id"]))
    (run / "image_findings.json").write_text(json.dumps(out, indent=1, default=int))
    kinds = {}
    for o in out:
        kinds[o["kind"]] = kinds.get(o["kind"], 0) + 1
    print("%d views, image findings: %s" % (len(views), kinds))


if __name__ == "__main__":
    main()

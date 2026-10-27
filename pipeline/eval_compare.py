"""Compare model renders with the evaluation photographs and score their alignment.

    python3 pipeline/eval_compare.py [compare] [--only a,b]   # compare images + sheet + scores
    python3 pipeline/eval_compare.py overlay NAME [--suffix _try]   # pose-refinement overlay
    python3 pipeline/eval_compare.py refine NAME [--params heading,pitch,fov] [--iters 6] [--write]

Inputs : data/reference/eval_cams.json, the photos, renders/eval/<name>_model.png / _mask.png /
         _model.json written by blender/render_eval.py.
Outputs: renders/eval/<name>_compare.jpg   photo | model, credits, pose and scores
         renders/eval/<name>_overlay.jpg   photo/model 50% blend | edge + skyline overlay
         renders/eval/<name>_photo_sky.png automatic sky segmentation of the photo (check it!)
         renders/eval/sheet.jpg            contact sheet of every cam (photo | model | overlay)
         renders/eval/scores.json          latest scores; renders/eval/history.jsonl one line per run

Scores (all computed at 480 px on the long side, numpy only):
  sky      IoU of the sky regions (photo: flood fill from the top edge; model: render alpha).
  skyline  median |row of first non-sky pixel| difference per column, % of image height.
           Small = building tops/silhouettes line up. Grows when the pose drifts or heights change.
  edges    F1 of Canny-like edge maps matched within 1% of the image diagonal.
  align    0.5 * sky + 0.5 * edges (0..1); the single number to track per cam.
"""
import argparse
import datetime
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parent.parent
CAMS = ROOT / "data/reference/eval_cams.json"
OUT = ROOT / "renders/eval"
WORK = 480                       # long side for scoring
FONT_PATHS = ["/usr/share/fonts/TTF/DejaVuSans.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
              "/usr/share/fonts/dejavu/DejaVuSans.ttf"]


def font(size):
    for p in FONT_PATHS:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


# ---------------------------------------------------------------- image ops (numpy only)
def shift(a, dy, dx, fill=0):
    """out[y, x] = a[y - dy, x - dx]  (content moves by +dy, +dx)."""
    out = np.full_like(a, fill)
    h, w = a.shape[:2]
    ys, yd = (slice(0, h - dy), slice(dy, h)) if dy >= 0 else (slice(-dy, h), slice(0, h + dy))
    xs, xd = (slice(0, w - dx), slice(dx, w)) if dx >= 0 else (slice(-dx, w), slice(0, w + dx))
    out[yd, xd] = a[ys, xs]
    return out


def blur(a, sigma):
    r = max(1, int(3 * sigma + 0.5))
    k = np.exp(-np.arange(-r, r + 1) ** 2 / (2 * sigma * sigma))
    k /= k.sum()
    p = np.pad(a, [(r, r), (r, r)] + [(0, 0)] * (a.ndim - 2), mode="edge")
    tmp = sum(k[i] * p[i:i + a.shape[0]] for i in range(2 * r + 1))
    return sum(k[i] * tmp[:, i:i + a.shape[1]] for i in range(2 * r + 1))


def dilate(m, r):
    out = m.copy()
    for dy in range(-r, r + 1):
        for dx in range(-r, r + 1):
            if dy or dx:
                out |= shift(m, dy, dx, False)
    return out


def canny(gray, sigma=1.4, hi_pct=85.0, lo_ratio=0.45):
    g = blur(gray.astype(np.float32), sigma)
    gx = (shift(g, 0, -1) - shift(g, 0, 1)) * 2 + (shift(g, -1, -1) - shift(g, -1, 1)) + (shift(g, 1, -1) - shift(g, 1, 1))
    gy = (shift(g, -1, 0) - shift(g, 1, 0)) * 2 + (shift(g, -1, -1) - shift(g, 1, -1)) + (shift(g, -1, 1) - shift(g, 1, 1))
    mag = np.hypot(gx, gy)
    mag[:2], mag[-2:], mag[:, :2], mag[:, -2:] = 0, 0, 0, 0
    ang = (np.degrees(np.arctan2(gy, gx)) + 180) % 180
    nms = np.zeros_like(mag, bool)
    for lo, hi, (dy, dx) in ((0, 22.5, (0, 1)), (157.5, 180.1, (0, 1)), (22.5, 67.5, (1, 1)),
                             (67.5, 112.5, (1, 0)), (112.5, 157.5, (1, -1))):
        sel = (ang >= lo) & (ang < hi)
        nms |= sel & (mag >= shift(mag, dy, dx)) & (mag >= shift(mag, -dy, -dx))
    nms &= mag > 1e-3
    if not nms.any():
        return nms
    hi_t = np.percentile(mag[nms], hi_pct)
    strong, weak = nms & (mag >= hi_t), nms & (mag >= hi_t * lo_ratio)
    e = strong
    for _ in range(60):
        n = dilate(e, 1) & weak
        if n.sum() == e.sum():
            break
        e = n
    return e


def photo_sky(rgb):
    """Sky = smooth, bright-ish region flood-filled from the top edge (numpy, no ML).
    rgb float32 HxWx3 0..255 at working resolution."""
    s = blur(rgb, 1.0)
    r, g, b = s[..., 0], s[..., 1], s[..., 2]
    v = s.max(axis=2)
    sat = (v - s.min(axis=2)) / np.maximum(v, 1)
    gray = s.mean(axis=2)
    gm = np.hypot(shift(gray, 0, 1) - shift(gray, 0, -1), shift(gray, 1, 0) - shift(gray, -1, 0))
    blue = (b > r + 8) & (v > 80)
    white = (sat < 0.18) & (v > 150)
    smooth = gm < 14
    # clear blue sky at the top -> do not accept white/grey pixels (pale sunlit stone leaks in)
    top_sky = ((blue | white) & smooth)[:3]
    if top_sky.any() and (blue & smooth)[:3][top_sky].mean() > 0.6:
        skylike = blue & smooth
    else:
        skylike = (blue | white) & smooth
    # seeds: sky-like pixels in the top row band
    seed = np.zeros_like(skylike)
    seed[:3] = skylike[:3]
    tol = 9.0
    oks = {}
    for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        diff = np.abs(s - shift(s, dy, dx)).max(axis=2)
        oks[(dy, dx)] = skylike & (diff < tol)
    m = seed
    for _ in range(4 * (rgb.shape[0] + rgb.shape[1])):
        n = m.copy()
        for (dy, dx), ok in oks.items():
            n |= shift(m, dy, dx, False) & ok
        if n.sum() == m.sum():
            break
        m = n
    # close pinholes (wires, lamp heads) but never grow below the true skyline much
    m = ~dilate(~dilate(m, 1), 1)
    return m


def skyline(sky):
    """Row index of the first non-sky pixel in each column (h if the column is all sky)."""
    h = sky.shape[0]
    ns = ~sky
    first = np.where(ns.any(axis=0), ns.argmax(axis=0), h)
    return first


def to_work(img, size):
    return np.asarray(img.convert("RGB").resize(size, Image.LANCZOS)).astype(np.float32)


# ---------------------------------------------------------------- scoring
def score(photo_img, model_img, model_mask_img, cache_sky=None):
    w, h = model_img.size
    k = WORK / max(w, h)
    size = (max(2, round(w * k)), max(2, round(h * k)))
    P = to_work(photo_img, size)
    M = to_work(model_img, size)
    msky = np.asarray(model_mask_img.convert("L").resize(size, Image.NEAREST)) < 128
    psky = photo_sky(P)
    if cache_sky:
        Image.fromarray((psky * 255).astype(np.uint8)).save(cache_sky)
    res = {}
    sky_frac = psky.mean()
    if sky_frac > 0.01:
        inter, union = (psky & msky).sum(), (psky | msky).sum()
        res["sky"] = round(float(inter / max(union, 1)), 3)
        sp, sm = skyline(psky), skyline(msky)
        cols = (sp > 0) | (sm > 0)            # columns where at least one image shows sky
        res["skyline"] = round(float(np.median(np.abs(sp - sm)[cols]) / size[1] * 100), 2) \
            if cols.mean() > 0.1 else None
    else:
        res["sky"], res["skyline"] = None, None
    pe = canny(P.mean(axis=2))
    me = canny(M.mean(axis=2)) | (dilate(msky, 1) & ~msky)
    tol = max(2, round(0.01 * math.hypot(*size)))
    pd, md = dilate(pe, tol), dilate(me, tol)
    prec = (me & pd).sum() / max(me.sum(), 1)
    rec = (pe & md).sum() / max(pe.sum(), 1)
    res["edges"] = round(float(2 * prec * rec / max(prec + rec, 1e-6)), 3)
    res["align"] = round(0.5 * (res["sky"] if res["sky"] is not None else res["edges"]) + 0.5 * res["edges"], 3)
    res["photo_sky_frac"] = round(float(sky_frac), 3)
    return res, (psky, msky, pe, me, size)


# ---------------------------------------------------------------- drawing
def load_photo(cam):
    return ImageOps.exif_transpose(Image.open(ROOT / cam["photo"])).convert("RGB")


def fit_h(img, h):
    return img.resize((max(1, round(img.width * h / img.height)), h), Image.LANCZOS)


def short_credit(credit, n=90):
    return credit if len(credit) <= n else credit[: n - 1] + "…"


def overlay_image(photo, model, dbg, h):
    """Left: 50% blend. Right: grey photo + photo edges (green), model edges (magenta),
    photo skyline (cyan) and model skyline (yellow)."""
    psky, msky, pe, me, size = dbg
    P = photo.resize(size, Image.LANCZOS)
    M = model.resize(size, Image.LANCZOS)
    blend = Image.blend(P, M, 0.5)
    g = np.asarray(P.convert("L")).astype(np.float32) * 0.55
    o = np.stack([g, g, g], axis=2)
    o[pe] = (60, 230, 60)
    o[me] = (255, 40, 255)
    o[pe & me] = (255, 255, 255)
    for sky, col in ((psky, (0, 230, 255)), (msky, (255, 230, 0))):
        line = skyline(sky)
        for x, y in enumerate(line):
            if 0 < y < size[1]:
                o[max(0, y - 1):y + 1, x] = col
    ov = Image.fromarray(o.clip(0, 255).astype(np.uint8))
    return fit_h(blend, h), fit_h(ov, h)


def header(draw, x, y, lines, fnt, fill="white"):
    for i, t in enumerate(lines):
        draw.text((x, y + i * (fnt.size + 4)), t, font=fnt, fill=fill)


def draw_labels(img, info, scale_w, scale_h, fnt):
    d = ImageDraw.Draw(img)
    used = []
    for lab in (info or {}).get("labels", [])[:14]:
        x, y = lab["u"] * scale_w, lab["v"] * scale_h
        if any(abs(x - ux) < 90 and abs(y - uy) < 16 for ux, uy in used):
            continue
        used.append((x, y))
        t = lab["text"]
        tw = d.textlength(t, font=fnt)
        d.rectangle((x - tw / 2 - 3, y - 2, x + tw / 2 + 3, y + fnt.size + 3), fill=(0, 0, 0))
        d.text((x - tw / 2, y), t, font=fnt, fill=(255, 235, 120))


def compare_image(name, cam, photo, model, info, sc, h=720):
    P, M = fit_h(photo, h), fit_h(model, h)
    M = M.resize((P.width, h), Image.LANCZOS) if abs(M.width - P.width) > 2 else M
    draw_labels(M, info, M.width, h, font(15))
    pad, top, bot = 8, 58, 34
    W = max(P.width + M.width + 3 * pad, 1240)          # room for the headers on portrait photos
    im = Image.new("RGB", (W, h + top + bot), (24, 24, 24))
    im.paste(P, (pad, top))
    im.paste(M, (2 * pad + P.width, top))
    d = ImageDraw.Draw(im)
    f1, f2 = font(20), font(14)
    d.text((pad, 6), "PHOTO  %s" % name, font=f1, fill="white")
    d.text((pad, 32), short_credit(cam.get("credit", ""), 120), font=f2, fill=(200, 200, 200))
    blend = Path((info or {}).get("blend", "")).name
    d.text((2 * pad + P.width, 6), "MODEL  %s" % blend, font=f1, fill="white")
    d.text((2 * pad + P.width, 32), "x %.1f  y %.1f  eye %.2f m  heading %.1f°  pitch %.1f°  vfov %.1f°" % (
        cam["x"], cam["y"], cam["z_eye"], cam["heading"], cam.get("pitch", 0), cam["fov"]), font=f2, fill=(200, 200, 200))
    d.text((pad, top + h + 8), score_text(sc), font=f2, fill=(255, 220, 120))
    return im


def score_text(sc):
    def f(v, fmt):
        return "n/a" if v is None else fmt % v
    return "align %s   sky IoU %s   skyline err %s   edges F1 %s" % (
        f(sc.get("align"), "%.2f"), f(sc.get("sky"), "%.2f"), f(sc.get("skyline"), "%.1f%%"), f(sc.get("edges"), "%.2f"))


def contact_sheet(rows, out, ph=260):
    """rows: [(name, photo, model, overlay_right, scores)] -> 2 cams per row."""
    cells = []
    for name, photo, model, ov, sc in rows:
        P, M, O = fit_h(photo, ph), fit_h(model, ph), fit_h(ov, ph)
        M = M.resize((P.width, ph)) if abs(M.width - P.width) > 2 else M
        O = O.resize((P.width, ph)) if abs(O.width - P.width) > 2 else O
        cw = P.width + M.width + O.width + 8
        cell = Image.new("RGB", (cw, ph + 48), (24, 24, 24))
        cell.paste(P, (0, 40))
        cell.paste(M, (P.width + 4, 40))
        cell.paste(O, (P.width + M.width + 8, 40))
        d = ImageDraw.Draw(cell)
        d.text((4, 2), name, font=font(18), fill="white")
        d.text((4, 22), score_text(sc), font=font(13), fill=(255, 220, 120))
        cells.append(cell)
    if not cells:
        return
    cols = 2
    cw = max(c.width for c in cells)
    chh = max(c.height for c in cells)
    nrows = math.ceil(len(cells) / cols)
    title_h = 40
    sheet = Image.new("RGB", (cols * cw + (cols + 1) * 10, title_h + nrows * (chh + 10) + 10), (12, 12, 12))
    d = ImageDraw.Draw(sheet)
    mean = [r[4]["align"] for r in rows if r[4].get("align") is not None]
    d.text((10, 8), "Evaluation sheet  %s   mean align %.3f   (photo | model | overlay: green photo edges, magenta model "
                    "edges, cyan photo skyline, yellow model skyline)" % (
                        datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), sum(mean) / max(len(mean), 1)),
           font=font(17), fill="white")
    for i, c in enumerate(cells):
        sheet.paste(c, (10 + (i % cols) * (cw + 10), title_h + (i // cols) * (chh + 10)))
    sheet.save(out, quality=88)


# ---------------------------------------------------------------- commands
def model_paths(name, suffix=""):
    return (OUT / ("%s_model%s.png" % (name, suffix)), OUT / ("%s_mask%s.png" % (name, suffix)),
            OUT / ("%s_model%s.json" % (name, suffix)))


def cmd_compare(a):
    cams = json.loads(CAMS.read_text())["cams"]
    only = {s for s in (a.only or "").split(",") if s}
    rows, scores = [], {}
    for name, cam in cams.items():
        if only and name not in only:
            continue
        mp, kp, jp = model_paths(name)
        if not mp.exists():
            print("no render for", name, "(run blender/render_eval.py)")
            continue
        if not (ROOT / cam["photo"]).exists():
            print("skip %s: photo missing (%s; ./fetch_data.sh --photos)" % (name, cam["photo"]))
            continue
        photo, model = load_photo(cam), Image.open(mp).convert("RGB")
        mask = Image.open(kp) if kp.exists() else Image.new("L", model.size, 255)
        info = json.loads(jp.read_text()) if jp.exists() else {}
        sc, dbg = score(photo, model, mask, cache_sky=OUT / ("%s_photo_sky.png" % name))
        scores[name] = sc
        compare_image(name, cam, photo, model, info, sc).save(OUT / ("%s_compare.jpg" % name), quality=88)
        bl, ov = overlay_image(photo, model, dbg, 540)
        ovi = Image.new("RGB", (bl.width + ov.width + 8, 540), (24, 24, 24))
        ovi.paste(bl, (0, 0))
        ovi.paste(ov, (bl.width + 8, 0))
        ovi.save(OUT / ("%s_overlay.jpg" % name), quality=88)
        rows.append((name, photo, model, ov, sc))
        print("%-18s %s" % (name, score_text(sc)))
    if not rows:
        return
    if not only:
        contact_sheet(rows, OUT / "sheet.jpg")
        print("sheet ->", (OUT / "sheet.jpg").relative_to(ROOT))
    blend, blend_mtime, poses = None, None, {}
    for name in scores:
        jp = model_paths(name)[2]
        if jp.exists():
            info = json.loads(jp.read_text())
            blend, blend_mtime = blend or info.get("blend"), blend_mtime or info.get("blend_mtime")
            pz = info.get("pose", {})
            poses[name] = [pz.get(k) for k in ("x", "y", "z_eye", "heading", "pitch", "fov")]
    rec = {"time": datetime.datetime.now().isoformat(timespec="seconds"), "blend": blend,
           "blend_mtime": blend_mtime,
           "mean_align": round(sum(s["align"] for s in scores.values()) / len(scores), 3), "cams": scores,
           "poses": poses}
    if not only:
        (OUT / "scores.json").write_text(json.dumps(rec, indent=1) + "\n")
        with open(OUT / "history.jsonl", "a") as f:
            f.write(json.dumps(rec) + "\n")
        print("mean align %.3f  -> renders/eval/scores.json, history.jsonl" % rec["mean_align"])


def cmd_overlay(a):
    cams = json.loads(CAMS.read_text())["cams"]
    cam = cams[a.name]
    mp, kp, _ = model_paths(a.name, a.suffix)
    photo, model = load_photo(cam), Image.open(mp).convert("RGB")
    mask = Image.open(kp) if kp.exists() else Image.new("L", model.size, 255)
    sc, dbg = score(photo, model, mask)
    bl, ov = overlay_image(photo, model, dbg, a.height)
    P, M = fit_h(photo, a.height), fit_h(model, a.height)
    im = Image.new("RGB", (P.width * 2 + 8, a.height * 2 + 8 + 26), (24, 24, 24))
    im.paste(P, (0, 26))
    im.paste(M, (P.width + 8, 26))
    im.paste(bl, (0, a.height + 34))
    im.paste(ov, (P.width + 8, a.height + 34))
    ImageDraw.Draw(im).text((4, 4), "%s%s  %s" % (a.name, a.suffix, score_text(sc)), font=font(16), fill="white")
    out = Path(a.out) if a.out else OUT / ("%s_overlay%s.jpg" % (a.name, a.suffix))
    im.save(out, quality=88)
    print(out, score_text(sc))


def hfov(cam, aspect):
    return math.degrees(2 * math.atan(math.tan(math.radians(cam["fov"]) / 2) * aspect))


def cmd_plan(a):
    """Top-down plan of the footprints (data/scene_spec.json) with every camera's position and
    horizontal field of view -> renders/eval/cams_plan.png. Use it to sanity-check poses."""
    spec = json.loads((ROOT / "data/scene_spec.json").read_text())
    cams = json.loads(CAMS.read_text())["cams"]
    xs = [c["x"] for c in cams.values()] + [0, 140]
    ys = [c["y"] for c in cams.values()] + [-40, 40]
    x0, x1, y0, y1 = min(xs) - 25, max(xs) + 25, min(ys) - 25, max(ys) + 25
    s = a.scale

    def P(p):
        return ((p[0] - x0) * s, (y1 - p[1]) * s)
    im = Image.new("RGB", (int((x1 - x0) * s), int((y1 - y0) * s)), (245, 242, 235))
    d = ImageDraw.Draw(im)
    for gx in range(int(x0 // 20 * 20), int(x1) + 1, 20):
        d.line([P((gx, y0)), P((gx, y1))], fill=(225, 222, 215))
        d.text(P((gx + 0.5, y1 - 1)), str(gx), font=font(11), fill=(150, 150, 150))
    for gy in range(int(y0 // 20 * 20), int(y1) + 1, 20):
        d.line([P((x0, gy)), P((x1, gy))], fill=(225, 222, 215))
        d.text(P((x0 + 0.5, gy + 2)), str(gy), font=font(11), fill=(150, 150, 150))
    cit = spec.get("citadel", {})
    if cit.get("outer"):
        d.polygon([P(p) for p in cit["outer"]], fill=(222, 214, 196), outline=(170, 160, 140))
    for b in spec.get("buildings", []):
        ring = b.get("ring")
        if ring:
            hero = b.get("tier") == "hero" or b.get("detailed")
            d.polygon([P(p) for p in ring], fill=(200, 184, 156) if hero else (215, 205, 188), outline=(120, 105, 85))
            if hero and b.get("top") is not None:
                c = b.get("c") or [sum(p[0] for p in ring) / len(ring), sum(p[1] for p in ring) / len(ring)]
                d.text(P(c), "%.0fm" % (b["top"] - b.get("ground", 0)), font=font(10), fill=(90, 70, 50))
    if cit.get("mass"):
        d.polygon([P(p) for p in cit["mass"]], fill=(185, 168, 140), outline=(90, 75, 55))
    for t in cit.get("towers", []):
        if t.get("kind") == "box":
            cx, cy = t["c"]
            hw, hh = t["size"][0] / 2, t["size"][1] / 2
            r = math.radians(t.get("rot", 0))
            pts = [(cx + u * math.cos(r) - v * math.sin(r), cy + u * math.sin(r) + v * math.cos(r))
                   for u, v in ((-hw, -hh), (hw, -hh), (hw, hh), (-hw, hh))]
            d.polygon([P(p) for p in pts], fill=(165, 145, 115), outline=(80, 65, 45))
    for w in spec.get("city_walls", []):
        d.line([P(p) for p in w["pts"]], fill=(90, 70, 50), width=max(2, int(w.get("thick", 3) * s)))
    g = spec.get("gatehouse", {})
    if g.get("ring"):
        d.polygon([P(p) for p in g["ring"]], fill=(150, 125, 95), outline=(60, 45, 30))
    for name, c in cams.items():
        try:
            w, h = ImageOps.exif_transpose(Image.open(ROOT / c["photo"])).size
        except OSError:
            w, h = 4, 3
        hf = hfov(c, w / h)
        e = P((c["x"], c["y"]))
        L = 40
        pts = [e]
        for k in range(13):
            ang = math.radians(c["heading"] - hf / 2 + hf * k / 12)
            pts.append(P((c["x"] + L * math.sin(ang), c["y"] + L * math.cos(ang))))
        d.polygon(pts, fill=None, outline=(30, 90, 200))
        d.line([e, P((c["x"] + L * math.sin(math.radians(c["heading"])), c["y"] + L * math.cos(math.radians(c["heading"]))))],
               fill=(30, 90, 200), width=2)
        d.ellipse((e[0] - 4, e[1] - 4, e[0] + 4, e[1] + 4), fill=(220, 40, 40))
        d.text((e[0] + 6, e[1] - 6), name, font=font(13), fill=(160, 20, 20))
    out = OUT / "cams_plan.png"
    im.save(out)
    print(out.relative_to(ROOT))


def blender_env():
    """Render on the discrete GPU when there is one (Mesa PRIME offload, as build.sh does)."""
    env = dict(os.environ)
    try:
        if "DRI_PRIME" not in env and sum(n.startswith("renderD") for n in os.listdir("/dev/dri")) > 1:
            env["DRI_PRIME"] = "1"
    except OSError:
        pass
    return env


STEPS = {"heading": 2.0, "pitch": 1.0, "roll": 1.0, "fov": 3.0, "x": 1.5, "y": 1.5, "z_eye": 0.4}


def cmd_refine(a):
    """Coordinate search on the pose, scoring low-res renders. Use as a helper after a manual
    estimate: it can trade pose errors for model errors, so check the overlay afterwards."""
    data = json.loads(CAMS.read_text())
    cam = dict(data["cams"][a.name])
    params = a.params.split(",")
    steps = {p: STEPS[p] * a.scale for p in params}
    photo = load_photo(cam)
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = Path(tempfile.mkdtemp(prefix="_refine_%s_" % a.name, dir=OUT))
    best_sc = None

    def run(variants):
        vf = tmp / "variants.json"
        vf.write_text(json.dumps(variants))
        cmd = [a.blender, "-b", a.blend, "--python-exit-code", "1", "-P", str(ROOT / "blender/render_eval.py"),
               "--", "--variants", str(vf), "--long", str(a.long), "--fast", "--cams", str(CAMS)]
        r = subprocess.run(cmd, capture_output=True, text=True, env=blender_env())
        if r.returncode:
            sys.exit(r.stdout[-2000:] + r.stderr[-2000:])
        out = []
        for v in variants:
            mp = Path(v["out"])
            kp = Path(str(mp.with_suffix("")) + "_mask.png")
            sc, _ = score(photo, Image.open(mp).convert("RGB"), Image.open(kp))
            out.append(sc)
        return out

    def objective(sc):
        if sc["sky"] is None:
            return sc["edges"]
        return 0.45 * sc["sky"] + 0.35 * sc["edges"] + 0.2 * max(0.0, 1 - sc["skyline"] / 10)

    for it in range(a.iters):
        variants = [{"cam": a.name, "out": str(tmp / "v0.png"), "set": {p: cam[p] for p in params}}]
        for p in params:
            for sgn in (-2, -1, 1, 2):
                s = {q: cam[q] for q in params}
                s[p] = round(cam[p] + sgn * steps[p], 3)
                variants.append({"cam": a.name, "out": str(tmp / ("v%d.png" % len(variants))), "set": s})
        scs = run(variants)
        objs = [objective(s) for s in scs]
        k = int(np.argmax(objs))
        best_sc = scs[k]
        print("iter %d  %s  obj %.3f  %s" % (it, {p: variants[k]["set"][p] for p in params}, objs[k], score_text(scs[k])),
              flush=True)
        if k == 0:
            steps = {p: s / 2 for p, s in steps.items()}
            if all(steps[p] < STEPS[p] * 0.12 for p in params):
                break
        else:
            cam.update(variants[k]["set"])
    shutil.rmtree(tmp, ignore_errors=True)
    print("refined:", {p: cam[p] for p in params}, score_text(best_sc or {}))
    if a.write:
        data = json.loads(CAMS.read_text())          # re-read: other edits may have happened meanwhile
        data["cams"][a.name].update({p: cam[p] for p in params})
        CAMS.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n")
        print("written to", CAMS.relative_to(ROOT), "(run pipeline/eval_set.py sync to copy it to the game)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd")
    s = sub.add_parser("compare")
    s.add_argument("--only")
    s.set_defaults(f=cmd_compare)
    s = sub.add_parser("overlay")
    s.add_argument("name")
    s.add_argument("--suffix", default="")
    s.add_argument("--height", type=int, default=420)
    s.add_argument("--out")
    s.set_defaults(f=cmd_overlay)
    s = sub.add_parser("plan")
    s.add_argument("--scale", type=float, default=6.0, help="pixels per metre")
    s.set_defaults(f=cmd_plan)
    s = sub.add_parser("refine")
    s.add_argument("name")
    s.add_argument("--params", default="heading,pitch,fov")
    s.add_argument("--iters", type=int, default=8)
    s.add_argument("--scale", type=float, default=1.0, help="multiply the initial step sizes")
    s.add_argument("--long", type=int, default=480)
    s.add_argument("--blend", default=str(ROOT / "build/city.blend"))
    s.add_argument("--blender", default="blender")
    s.add_argument("--write", action="store_true")
    s.set_defaults(f=cmd_refine)
    a = ap.parse_args()
    if not a.cmd:
        a = ap.parse_args(["compare"] + sys.argv[1:])
    a.f(a)


if __name__ == "__main__":
    main()

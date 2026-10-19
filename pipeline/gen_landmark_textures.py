"""Textures for the hand-modelled Haram landmarks (blender/landmarks_haram.py).

    .venv/bin/python pipeline/gen_landmark_textures.py   -> data/textures/gen/landmarks/*.jpg|png + manifest.json

  gold      gilded plates of the Dome of the Rock (tile 4.4 m: 4 x 4 plates of 1.1 m), + normals
  leaddome  grey lead sheeting with standing seams (Al-Aqsa, Dome of the Chain, minaret caps), + normals
  herodian  Herodian ashlar of the Western Wall: courses of ~1.14 m (7 per 8 m tile), blocks 1.2-5 m
            long with sunken drafted margins and flat bosses, honey limestone weathered grey, + normals
  faience   atlas of the Dome of the Rock's tiled and marble-clad walls (window bays, blind bays,
            the Ya-Sin inscription frieze, marble dado, drum bays and band, tile fields, column marble,
            the brass-plated doors, porch hood, a generic arched window with grille), + normals.
            Cells are pixel rectangles (not a grid): manifest "cells" holds UV rects (u0, v0, u1, v1)
            with v up, inset by 4 px against mip bleeding.

Sources for colours and layout: data/photos_ref/landmarks_haram/ (H:03-H:07 facades and dome,
H:12 the lead dome of Al-Aqsa, H:27-H:31 the Western Wall). Normal maps: OpenGL convention.
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/textures/gen/landmarks"
REL = "data/textures/gen/landmarks/"
rng = np.random.default_rng(691)            # the Dome of the Rock was completed in 691-692
FONT = Path("/usr/share/fonts/noto/NotoNaskhArabic-Bold.ttf")


# ---------------------------------------------------------------- helpers
def vnoise(h, w, cy, cx, wrap=True):
    g = rng.random((cy, cx)).astype(np.float32)
    big = np.tile(g, (3, 3)) if wrap else g
    im = Image.fromarray((big * 255).astype(np.uint8)).resize(((w * 3) if wrap else w, (h * 3) if wrap else h),
                                                              Image.BICUBIC)
    a = np.asarray(im, np.float32) / 255
    return a[h:2 * h, w:2 * w] if wrap else a


def fbm(h, w, base=4, octaves=5, gain=0.5, wrap=True):
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    for o in range(octaves):
        c = base * 2 ** o
        out += amp * vnoise(h, w, max(1, int(c * h / max(h, w))), max(1, int(c * w / max(h, w))), wrap)
        tot += amp
        amp *= gain
    return out / tot


def normal_map(height_m, px_per_m, wrap=True):
    if wrap:
        dx = (np.roll(height_m, -1, 1) - np.roll(height_m, 1, 1)) * px_per_m / 2
        dr = (np.roll(height_m, -1, 0) - np.roll(height_m, 1, 0)) * px_per_m / 2
    else:
        dx = np.gradient(height_m, axis=1) * px_per_m
        dr = np.gradient(height_m, axis=0) * px_per_m
    n = np.stack([-dx, dr, np.ones_like(dx)], -1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    return Image.fromarray(((n * 0.5 + 0.5) * 255).astype(np.uint8))


def to_img(rgb):
    return Image.fromarray((np.clip(rgb, 0, 1) * 255).astype(np.uint8))


def srgb(c):
    return np.array(c, np.float32) / 255.0


# ---------------------------------------------------------------- gold plates (tile 4.4 m, 1024 px)
def gold(N=1024, plates=4):
    """Gilded plates in courses; the dome is UV-mapped so u follows the parallels, v the meridians."""
    p = N // plates
    yy, xx = np.mgrid[0:N, 0:N]
    row = yy // p
    off = (row % 2) * (p // 2)                                 # staggered vertical seams
    col = ((xx + off) // p) % plates
    fx = ((xx + off) % p) / p
    fy = (yy % p) / p
    seam = np.minimum(np.minimum(fx, 1 - fx), np.minimum(fy, 1 - fy)) * p      # px to the plate edge
    pid = row * plates + col
    var = rng.uniform(0.9, 1.08, plates * plates + plates)[pid % (plates * plates + plates)]
    n = fbm(N, N, 6, 4)
    base = srgb((226, 170, 62))
    rgb = base[None, None, :] * (var * (0.94 + 0.12 * n))[..., None]
    # slight sheen gradient inside a plate (plates are a little domed) and dark seams
    bulge = (1 - (2 * fx - 1) ** 2) * (1 - (2 * fy - 1) ** 2)
    rgb *= (0.96 + 0.08 * bulge)[..., None]
    rgb *= (0.55 + 0.45 * np.clip(seam / 3.0, 0, 1))[..., None]
    h = 0.004 * bulge - 0.003 * (seam < 2.5)
    return to_img(rgb), normal_map(h.astype(np.float32), N / 4.4)


# ---------------------------------------------------------------- lead sheeting (tile 2.0 m, 1024 px)
def leaddome(N=1024, tile=2.0):
    px = N / tile
    yy, xx = np.mgrid[0:N, 0:N]
    seam_every = 0.5                                           # standing seams every 0.5 m (along v)
    sx = (xx / px) % seam_every
    dseam = np.minimum(sx, seam_every - sx) * px
    course = 1.0                                               # cross joints every 1 m, staggered
    cy = (yy / px + 0.5 * ((xx / px // seam_every) % 2)) % course
    dcross = np.minimum(cy, course - cy) * px
    n1 = fbm(N, N, 5, 5)
    n2 = fbm(N, N, 24, 3)
    g = 0.5 + 0.08 * (n1 - 0.5) + 0.04 * (n2 - 0.5)
    sheet = ((xx / px) // seam_every).astype(int) * 7 + ((yy / px) // course).astype(int)
    g = g * (0.95 + 0.07 * ((sheet * 2654435761) % 1000 / 1000.0))
    rgb = np.stack([g * 0.98, g * 1.0, g * 1.04], -1)
    rgb[dseam < 2.0] *= 1.18                                   # seams catch the light
    rgb[(dcross < 1.0)] *= 0.85
    # pale streaks from oxidation (white lead carbonate), vertical
    streak = np.asarray(Image.fromarray((fbm(N, N, 3, 4) * np.clip((vnoise(N, N, 4, 64) - 0.6) * 3, 0, 1) * 255)
                                        .astype(np.uint8)).filter(ImageFilter.GaussianBlur(6)), np.float32) / 255
    rgb = rgb + 0.06 * streak[..., None]
    h = 0.012 * np.clip(1 - dseam / 3.0, 0, 1) - 0.002 * (dcross < 1.0) + 0.001 * n2
    return to_img(rgb), normal_map(h.astype(np.float32), px)


# ---------------------------------------------------------------- Herodian ashlar (tile 8 m, 2048 px)
def herodian(N=2048, tile=8.0, courses=7):
    px = N / tile
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    ch = tile / courses
    rgb = np.zeros((N, N, 3), np.float32)
    h = np.zeros((N, N), np.float32)
    n_big = fbm(N, N, 8, 6)
    n_fine = fbm(N, N, 64, 3)
    pits = fbm(N, N, 40, 3)
    rr = np.random.default_rng(37)
    honey = [srgb(c) for c in ((212, 190, 150), (200, 182, 146), (220, 204, 168), (190, 176, 150), (208, 196, 170),
                               (182, 168, 140))]
    for k in range(courses):
        y0, y1 = k * ch, (k + 1) * ch
        r0, r1 = int(round(y0 * px)), int(round(y1 * px))
        # block joints along the course (wrapping)
        cuts, x = [], rr.uniform(0, tile)
        start = x
        while x < start + tile - 1.0:
            cuts.append(x % tile)
            x += rr.choice([1.3, 1.8, 2.4, 3.0, 3.6, 4.6]) * rr.uniform(0.85, 1.15)
        cuts = np.sort(np.array(cuts))
        xs = (np.arange(N) + 0.5) / px
        bid = np.searchsorted(cuts, xs, side="right") % len(cuts)
        # distance to the nearest vertical joint (wrapping)
        d = np.abs(((xs[:, None] - cuts[None, :]) + tile / 2) % tile - tile / 2)
        dx = d.min(axis=1)
        rows = np.arange(r0, r1)
        dy = np.minimum((rows + 0.5) / px - y0, y1 - (rows + 0.5) / px)
        dist = np.minimum(dx[None, :], dy[:, None])                         # metres to the block edge
        margin = 0.075 + 0.02 * np.sin(bid * 1.7)[None, :]                  # drafted margin width
        cols = np.stack([honey[(b * 7 + k * 3) % len(honey)] for b in bid])  # (N, 3)
        tone = rr.uniform(0.8, 1.1, len(cuts))[bid]
        eroded = rr.random(len(cuts))[bid] < 0.25
        sub = slice(r0, r1)
        c = cols[None, :, :] * tone[None, :, None]
        boss = dist > margin
        # boss: slightly darker, rougher; margin: smoother, paler; joints dark
        nb = n_big[sub] - 0.5
        nf = n_fine[sub] - 0.5
        lum = 1.0 + 0.22 * nb + np.where(boss, 0.16 * nf, 0.05 * nf)
        lum = np.where(boss, lum * 0.96, lum * 1.03)
        lum = np.where((dist > margin - 0.012) & (dist < margin + 0.006), lum * 0.9, lum)  # faint boss edge
        er = eroded[None, :] & (pits[sub] > 0.55) & boss
        lum = np.where(er, lum * (0.78 + 0.2 * pits[sub]), lum)
        joint = dist < 0.02
        lum = np.where(joint, 0.42, lum)
        rgb[sub] = c * lum[..., None]
        hh = np.where(boss, 0.025 + 0.01 * nf, 0.0) - np.where(joint, 0.03, 0.0) - np.where(er, 0.015 * pits[sub], 0.0)
        hh = hh + 0.012 * np.clip(dist / 0.03, 0, 1) * (~boss)                # margin rises from the joint
        h[sub] = hh
    # grey weathering: darker streaks running down, greyer towards the top of the tile repeat
    streaks = vnoise(N, N, 3, 90) * fbm(N, N, 4, 3)
    grey = np.clip((streaks - 0.3) * 1.8, 0, 1)[..., None]
    rgb = rgb * (1 - 0.5 * grey) + 0.5 * grey * rgb.mean(-1, keepdims=True) * 0.8
    blotch = fbm(N, N, 14, 4)[..., None]
    rgb = rgb * (0.8 + 0.4 * blotch)
    rust = np.clip((fbm(N, N, 6, 4) - 0.55) * 3, 0, 1)[..., None]          # warm iron-oxide patches
    rgb = rgb * (1 - 0.25 * rust) + 0.25 * rust * srgb((176, 128, 80))
    return to_img(rgb), normal_map(h, px)


# ---------------------------------------------------------------- faience atlas (2048 px, drawn at 2x)
S = 2                                                      # supersampling
W = 2048
CELLS = {                                                  # name: (x, y, w, h) px in the final atlas, y down
    "parapet": (0, 0, 2048, 280),          # one octagon face: 20.3 m x 2.8 m (band of rectangles + Ya-Sin frieze)
    "drum_band": (0, 280, 2048, 222),      # a quarter of the drum: 18.4 m x 2.0 m inscription band
    "bay_window": (0, 502, 352, 528),      # 2.9 m x 4.4 m: arched window in a tiled field
    "bay_blind": (352, 502, 352, 528),     # 2.9 m x 4.4 m: blind arch (tile panel), end bays
    "marble_bay": (704, 502, 352, 588),    # 2.9 m x 4.9 m: marble dado with framed panels
    "drum_window": (1056, 502, 460, 650),  # 4.6 m x 6.5 m: drum bay with arched window
    "tile_field": (1516, 502, 512, 512),   # 1.5 m square repeat: blue-white star tiles
    "door_bronze": (0, 1152, 340, 512),    # brass-plated double door, 3.0 x 4.5 m
    "column": (340, 1152, 256, 512),       # veined grey-pink marble (column shafts)
    "hood": (596, 1152, 512, 512),         # porch hood / arch soffit: deep blue with white florals
    "window_grille": (1108, 1152, 256, 384),  # stone-framed pointed window with grille (generic)
    "tile_green": (1364, 1152, 256, 256),  # turquoise-green tile field
    "chain_drum": (1620, 1152, 420, 280),  # Dome of the Chain hexagonal drum face: arch + tiles
    "lattice": (1364, 1408, 256, 256),     # dark wooden mashrabiya lattice (minaret / porch grilles)
}

BLUE = (28, 62, 140)
DEEP = (16, 36, 96)
TURQ = (40, 150, 160)
GREEN = (38, 128, 92)
WHITE = (232, 236, 238)
YELLOW = (226, 186, 70)
BLACK = (18, 20, 28)


def jitter(im, amount=0.06, scale=8):
    a = np.asarray(im, np.float32) / 255
    h, w = a.shape[:2]
    n = fbm(h, w, scale, 3, wrap=False)
    a = a * (1 + amount * (n[..., None] - 0.5) * 2)
    return to_img(a)


def tile_pattern(w, h, cell_px, palette, star=True, seed=0, grout=(205, 205, 200)):
    """Square tiles with a star/cross motif (Iznik-like), drawn at scale."""
    im = Image.new("RGB", (w, h), palette[0])
    d = ImageDraw.Draw(im)
    rr = np.random.default_rng(seed)
    for j in range(0, h + cell_px, cell_px):
        for i in range(0, w + cell_px, cell_px):
            cx, cy = i + cell_px / 2, j + cell_px / 2
            r = cell_px * 0.42
            if star:
                pts = []
                for k in range(16):
                    a = math.pi * k / 8
                    rad = r if k % 2 == 0 else r * 0.55
                    pts.append((cx + rad * math.cos(a), cy + rad * math.sin(a)))
                d.polygon(pts, fill=palette[1])
                d.ellipse([cx - r * 0.3, cy - r * 0.3, cx + r * 0.3, cy + r * 0.3], fill=palette[2])
            else:
                d.rectangle([i + 2 * S, j + 2 * S, i + cell_px - 2 * S, j + cell_px - 2 * S], fill=palette[1])
                d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], fill=palette[2])
            # corner quarter-flowers
            for (ox, oy) in ((i, j), (i + cell_px, j), (i, j + cell_px), (i + cell_px, j + cell_px)):
                q = cell_px * 0.16
                d.ellipse([ox - q, oy - q, ox + q, oy + q], fill=palette[3 % len(palette)])
            d.line([(i, j), (i + cell_px, j)], fill=grout, width=S)
            d.line([(i, j), (i, j + cell_px)], fill=grout, width=S)
    return im


def arch_poly(x0, x1, y_bottom, y_spring, pointed=0.12, seg=24):
    """Arch outline in image coordinates (y down): rectangle up to y_spring, then a slightly pointed arch."""
    w = x1 - x0
    cx = (x0 + x1) / 2
    pts = [(x0, y_bottom), (x0, y_spring)]
    for k in range(1, seg):
        t = k / seg
        a = math.pi * t
        x = cx - math.cos(a) * w / 2
        y = y_spring - math.sin(a) * w / 2 - pointed * w / 2 * (1 - abs(1 - 2 * t)) ** 3   # slight peak
        pts.append((x, y))
    pts += [(x1, y_spring), (x1, y_bottom)]
    return pts


def grille(d, box, col=BLACK, bar=(70, 110, 170), step=14):
    x0, y0, x1, y1 = box
    for x in np.arange(x0, x1, step * S):
        d.line([(x, y0), (x, y1)], fill=bar, width=2 * S)
    for y in np.arange(y0, y1, step * S):
        d.line([(x0, y), (x1, y)], fill=bar, width=2 * S)
    for x in np.arange(x0, x1, step * S):
        for y in np.arange(y0, y1, step * S):
            d.ellipse([x + 3 * S, y + 3 * S, x + (step - 3) * S, y + (step - 3) * S], outline=(120, 170, 220), width=S)


def bay(window=True):
    """2.9 x 4.4 m upper-wall bay (photos H:04-H:06): vertical blue-white borders, turquoise/green
    tiled field, an arched window framed by a deep blue band with white zig-zag, yellow inner rim."""
    w, h = 352 * S, 528 * S
    pxm = w / 2.9
    im = tile_pattern(w, h, int(0.22 * pxm), [GREEN, (34, 132, 120), YELLOW, (200, 220, 210)], star=False, seed=3,
                      grout=(30, 90, 80))
    d = ImageDraw.Draw(im)
    # side borders (between bays): blue with white diamonds
    bw = int(0.18 * pxm)
    for x in (0, w - bw):
        d.rectangle([x, 0, x + bw, h], fill=BLUE)
        for y in range(0, h, bw):
            q = bw * 0.3
            d.polygon([(x + bw / 2, y + q), (x + bw - q, y + bw / 2), (x + bw / 2, y + bw - q), (x + q, y + bw / 2)], fill=WHITE)
    # top border
    d.rectangle([0, 0, w, int(0.16 * pxm)], fill=DEEP)
    for x in range(0, w, int(0.16 * pxm)):
        d.ellipse([x + 4 * S, 4 * S, x + int(0.16 * pxm) - 4 * S, int(0.16 * pxm) - 4 * S], fill=WHITE)
    # bottom border
    d.rectangle([0, h - int(0.14 * pxm), w, h], fill=DEEP)
    # arch
    x0, x1 = 0.55 * pxm, 2.35 * pxm
    yb, ys = h - 0.35 * pxm, h - 3.0 * pxm
    outer = arch_poly(x0 - 0.16 * pxm, x1 + 0.16 * pxm, yb + 0.12 * pxm, ys, 0.15)
    d.polygon(outer, fill=DEEP)
    rim = arch_poly(x0 - 0.05 * pxm, x1 + 0.05 * pxm, yb + 0.04 * pxm, ys, 0.15)
    d.polygon(rim, fill=YELLOW)
    inner = arch_poly(x0, x1, yb, ys, 0.15)
    if window:
        d.polygon(inner, fill=(26, 44, 96))
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).polygon(inner, fill=255)
        gr = Image.new("RGB", (w, h), (26, 44, 96))
        grille(ImageDraw.Draw(gr), (0, 0, w, h), bar=(200, 180, 120), step=18)
        im.paste(gr, (0, 0), mask)
    else:
        mask = Image.new("L", (w, h), 0)
        ImageDraw.Draw(mask).polygon(inner, fill=255)
        tp = tile_pattern(w, h, int(0.3 * pxm), [BLUE, WHITE, TURQ, YELLOW], star=True, seed=5)
        im.paste(tp, (0, 0), mask)
    # zig-zag on the outer band
    for k in range(0, len(outer) - 1, 2):
        d.line([outer[k], rim[min(k + 1, len(rim) - 1)]], fill=WHITE, width=S * 2)
    return jitter(im, 0.05, 12)


def parapet():
    """Top zone of an octagon face (20.3 m x 2.8 m): a band of small white rectangles on blue,
    then the deep-blue frieze with the Ya-Sin inscription in white, a thin white top rim."""
    w, h = 2048 * S, 280 * S
    pxm = h / 2.8
    im = Image.new("RGB", (w, h), DEEP)
    d = ImageDraw.Draw(im)
    band_h = int(0.62 * pxm)
    d.rectangle([0, h - band_h, w, h], fill=BLUE)
    step = int(0.42 * pxm)
    for x in range(0, w, step):
        d.rectangle([x + 4 * S, h - band_h + 10 * S, x + step - 4 * S, h - 10 * S], fill=WHITE)
        d.rectangle([x + 10 * S, h - band_h + 18 * S, x + step - 10 * S, h - 18 * S], fill=(110, 150, 210))
    d.rectangle([0, 0, w, int(0.12 * pxm)], fill=WHITE)
    d.rectangle([0, h - band_h - int(0.08 * pxm), w, h - band_h], fill=TURQ)
    text = ("بسم الله الرحمن الرحيم  يس  والقرآن الحكيم  إنك لمن المرسلين  على صراط مستقيم  "
            "تنزيل العزيز الرحيم  لتنذر قوما ما أنذر آباؤهم فهم غافلون  لقد حق القول على أكثرهم فهم لا يؤمنون")
    try:
        f = ImageFont.truetype(str(FONT), int(0.95 * pxm), layout_engine=ImageFont.Layout.RAQM)
        tw = d.textlength(text, font=f, direction="rtl", language="ar")
        scale = (w * 0.985) / tw
        f = ImageFont.truetype(str(FONT), int(0.95 * pxm * min(1.0, scale)), layout_engine=ImageFont.Layout.RAQM)
        d.text((w / 2, int(0.12 * pxm) + (h - band_h - int(0.2 * pxm)) / 2), text, font=f, fill=WHITE, anchor="mm",
               direction="rtl", language="ar")
    except Exception:                                      # noqa: BLE001  (no raqm: pseudo-script strokes)
        for x in range(0, w, 18 * S):
            hh = (0.4 + 0.5 * rng.random()) * pxm
            d.line([(x, h - band_h - 0.3 * pxm), (x, h - band_h - 0.3 * pxm - hh)], fill=WHITE, width=5 * S)
    return jitter(im, 0.04, 20)


def drum_band():
    w, h = 2048 * S, 222 * S
    pxm = h / 2.0
    im = Image.new("RGB", (w, h), DEEP)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, int(0.14 * pxm)], fill=WHITE)
    d.rectangle([0, h - int(0.14 * pxm), w, h], fill=TURQ)
    text = ("الله لا إله إلا هو الحي القيوم لا تأخذه سنة ولا نوم له ما في السماوات وما في الأرض "
            "من ذا الذي يشفع عنده إلا بإذنه يعلم ما بين أيديهم وما خلفهم ولا يحيطون بشيء من علمه إلا بما شاء")
    try:
        f = ImageFont.truetype(str(FONT), int(0.75 * pxm), layout_engine=ImageFont.Layout.RAQM)
        tw = d.textlength(text, font=f, direction="rtl", language="ar")
        f = ImageFont.truetype(str(FONT), int(0.75 * pxm * min(1.0, w * 0.985 / tw)), layout_engine=ImageFont.Layout.RAQM)
        d.text((w / 2, h / 2), text, font=f, fill=WHITE, anchor="mm", direction="rtl", language="ar")
    except Exception:                                      # noqa: BLE001
        pass
    return jitter(im, 0.04, 20)


def marble_panel_fill(w, h, base=(226, 224, 218), vein=(150, 150, 155), seed=0):
    a = np.ones((h, w, 3), np.float32) * srgb(base)
    n = fbm(h, w, 6, 6, wrap=False)
    v = np.abs(np.sin((n * 9 + np.linspace(0, 3, w)[None, :]) * math.pi))
    veins = np.clip(1 - v * 12, 0, 1) * 0.5 + np.clip(1 - v * 40, 0, 1) * 0.5
    a = a * (1 - 0.35 * veins[..., None]) + srgb(vein) * 0.35 * veins[..., None]
    a *= (0.95 + 0.08 * fbm(h, w, 20, 3, wrap=False))[..., None]
    return to_img(a)


def marble_bay():
    """Lower 4.9 m of a bay (photo H:06): white marble revetment in framed panels, a darker plinth,
    inlaid roundels and a lattice panel."""
    w, h = 352 * S, 588 * S
    pxm = w / 2.9
    im = marble_panel_fill(w, h, (222, 220, 214), (140, 140, 146))
    d = ImageDraw.Draw(im)
    # frame lines
    fr = (120, 112, 104)
    d.rectangle([0, h - int(0.35 * pxm), w, h], fill=(176, 170, 160))
    m = int(0.18 * pxm)
    boxes = [(m, int(0.25 * pxm), w - m, int(2.3 * pxm)), (m, int(2.5 * pxm), w - m, h - int(0.55 * pxm))]
    for b in boxes:
        d.rectangle(b, outline=fr, width=4 * S)
        d.rectangle([b[0] + 10 * S, b[1] + 10 * S, b[2] - 10 * S, b[3] - 10 * S], outline=(190, 150, 120), width=2 * S)
    # roundel in the upper panel, pink/grey marble inlay
    cx, cy, r = w / 2, (boxes[0][1] + boxes[0][3]) / 2, 0.36 * pxm
    inlay = marble_panel_fill(int(2 * r), int(2 * r), (178, 172, 168), (110, 104, 104), 2)
    for b in boxes:                                        # slender vertical sub-panels (H:05)
        for fx in (0.3, 0.7):
            x = b[0] + (b[2] - b[0]) * fx
            d.line([(x, b[1] + 14 * S), (x, b[3] - 14 * S)], fill=(160, 150, 140), width=2 * S)
    mask = Image.new("L", inlay.size, 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
    im.paste(inlay, (int(cx - r), int(cy - r)), mask)
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fr, width=3 * S)
    d.ellipse([cx - r * 0.45, cy - r * 0.45, cx + r * 0.45, cy + r * 0.45], outline=(70, 90, 130), width=3 * S)
    # lower panel: grey rectangle with a lozenge
    b = boxes[1]
    d.polygon([((b[0] + b[2]) / 2, b[1] + 25 * S), (b[2] - 25 * S, (b[1] + b[3]) / 2), ((b[0] + b[2]) / 2, b[3] - 25 * S),
               (b[0] + 25 * S, (b[1] + b[3]) / 2)], outline=fr, width=3 * S)
    return jitter(im, 0.03, 10)


def drum_window():
    """Drum bay (H:04/H:05): an arched window with a blue-white grille in a frame of turquoise and
    white tiles, flanked by vertical panels of dark blue tiles."""
    w, h = 460 * S, 650 * S
    pxm = w / 4.6
    im = tile_pattern(w, h, int(0.3 * pxm), [BLUE, WHITE, TURQ, YELLOW], star=True, seed=11)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, int(0.25 * pxm), h], fill=DEEP)
    d.rectangle([w - int(0.25 * pxm), 0, w, h], fill=DEEP)
    x0, x1 = 1.3 * pxm, 3.3 * pxm
    yb, ys = h - 1.2 * pxm, h - 4.4 * pxm
    d.polygon(arch_poly(x0 - 0.3 * pxm, x1 + 0.3 * pxm, yb + 0.3 * pxm, ys, 0.1), fill=TURQ)
    d.polygon(arch_poly(x0 - 0.12 * pxm, x1 + 0.12 * pxm, yb + 0.1 * pxm, ys, 0.1), fill=WHITE)
    inner = arch_poly(x0, x1, yb, ys, 0.1)
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(inner, fill=255)
    gr = Image.new("RGB", (w, h), (24, 34, 60))
    grille(ImageDraw.Draw(gr), (0, 0, w, h), step=18)
    im.paste(gr, (0, 0), mask)
    # squared panels below the window
    for k in range(3):
        xx = int((0.6 + 1.2 * k) * pxm)
        d.rectangle([xx, h - 0.95 * pxm, xx + 0.9 * pxm, h - 0.25 * pxm], fill=GREEN, outline=WHITE, width=3 * S)
    return jitter(im, 0.05, 12)


def door_bronze():
    w, h = 340 * S, 512 * S
    im = Image.new("RGB", (w, h), (120, 88, 40))
    d = ImageDraw.Draw(im)
    for leaf in (0, 1):
        x0 = leaf * w / 2 + 6 * S
        x1 = (leaf + 1) * w / 2 - 6 * S
        d.rectangle([x0, 6 * S, x1, h - 6 * S], fill=(150, 112, 52), outline=(70, 50, 24), width=4 * S)
        rows = 6
        for r in range(rows):
            y0 = 14 * S + r * (h - 28 * S) / rows
            y1 = y0 + (h - 28 * S) / rows - 8 * S
            d.rectangle([x0 + 10 * S, y0, x1 - 10 * S, y1], outline=(200, 160, 80), width=3 * S)
            cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
            d.ellipse([cx - 14 * S, cy - 14 * S, cx + 14 * S, cy + 14 * S], fill=(205, 168, 90))
    return jitter(im, 0.08, 10)


def hood():
    w = h = 512 * S
    im = tile_pattern(w, h, 64 * S, [DEEP, BLUE, WHITE, TURQ], star=True, seed=21)
    return jitter(im, 0.05, 8)


def window_grille():
    """Generic stone window: pale frame, pointed arch, dark glass behind an iron grille."""
    w, h = 256 * S, 384 * S
    im = Image.new("RGB", (w, h), (196, 184, 160))
    d = ImageDraw.Draw(im)
    inner = arch_poly(0.12 * w, 0.88 * w, 0.95 * h, 0.42 * h, 0.2)
    d.polygon(arch_poly(0.04 * w, 0.96 * w, h, 0.42 * h, 0.2), fill=(214, 204, 182))
    d.polygon(inner, fill=(26, 30, 36))
    mask = Image.new("L", (w, h), 0)
    ImageDraw.Draw(mask).polygon(inner, fill=255)
    gr = Image.new("RGB", (w, h), (26, 30, 36))
    gd = ImageDraw.Draw(gr)
    for x in range(0, w, 20 * S):
        gd.line([(x, 0), (x, h)], fill=(60, 60, 58), width=3 * S)
    for y in range(0, h, 30 * S):
        gd.line([(0, y), (w, y)], fill=(60, 60, 58), width=3 * S)
    im.paste(gr, (0, 0), mask)
    return jitter(im, 0.05, 6)


def lattice():
    w = h = 256 * S
    im = Image.new("RGB", (w, h), (20, 16, 12))
    d = ImageDraw.Draw(im)
    for k in range(-h, w + h, 22 * S):
        d.line([(k, 0), (k + h, h)], fill=(96, 68, 40), width=5 * S)
        d.line([(k, h), (k + h, 0)], fill=(96, 68, 40), width=5 * S)
    return jitter(im, 0.06, 6)


def chain_drum():
    """One face of the Dome of the Chain's hexagonal drum (H:13): arched panel, green/blue tiles."""
    w, h = 420 * S, 280 * S
    pxm = w / 3.2
    im = tile_pattern(w, h, int(0.25 * pxm), [TURQ, WHITE, BLUE, YELLOW], star=True, seed=31)
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, w, int(0.18 * pxm)], fill=DEEP)
    d.rectangle([0, h - int(0.12 * pxm), w, h], fill=DEEP)
    outer = arch_poly(0.25 * w, 0.75 * w, h - 0.12 * pxm, h * 0.55, 0.15)
    d.polygon(outer, fill=DEEP)
    d.polygon(arch_poly(0.3 * w, 0.7 * w, h - 0.12 * pxm, h * 0.58, 0.15), fill=(24, 32, 56))
    return jitter(im, 0.05, 10)


def faience():
    canvas = Image.new("RGB", (W * S, W * S), (40, 60, 120))
    height = Image.new("L", (W * S, W * S), 128)
    parts = {
        "parapet": parapet(), "drum_band": drum_band(), "bay_window": bay(True), "bay_blind": bay(False),
        "marble_bay": marble_bay(), "drum_window": drum_window(),
        "tile_field": tile_pattern(512 * S, 512 * S, 64 * S, [WHITE, BLUE, TURQ, DEEP], star=True, seed=41),
        "door_bronze": door_bronze(), "column": marble_panel_fill(256 * S, 512 * S, (200, 186, 182), (110, 96, 100), 4),
        "hood": hood(), "window_grille": window_grille(),
        "tile_green": tile_pattern(256 * S, 256 * S, 42 * S, [GREEN, TURQ, WHITE, YELLOW], star=False, seed=51),
        "chain_drum": chain_drum(), "lattice": lattice(),
    }
    cells = {}
    hd = ImageDraw.Draw(height)
    for name, (x, y, w, h) in CELLS.items():
        im = parts[name].resize((w * S, h * S))
        canvas.paste(im, (x * S, y * S))
        # grout grid on tiled cells for the normal map (tile pitch ~ 0.2 m)
        if name in ("bay_window", "bay_blind", "drum_window", "tile_field", "tile_green", "hood", "chain_drum"):
            step = 22 * S
            for gx in range(x * S, (x + w) * S, step):
                hd.line([(gx, y * S), (gx, (y + h) * S)], fill=100, width=S)
            for gy in range(y * S, (y + h) * S, step):
                hd.line([(x * S, gy), ((x + w) * S, gy)], fill=100, width=S)
        e = 4
        cells[name] = [round((x + e) / W, 5), round(1 - (y + h - e) / W, 5), round((x + w - e) / W, 5),
                       round(1 - (y + e) / W, 5)]
    diff = canvas.resize((W, W), Image.LANCZOS)
    hm = np.asarray(height.resize((W, W), Image.BILINEAR), np.float32) / 255 * 0.004
    return diff, normal_map(hm, W / 10.0, wrap=False), cells


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    man = {}
    d, n = gold()
    d.save(OUT / "gold_diff.jpg", quality=90)
    n.save(OUT / "gold_nor.png")
    man["gold"] = {"diff": REL + "gold_diff.jpg", "nor": REL + "gold_nor.png", "tile": 4.4,
                   "metallic": 0.75, "rough": 0.32}
    d, n = leaddome()
    d.save(OUT / "leaddome_diff.jpg", quality=90)
    n.save(OUT / "leaddome_nor.png")
    man["leaddome"] = {"diff": REL + "leaddome_diff.jpg", "nor": REL + "leaddome_nor.png", "tile": 2.0,
                       "metallic": 0.35, "rough": 0.55}
    d, n = herodian()
    d.save(OUT / "herodian_diff.jpg", quality=90)
    n.save(OUT / "herodian_nor.png")
    man["herodian"] = {"diff": REL + "herodian_diff.jpg", "nor": REL + "herodian_nor.png", "tile": 8.0,
                       "metallic": 0.0, "rough": 0.9}
    d, n, cells = faience()
    d.save(OUT / "faience_diff.jpg", quality=92)
    n.save(OUT / "faience_nor.png")
    man["faience"] = {"diff": REL + "faience_diff.jpg", "nor": REL + "faience_nor.png", "tile": 1.5,
                      "metallic": 0.0, "rough": 0.35, "cells": cells}
    (OUT / "manifest.json").write_text(json.dumps(man, indent=1))
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()

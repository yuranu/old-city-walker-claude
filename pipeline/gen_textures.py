"""Procedural textures that Poly Haven does not have: Jerusalem slab paving, road setts, closed
shop doors / shutters / windows (atlas + normals), iron grilles, railings, foliage cards
(RGBA cutouts) and decals (streaks, rust, posters, graffiti, manholes).

    python3 pipeline/gen_textures.py        -> data/textures/gen/*.png|jpg + manifest.json

Normal maps follow the OpenGL / glTF convention (+Y towards the top of the image).
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/textures/gen"
rng = np.random.default_rng(1538)          # the year Suleiman's masons finished the walls
FONT_DIR = Path("/usr/share/fonts/noto")


# ---------------------------------------------------------------- noise helpers
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


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def normal_map(height_m, px_per_m, wrap=True):
    """height in metres -> RGB normal map (OpenGL convention)."""
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


# ---------------------------------------------------------------- paving (4 x 4 m, 2048 px)
def courses(total, options, rr):
    out = []
    while sum(out) < total - 1e-6:
        out.append(float(rr.choice(options)))
    out[-1] -= sum(out) - total
    if out[-1] < min(options) * 0.6:
        extra = out.pop()
        out[-1] += extra
    return out


def slab_field(N, tile, rows_opt, len_rng, joint_m, rr):
    """Per-pixel slab id, distance to nearest joint (m) for a running-bond slab pattern."""
    px = N / tile
    sid = np.zeros((N, N), np.int32)
    dist = np.zeros((N, N), np.float32)
    y = 0.0
    nid = 0
    xs = (np.arange(N) + 0.5) / px
    for rh in courses(tile, rows_opt, rr):
        r0, r1 = int(round(y * px)), int(round((y + rh) * px))
        cuts = []
        x = rr.uniform(0, tile)
        start = x
        while x < start + tile - len_rng[0] * 0.8:
            cuts.append(x % tile)
            x += rr.uniform(*len_rng)
        cuts = np.sort(np.array(cuts))
        # slab index per column (wrapping)
        idx = np.searchsorted(cuts, xs, side="right") % len(cuts)
        dx = np.min(np.abs(((xs[:, None] - cuts[None, :]) + tile / 2) % tile - tile / 2), axis=1)
        rows = np.arange(r0, r1)
        dy = np.minimum((rows + 0.5) / px - y, y + rh - (rows + 0.5) / px)
        sid[r0:r1] = nid + idx[None, :]
        dist[r0:r1] = np.minimum(dx[None, :], dy[:, None])
        nid += len(cuts)
        y += rh
    return sid, dist, nid


def paving(N=2048, tile=4.0):
    rr = np.random.default_rng(7)
    px = N / tile
    sid, dist, n = slab_field(N, tile, [0.4, 0.45, 0.5, 0.55, 0.6], (0.55, 1.25), 0.004, rr)
    # Jerusalem limestone: cream, beige, warm grey, faintly pink; subtle per-slab variation
    palette = np.array([[0.82, 0.76, 0.64], [0.78, 0.72, 0.60], [0.75, 0.71, 0.62], [0.81, 0.74, 0.62],
                        [0.84, 0.79, 0.68]], np.float32)    # warm beige limestone flags (eval: not blue-grey)
    pick = rr.integers(0, len(palette), n)
    tone = rr.normal(1.0, 0.035, n).astype(np.float32)
    tilt = rr.normal(0, 0.0025, (n, 2)).astype(np.float32)
    detail = fbm(N, N, 24, 5)
    macro = fbm(N, N, 3, 3)
    speck = (vnoise(N, N, 1400, 1400) > 0.9).astype(np.float32) * vnoise(N, N, 600, 600) * 0.6
    rgb = palette[pick][sid] * tone[sid][..., None]
    rgb = rgb * (0.86 + 0.22 * detail[..., None]) * (0.92 + 0.12 * macro[..., None])
    rgb -= speck[..., None] * 0.18
    polish = smooth(0.55, 0.8, fbm(N, N, 5, 3))                       # foot-polished paths
    rgb = rgb * (1 + 0.06 * polish[..., None])
    gum = (vnoise(N, N, 220, 220) > 0.93) & (vnoise(N, N, 90, 90) > 0.5)
    rgb[gum] *= 0.74
    joint = 0.004
    jm = smooth(joint * 0.6, joint * 1.6, dist)
    ao = 0.78 + 0.22 * smooth(0.0, 0.03, dist)
    rgb = rgb * ao[..., None]
    jcol = np.array([0.33, 0.30, 0.26], np.float32) * (0.8 + 0.4 * detail[..., None])
    rgb = rgb * jm[..., None] + jcol * (1 - jm[..., None])
    yy, xx = np.mgrid[0:N, 0:N] / px
    h = 0.006 * smooth(0.0, 0.012, dist) + tilt[sid][..., 0] * (xx % 1) + tilt[sid][..., 1] * (yy % 1)
    h += (detail - 0.5) * 0.0012 - speck * 0.0006
    return to_img(rgb), normal_map(h.astype(np.float32), px)


def setts(N=1024, tile=2.0):
    rr = np.random.default_rng(11)
    px = N / tile
    sid, dist, n = slab_field(N, tile, [0.1, 0.11, 0.12, 0.13], (0.1, 0.2), 0.008, rr)
    # road pavers: same limestone family as the plaza, a touch greyer and smaller (photos: back_to_gate)
    palette = np.array([[0.64, 0.62, 0.58], [0.59, 0.58, 0.55], [0.68, 0.65, 0.59], [0.62, 0.60, 0.56]], np.float32)
    pick = rr.integers(0, len(palette), n)
    tone = rr.normal(1.0, 0.07, n).astype(np.float32)
    detail = fbm(N, N, 16, 5)
    rgb = palette[pick][sid] * tone[sid][..., None]
    rgb *= (0.82 + 0.3 * detail[..., None])
    jm = smooth(0.003, 0.008, dist)
    rgb = rgb * (0.7 + 0.3 * smooth(0, 0.025, dist))[..., None]
    jcol = np.array([0.30, 0.27, 0.22], np.float32)
    rgb = rgb * jm[..., None] + jcol * (1 - jm[..., None])
    h = 0.012 * np.sqrt(smooth(0.0, 0.05, dist)) + (detail - 0.5) * 0.002
    return to_img(rgb), normal_map(h.astype(np.float32), px)


def asphalt(N=1024, tile=3.0):
    """Worn grey asphalt of the roads round the walls (Street View: Ma'ale HaShalom, the Zion and Dung Gate
    roads): fine aggregate speckle, broad tonal patches, a few darker patch repairs and hairline cracks."""
    rr = np.random.default_rng(23)
    px = N / tile
    base = np.array([0.36, 0.35, 0.34], np.float32)
    broad = fbm(N, N, 3, 4)
    fine = fbm(N, N, 64, 3)
    speck = rr.random((N, N)).astype(np.float32)
    rgb = base * (0.93 + 0.1 * broad[..., None]) * (0.9 + 0.16 * fine[..., None])
    rgb = np.where((speck > 0.985)[..., None], rgb * 1.35, rgb)
    rgb = np.where((speck < 0.01)[..., None], rgb * 0.7, rgb)
    patch = fbm(N, N, 2, 3)
    rgb = rgb * (1.0 - 0.07 * smooth(0.6, 0.7, patch)[..., None])              # repaired patches, darker
    crack = smooth(0.0, 0.004, np.abs(fbm(N, N, 6, 4) - 0.5))
    rgb = rgb * (0.75 + 0.25 * crack[..., None])
    h = (fine - 0.5) * 0.002 + (speck > 0.985) * 0.0008 - (1 - crack) * 0.002
    return to_img(rgb), normal_map(h.astype(np.float32), px)


# ---------------------------------------------------------------- doors / shutters / windows atlas
CELL = 512


def chips(h, w, amount):
    n = fbm(h, w, 10, 5, wrap=False)
    return smooth(1 - amount - 0.03, 1 - amount + 0.03, n)


def steel_door(color, ribbed=True, graffiti=False, seed=0):
    rr = np.random.default_rng(seed)
    H = W = CELL
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rgb = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    hgt = np.zeros((H, W), np.float32)
    # two leaves, frame, horizontal rails
    seam = np.abs(xx - W / 2) < 2.5
    border = (xx < 10) | (xx > W - 11) | (yy > H - 10)
    rails = np.zeros((H, W), bool)
    for ry in (0.32, 0.62, 0.86):
        rails |= np.abs(yy - ry * H) < 6
    if ribbed:
        rib = 0.5 + 0.5 * np.sin(xx / W * 2 * math.pi * 22)
        hgt += rib * 0.004
        rgb *= (0.88 + 0.16 * rib)[..., None]
    else:                                                  # recessed panels
        for (y0, y1) in ((0.06, 0.29), (0.36, 0.59), (0.66, 0.83)):
            for (x0, x1) in ((0.07, 0.45), (0.55, 0.93)):
                inside = (xx > x0 * W) & (xx < x1 * W) & (yy > y0 * H) & (yy < y1 * H)
                edge = inside & ((np.abs(xx - x0 * W) < 6) | (np.abs(xx - x1 * W) < 6) |
                                 (np.abs(yy - y0 * H) < 6) | (np.abs(yy - y1 * H) < 6))
                hgt[inside] -= 0.004
                rgb[edge] *= 0.8
    hgt[rails | border] += 0.006
    rgb[rails | border] *= 1.06
    rgb[seam] *= 0.35
    hgt[seam] -= 0.004
    # padlock hasp at the centre
    hasp = (np.abs(xx - W / 2) < 16) & (np.abs(yy - 0.58 * H) < 10)
    rgb[hasp] = [0.15, 0.14, 0.12]
    lock = ((xx - W / 2) ** 2 / 64 + (yy - 0.62 * H) ** 2 / 144) < 1
    rgb[lock] = [0.55, 0.45, 0.2]
    # wear: chips to rust/grey primer, dirt towards the bottom, rust streaks
    c = chips(H, W, 0.18)
    rust = np.array([0.36, 0.2, 0.1]) * (0.7 + 0.6 * fbm(H, W, 30, 3, wrap=False))[..., None]
    rgb = rgb * (1 - c[..., None] * 0.9) + rust * c[..., None] * 0.9
    dirt = smooth(0.7, 1.0, yy / H) * (0.3 + 0.4 * fbm(H, W, 6, 3, wrap=False))
    rgb *= (1 - dirt[..., None] * 0.55)
    streak = smooth(0.6, 0.95, fbm(H, W, 3, 2, wrap=False)) * (fbm(H, W, 1, 1, wrap=False) * 0 + 1)
    rgb *= (1 - 0.15 * streak[..., None] * smooth(0.0, 0.3, yy / H)[..., None])
    rgb *= (0.92 + 0.12 * fbm(H, W, 40, 3, wrap=False))[..., None]
    img = to_img(rgb)
    if graffiti:
        d = ImageDraw.Draw(img)
        for _ in range(int(rr.integers(4, 8))):
            col = tuple(int(v) for v in rr.choice([[20, 20, 20], [180, 30, 30], [230, 230, 230], [40, 60, 160]]))
            x, y = rr.uniform(40, W - 40), rr.uniform(H * 0.35, H * 0.85)
            pts = [(x, y)]
            for _ in range(int(rr.integers(6, 14))):
                x += rr.normal(0, 18)
                y += rr.normal(0, 10)
                pts.append((x, y))
            d.line(pts, fill=col, width=int(rr.integers(4, 9)), joint="curve")
    return img, hgt


def souq_door(color, seed=0):
    """David Street closed shop: steel leaves of tall panels, two horizontal hasp bars (notes C3)."""
    rr = np.random.default_rng(seed)
    H = W = CELL
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rgb = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    hgt = np.zeros((H, W), np.float32)
    leaves = 3
    lw = W / leaves
    for k in range(leaves):
        x0 = k * lw
        seam = np.abs(xx - x0) < 2.5
        rgb[seam] *= 0.4
        for (py0, py1) in ((0.04, 0.33), (0.36, 0.64), (0.67, 0.96)):     # three tall panels per leaf
            ins = (xx > x0 + 0.14 * lw) & (xx < x0 + 0.86 * lw) & (yy > py0 * H) & (yy < py1 * H)
            hgt[ins] -= 0.003
            edge = ins & ((np.abs(xx - x0 - 0.14 * lw) < 4) | (np.abs(xx - x0 - 0.86 * lw) < 4) |
                          (np.abs(yy - py0 * H) < 4) | (np.abs(yy - py1 * H) < 4))
            rgb[edge] *= 0.78
    for hy in (0.33, 0.62):                                                # hasp bars at ~1.0 m and ~1.9 m
        bar = np.abs(yy - (1 - hy) * H) < 7
        rgb[bar] = np.array([0.12, 0.12, 0.11])
        hgt[bar] += 0.008
        for px in (0.33, 0.66):
            lock = ((xx - px * W) ** 2 / 70 + (yy - (1 - hy) * H - 14) ** 2 / 130) < 1
            rgb[lock] = [0.55, 0.45, 0.18]
    c = chips(H, W, 0.16)
    rust = np.array([0.38, 0.22, 0.1]) * (0.7 + 0.6 * fbm(H, W, 30, 3, wrap=False))[..., None]
    rgb = rgb * (1 - c[..., None] * 0.85) + rust * c[..., None] * 0.85
    rgb *= (1 - smooth(0.72, 1.0, yy / H)[..., None] * 0.5)                # dirt and rust at the foot
    rgb *= (0.92 + 0.12 * fbm(H, W, 40, 3, wrap=False))[..., None]
    return to_img(rgb), hgt


def grass(N=1024, tile=3.0):
    """Mown lawn (the Citadel moat floor, notes A1)."""
    rr = np.random.default_rng(21)
    px = N / tile
    base = fbm(N, N, 6, 5)
    blades = vnoise(N, N, 400, 400)
    rgb = np.stack([0.20 + 0.10 * base, 0.36 + 0.14 * base, 0.12 + 0.05 * base], -1)
    rgb *= (0.75 + 0.45 * blades[..., None])
    stripes = 0.94 + 0.06 * np.sin(np.arange(N)[None, :] / N * 2 * math.pi * 3)       # mowing stripes
    rgb *= stripes[..., None]
    dry = smooth(0.62, 0.8, fbm(N, N, 4, 3))
    rgb = rgb * (1 - dry[..., None] * 0.5) + np.array([0.42, 0.38, 0.22]) * dry[..., None] * 0.5
    h = (blades - 0.5) * 0.004 + (base - 0.5) * 0.01
    return to_img(rgb), normal_map(h.astype(np.float32), px)


def corrugated(N=512, tile=1.0):
    """Corrugated sheet for canopies and awnings: ribs, dust, rust streaks (citadel_east.md C4)."""
    px = N / tile
    yy, xx = np.mgrid[0:N, 0:N].astype(np.float32)
    rib = 0.5 + 0.5 * np.cos(xx / N * 2 * math.pi * 13)            # 13 ribs per metre (76 mm pitch)
    base = np.array([0.42, 0.44, 0.42], np.float32)
    rgb = base * (0.78 + 0.32 * rib)[..., None]
    dust = fbm(N, N, 6, 4)
    rgb = rgb * (0.85 + 0.25 * dust[..., None])
    streak = smooth(0.62, 0.9, np.asarray(Image.fromarray((fbm(N, N, 8, 3) * 255).astype(np.uint8)).resize((N // 16, N)).resize((N, N)), np.float32) / 255)
    rgb = rgb * (1 - streak[..., None] * 0.25) + np.array([0.36, 0.22, 0.12]) * streak[..., None] * 0.25
    h = rib * 0.012
    return to_img(rgb), normal_map(h.astype(np.float32), px)


def bark(N=512, tile=1.0):
    """Olive / pine bark: grey-brown, deep vertical fissures between flat plates (trunks were a flat colour)."""
    px = N / tile
    fiss = 0.6 * vnoise(N, N, 4, 48) + 0.3 * vnoise(N, N, 8, 96) + 0.1 * vnoise(N, N, 32, 160)   # long in y: fissures
    plates = smooth(0.35, 0.6, fiss)
    tone = fbm(N, N, 5, 4)
    base = np.array([0.36, 0.31, 0.26], np.float32)
    rgb = base * (0.45 + 0.6 * plates[..., None]) * (0.85 + 0.3 * tone[..., None])
    lichen = smooth(0.7, 0.85, fbm(N, N, 6, 3))
    rgb = rgb * (1 - lichen[..., None] * 0.35) + np.array([0.55, 0.56, 0.48]) * lichen[..., None] * 0.35
    h = plates * 0.012 + tone * 0.003
    return to_img(rgb), normal_map(h.astype(np.float32), px)


def lime(N=512, tile=2.0):
    """Lime plaster / pale limestone (roofs, bollards, benches, blank boards were a flat colour): soft mottling,
    fine grain, faint weathering streaks."""
    px = N / tile
    mott = fbm(N, N, 4, 5)
    grain = vnoise(N, N, 160, 160)
    streak = 0.6 * vnoise(N, N, 3, 40) + 0.4 * vnoise(N, N, 6, 80)        # long in y: rain streaks
    base = np.array([0.80, 0.77, 0.71], np.float32)          # the flat lime it replaces: (0.74, 0.71, 0.65)
    rgb = base * (0.9 + 0.14 * mott[..., None]) * (0.96 + 0.06 * grain[..., None])
    rgb = rgb * (1 - smooth(0.7, 0.95, streak)[..., None] * 0.05)
    h = mott * 0.003 + grain * 0.0015
    return to_img(rgb), normal_map(h.astype(np.float32), px)


def rolldown(color, seed=0):
    H = W = CELL
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    slat = (yy % 18) / 18
    rgb = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    prof = 0.5 + 0.5 * np.cos(slat * 2 * math.pi)
    rgb *= (0.78 + 0.3 * prof)[..., None]
    hgt = prof * 0.004
    bar = yy > H - 26
    rgb[bar] *= 0.75
    hgt[bar] += 0.006
    for x0 in (0.3, 0.7):
        lk = (np.abs(xx - x0 * W) < 9) & (np.abs(yy - (H - 13)) < 7)
        rgb[lk] = [0.2, 0.2, 0.2]
    c = chips(H, W, 0.1)
    rgb = rgb * (1 - c[..., None] * 0.5) + np.array([0.4, 0.25, 0.14]) * c[..., None] * 0.5
    rgb *= (1 - smooth(0.75, 1.0, yy / H) * 0.4)[..., None]
    rgb *= (0.9 + 0.15 * fbm(H, W, 30, 3, wrap=False))[..., None]
    return to_img(rgb), hgt.astype(np.float32)


def wood_door(seed=0):
    H = W = CELL
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    plank = (xx % 46) / 46
    grain = fbm(H, W, 3, 4, wrap=False)
    grain = np.asarray(Image.fromarray((grain * 255).astype(np.uint8)).resize((W // 8, H)).resize((W, H)),
                       np.float32) / 255
    base = np.array([0.30, 0.17, 0.08])
    rgb = base * (0.7 + 0.5 * grain[..., None])
    gap = (plank < 0.05)
    rgb[gap] *= 0.35
    hgt = np.where(gap, -0.004, 0.0).astype(np.float32)
    seam = np.abs(xx - W / 2) < 3
    rgb[seam] *= 0.3
    for ry in np.linspace(0.08, 0.92, 9):          # rows of iron studs
        for rx in np.linspace(0.08, 0.92, 8):
            st = ((xx - rx * W) ** 2 + (yy - ry * H) ** 2) < 30
            rgb[st] = [0.12, 0.11, 0.1]
            hgt[st] += 0.004
    for rx in (0.43, 0.57):
        ring = np.abs(np.sqrt((xx - rx * W) ** 2 + (yy - 0.52 * H) ** 2) - 16) < 2.5
        rgb[ring] = [0.15, 0.13, 0.1]
    rgb *= (1 - smooth(0.85, 1.0, yy / H) * 0.4)[..., None]
    return to_img(rgb), hgt


def louvres(color, seed=0):
    H = W = CELL
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    rgb = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    frame = (xx < 18) | (xx > W - 19) | (yy < 18) | (yy > H - 19) | (np.abs(xx - W / 2) < 9)
    lv = (yy % 22) / 22
    prof = np.clip(lv * 1.4, 0, 1)
    rgb *= (0.65 + 0.45 * prof)[..., None]
    hgt = (prof * 0.006).astype(np.float32)
    rgb[frame] = np.array(color) * 1.05
    hgt[frame] = 0.008
    c = chips(H, W, 0.15)
    rgb = rgb * (1 - c[..., None] * 0.7) + np.array([0.55, 0.5, 0.42]) * c[..., None] * 0.7
    rgb *= (0.9 + 0.15 * fbm(H, W, 30, 3, wrap=False))[..., None]
    return to_img(rgb), hgt


def window(curtain=False, seed=0):
    H = W = CELL
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    sky = 0.05 + 0.12 * (1 - yy / H)
    rgb = np.stack([sky * 0.8, sky * 0.9, sky * 1.05], -1) + 0.04 * fbm(H, W, 4, 3, wrap=False)[..., None]
    if curtain:
        folds = 0.5 + 0.5 * np.sin(xx / W * 2 * math.pi * 9 + 2 * fbm(H, W, 3, 2, wrap=False))
        cur = np.array([0.55, 0.5, 0.42]) * (0.55 + 0.45 * folds)[..., None]
        m = ((xx < 0.42 * W) | (xx > 0.58 * W))[..., None]
        rgb = np.where(m, cur * 0.75 + rgb * 0.25, rgb)
    frame = (np.abs(xx - W / 2) < 7) | (np.abs(yy - 0.38 * H) < 6) | (xx < 12) | (xx > W - 13) | (yy < 12) | (yy > H - 13)
    rgb[frame] = [0.62, 0.6, 0.55]
    hgt = np.where(frame, 0.01, 0.0).astype(np.float32)
    return to_img(rgb), hgt


def doors_atlas():
    G = 4
    cells = {}
    diff = Image.new("RGB", (G * CELL, G * CELL))
    nor = Image.new("RGB", (G * CELL, G * CELL))
    items = [
        ("door_green", lambda: steel_door([0.10, 0.30, 0.19], True, seed=1)),
        ("door_green2", lambda: steel_door([0.20, 0.40, 0.26], False, seed=2)),
        ("door_blue", lambda: steel_door([0.10, 0.20, 0.36], True, seed=3)),
        ("door_blue2", lambda: steel_door([0.20, 0.33, 0.50], False, seed=4)),
        ("rolldown_grey", lambda: rolldown([0.52, 0.52, 0.5], 5)),
        ("rolldown_green", lambda: rolldown([0.16, 0.32, 0.22], 6)),
        ("door_green_graffiti", lambda: steel_door([0.12, 0.33, 0.21], True, graffiti=True, seed=7)),
        ("door_wood", lambda: wood_door(8)),
        ("shutter_green", lambda: louvres([0.13, 0.33, 0.22], 9)),
        ("shutter_blue", lambda: louvres([0.14, 0.27, 0.42], 10)),
        ("shutter_brown", lambda: louvres([0.33, 0.20, 0.10], 11)),
        ("glass", lambda: window(False, 12)),
        ("glass_curtain", lambda: window(True, 13)),
        ("rolldown_blue", lambda: rolldown([0.15, 0.24, 0.40], 14)),
        ("door_teal", lambda: souq_door([0.33, 0.52, 0.47], 15)),     # pale teal / verdigris (notes C3)
        ("door_olive", lambda: souq_door([0.38, 0.40, 0.31], 16)),    # olive-grey variant
    ]
    for k, (name, fn) in enumerate(items):
        img, hgt = fn()
        c, r = k % G, k // G
        diff.paste(img, (c * CELL, r * CELL))
        nor.paste(normal_map(hgt, CELL / 1.5, wrap=False), (c * CELL, r * CELL))
        cells[name] = [c, r]
    return diff, nor, {"grid": [G, G], "cells": cells}


# ---------------------------------------------------------------- RGBA cutouts atlas
def rgba_canvas():
    return Image.new("RGBA", (CELL, CELL), (0, 0, 0, 0))


def fanlight():
    im = rgba_canvas()
    d = ImageDraw.Draw(im)
    iron = (24, 24, 22, 255)
    cx, cy, R = CELL / 2, CELL - 4, CELL / 2 - 6
    for k in range(13):
        a = math.pi * k / 12
        d.line([(cx, cy), (cx + math.cos(a) * R, cy - math.sin(a) * R)], fill=iron, width=7)
    for rr_ in (0.3, 0.62, 0.98):
        d.arc([cx - R * rr_, cy - R * rr_, cx + R * rr_, cy + R * rr_], 180, 360, fill=iron, width=8)
    d.line([(0, CELL - 5), (CELL, CELL - 5)], fill=iron, width=10)
    return im


def grille():
    im = rgba_canvas()
    d = ImageDraw.Draw(im)
    iron = (22, 22, 20, 255)
    for x in np.linspace(20, CELL - 20, 8):
        d.line([(x, 0), (x, CELL)], fill=iron, width=9)
    for y in (40, CELL / 2, CELL - 40):
        d.line([(0, y), (CELL, y)], fill=iron, width=10)
    for x in np.linspace(20, CELL - 20, 8)[:-1]:
        d.ellipse([x + 8, CELL / 2 - 70, x + 56, CELL / 2 - 22], outline=iron, width=6)
    return im


def railing(balcony=True):
    im = rgba_canvas()
    d = ImageDraw.Draw(im)
    iron = (20, 20, 19, 255)
    d.rectangle([0, 0, CELL, 22], fill=iron)
    d.rectangle([0, CELL - 26, CELL, CELL - 10], fill=iron)
    step = 34 if balcony else 42
    for x in range(10, CELL, step):
        d.line([(x, 0), (x, CELL)], fill=iron, width=7 if balcony else 9)
    if balcony:
        d.rectangle([0, CELL * 0.62, CELL, CELL * 0.62 + 10], fill=iron)
        for x in range(10, CELL - step, step):
            d.ellipse([x + 4, CELL * 0.66, x + step - 4, CELL * 0.66 + step - 8], outline=iron, width=5)
    else:
        d.rectangle([0, 0, 18, CELL], fill=iron)
        d.rectangle([CELL - 18, 0, CELL, CELL], fill=iron)
    return im


def balustrade():
    im = rgba_canvas()
    d = ImageDraw.Draw(im)
    stone = np.array([206, 194, 170])
    d.rectangle([0, 0, CELL, 60], fill=tuple(stone) + (255,))
    d.rectangle([0, CELL - 70, CELL, CELL], fill=tuple(stone) + (255,))
    for x0 in range(0, CELL, 64):
        cx = x0 + 32
        prof = []
        for t in np.linspace(0, 1, 40):
            r = 9 + 12 * math.sin(math.pi * t) ** 2 * (1.2 if t > 0.5 else 0.8) + (6 if t < 0.12 or t > 0.88 else 0)
            prof.append(r)
        ys = np.linspace(60, CELL - 70, 40)
        poly = [(cx - r, y) for r, y in zip(prof, ys)] + [(cx + r, y) for r, y in zip(prof[::-1], ys[::-1])]
        d.polygon(poly, fill=tuple((stone * 0.95).astype(int)) + (255,))
        d.line([(cx + 6, 64), (cx + 6, CELL - 74)], fill=tuple((stone * 1.08).clip(0, 255).astype(int)) + (255,), width=3)
    return im


def foliage(kind):
    im = rgba_canvas()
    d = ImageDraw.Draw(im)
    rr = np.random.default_rng({"caper": 1, "weeds": 2, "olive": 3, "ficus": 4, "cypress": 5}[kind])
    if kind == "weeds":                    # dry, sun-bleached tufts that grow in paving joints
        dry = [[118, 120, 66], [142, 132, 80], [96, 104, 56], [156, 144, 96], [84, 96, 52], [128, 112, 70]]
        for _ in range(85):
            x = rr.normal(CELL / 2, CELL / 7)
            h = rr.uniform(0.2, 0.7) * CELL
            bend = rr.normal(0, 45)
            col = tuple(int(v) for v in (np.array(dry[int(rr.integers(0, len(dry)))]) * rr.uniform(0.75, 1.15)).clip(0, 255)) + (255,)
            d.line([(x, CELL), (x + bend * 0.5, CELL - h * 0.55), (x + bend, CELL - h)], fill=col, width=int(rr.integers(2, 5)))
        for _ in range(14):
            x, y = rr.normal(CELL / 2, CELL / 6), rr.uniform(CELL * 0.7, CELL)
            d.ellipse([x - 10, y - 6, x + 10, y + 6], fill=(98, 104, 58, 255))
    elif kind == "caper":
        for _ in range(110):
            a = rr.uniform(0, 2 * math.pi)
            r = abs(rr.normal(0, CELL / 4.5))
            x, y = CELL / 2 + math.cos(a) * r, CELL / 2 + math.sin(a) * r * 0.8
            s = rr.uniform(14, 26)
            col = tuple(int(v) for v in (np.array([62, 108, 48]) * rr.uniform(0.7, 1.25)).clip(0, 255)) + (255,)
            d.ellipse([x - s, y - s * 0.85, x + s, y + s * 0.85], fill=col)
        for _ in range(9):
            x, y = rr.normal(CELL / 2, CELL / 6), rr.normal(CELL / 2, CELL / 7)
            d.ellipse([x - 12, y - 12, x + 12, y + 12], fill=(235, 220, 235, 255))
            d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=(170, 80, 150, 255))
    else:
        base = {"olive": [120, 135, 95], "ficus": [45, 85, 35], "cypress": [35, 60, 30]}[kind]
        n = {"olive": 900, "ficus": 500, "cypress": 1200}[kind]
        for _ in range(n):
            if kind == "cypress":
                x, y = rr.normal(CELL / 2, CELL / 9), rr.uniform(0, CELL)
            else:
                a = rr.uniform(0, 2 * math.pi)
                r = CELL / 2.2 * math.sqrt(rr.uniform(0, 1))
                x, y = CELL / 2 + math.cos(a) * r, CELL / 2 + math.sin(a) * r
            ang = rr.uniform(0, math.pi)
            ln = {"olive": 20, "ficus": 26, "cypress": 10}[kind]
            wd = {"olive": 5, "ficus": 14, "cypress": 6}[kind]
            col = tuple(int(v) for v in (np.array(base) * rr.uniform(0.6, 1.35)).clip(0, 255)) + (255,)
            pts = [(x + math.cos(ang) * ln, y + math.sin(ang) * ln), (x + math.cos(ang + 1.57) * wd, y + math.sin(ang + 1.57) * wd),
                   (x - math.cos(ang) * ln, y - math.sin(ang) * ln), (x - math.cos(ang + 1.57) * wd, y - math.sin(ang + 1.57) * wd)]
            d.polygon(pts, fill=col)
    return im


def cut_atlas():
    G = 4
    items = [("fanlight", fanlight), ("grille", grille), ("rail_balcony", lambda: railing(True)),
             ("rail_moat", lambda: railing(False)), ("balustrade", balustrade), ("caper", lambda: foliage("caper")),
             ("weeds", lambda: foliage("weeds")), ("olive", lambda: foliage("olive")), ("ficus", lambda: foliage("ficus")),
             ("cypress", lambda: foliage("cypress"))]
    atlas = Image.new("RGBA", (G * CELL, G * CELL), (0, 0, 0, 0))
    cells = {}
    for k, (name, fn) in enumerate(items):
        c, r = k % G, k // G
        atlas.paste(fn(), (c * CELL, r * CELL))
        cells[name] = [c, r]
    # bleed colour into transparent pixels so mipmaps do not get dark fringes
    rgb = atlas.convert("RGB").filter(ImageFilter.MaxFilter(5))
    out = Image.composite(atlas, Image.merge("RGBA", (*rgb.split(), Image.new("L", atlas.size, 0))), atlas.split()[3])
    return out, {"grid": [G, G], "cells": cells}


# ---------------------------------------------------------------- decals atlas (RGBA)
DC = 256


def font(name, size):
    for fn in [FONT_DIR / name, Path("/usr/share/fonts/TTF/DejaVuSans.ttf")]:
        if fn.exists():
            return ImageFont.truetype(str(fn), size, layout_engine=ImageFont.Layout.RAQM)
    return ImageFont.load_default()


def decal_streak(color, width=0.5, seed=0):
    H, W = DC, DC
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    n = fbm(H, W, 6, 4, wrap=False)
    col = np.abs(xx - W / 2) / (W / 2)
    cols = fbm(1, W, 12, 3, wrap=False)[0]
    a = (1 - smooth(width * 0.4, width, col + 0.2 * (n - 0.5))) * (0.35 + 0.65 * cols[None, :])
    a *= smooth(0.0, 0.25, 1 - yy / H) * (0.6 + 0.4 * n)     # fades towards the bottom
    a *= smooth(0.0, 0.04, yy / H)
    rgb = np.ones((H, W, 3)) * np.array(color)
    return Image.fromarray(np.dstack([rgb * 255, a * 255 * 0.85]).astype(np.uint8), "RGBA")


def decal_poster(seed, title_he, title_ar, title_en, bg):
    rr = np.random.default_rng(seed)
    im = Image.new("RGBA", (DC, DC), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    W = int(DC * 0.72)
    x0 = (DC - W) // 2
    paper = tuple(bg) + (255,)
    d.rectangle([x0, 4, x0 + W, DC - 4], fill=paper)
    d.text((x0 + W - 8, 12), title_he, font=font("NotoSansHebrew-Bold.ttf", 26), fill=(30, 30, 30, 255), anchor="ra",
           direction="rtl")
    d.text((x0 + W - 8, 52), title_ar, font=font("NotoSansArabic-Bold.ttf", 22), fill=(150, 20, 20, 255), anchor="ra",
           direction="rtl")
    d.text((x0 + 8, 96), title_en, font=font("NotoSans-Bold.ttf", 18), fill=(20, 40, 90, 255))
    for k in range(7):
        y = 130 + k * 15
        d.rectangle([x0 + 10, y, x0 + W - 10 - int(rr.uniform(0, 60)), y + 6], fill=(90, 90, 90, 255))
    arr = np.asarray(im).astype(np.float32)
    fade = 0.75 + 0.25 * fbm(DC, DC, 8, 3, wrap=False)
    arr[..., :3] = arr[..., :3] * fade[..., None] + 30 * (1 - fade[..., None])
    torn = fbm(DC, DC, 10, 4, wrap=False) > 0.68
    arr[..., 3][torn & (arr[..., 3] > 0)] *= 0.0
    return Image.fromarray(arr.clip(0, 255).astype(np.uint8), "RGBA")


def decal_manhole():
    im = Image.new("RGBA", (DC, DC), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([8, 8, DC - 8, DC - 8], fill=(52, 48, 44, 255), outline=(85, 80, 72, 255), width=10)
    for k in range(-5, 6):
        d.line([(DC / 2 + k * 18, 30), (DC / 2 + k * 18, DC - 30)], fill=(70, 66, 60, 255), width=5)
    d.text((DC / 2, DC / 2), "JERUSALEM", font=font("NotoSans-Bold.ttf", 22), fill=(95, 90, 82, 255), anchor="mm")
    return im


def decal_drain():
    im = Image.new("RGBA", (DC, DC), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([30, 70, DC - 30, DC - 70], fill=(40, 38, 35, 255), outline=(80, 76, 70, 255), width=8)
    for x in range(44, DC - 40, 16):
        d.rectangle([x, 82, x + 7, DC - 82], fill=(12, 12, 12, 255))
    return im


def decal_stain(seed):
    H = W = DC
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt((xx - W / 2) ** 2 + (yy - H / 2) ** 2) / (W / 2)
    n = fbm(H, W, 5, 4, wrap=False)
    a = (1 - smooth(0.4, 0.95, r + 0.4 * (n - 0.5))) * 0.55
    return Image.fromarray(np.dstack([np.ones((H, W, 3)) * [35, 30, 25], a * 255]).astype(np.uint8), "RGBA")


def decal_graffiti(seed):
    rr = np.random.default_rng(seed)
    im = Image.new("RGBA", (DC, DC), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for _ in range(3):
        col = tuple(int(v) for v in rr.choice([[25, 25, 25], [160, 25, 25], [30, 50, 140]])) + (230,)
        x, y = rr.uniform(40, 200), rr.uniform(80, 170)
        pts = [(x, y)]
        for _ in range(12):
            x += rr.normal(6, 14)
            y += rr.normal(0, 16)
            pts.append((x, y))
        d.line(pts, fill=col, width=int(rr.integers(5, 10)), joint="curve")
    return im


def decal_atlas():
    G = 4
    items = [
        ("streak", lambda: decal_streak([0.08, 0.07, 0.05], 0.55)),
        ("streak_wide", lambda: decal_streak([0.1, 0.09, 0.07], 0.95)),
        ("rust", lambda: decal_streak([0.35, 0.18, 0.06], 0.45)),
        ("damp", lambda: decal_stain(1)),
        ("poster_a", lambda: decal_poster(1, "הופעה", "حفلة موسيقية", "CONCERT", [235, 225, 200])),
        ("poster_b", lambda: decal_poster(2, "הודעה", "إعلان", "NOTICE", [245, 240, 225])),
        ("poster_c", lambda: decal_poster(3, "שיעור תורה", "محاضرة", "LECTURE", [215, 230, 240])),
        ("poster_d", lambda: decal_poster(4, "למכירה", "للبيع", "FOR SALE", [250, 220, 120])),
        ("manhole", decal_manhole),
        ("drain", decal_drain),
        ("stain", lambda: decal_stain(2)),
        ("graffiti", lambda: decal_graffiti(3)),
    ]
    atlas = Image.new("RGBA", (G * DC, G * DC), (0, 0, 0, 0))
    cells = {}
    for k, (name, fn) in enumerate(items):
        c, r = k % G, k // G
        atlas.paste(fn(), (c * DC, r * DC))
        cells[name] = [c, r]
    return atlas, {"grid": [G, G], "cells": cells}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    man = {}
    d, n = paving()
    d.save(OUT / "paving_diff.jpg", quality=90)
    n.save(OUT / "paving_nor.png")
    man["paving"] = {"diff": "data/textures/gen/paving_diff.jpg", "nor": "data/textures/gen/paving_nor.png", "tile": 4.0}
    d, n = setts()
    d.save(OUT / "setts_diff.jpg", quality=90)
    n.save(OUT / "setts_nor.png")
    man["setts"] = {"diff": "data/textures/gen/setts_diff.jpg", "nor": "data/textures/gen/setts_nor.png", "tile": 2.0}
    d, n = asphalt()
    d.save(OUT / "asphalt_diff.jpg", quality=90)
    n.save(OUT / "asphalt_nor.png")
    man["asphalt"] = {"diff": "data/textures/gen/asphalt_diff.jpg", "nor": "data/textures/gen/asphalt_nor.png", "tile": 3.0}
    d, n = corrugated()
    d.save(OUT / "corrugated_diff.jpg", quality=90)
    n.save(OUT / "corrugated_nor.png")
    man["corrugated"] = {"diff": "data/textures/gen/corrugated_diff.jpg", "nor": "data/textures/gen/corrugated_nor.png", "tile": 1.0}
    d, n = grass()
    d.save(OUT / "grass_diff.jpg", quality=90)
    n.save(OUT / "grass_nor.png")
    man["grass"] = {"diff": "data/textures/gen/grass_diff.jpg", "nor": "data/textures/gen/grass_nor.png", "tile": 3.0}
    d, n, cells = doors_atlas()
    d.save(OUT / "doors_diff.jpg", quality=90)
    n.save(OUT / "doors_nor.png")
    man["doors"] = {"diff": "data/textures/gen/doors_diff.jpg", "nor": "data/textures/gen/doors_nor.png", **cells}
    a, cells = cut_atlas()
    a.save(OUT / "cutout.png")
    man["cutout"] = {"img": "data/textures/gen/cutout.png", **cells}
    a, cells = decal_atlas()
    a.save(OUT / "decal.png")
    man["decal"] = {"img": "data/textures/gen/decal.png", **cells}
    d, n = bark()
    d.save(OUT / "bark_diff.jpg", quality=90)
    n.save(OUT / "bark_nor.png")
    man["bark"] = {"diff": "data/textures/gen/bark_diff.jpg", "nor": "data/textures/gen/bark_nor.png", "tile": 1.0}
    d, n = lime()
    d.save(OUT / "lime_diff.jpg", quality=90)
    n.save(OUT / "lime_nor.png")
    man["lime"] = {"diff": "data/textures/gen/lime_diff.jpg", "nor": "data/textures/gen/lime_nor.png", "tile": 2.0}
    (OUT / "manifest.json").write_text(json.dumps(man, indent=1))
    print("wrote", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()

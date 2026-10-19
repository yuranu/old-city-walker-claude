#!/usr/bin/env python3
"""Signage texture atlas for the Jaffa Gate / Omar Ibn el-Khattab Square area.

    .venv/bin/python pipeline/gen_signs.py
        -> data/textures/gen/signs.png    2048x2048 RGBA atlas (8 px+ transparent padding,
                                           colour bled into the transparent texels)
        -> data/textures/gen/signs.json   {"size": [2048, 2048], "signs": {name: {"rect": [x, y, w, h],
                                           "w_m", "h_m", "kind", ...}}}  rect in px from the top-left
        -> renders/signs/preview.png      every sign on a limestone background, for checking

Designs and texts come from photographs where they exist (data/photos, data/photos_ref) and are
marked "verified": true in the json; the rest are plausible for the Old City. Street names follow
the Karakashian ceramic street tiles (Hebrew strip on top, Arabic + English panel below, green leaf
trim, blue/black hand-painted letters), cross-checked with the OSM name / name:he / name:ar tags.

Every sign is rendered at 2x and downsampled. Hebrew and Arabic go through raqm (shaping + bidi).
"""
import json
import math
import zlib
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "data/textures/gen"
PREVIEW_DIR = ROOT / "renders/signs"
ATLAS = 2048
PAD = 8          # transparent texels kept around every sign (each side)
SS = 2           # supersampling

NOTO = Path("/usr/share/fonts/noto")
GS = Path("/usr/share/fonts/gsfonts")
FONTS = {
    "sans": NOTO / "NotoSans-Regular.ttf",
    "sans_m": NOTO / "NotoSans-Medium.ttf",
    "sans_b": NOTO / "NotoSans-Bold.ttf",
    "sans_blk": NOTO / "NotoSans-Black.ttf",
    "sans_blk_i": NOTO / "NotoSans-BlackItalic.ttf",
    "serif_b": NOTO / "NotoSerif-Bold.ttf",
    "serif_blk": NOTO / "NotoSerif-Black.ttf",
    "disp_b": NOTO / "NotoSerifDisplay-Bold.ttf",
    "disp_sb": NOTO / "NotoSerifDisplay-Medium.ttf",
    "narrow_b": GS / "NimbusSansNarrow-Bold.otf",
    "helv_b": GS / "NimbusSans-Bold.otf",
    "roman_b": GS / "NimbusRoman-Bold.otf",
    "century_b": GS / "C059-Bold.otf",
    "palat_b": GS / "P052-Bold.otf",
    "bookman": GS / "URWBookman-Demi.otf",
    "gothic": GS / "URWGothic-Demi.otf",
    "chancery": GS / "Z003-MediumItalic.otf",
    "he_sans": NOTO / "NotoSansHebrew-Medium.ttf",
    "he_sans_b": NOTO / "NotoSansHebrew-Bold.ttf",
    "he_sans_blk": NOTO / "NotoSansHebrew-Black.ttf",
    "he_serif_b": NOTO / "NotoSerifHebrew-Bold.ttf",
    "he_serif_blk": NOTO / "NotoSerifHebrew-Black.ttf",
    "alef": Path("/usr/share/fonts/TTF/Alef-Regular.ttf"),        # Hebrew + Latin digits/punctuation
    "alef_b": Path("/usr/share/fonts/TTF/Alef-Bold.ttf"),
    "ar_naskh": NOTO / "NotoNaskhArabic-Medium.ttf",
    "ar_naskh_b": NOTO / "NotoNaskhArabic-Bold.ttf",
    "ar_kufi_b": NOTO / "NotoKufiArabic-Bold.ttf",
    "ar_kufi_blk": NOTO / "NotoKufiArabic-Black.ttf",
    "ar_sans": NOTO / "NotoSansArabic-Medium.ttf",
    "ar_sans_b": NOTO / "NotoSansArabic-Bold.ttf",
}


# =============================================================================== small helpers
def col(c):
    return np.asarray(c, np.float32)[:3]


def smooth(e0, e1, x):
    t = np.clip((x - e0) / (e1 - e0), 0, 1)
    return t * t * (3 - 2 * t)


def box1d(a, r, axis):
    if r < 1:
        return a
    n = a.shape[axis]
    pad = [(0, 0)] * a.ndim
    pad[axis] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=axis, dtype=np.float32)
    hi = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
    lo = np.take(c, np.arange(0, n), axis=axis)
    return (hi - lo) / (2 * r + 1)


def blur(a, sigma, axis=None):
    """~Gaussian blur (three box passes) of a 2-D float array."""
    if sigma <= 0.3:
        return a
    r = max(1, int(round(math.sqrt(sigma * sigma + 0.25) - 0.5)))
    out = a.astype(np.float32)
    for _ in range(3):
        if axis in (None, 1):
            out = box1d(out, r, 1)
        if axis in (None, 0):
            out = box1d(out, r, 0)
    return out


def shift(a, dx, dy):
    out = np.zeros_like(a)
    H, W = a.shape[:2]
    dx, dy = int(round(dx)), int(round(dy))
    xs0, xs1 = max(0, -dx), min(W, W - dx)
    ys0, ys1 = max(0, -dy), min(H, H - dy)
    if xs1 > xs0 and ys1 > ys0:
        out[ys0 + dy:ys1 + dy, xs0 + dx:xs1 + dx] = a[ys0:ys1, xs0:xs1]
    return out


def dilate(m, r):
    out = m.copy()
    for _ in range(int(r)):
        o = out.copy()
        o[1:] = np.maximum(o[1:], out[:-1])
        o[:-1] = np.maximum(o[:-1], out[1:])
        o[:, 1:] = np.maximum(o[:, 1:], out[:, :-1])
        o[:, :-1] = np.maximum(o[:, :-1], out[:, 1:])
        out = o
    return out


def erode(m, r):
    return 1 - dilate(1 - m, r)


def vnoise(rng, h, w, cy, cx):
    g = rng.random((max(2, int(cy)), max(2, int(cx)))).astype(np.float32)
    return np.asarray(Image.fromarray(g, "F").resize((w, h), Image.BICUBIC), np.float32)


def fbm(rng, h, w, scale=4.0, octaves=5, gain=0.5, sx=1.0, sy=1.0):
    """Value-noise fbm in [0,1]; `scale` = cells across the longer side for the first octave."""
    out = np.zeros((h, w), np.float32)
    amp, tot = 1.0, 0.0
    L = max(h, w)
    for o in range(octaves):
        c = scale * 2 ** o
        cx = min(w / 2, c * w / L * sx) + 2
        cy = min(h / 2, c * h / L * sy) + 2
        out += amp * vnoise(rng, h, w, cy, cx)
        tot += amp
        amp *= gain
    return np.clip(out / tot, 0, 1)


def warp(m, rng, amp, scale=3.0):
    """Displace a mask by low-frequency noise (hand-painted wobble). amp in px."""
    H, W = m.shape
    dx = (fbm(rng, H, W, scale, 3) - 0.5) * 2 * amp
    dy = (fbm(rng, H, W, scale, 3) - 0.5) * 2 * amp
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    x = np.clip(xx + dx, 0, W - 1.001)
    y = np.clip(yy + dy, 0, H - 1.001)
    x0, y0 = x.astype(np.int32), y.astype(np.int32)
    fx, fy = x - x0, y - y0
    a = m[y0, x0] * (1 - fx) + m[y0, x0 + 1] * fx
    b = m[y0 + 1, x0] * (1 - fx) + m[y0 + 1, x0 + 1] * fx
    return a * (1 - fy) + b * fy


def lum(rgb):
    return rgb[..., 0] * 0.299 + rgb[..., 1] * 0.587 + rgb[..., 2] * 0.114


# =============================================================================== text
_FC = {}


def font(key, px):
    px = max(4, int(round(px)))
    k = (key, px)
    if k not in _FC:
        _FC[k] = ImageFont.truetype(str(FONTS[key]), px, layout_engine=ImageFont.Layout.RAQM)
    return _FC[k]


_NOTDEF = {}
COMBINING = set(range(0x0591, 0x05C8)) | set(range(0x064B, 0x0660)) | {0x0670}


def check_glyphs(text, key):
    """raise if the font has no glyph for a character (would render as a tofu box)"""
    f = font(key, 40)
    if key not in _NOTDEF:
        nd = f.getmask("\uffff")
        _NOTDEF[key] = (nd.size, bytes(nd))
    bad = []
    for ch in set(text):
        if ch.isspace() or ord(ch) in COMBINING:
            continue
        m = f.getmask(ch)
        if (m.size, bytes(m)) == _NOTDEF[key]:
            bad.append(ch)
    if bad:
        raise ValueError(f"font {key} has no glyph for {bad!r} in {text!r}")


def text_dir(text):
    for ch in text:
        o = ord(ch)
        if 0x0590 <= o <= 0x05FF or 0xFB1D <= o <= 0xFB4F:
            return "rtl", "he"
        if 0x0600 <= o <= 0x06FF or 0xFB50 <= o <= 0xFEFF:
            return "rtl", "ar"
    return "ltr", "en"


def text_img(text, key, px, tracking=0.0):
    """Tight 'L' image of the text's ink. tracking = extra letter spacing in em (LTR only)."""
    px = max(4, int(round(px)))
    check_glyphs(text, key)
    d, lang = text_dir(text)
    f = font(key, px)
    if d == "ltr" and tracking:
        widths = [f.getlength(c) for c in text]
        total = sum(widths) + tracking * px * (len(text) - 1)
        asc, desc = f.getmetrics()
        im = Image.new("L", (int(total + 2 * px), asc + desc + px), 0)
        dr = ImageDraw.Draw(im)
        x = px
        for c, w in zip(text, widths):
            dr.text((x, px / 2), c, font=f, fill=255)
            x += w + tracking * px
    else:
        kw = {"direction": d, "language": lang} if d == "rtl" else {}
        l, t, r, b = f.getbbox(text, **kw)
        im = Image.new("L", (r - l + px, b - t + px), 0)
        ImageDraw.Draw(im).text((px / 2 - l, px / 2 - t), text, font=f, fill=255, **kw)
    bb = im.getbbox()
    return im.crop(bb) if bb else im


def fit_text(text, key, bw, bh, sx=1.0, tracking=0.0, max_h=None):
    probe = text_img(text, key, 160, tracking)
    s = min(bh / probe.height, bw / (probe.width * sx))
    if max_h:
        s = min(s, max_h / probe.height)
    img = text_img(text, key, max(6, 160 * s), tracking)
    tw = max(1, int(round(probe.width * s * sx)))
    th = max(1, int(round(probe.height * s)))
    return img.resize((tw, th), Image.LANCZOS)


def wrap_words(text, key, px, width):
    d, lang = text_dir(text)
    f = font(key, px)
    kw = {"direction": d, "language": lang} if d == "rtl" else {}
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if f.getlength(t, **kw) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


# =============================================================================== canvas
class Canvas:
    def __init__(self, W, H, w_m, h_m, rng):
        self.W, self.H = W, H
        self.ppm = W / w_m
        self.rng = rng
        self.rgb = np.zeros((H, W, 3), np.float32)
        self.a = np.ones((H, W), np.float32)
        yy, xx = np.mgrid[0:H, 0:W]
        self.u = ((xx + 0.5) / W).astype(np.float32)
        self.v = ((yy + 0.5) / H).astype(np.float32)

    # -- geometry helpers (fractions of the sign or metres)
    def p(self, m):
        return m * self.ppm

    def bx(self, x0, y0, x1, y1):
        """fractional box -> px box"""
        return (x0 * self.W, y0 * self.H, x1 * self.W, y1 * self.H)

    def noise(self, scale=4, octaves=5, sx=1.0, sy=1.0):
        return fbm(self.rng, self.H, self.W, scale, octaves, sx=sx, sy=sy)

    def noise_m(self, feature_m, octaves=5, sx=1.0, sy=1.0):
        """fbm whose first octave has features of about feature_m metres"""
        long_m = max(self.W, self.H) / self.ppm
        return fbm(self.rng, self.H, self.W, max(1.0, long_m / feature_m), octaves, sx=sx, sy=sy)

    def layer(self):
        im = Image.new("L", (self.W, self.H), 0)
        return im, ImageDraw.Draw(im)

    @staticmethod
    def arr(im):
        return np.asarray(im, np.float32) / 255.0

    def m_rect(self, box, r=0):
        im, d = self.layer()
        box = [float(v) for v in box]
        if r > 0:
            d.rounded_rectangle(box, radius=r, fill=255)
        else:
            d.rectangle(box, fill=255)
        return self.arr(im)

    def m_ellipse(self, box):
        im, d = self.layer()
        d.ellipse([float(v) for v in box], fill=255)
        return self.arr(im)

    def m_poly(self, pts):
        im, d = self.layer()
        d.polygon([(float(x), float(y)) for x, y in pts], fill=255)
        return self.arr(im)

    def m_line(self, pts, width):
        im, d = self.layer()
        d.line([(float(x), float(y)) for x, y in pts], fill=255, width=max(1, int(round(width))), joint="curve")
        return self.arr(im)

    def frame_mask(self, box, w, r=0):
        x0, y0, x1, y1 = box
        return np.clip(self.m_rect(box, r) - self.m_rect((x0 + w, y0 + w, x1 - w, y1 - w), max(0, r - w)), 0, 1)

    # -- paint
    def fill(self, color, mask=None, op=1.0):
        c = col(color)
        if mask is None:
            self.rgb[:] = c
            return
        m = np.clip(mask * op, 0, 1)[..., None]
        self.rgb = self.rgb * (1 - m) + c * m

    def fill_rgb(self, rgb, mask, op=1.0):
        m = np.clip(mask * op, 0, 1)[..., None]
        self.rgb = self.rgb * (1 - m) + rgb * m

    def text_mask(self, text, key, box, align="c", valign="c", sx=1.0, tracking=0.0, max_h=None):
        x0, y0, x1, y1 = box
        img = fit_text(text, key, x1 - x0, y1 - y0, sx, tracking, max_h)
        tw, th = img.size
        x = x0 if align == "l" else (x1 - tw if align == "r" else x0 + (x1 - x0 - tw) / 2)
        y = y0 if valign == "t" else (y1 - th if valign == "b" else y0 + (y1 - y0 - th) / 2)
        im = Image.new("L", (self.W, self.H), 0)
        im.paste(img, (int(round(x)), int(round(y))))
        return self.arr(im), (x, y, x + tw, y + th)

    def text(self, text, key, box, color, align="c", valign="c", sx=1.0, tracking=0.0, max_h=None,
             wobble=0.0, cover=0.0, op=1.0, shadow=None, outline=None):
        m, bb = self.text_mask(text, key, box, align, valign, sx, tracking, max_h)
        if wobble:
            m = warp(m, self.rng, wobble * self.H / 100, scale=6)
        if outline:
            oc, ow = outline
            om = np.clip(blur(dilate(m, max(1, int(round(ow)))), 0.6), 0, 1)
            self.fill(oc, om, op)
        if shadow:
            dx, dy, sb, sc, so = shadow
            sm = blur(shift(m, dx, dy), sb)
            self.fill(sc, sm, so * op)
        if cover:
            n = fbm(self.rng, self.H, self.W, 10, 4, sx=0.25, sy=3.0)
            m = m * (1 - cover * smooth(0.35, 0.75, n))
        self.fill(color, m, op)
        return m, bb

    def paste_rgba(self, im, xy=(0, 0)):
        """composite a straight-alpha PIL RGBA image"""
        layer = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        layer.paste(im, (int(xy[0]), int(xy[1])))
        a = np.asarray(layer, np.float32) / 255.0
        self.fill_rgb(a[..., :3], a[..., 3])

    # -- materials and wear -----------------------------------------------------------------
    def grain(self, amt=0.02, scale=1.0):
        n = self.rng.normal(0, 1, (self.H, self.W)).astype(np.float32)
        if scale > 1:
            n = blur(n, scale * 0.5) * scale
        self.rgb *= (1 + n * amt)[..., None]
        low = self.noise(3, 4)
        self.rgb *= (1 + (low - 0.5) * amt * 3)[..., None]

    def fade(self, amt, top_bias=0.35):
        """sun bleaching: desaturate and lighten (reds go pink, blues chalky)."""
        if amt <= 0:
            return
        L = lum(self.rgb)
        pale = np.stack([L * 0.55 + 0.42 + 0.015, L * 0.55 + 0.41, L * 0.55 + 0.38], -1)
        n = self.noise(2.5, 4)
        m = amt * (0.55 + 0.45 * n) * (1 - top_bias * self.v)
        self.rgb = self.rgb * (1 - m[..., None]) + pale * m[..., None]

    def dust(self, amt, color=(0.80, 0.74, 0.63)):
        if amt <= 0:
            return
        n = self.noise_m(0.25, 6)
        edge = self.edge_dist()
        m = amt * (0.3 + 0.7 * smooth(0.3, 0.8, n)) * (0.6 + 0.4 * (1 - smooth(0, 0.08, edge)))
        self.fill(color, m)

    def edge_dist(self):
        """distance to the nearest sign edge in metres (rectangular)"""
        dx = np.minimum(self.u, 1 - self.u) * self.W / self.ppm
        dy = np.minimum(self.v, 1 - self.v) * self.H / self.ppm
        return np.minimum(dx, dy)

    def grime(self, amt, color=(0.20, 0.16, 0.11), bottom=0.5):
        if amt <= 0:
            return
        n = self.noise_m(0.35, 6)
        fine = self.noise_m(0.03, 3)
        e = 1 - smooth(0.0, 0.10, self.edge_dist())
        m = amt * (0.25 + 0.55 * smooth(0.25, 0.85, n) + 0.2 * fine) * (0.3 + 0.7 * np.maximum(e, bottom * self.v ** 2))
        c = col(color)
        self.rgb = self.rgb * (1 - 0.6 * m[..., None]) + c * 0.6 * m[..., None]

    def streaks(self, amt, color=(0.22, 0.17, 0.12), length=0.8, density=0.5, from_y=0.0):
        """vertical run-off streaks from the top edge (or from_y)"""
        if amt <= 0:
            return
        H, W = self.H, self.W
        cols_ = np.asarray(Image.fromarray(self.rng.random((1, max(4, int(W / (self.ppm * 0.025))))).astype(np.float32), "F")
                           .resize((W, 1), Image.BICUBIC), np.float32)[0]
        cols_ = smooth(1 - density * 0.6, 1.0, cols_)
        fine = np.asarray(Image.fromarray(self.rng.random((1, max(8, W // 3))).astype(np.float32), "F")
                          .resize((W, 1), Image.BILINEAR), np.float32)[0]
        lens = (0.2 + 0.8 * np.asarray(Image.fromarray(self.rng.random((1, 12)).astype(np.float32), "F")
                                        .resize((W, 1), Image.BICUBIC), np.float32)[0]) * length
        vv = np.clip((self.v - from_y) / max(1e-3, 1 - from_y), 0, 1)
        fall = np.clip(1 - vv / np.maximum(lens[None, :], 1e-3), 0, 1) ** 1.5 * (self.v >= from_y)
        n = self.noise(4, 4, sx=0.5, sy=2)
        m = amt * cols_[None, :] * (0.6 + 0.4 * fine[None, :]) * fall * (0.5 + 0.5 * n)
        c = col(color)
        self.rgb = self.rgb * (1 - m[..., None]) + c * m[..., None]

    def runs_from(self, mask, amt, color=(0.40, 0.20, 0.08), length_m=0.15):
        """streaks running down from a mask (rust under screws, dirt under letters)"""
        H = self.H
        L = max(2, int(self.p(length_m)))
        steps = 24
        acc = np.zeros_like(mask)
        for i in range(steps):
            d = int(L * i / steps)
            acc = np.maximum(acc, shift(mask, 0, d) * (1 - i / steps) ** 1.3)
        acc = blur(acc, max(1.0, self.p(0.004)), axis=1)
        n = self.noise(6, 3, sx=0.4, sy=2.5)
        m = amt * acc * (0.5 + 0.5 * n)
        c = col(color)
        self.rgb = self.rgb * (1 - m[..., None]) + c * m[..., None]
        return acc

    def rust(self, amt, edge_m=0.06, spots=0.3):
        if amt <= 0:
            return
        n = self.noise_m(0.10, 5)
        e = 1 - smooth(0.0, edge_m, self.edge_dist())
        v = n * (0.45 + 0.55 * e) + spots * 0.2 * self.noise_m(0.02, 3)
        m = smooth(0.52, 0.66, v) * amt
        core = smooth(0.62, 0.74, v) * amt
        self.fill((0.47, 0.25, 0.10), m, 0.9)
        self.fill((0.25, 0.12, 0.05), core, 0.7)
        self.runs_from(m * 0.8, 0.35 * amt, (0.45, 0.24, 0.1), 0.12)

    def chips(self, amt, under=(0.13, 0.12, 0.11), n=None, rmax_m=0.012, edge_bias=0.7):
        """enamel / paint chips: small irregular holes showing metal, with a rust halo"""
        if amt <= 0:
            return
        if n is None:
            n = int(amt * 40 * (self.W * self.H) / (self.ppm ** 2) + 2)
        im, d = self.layer()
        for _ in range(n):
            if self.rng.random() < edge_bias:
                side = self.rng.integers(0, 4)
                t = self.rng.random()
                off = abs(self.rng.normal(0, 0.012)) * self.ppm
                x, y = [(t * self.W, off), (t * self.W, self.H - off), (off, t * self.H), (self.W - off, t * self.H)][side]
            else:
                x, y = self.rng.random() * self.W, self.rng.random() * self.H
            r = self.p(rmax_m) * (0.2 + 0.8 * self.rng.random() ** 2)
            pts = []
            k = 7
            for i in range(k):
                ang = 2 * math.pi * i / k + self.rng.random() * 0.6
                rr = r * (0.5 + 0.7 * self.rng.random())
                pts.append((x + rr * math.cos(ang), y + rr * 0.8 * math.sin(ang)))
            d.polygon(pts, fill=255)
        m = self.arr(im)
        halo = np.clip(blur(m, self.p(0.004)) * 1.6 - m, 0, 1)
        self.fill((0.42, 0.24, 0.12), halo, 0.55)
        self.fill(under, m)
        self.runs_from(m * 0.6, 0.25, (0.42, 0.22, 0.10), 0.08)

    def scratches(self, n, color=(0.85, 0.84, 0.80), op=0.35, max_len=0.2):
        im, d = self.layer()
        for _ in range(n):
            x, y = self.rng.random() * self.W, self.rng.random() * self.H
            ang = self.rng.normal(0.2, 0.6)
            L = self.p(max_len) * self.rng.random()
            pts = [(x, y)]
            for i in range(4):
                ang += self.rng.normal(0, 0.15)
                x += math.cos(ang) * L / 4
                y += math.sin(ang) * L / 4
                pts.append((x, y))
            d.line(pts, fill=int(120 + 135 * self.rng.random()), width=1)
        self.fill(color, self.arr(im), op)

    def peel(self, amt, under, edge_m=0.08, lip=(0.95, 0.93, 0.88), scale=10):
        """flaking paint near the edges and along cracks"""
        if amt <= 0:
            return np.zeros((self.H, self.W), np.float32)
        n = self.noise_m(2.0 / scale, 5)
        e = 1 - smooth(0.0, edge_m, self.edge_dist())
        v = n * 0.75 + e * 0.35 + 0.1 * self.noise_m(0.01, 2)
        t = 1.0 - amt * 0.45
        m = smooth(t, t + 0.04, v)
        ring = np.clip(dilate(m, 1) - m, 0, 1)
        self.fill(lip, ring, 0.35)
        self.fill_rgb(under if isinstance(under, np.ndarray) else np.broadcast_to(col(under), self.rgb.shape), m)
        return m

    def screws(self, pts_m, r_m=0.006, rust=0.6):
        m = np.zeros((self.H, self.W), np.float32)
        for (x, y) in pts_m:
            px, py = x * self.W if x <= 1 else self.p(x), y * self.H if y <= 1 else self.p(y)
            r = self.p(r_m)
            m = np.maximum(m, self.m_ellipse((px - r, py - r, px + r, py + r)))
        self.fill((0.55, 0.53, 0.50), m)
        hl = shift(m, -self.p(r_m) * 0.3, -self.p(r_m) * 0.3) * m
        self.fill((0.78, 0.76, 0.72), hl, 0.5)
        if rust:
            halo = np.clip(blur(m, self.p(r_m * 0.8)) * 2 - m, 0, 1)
            self.fill((0.45, 0.22, 0.08), halo, 0.5 * rust)
            self.runs_from(m, 0.45 * rust, (0.45, 0.22, 0.08), 0.18)

    def crazing(self, amt, box=None, scale=18, color=(0.42, 0.37, 0.30)):
        """fine crack network in old glaze (dirt in the cracks)"""
        if amt <= 0:
            return
        cell = 0.6 / scale                       # scale kept as "cells per 0.6 m"
        n1 = self.noise_m(cell, 3)
        n2 = self.noise_m(cell * 0.45, 2)
        r = 1 - np.abs(2 * n1 - 1)
        r2 = 1 - np.abs(2 * n2 - 1)
        lines = np.maximum(smooth(0.965, 0.995, r), 0.7 * smooth(0.97, 0.995, r2))
        m = lines * amt * 0.7 * (0.3 + 0.7 * self.noise(3, 3))
        if box is not None:
            m = m * box
        self.fill(color, m)

    def bevel(self, mask, strength=0.35, radius=None, light=(-0.6, -0.8)):
        """fake relief shading for raised metal letters"""
        r = radius or max(1.0, self.p(0.004))
        h = blur(mask, r)
        gy, gx = np.gradient(h)
        sh = (gx * light[0] + gy * light[1]) * r * 2.2
        self.rgb *= (1 + np.clip(sh, -1, 1) * strength * mask)[..., None]

    def finish(self):
        rgb = np.clip(self.rgb, 0, 1)
        a = np.clip(self.a, 0, 1)
        im = Image.fromarray((np.dstack([rgb, a[..., None]]) * 255 + 0.5).astype(np.uint8), "RGBA")
        return im


# =============================================================================== border patterns
def vine_strip(length, b, ss=1):
    """Karakashian street-tile trim: yellow band, green wavy stem with leaves and orange berries,
    thin green outer and orange inner lines. Returns RGBA (length x b), outer edge at the top."""
    S = 3
    L, B = int(length * S), int(b * S)
    im = Image.new("RGBA", (L, B), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    yellow, green, dkgreen, orange, berry = (226, 190, 70), (52, 128, 62), (24, 96, 70), (196, 104, 34), (214, 84, 34)
    d.rectangle([0, 0, L, B], fill=yellow + (255,))
    d.rectangle([0, 0, L, int(B * 0.13)], fill=dkgreen + (255,))
    d.rectangle([0, int(B * 0.88), L, B], fill=orange + (255,))
    cy = B * 0.5
    A = B * 0.17
    P = B * 1.7
    pts = [(x, cy + A * math.sin(2 * math.pi * x / P)) for x in np.arange(0, L + 2, 2)]
    d.line(pts, fill=green + (255,), width=max(1, int(B * 0.06)))
    k = 0
    x = P * 0.25
    while x < L + P:
        for side in (1, -1):
            xx = x + (0 if side == 1 else P / 2)
            yy = cy + A * math.sin(2 * math.pi * xx / P)
            ang = math.radians(-45 if side == 1 else 45)
            lx, ly = xx + math.cos(ang) * B * 0.17, yy + side * abs(math.sin(ang)) * B * 0.17
            pts_leaf = []
            for t in np.linspace(0, 2 * math.pi, 14):
                ex, ey = math.cos(t) * B * 0.16, math.sin(t) * B * 0.065
                ca, sa = math.cos(ang * side), math.sin(ang * side)
                pts_leaf.append((lx + ex * ca - ey * sa, ly + ex * sa + ey * ca))
            d.polygon(pts_leaf, fill=green + (255,))
            bx_, by_ = xx - B * 0.16, yy - side * B * 0.16
            r = B * 0.045
            d.ellipse([bx_ - r, by_ - r, bx_ + r, by_ + r], fill=berry + (255,))
        x += P
        k += 1
    return im.resize((max(1, int(length)), max(1, int(b))), Image.LANCZOS)


def braid_strip(length, b):
    """Jaffa Gate tile trim: dark green band with a white two-strand braid."""
    S = 3
    L, B = int(length * S), int(b * S)
    im = Image.new("RGBA", (L, B), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    green, white, line = (22, 72, 52), (238, 236, 226), (12, 40, 28)
    d.rectangle([0, 0, L, B], fill=green + (255,))
    cy, A, P = B * 0.5, B * 0.26, B * 0.9
    w = max(2, int(B * 0.17))
    for ph in (0, math.pi):
        pts = [(x, cy + A * math.sin(2 * math.pi * x / P + ph)) for x in np.arange(-P, L + P, 2)]
        d.line(pts, fill=line + (255,), width=w + max(2, int(B * 0.06)))
        d.line(pts, fill=white + (255,), width=w)
    # re-draw every other crossing of strand 0 on top so the strands interlace
    for i in range(int(L / P) + 2):
        x0 = i * P - P * 0.25
        if i % 2 == 0:
            pts = [(x, cy + A * math.sin(2 * math.pi * x / P)) for x in np.arange(x0, x0 + P * 0.5, 2)]
            d.line(pts, fill=line + (255,), width=w + max(2, int(B * 0.06)))
            d.line(pts, fill=white + (255,), width=w)
    d.rectangle([0, int(B * 0.92), L, B], fill=white + (255,))
    return im.resize((max(1, int(length)), max(1, int(b))), Image.LANCZOS)


def flower_strip(length, b, bg=(30, 70, 150), petal=(90, 190, 200), centre=(250, 245, 230), leaf=(60, 150, 90)):
    """Armenian-pottery style border: cobalt band with small turquoise four-petal flowers."""
    S = 3
    L, B = int(length * S), int(b * S)
    im = Image.new("RGBA", (L, B), bg + (255,))
    d = ImageDraw.Draw(im)
    P = B * 1.25
    x = P / 2
    while x < L + P:
        cy = B / 2
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            px, py = x + math.cos(a) * B * 0.17, cy + math.sin(a) * B * 0.17
            r = B * 0.13
            d.ellipse([px - r, py - r, px + r, py + r], fill=petal + (255,))
        r = B * 0.08
        d.ellipse([x - r, cy - r, x + r, cy + r], fill=centre + (255,))
        lx = x + P / 2
        d.ellipse([lx - B * 0.12, cy - B * 0.05, lx + B * 0.12, cy + B * 0.05], fill=leaf + (255,))
        x += P
    d.rectangle([0, 0, L, int(B * 0.08)], fill=(250, 245, 230, 255))
    d.rectangle([0, int(B * 0.92), L, B], fill=(250, 245, 230, 255))
    return im.resize((max(1, int(length)), max(1, int(b))), Image.LANCZOS)


def kilim_strip(length, b, bg=(110, 22, 26), c1=(236, 222, 190), c2=(30, 24, 22), c3=(214, 130, 40)):
    S = 3
    L, B = int(length * S), int(b * S)
    im = Image.new("RGBA", (L, B), bg + (255,))
    d = ImageDraw.Draw(im)
    P = B * 1.2
    x = 0
    while x < L + P:
        cy = B / 2
        d.polygon([(x, cy), (x + P / 2, cy - B * 0.36), (x + P, cy), (x + P / 2, cy + B * 0.36)], fill=c1 + (255,))
        d.polygon([(x + P * 0.22, cy), (x + P / 2, cy - B * 0.2), (x + P * 0.78, cy), (x + P / 2, cy + B * 0.2)], fill=c2 + (255,))
        d.polygon([(x + P * 0.38, cy), (x + P / 2, cy - B * 0.08), (x + P * 0.62, cy), (x + P / 2, cy + B * 0.08)], fill=c3 + (255,))
        x += P
    d.rectangle([0, 0, L, int(B * 0.08)], fill=c1 + (255,))
    d.rectangle([0, int(B * 0.92), L, B], fill=c1 + (255,))
    return im.resize((max(1, int(length)), max(1, int(b))), Image.LANCZOS)


def border(cv, box, b, strip_fn, corner=None):
    """Lay a strip pattern (outer edge = top of the strip) around a box."""
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    b = int(round(b))
    w, h = x1 - x0, y1 - y0
    top = strip_fn(w, b)
    cv.paste_rgba(top, (x0, y0))
    cv.paste_rgba(strip_fn(w, b).rotate(180), (x0, y1 - b))
    side = strip_fn(h, b)
    cv.paste_rgba(side.rotate(90, expand=True), (x0, y0))
    cv.paste_rgba(strip_fn(h, b).rotate(-90, expand=True), (x1 - b, y0))
    if corner is not None:
        for cx, cy in ((x0, y0), (x1 - b, y0), (x0, y1 - b), (x1 - b, y1 - b)):
            cv.paste_rgba(corner(b), (cx, cy))


def vine_corner(b):
    S = 3
    B = int(b * S)
    im = Image.new("RGBA", (B, B), (226, 190, 70, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, B, int(B * 0.13)], fill=(24, 96, 70, 255))
    d.rectangle([0, 0, int(B * 0.13), B], fill=(24, 96, 70, 255))
    d.rectangle([0, B - int(B * 0.13), B, B], fill=(24, 96, 70, 255))
    d.rectangle([B - int(B * 0.13), 0, B, B], fill=(24, 96, 70, 255))
    r = B * 0.16
    d.ellipse([B / 2 - r, B / 2 - r, B / 2 + r, B / 2 + r], fill=(214, 84, 34, 255))
    return im.resize((b, b), Image.LANCZOS)


# =============================================================================== shared sign bodies
INK_NAVY = (0.10, 0.14, 0.33)
INK_BLACK = (0.07, 0.07, 0.08)
GLAZE = (0.93, 0.925, 0.89)


def mortar_rim(cv, rim_px):
    """cement bed around a set-in plaque: grey, irregular outer edge"""
    inner = cv.m_rect((rim_px, rim_px, cv.W - rim_px, cv.H - rim_px))
    n = cv.noise(12, 4)
    e = cv.edge_dist() * cv.ppm
    alpha = smooth(0.0, rim_px * 0.6, e + (n - 0.5) * rim_px * 0.9)
    mort = np.stack([0.64 + 0.1 * n, 0.62 + 0.1 * n, 0.57 + 0.1 * n], -1)
    cv.fill_rgb(mort, 1 - inner)
    cv.a = np.maximum(alpha, inner)


def tile_grid(cv, box, nx, ny, var=0.035, grout=(0.78, 0.76, 0.70), grout_m=0.0025, dirt=0.5):
    x0, y0, x1, y1 = box
    tw, th = (x1 - x0) / nx, (y1 - y0) / ny
    tone = np.ones((cv.H, cv.W), np.float32)
    tint = np.zeros((cv.H, cv.W, 3), np.float32)
    ids = []
    for j in range(ny):
        for i in range(nx):
            m = cv.m_rect((x0 + i * tw, y0 + j * th, x0 + (i + 1) * tw, y0 + (j + 1) * th))
            tone += m * cv.rng.normal(0, var)
            tint += m[..., None] * cv.rng.normal(0, var * 0.4, 3).astype(np.float32)
    ripple = cv.noise(9, 3)
    cv.rgb = cv.rgb * (tone * (0.985 + 0.03 * ripple))[..., None] + tint
    g = max(1, cv.p(grout_m))
    lines = np.zeros((cv.H, cv.W), np.float32)
    for i in range(1, nx):
        x = x0 + i * tw
        lines = np.maximum(lines, cv.m_rect((x - g / 2, y0, x + g / 2, y1)))
    for j in range(1, ny):
        y = y0 + j * th
        lines = np.maximum(lines, cv.m_rect((x0, y - g / 2, x1, y + g / 2)))
    soft = np.clip(blur(lines, g * 0.8) * 1.8, 0, 1)
    cv.fill((0.45, 0.40, 0.33), soft, 0.35 * dirt)
    cv.fill(grout, lines, 0.9)
    cv.fill((0.35, 0.30, 0.24), lines * cv.noise(8, 3), 0.6 * dirt)
    return tw, th


def tile_chips(cv, box, nx, ny, n, body=(0.80, 0.66, 0.50)):
    x0, y0, x1, y1 = box
    tw, th = (x1 - x0) / nx, (y1 - y0) / ny
    im, d = cv.layer()
    for _ in range(n):
        i, j = cv.rng.integers(0, nx + 1), cv.rng.integers(0, ny + 1)
        cx, cy = x0 + i * tw + cv.rng.normal(0, tw * 0.08), y0 + j * th + cv.rng.normal(0, th * 0.08)
        r = cv.p(0.006) * (0.5 + cv.rng.random())
        pts = [(cx + r * (0.5 + 0.7 * cv.rng.random()) * math.cos(a), cy + r * (0.5 + 0.7 * cv.rng.random()) * math.sin(a))
               for a in np.linspace(0, 2 * math.pi, 8, endpoint=False)]
        d.polygon(pts, fill=255)
    m = cv.arr(im)
    cv.fill(body, m)
    cv.fill((0.30, 0.25, 0.20), np.clip(dilate(m, 1) - m, 0, 1), 0.6)
    cv.fill((0.35, 0.28, 0.22), m * cv.noise(20, 2), 0.5)


def metal_rim(cv, w_m=0.012, color=None, dark=0.75):
    """folded edge of a sheet-metal sign"""
    w = cv.p(w_m)
    fm = cv.frame_mask((0, 0, cv.W, cv.H), w)
    if color is None:
        cv.rgb = cv.rgb * (1 - fm[..., None] * (1 - dark))
    else:
        cv.fill(color, fm)
    hl = cv.frame_mask((w * 0.9, w * 0.9, cv.W - w * 0.9, cv.H - w * 0.9), max(1, w * 0.25))
    cv.fill((1, 1, 1), hl, 0.12)


def wood(cv, base=(0.55, 0.42, 0.28), planks=1, vertical=False):
    n1 = fbm(cv.rng, cv.H, cv.W, 6, 4, sx=0.12 if not vertical else 4, sy=4 if not vertical else 0.12)
    rings = np.sin((n1 * 40 + (cv.v if not vertical else cv.u) * 6) * math.pi)
    g = 0.88 + 0.12 * rings * 0.5 + 0.08 * (n1 - 0.5)
    cv.rgb = col(base) * g[..., None]
    if planks > 1:
        for k in range(1, planks):
            y = k * cv.H / planks
            m = cv.m_rect((0, y - cv.p(0.003), cv.W, y + cv.p(0.003)))
            cv.fill((0.15, 0.11, 0.08), m, 0.8)


# =============================================================================== SHOP SIGNS
def three_block(cv, he, ar, en, sub, fonts, colors, split=(0.21, 0.79), en_box=(0.14, 0.66), sub_box=(0.70, 0.86),
                margin=0.035, rule=None, en_kw=None, side_kw=None):
    """Common shop layout: Arabic block left, big English in the middle (+ small line), Hebrew block right."""
    W, H = cv.W, cv.H
    fe, fs, fh, fa = fonts
    ce, cs, ch, ca = colors
    m = margin
    en_kw = en_kw or {}
    side_kw = side_kw or {}
    if en:
        cv.text(en, fe, cv.bx(split[0] + 0.02, en_box[0], split[1] - 0.02, en_box[1]), ce, **en_kw)
    if sub:
        cv.text(sub, fs, cv.bx(split[0] + 0.03, sub_box[0], split[1] - 0.03, sub_box[1]), cs,
                **{k: v for k, v in en_kw.items() if k in ("wobble", "cover", "shadow")})
    if ar:
        cv.text(ar, fa, cv.bx(m, 0.2, split[0] - 0.02, 0.8), ca, **side_kw)
    if he:
        cv.text(he, fh, cv.bx(split[1] + 0.02, 0.2, 1 - m, 0.8), ch, **side_kw)
    if rule:
        rc, rw = rule
        for x in split:
            cv.fill(rc, cv.m_rect((x * W - cv.p(rw) / 2, 0.16 * H, x * W + cv.p(rw) / 2, 0.84 * H)))


def stack(cv, lines, key, box, color, gap=0.1, **kw):
    """lines stacked in a box, all at the same text height"""
    x0, y0, x1, y1 = box
    n = len(lines)
    h = (y1 - y0) / n
    probes = [text_img(ln, key, 160) for ln in lines]
    s = min(min(h * (1 - gap) / p.height, (x1 - x0) / p.width) for p in probes)
    for i, ln in enumerate(lines):
        cv.text(ln, key, (x0, y0 + i * h, x1, y0 + (i + 1) * h), color, max_h=probes[i].height * s, **kw)


def sign_souvenirs(cv):
    red, cream = (0.60, 0.15, 0.11), (0.94, 0.88, 0.72)
    cv.fill(red)
    cv.grain(0.025)
    inset = cv.p(0.035)
    cv.fill(cream, cv.frame_mask((inset, inset, cv.W - inset, cv.H - inset), cv.p(0.012), cv.p(0.02)))
    sh = (cv.p(0.008), cv.p(0.008), cv.p(0.004), (0.18, 0.04, 0.03), 0.8)
    three_block(cv, "מזכרות", None, "SOUVENIRS", "GIFTS  ·  ROSARIES  ·  POSTCARDS  ·  OLIVE WOOD",
                ("gothic", "sans_b", "he_sans_blk", "ar_kufi_b"), (cream, (0.98, 0.80, 0.30), cream, cream),
                split=(0.22, 0.78), en_box=(0.13, 0.64), sub_box=(0.70, 0.84),
                rule=(cream, 0.008), en_kw=dict(tracking=0.06, shadow=sh), side_kw=dict(shadow=sh))
    stack(cv, ["هدايا", "تذكارية"], "ar_kufi_b", cv.bx(0.04, 0.14, 0.20, 0.86), cream, shadow=sh)
    cv.screws([(0.01, 0.5), (0.99, 0.5)], rust=0.8)
    metal_rim(cv)
    cv.fade(0.38)
    cv.rust(0.35)
    cv.chips(0.25, under=(0.40, 0.36, 0.33))
    cv.scratches(25)
    cv.streaks(0.35, length=0.9)
    cv.grime(0.35)
    cv.dust(0.15)


def sign_exchange(cv):
    """after the black 'authorized best money changer ATM' boards on the square (photo 141)"""
    black, yellow, white = (0.05, 0.05, 0.06), (0.98, 0.80, 0.08), (0.95, 0.95, 0.93)
    cv.fill(black)
    cv.grain(0.015)
    W, H = cv.W, cv.H
    # ATM block on the left
    atm = cv.bx(0.03, 0.14, 0.22, 0.86)
    cv.fill(white, cv.frame_mask(atm, cv.p(0.012), cv.p(0.04)))
    cv.text("ATM", "sans_blk", (atm[0] + cv.p(0.04), atm[1] + cv.p(0.07), atm[2] - cv.p(0.04), atm[3] - cv.p(0.13)), white)
    cv.text("24 HOURS", "sans_b", (atm[0] + cv.p(0.05), atm[3] - cv.p(0.12), atm[2] - cv.p(0.05), atm[3] - cv.p(0.04)), yellow)
    cv.text("AUTHORIZED", "sans_b", cv.bx(0.26, 0.10, 0.74, 0.27), white, tracking=0.25)
    cv.text("MONEY CHANGER", "narrow_b", cv.bx(0.25, 0.30, 0.75, 0.70), yellow)
    cv.text("$   €   £   ₪   ¥", "sans_b", cv.bx(0.30, 0.74, 0.70, 0.90), white)
    cv.text("חלפן כספים", "he_sans_b", cv.bx(0.77, 0.12, 0.97, 0.48), white)
    cv.text("صرافة", "ar_kufi_b", cv.bx(0.79, 0.52, 0.95, 0.90), yellow)
    metal_rim(cv, 0.016, color=(0.62, 0.62, 0.63))
    cv.dust(0.22, (0.62, 0.58, 0.52))
    cv.fade(0.12)
    cv.scratches(60, (0.7, 0.7, 0.7), 0.2, 0.3)
    cv.streaks(0.25, (0.55, 0.50, 0.42), length=0.6)
    cv.grime(0.2, (0.30, 0.27, 0.22))


def sign_ceramics(cv):
    cv.fill(GLAZE)
    W, H = cv.W, cv.H
    b = cv.p(0.05)
    blue, turq = (0.08, 0.20, 0.55), (0.05, 0.48, 0.50)
    border(cv, (0, 0, W, H), b, flower_strip)
    cv.text("ARMENIAN CERAMICS", "serif_b", (W * 0.22, b + cv.p(0.03), W * 0.78, H * 0.62), blue, tracking=0.04)
    cv.text("HAND PAINTED POTTERY  ·  TILES  ·  PLATES", "serif_b", (W * 0.24, H * 0.66, W * 0.76, H - b - cv.p(0.035)), turq)
    for x in (0.2, 0.8):
        cv.fill(blue, cv.m_rect((W * x - cv.p(0.004), b + cv.p(0.03), W * x + cv.p(0.004), H - b - cv.p(0.03))))
    stack(cv, ["خزف", "أرمني"], "ar_naskh_b", (b + cv.p(0.04), b + cv.p(0.0), W * 0.2 - cv.p(0.04), H - b - cv.p(0.0)), blue)
    stack(cv, ["קרמיקה", "ארמנית"], "he_serif_b", (W * 0.8 + cv.p(0.045), b + cv.p(0.02), W - b - cv.p(0.045), H - b - cv.p(0.02)), blue)
    nx, ny = 13, 3
    tile_grid(cv, (0, 0, W, H), nx, ny, var=0.02)
    cv.crazing(0.45)
    tile_chips(cv, (0, 0, W, H), nx, ny, 10)
    cv.streaks(0.25, (0.45, 0.38, 0.28), length=0.7)
    cv.grime(0.2, (0.35, 0.30, 0.22))
    cv.dust(0.12)


def gilt(cv, mask, base=(0.80, 0.63, 0.28)):
    n = cv.noise(10, 4)
    band = 0.5 + 0.5 * np.sin((cv.u * 2.0 + cv.v * 1.3) * math.pi * 2)
    g = col(base)[None, None, :] * (0.78 + 0.25 * band[..., None] + 0.15 * (n[..., None] - 0.5))
    cv.fill_rgb(g, mask)


def sign_jewelry(cv):
    W, H = cv.W, cv.H
    wood(cv, (0.07, 0.06, 0.055))
    cv.grain(0.02)
    gold = (0.82, 0.64, 0.28)
    f1 = cv.frame_mask((cv.p(0.03), cv.p(0.03), W - cv.p(0.03), H - cv.p(0.03)), cv.p(0.008))
    f2 = cv.frame_mask((cv.p(0.05), cv.p(0.05), W - cv.p(0.05), H - cv.p(0.05)), cv.p(0.003))
    gilt(cv, np.maximum(f1, f2))
    m, _ = cv.text_mask("JEWELRY", "disp_b", cv.bx(0.24, 0.15, 0.76, 0.66), tracking=0.18)
    gilt(cv, m)
    m2, _ = cv.text_mask("GOLD  ·  SILVER  ·  PRECIOUS STONES", "disp_b", cv.bx(0.25, 0.70, 0.75, 0.84))
    gilt(cv, m2)
    m3, _ = cv.text_mask("مجوهرات", "ar_naskh_b", cv.bx(0.05, 0.18, 0.20, 0.82))
    m4, _ = cv.text_mask("תכשיטים", "he_serif_b", cv.bx(0.80, 0.25, 0.95, 0.75))
    gilt(cv, m3)
    gilt(cv, m4)
    for x in (0.225, 0.775):
        cx, cy, r = x * W, H / 2, cv.p(0.018)
        gilt(cv, cv.m_poly([(cx, cy - r), (cx + r * 0.6, cy), (cx, cy + r), (cx - r * 0.6, cy)]))
    cv.bevel(np.maximum.reduce([m, m2, m3, m4]), 0.25)
    cv.fade(0.22)
    cv.crazing(0.25, scale=10, color=(0.3, 0.28, 0.25))
    cv.peel(0.25, (0.48, 0.38, 0.26), edge_m=0.05)
    cv.dust(0.25, (0.62, 0.57, 0.50))
    cv.streaks(0.2, (0.45, 0.42, 0.36), length=0.5)
    cv.grime(0.15, (0.35, 0.3, 0.25))


def sign_books(cv):
    W, H = cv.W, cv.H
    wood(cv, (0.50, 0.44, 0.36), planks=2)
    under = cv.rgb.copy()
    green, cream = (0.09, 0.28, 0.19), (0.93, 0.88, 0.74)
    grain = fbm(cv.rng, H, W, 6, 4, sx=0.12, sy=4)
    cv.fill(green, op=1.0)
    cv.rgb *= (0.92 + 0.12 * grain)[..., None]
    cv.fill(cream, cv.frame_mask((cv.p(0.03), cv.p(0.03), W - cv.p(0.03), H - cv.p(0.03)), cv.p(0.01)))
    cv.text("BOOKSHOP", "century_b", cv.bx(0.23, 0.14, 0.77, 0.64), cream, tracking=0.08, wobble=0.25, cover=0.15)
    cv.text("BOOKS  ·  MAPS  ·  GUIDES  ·  POSTCARDS", "century_b", cv.bx(0.25, 0.69, 0.75, 0.84), (0.90, 0.78, 0.45),
            wobble=0.2, cover=0.2)
    cv.text("مكتبة", "ar_naskh_b", cv.bx(0.05, 0.16, 0.20, 0.84), cream, wobble=0.25, cover=0.15)
    cv.text("חנות ספרים", "he_serif_b", cv.bx(0.79, 0.22, 0.95, 0.78), cream, wobble=0.25, cover=0.15)
    cv.peel(0.55, under, edge_m=0.07, scale=14)
    cv.fade(0.3)
    cv.streaks(0.3, length=0.8)
    cv.grime(0.35)
    cv.dust(0.15)


def cup_icon(cv, cx, cy, s, color):
    m = cv.m_poly([(cx - s * 0.45, cy - s * 0.25), (cx + s * 0.45, cy - s * 0.25), (cx + s * 0.32, cy + s * 0.35),
                   (cx - s * 0.32, cy + s * 0.35)])
    m = np.maximum(m, cv.frame_mask((cx + s * 0.30, cy - s * 0.15, cx + s * 0.62, cy + s * 0.17), s * 0.07, s * 0.15))
    m = np.maximum(m, cv.m_rect((cx - s * 0.6, cy + s * 0.38, cx + s * 0.6, cy + s * 0.46), s * 0.04))
    for k in (-0.2, 0.05, 0.3):
        pts = [(cx + k * s + 0.06 * s * math.sin(t * 6), cy - s * 0.35 - t * s * 0.4) for t in np.linspace(0, 1, 12)]
        m = np.maximum(m, cv.m_line(pts, s * 0.05))
    cv.fill(color, m)


def sign_cafe(cv):
    W, H = cv.W, cv.H
    ivory, brown, terra = (0.91, 0.85, 0.69), (0.30, 0.17, 0.09), (0.66, 0.26, 0.12)
    cv.fill(brown)
    body = cv.m_rect((cv.p(0.03), cv.p(0.03), W - cv.p(0.03), H - cv.p(0.03)), cv.p(0.06))
    cv.fill(ivory, body)
    cv.grain(0.02)
    cv.fill(brown, cv.frame_mask((cv.p(0.05), cv.p(0.05), W - cv.p(0.05), H - cv.p(0.05)), cv.p(0.006), cv.p(0.045)))
    cv.text("Café", "chancery", cv.bx(0.30, 0.06, 0.66, 0.66), brown)
    cup_icon(cv, W * 0.26, H * 0.38, H * 0.42, terra)
    cv.text("COFFEE  ·  TEA  ·  FRESH JUICE", "sans_b", cv.bx(0.24, 0.70, 0.76, 0.84), terra, tracking=0.08)
    cv.text("مقهى", "ar_naskh_b", cv.bx(0.05, 0.18, 0.18, 0.82), brown)
    cv.text("בית קפה", "he_sans_b", cv.bx(0.78, 0.26, 0.95, 0.74), brown)
    cv.screws([(0.015, 0.5), (0.985, 0.5)], rust=1.0)
    cv.fade(0.3)
    cv.rust(0.25)
    cv.chips(0.15, under=(0.35, 0.3, 0.27))
    cv.streaks(0.4, length=0.9)
    cv.grime(0.4)
    cv.dust(0.12)


def sign_spices(cv):
    W, H = cv.W, cv.H
    ochre, brown = (0.86, 0.56, 0.16), (0.40, 0.11, 0.05)
    cv.fill(ochre)
    cv.grain(0.03, 2)
    cv.text("SPICES & HERBS", "bookman", cv.bx(0.22, 0.10, 0.78, 0.62), brown, wobble=0.35, cover=0.25)
    cv.text("ZA'ATAR  ·  SAFFRON  ·  TEA  ·  NUTS", "bookman", cv.bx(0.25, 0.68, 0.75, 0.85), (0.15, 0.30, 0.12),
            wobble=0.3, cover=0.25)
    stack(cv, ["بهارات", "وأعشاب"], "ar_kufi_b", cv.bx(0.035, 0.10, 0.20, 0.90), brown, wobble=0.35, cover=0.25)
    cv.text("תבלינים", "he_sans_blk", cv.bx(0.80, 0.25, 0.97, 0.75), brown, wobble=0.35, cover=0.25)
    metal_rim(cv, 0.01)
    cv.screws([(0.012, 0.18), (0.012, 0.82), (0.988, 0.18), (0.988, 0.82)], rust=1.0)
    cv.fade(0.42)
    cv.rust(0.55, edge_m=0.08)
    cv.scratches(30)
    cv.streaks(0.45, length=1.0)
    cv.grime(0.4)


def greek_cross(cv, cx, cy, s, mask_only=False):
    a = s * 0.18
    m = np.maximum(cv.m_rect((cx - a, cy - s / 2, cx + a, cy + s / 2)), cv.m_rect((cx - s / 2, cy - a, cx + s / 2, cy + a)))
    for dx, dy in ((0, -1), (0, 1), (-1, 0), (1, 0)):
        r = a * 1.25
        m = np.maximum(m, cv.m_ellipse((cx + dx * s / 2 - r, cy + dy * s / 2 - r, cx + dx * s / 2 + r, cy + dy * s / 2 + r)))
    return m


def sign_icons(cv):
    W, H = cv.W, cv.H
    blue = (0.10, 0.17, 0.42)
    cv.fill(blue)
    cv.grain(0.015)
    fr = cv.frame_mask((cv.p(0.025), cv.p(0.025), W - cv.p(0.025), H - cv.p(0.025)), cv.p(0.009))
    gilt(cv, fr)
    m1, _ = cv.text_mask("ICONS", "serif_b", cv.bx(0.34, 0.10, 0.66, 0.58), tracking=0.25)
    m2, _ = cv.text_mask("ΕΙΚΟΝΕΣ  ·  ИКОНЫ", "serif_b", cv.bx(0.30, 0.62, 0.70, 0.75))
    m3, _ = cv.text_mask("CROSSES  ·  INCENSE  ·  CANDLES", "sans_b", cv.bx(0.28, 0.79, 0.72, 0.89), tracking=0.06)
    m4, _ = cv.text_mask("أيقونات", "ar_naskh_b", cv.bx(0.04, 0.18, 0.205, 0.82))
    m5, _ = cv.text_mask("איקונין", "he_serif_b", cv.bx(0.795, 0.25, 0.96, 0.75))
    for x in (0.215, 0.785):
        gilt(cv, cv.m_rect((W * x - cv.p(0.003), H * 0.15, W * x + cv.p(0.003), H * 0.85)))
    c1 = greek_cross(cv, W * 0.268, H * 0.36, H * 0.26)
    c2 = greek_cross(cv, W * 0.732, H * 0.36, H * 0.26)
    for m in (m1, m2, m4, m5, c1, c2):
        gilt(cv, m)
    cv.fill((0.88, 0.86, 0.80), m3)
    cv.fade(0.2)
    cv.chips(0.35)
    cv.screws([(0.01, 0.5), (0.99, 0.5)])
    cv.streaks(0.25, length=0.7)
    cv.grime(0.25)
    cv.dust(0.1)


def sign_photo(cv):
    W, H = cv.W, cv.H
    yellow, red, black = (0.97, 0.79, 0.10), (0.80, 0.11, 0.08), (0.08, 0.07, 0.07)
    cv.fill(yellow)
    cv.fill(red, cv.m_rect((0, 0, W * 0.40, H)))
    cv.fill(yellow, cv.m_rect((W * 0.40, 0, W * 0.415, H)))
    cv.text("PHOTO", "sans_blk_i", cv.bx(0.04, 0.16, 0.37, 0.84), yellow)
    cv.text("FILM  ·  CAMERAS  ·  PASSPORT PHOTOS", "sans_b", cv.bx(0.45, 0.10, 0.96, 0.36), black)
    cv.fill(black, cv.m_rect((W * 0.45, H * 0.43, W * 0.96, H * 0.45)))
    cv.text("צילום", "he_sans_blk", cv.bx(0.72, 0.52, 0.95, 0.90), red)
    cv.text("تصوير", "ar_kufi_blk", cv.bx(0.46, 0.50, 0.68, 0.90), red)
    metal_rim(cv, 0.01, color=(0.75, 0.74, 0.72))
    cv.fade(0.55, top_bias=0.5)
    cv.crazing(0.3, scale=6, color=(0.5, 0.45, 0.35))
    cv.chips(0.2, under=(0.85, 0.83, 0.78))
    cv.streaks(0.35, length=0.9)
    cv.grime(0.35)


def star_of_david(cv, cx, cy, r, w):
    tri = lambda a0: [(cx + r * math.cos(a0 + k * 2 * math.pi / 3), cy + r * math.sin(a0 + k * 2 * math.pi / 3)) for k in range(3)]
    m = np.zeros((cv.H, cv.W), np.float32)
    for a0 in (-math.pi / 2, math.pi / 2):
        pts = tri(a0)
        m = np.maximum(m, cv.m_line(pts + [pts[0]], w))
    return m


def sign_judaica(cv):
    W, H = cv.W, cv.H
    blue, white, light = (0.07, 0.20, 0.50), (0.96, 0.96, 0.95), (0.70, 0.80, 0.95)
    cv.fill(blue)
    cv.grain(0.012)
    cv.fill(white, cv.frame_mask((cv.p(0.025), cv.p(0.025), W - cv.p(0.025), H - cv.p(0.025)), cv.p(0.006)))
    m1, _ = cv.text("JUDAICA", "serif_b", cv.bx(0.06, 0.10, 0.44, 0.64), white, tracking=0.12)
    m2, _ = cv.text("יודאיקה", "he_serif_blk", cv.bx(0.56, 0.10, 0.94, 0.64), white)
    sd = star_of_david(cv, W * 0.5, H * 0.38, H * 0.2, cv.p(0.012))
    gilt(cv, sd, (0.78, 0.78, 0.80))
    cv.fill(white, cv.m_rect((W * 0.06, H * 0.69, W * 0.94, H * 0.70)))
    cv.text("TALLITOT  ·  KIPOT  ·  MEZUZOT  ·  MENORAHS", "sans_b", cv.bx(0.06, 0.74, 0.47, 0.88), light, tracking=0.05)
    cv.text("טליתות  ·  כיפות  ·  מזוזות  ·  חנוכיות", "alef_b", cv.bx(0.53, 0.73, 0.94, 0.89), light)
    cv.bevel(np.maximum(m1, m2), 0.2)
    cv.dust(0.15, (0.6, 0.58, 0.55))
    cv.fade(0.1)
    cv.streaks(0.15, (0.35, 0.33, 0.30), length=0.5)
    cv.grime(0.12)


def sign_bakery(cv):
    W, H = cv.W, cv.H
    wood(cv, (0.55, 0.45, 0.33), planks=3)
    under = cv.rgb.copy()
    cv.fill((0.89, 0.87, 0.81))
    cv.rgb *= (0.94 + 0.08 * fbm(cv.rng, H, W, 6, 4, sx=0.1, sy=4))[..., None]
    for k in (1, 2):
        cv.fill((0.45, 0.42, 0.36), cv.m_rect((0, k * H / 3 - cv.p(0.003), W, k * H / 3 + cv.p(0.003))), 0.8)
    green, red = (0.10, 0.42, 0.22), (0.70, 0.14, 0.10)
    cv.text("مخبز", "ar_naskh_b", cv.bx(0.04, 0.06, 0.30, 0.90), green, wobble=0.35, cover=0.3)
    cv.text("BAKERY", "bookman", cv.bx(0.33, 0.12, 0.67, 0.60), red, wobble=0.3, cover=0.3)
    cv.text("KA'AK  ·  PITA  ·  SWEETS", "bookman", cv.bx(0.34, 0.68, 0.66, 0.84), (0.12, 0.10, 0.08), wobble=0.3, cover=0.3)
    cv.text("מאפייה", "he_sans_blk", cv.bx(0.71, 0.18, 0.96, 0.80), green, wobble=0.35, cover=0.3)
    cv.peel(0.5, under, edge_m=0.06, scale=12)
    cv.streaks(0.4, length=0.9)
    cv.grime(0.45)
    cv.dust(0.1)


def sign_textiles(cv):
    W, H = cv.W, cv.H
    red, cream, ochre = (0.44, 0.08, 0.10), (0.94, 0.88, 0.74), (0.88, 0.64, 0.26)
    cv.fill(red)
    cv.grain(0.02)
    b = cv.p(0.06)
    border(cv, (0, 0, W, H), b, kilim_strip)
    cv.text("ORIENTAL TEXTILES", "roman_b", (W * 0.235, b + cv.p(0.03), W * 0.765, H * 0.62), cream, tracking=0.06)
    cv.text("CARPETS  ·  EMBROIDERY  ·  KEFFIYEH", "roman_b", (W * 0.25, H * 0.66, W * 0.75, H - b - cv.p(0.03)), ochre)
    stack(cv, ["أقمشة", "وسجاد"], "ar_naskh_b", (b + cv.p(0.03), b + cv.p(0.01), W * 0.195, H - b - cv.p(0.01)), cream)
    stack(cv, ["טקסטיל", "ושטיחים"], "he_serif_b", (W * 0.805, b + cv.p(0.02), W - b - cv.p(0.03), H - b - cv.p(0.02)), cream)
    for x in (0.215, 0.785):
        cv.fill(ochre, cv.m_rect((W * x - cv.p(0.003), b + cv.p(0.04), W * x + cv.p(0.003), H - b - cv.p(0.04))))
    cv.fade(0.35)
    cv.chips(0.15, under=(0.3, 0.27, 0.24))
    cv.screws([(0.01, 0.5), (0.99, 0.5)])
    cv.streaks(0.3, length=0.8)
    cv.grime(0.3)
    cv.dust(0.12)


def sign_atm_changer(cv):
    """vertical ATM / MONEY CHANGER board at the New Petra entrance (photo_ref square_north/013)"""
    W, H = cv.W, cv.H
    white, black, red = (0.95, 0.94, 0.91), (0.08, 0.08, 0.08), (0.88, 0.30, 0.18)
    cv.fill(white)
    cv.grain(0.012)
    cv.text("A.T.M", "helv_b", cv.bx(0.18, 0.025, 0.82, 0.085), black, tracking=0.1)
    cv.text("MACHINE", "helv_b", cv.bx(0.33, 0.09, 0.67, 0.115), black)
    for x0, x1 in ((0.06, 0.28), (0.72, 0.94)):
        bar = cv.m_rect(cv.bx(x0, 0.14, x1, 0.86), cv.p(0.06))
        cv.fill(black, bar)
        for k, ch in enumerate("ATM"):
            cv.text(ch, "helv_b", cv.bx(x0 + 0.03, 0.17 + k * 0.19, x1 - 0.03, 0.33 + k * 0.19), white)
        cv.text("MACHINE", "narrow_b", cv.bx(x0 + 0.02, 0.77, x1 - 0.02, 0.81), white)
    letters = "MONEY" + "CHANGER"
    y = 0.15
    step = 0.70 / len(letters)
    for i, ch in enumerate(letters):
        cv.text(ch, "narrow_b", cv.bx(0.36, y + i * step + (0.012 if i >= 5 else 0), 0.64, y + (i + 1) * step - 0.006),
                red, outline=((0.35, 0.08, 0.05), cv.p(0.003)))
    arr = cv.m_poly([(W * 0.12, H * 0.92), (W * 0.22, H * 0.895), (W * 0.22, H * 0.912), (W * 0.88, H * 0.912),
                     (W * 0.88, H * 0.928), (W * 0.22, H * 0.928), (W * 0.22, H * 0.945)])
    cv.fill(red, arr)
    metal_rim(cv, 0.015, color=(0.80, 0.80, 0.80))
    cv.fade(0.2)
    cv.scratches(30, (0.5, 0.5, 0.5), 0.3, 0.3)
    cv.streaks(0.3, length=0.6)
    cv.grime(0.3)
    cv.dust(0.1)


# =============================================================================== STREET PLAQUES
def karakashian(cv, he, ar, en, nx, ink, he_font="he_serif_b", wear=1.0, rust_stain=False, ar_sx=1.0):
    """Old City street-name tiles: 15 cm glazed tiles, Hebrew strip (added after 1967) above the
    Arabic + English panel, each framed by the green-leaf trim (photos: David St., Suq el-Bazaar Rd.,
    Omar Ibn el-Khattab Sq.)."""
    W, H = cv.W, cv.H
    rim = cv.p(0.012)
    cv.fill(GLAZE)
    x0, y0, x1, y1 = rim, rim, W - rim, H - rim
    th = (y1 - y0) / 3
    b = cv.p(0.022)
    top = (x0, y0, x1, y0 + th)
    low = (x0, y0 + th, x1, y1)
    border(cv, top, b, vine_strip, vine_corner)
    border(cv, low, b, vine_strip, vine_corner)
    pad = cv.p(0.012)
    cv.text(he, he_font, (top[0] + b + pad * 2, top[1] + b + pad, top[2] - b - pad * 2, top[3] - b - pad), ink,
            wobble=0.12, cover=0.06)
    r2 = (low[0] + b + pad * 2, low[1] + b + pad * 0.5, low[2] - b - pad * 2, low[1] + th - pad * 0.2)
    r3 = (low[0] + b + pad * 2, low[1] + th + pad * 0.6, low[2] - b - pad * 2, low[3] - b - pad * 0.8)
    cv.text(ar, "ar_naskh_b", r2, ink, wobble=0.12, cover=0.07, sx=ar_sx)
    cv.text(en, "narrow_b", r3, ink, tracking=0.07, wobble=0.08, cover=0.1)
    tile_grid(cv, (x0, y0, x1, y1), nx, 3, var=0.02, dirt=0.6 * wear)
    cv.crazing(0.35 * wear)
    tile_chips(cv, (x0, y0, x1, y1), nx, 3, int(3 + 4 * wear))
    if rust_stain:
        m = np.zeros((H, W), np.float32)
        x = W * (0.3 + 0.4 * cv.rng.random())
        m = cv.m_ellipse((x - cv.p(0.004), y0 + th * 1.9, x + cv.p(0.004), y0 + th * 1.95))
        cv.runs_from(m, 0.7, (0.55, 0.28, 0.12), 0.08)
    cv.streaks(0.25 * wear, (0.40, 0.36, 0.30), length=0.9, density=0.6)
    cv.grime(0.22 * wear, (0.36, 0.32, 0.26))
    cv.dust(0.10 * wear)
    mortar_rim(cv, rim)


def plaque_omar(cv):
    karakashian(cv, "ככר עמר אבן כֿטאב", "ميدان عمر بن الخطاب", "OMAR IBN EL-KHATTAB SQ.", 5, INK_BLACK, rust_stain=True)


def plaque_david(cv):
    karakashian(cv, "רחוב דוד", "طريق سويقة علون", "DAVID ST.", 3, INK_NAVY, he_font="he_sans_blk", wear=1.4, ar_sx=0.72)


def plaque_bazaar(cv):
    karakashian(cv, "רְחוֹב דָּוִד", "طريق البازار", "SUQ EL-BAZAAR RD.", 4, INK_BLACK, wear=1.3)


def plaque_latin(cv):
    karakashian(cv, "רחוב הפטריארכיה הלטינית", "طريق البطريركية اللاتينية", "LATIN PATRIARCHATE RD.", 5, INK_NAVY)


def plaque_armenian(cv):
    karakashian(cv, "רחוב הפטריארכיה הארמנית", "طريق البطريركية الأرمنية", "ARMENIAN PATRIARCHATE RD.", 5, INK_BLACK, wear=0.8)


def plaque_greek(cv):
    karakashian(cv, "רחוב הפטריארכיה היוונית-קתולית", "طريق بطريركية الروم الكاثوليك", "GREEK CATHOLIC PATRIARCHATE ST.",
                6, INK_NAVY, wear=1.1)


def plaque_christian(cv):
    karakashian(cv, "רחוב הנוצרים", "طريق حارة النصارى", "CHRISTIAN QUARTER RD.", 5, INK_NAVY, wear=1.2, rust_stain=True)


def sign_jaffa_gate(cv):
    """the 3x3 tile name sign on the gate's east face: green braid trim, lobed white cartouche,
    English / Arabic / Hebrew in black (photos 090, 105, gate/g43)."""
    W, H = cv.W, cv.H
    rim = cv.p(0.01)
    green = (0.09, 0.28, 0.20)
    cv.fill(green)
    x0, y0, x1, y1 = rim, rim, W - rim, H - rim
    b = cv.p(0.042)
    border(cv, (x0, y0, x1, y1), b, braid_strip)
    ix0, iy0, ix1, iy1 = x0 + b, y0 + b, x1 - b, y1 - b
    iw, ih = ix1 - ix0, iy1 - iy0
    cart = cv.m_rect((ix0 + iw * 0.12, iy0 + ih * 0.05, ix1 - iw * 0.12, iy1 - ih * 0.05), iw * 0.05)
    for k in range(3):
        cy = iy0 + ih * (k + 0.5) / 3
        rx, ry = iw * 0.12, ih * 0.15
        for cx in (ix0 + iw * 0.13, ix1 - iw * 0.13):
            cart = np.maximum(cart, cv.m_ellipse((cx - rx, cy - ry, cx + rx, cy + ry)))
    cv.fill(GLAZE, cart)
    rows = [(iy0 + ih * 0.06, iy0 + ih * 0.33), (iy0 + ih * 0.36, iy0 + ih * 0.66), (iy0 + ih * 0.69, iy0 + ih * 0.94)]
    cv.text("JAFFA GATE", "century_b", (ix0 + iw * 0.07, rows[0][0], ix1 - iw * 0.07, rows[0][1]), INK_BLACK, wobble=0.1)
    cv.text("باب الخليل", "ar_naskh_b", (ix0 + iw * 0.06, rows[1][0], ix1 - iw * 0.06, rows[1][1]), INK_BLACK, wobble=0.1)
    cv.text("שער יפו", "he_serif_blk", (ix0 + iw * 0.2, rows[2][0] + ih * 0.03, ix1 - iw * 0.2, rows[2][1] - ih * 0.02),
            INK_BLACK, wobble=0.1)
    tile_grid(cv, (x0, y0, x1, y1), 3, 3, var=0.025, grout=(0.70, 0.66, 0.58), dirt=0.9)
    cv.crazing(0.5)
    # glaze losses showing the plaster bed (the real tile is badly damaged; kept legible here)
    n = cv.noise(7, 5)
    loss = smooth(0.70, 0.73, n * 0.8 + (1 - smooth(0, 0.05, cv.edge_dist())) * 0.25 + 0.05 * cv.noise(30, 2))
    plaster = np.stack([0.76 + 0.08 * n, 0.68 + 0.08 * n, 0.55 + 0.06 * n], -1)
    cv.fill((0.35, 0.28, 0.2), np.clip(dilate(loss, 2) - loss, 0, 1), 0.7)
    cv.fill_rgb(plaster, loss)
    tile_chips(cv, (x0, y0, x1, y1), 3, 3, 8, body=(0.78, 0.70, 0.56))
    cv.streaks(0.35, (0.38, 0.32, 0.25), length=0.9)
    cv.grime(0.3, (0.34, 0.29, 0.22))
    mortar_rim(cv, rim)


def plaque_jaffa_gate_info(cv):
    """black heritage plaque under the street tiles (gate/g43, photo 090): teal rule, three titles,
    three columns of text. English text as on the plaque; Hebrew/Arabic columns are faithful
    translations of it."""
    W, H = cv.W, cv.H
    cv.fill((0.10, 0.11, 0.12))
    cv.grain(0.01)
    teal, white = (0.10, 0.62, 0.60), (0.95, 0.95, 0.94)
    cv.fill(teal, cv.m_rect((0, 0, W, cv.p(0.012))))
    cv.text("שער יפו", "he_sans_b", (W * 0.45, H * 0.06, W * 0.95, H * 0.13), white, align="r")
    cv.text("باب الخليل", "ar_sans_b", (W * 0.45, H * 0.14, W * 0.95, H * 0.22), white, align="r")
    cv.text("Jaffa Gate", "sans_b", (W * 0.45, H * 0.23, W * 0.95, H * 0.30), white, align="r")
    en = ("One of the most beautiful and important gates within the Ottoman City walls, dating from the 16th "
          "century. The Gate led to Jaffa and to Hebron, and hence the origin of its name (in Arabic: Bab "
          "al-Khalil - Hebron Gate).")
    he = ("אחד השערים היפים והחשובים בחומות העיר העות׳מאניות, מן המאה ה-16. השער הוביל ליפו ולחברון, ומכאן "
          "שמו (בערבית: באב אל-ח׳ליל – שער חברון).")
    ar = ("من أجمل وأهم الأبواب في سور المدينة العثماني، ويعود إلى القرن السادس عشر. كان الباب يؤدي إلى يافا "
          "والخليل، ومن هنا جاء اسمه: باب الخليل.")
    colw = W * 0.28
    px = cv.p(0.0128)
    for text, key, x, align in ((en, "sans", W * 0.05, "l"), (ar, "ar_sans", W * 0.36, "r"), (he, "alef", W * 0.67, "r")):
        lines = wrap_words(text, key, px, colw)
        y = H * 0.36
        for ln in lines:
            img = text_img(ln, key, px)
            m = Image.new("L", (W, H), 0)
            xx = x if align == "l" else x + colw - img.width
            m.paste(img, (int(xx), int(y)))
            cv.fill(white, cv.arr(m), 0.92)
            y += px * 1.5
    cv.fill(teal, cv.m_rect((W * 0.85, H * 0.93, W * 0.95, H * 0.95)))
    metal_rim(cv, 0.004, color=(0.2, 0.21, 0.22))
    cv.dust(0.18, (0.55, 0.52, 0.46))
    cv.scratches(20, (0.6, 0.6, 0.6), 0.25, 0.1)
    cv.streaks(0.15, (0.5, 0.46, 0.4), length=0.6)


# =============================================================================== CUTOUT LETTERS
def cutout(cv, lines, key, color, tracking=0.0, sx=1.0, shadow=0.35, bevel=0.35, runs=0.2, fade=0.0,
           line_boxes=None, dust=0.25, rust=0.0):
    """Individual metal letters on a transparent background, with a contact shadow and dirt runs
    (semi-transparent) baked under them."""
    W, H = cv.W, cv.H
    m = np.zeros((H, W), np.float32)
    n = len(lines)
    for i, ln in enumerate(lines):
        box = line_boxes[i] if line_boxes else (W * 0.01, H * (0.04 + i / n * 0.92), W * 0.99, H * (0.04 + (i + 1) / n * 0.92 - 0.03))
        mm, _ = cv.text_mask(ln, key, box, tracking=tracking, sx=sx)
        m = np.maximum(m, mm)
    cv.fill(color)
    cv.grain(0.03, 1.5)
    if fade:
        cv.fade(fade, 0)
    if rust:
        cv.fill((0.45, 0.25, 0.12), smooth(0.6, 0.8, cv.noise(20, 4)) * rust)
    top_dust = np.clip(m - shift(m, 0, cv.p(0.006)), 0, 1)
    cv.fill((0.78, 0.72, 0.62), top_dust * dust)
    cv.bevel(m, bevel)
    sh = blur(shift(m, cv.p(0.004), cv.p(0.008)), cv.p(0.006)) * shadow
    if runs:
        drips = smooth(0.55, 0.85, vnoise(cv.rng, H, W, 3, max(4, W / cv.p(0.008))))
        run = cv.runs_from(m, 0.0, length_m=0.10) * runs * (0.25 + 0.75 * drips)
    else:
        run = np.zeros_like(m)
    under = np.clip(np.maximum(sh, run * (0.5 + 0.5 * cv.noise(8, 3))) * (1 - m), 0, 1)
    dark = np.broadcast_to(col((0.08, 0.07, 0.06)), cv.rgb.shape)
    cv.rgb = cv.rgb * m[..., None] + dark * (1 - m[..., None])
    cv.a = np.clip(m + under, 0, 1)
    return m


def sign_imperial_letters(cv):
    """'IMPERIAL HOTEL' dark metal Roman capitals on the stone band (photos 019, 039, square_north/035)"""
    cutout(cv, ["IMPERIAL HOTEL"], "roman_b", (0.17, 0.17, 0.18), tracking=0.14,
           line_boxes=[(cv.W * 0.01, cv.H * 0.12, cv.W * 0.99, cv.H * 0.84)], runs=0.25)


def sign_christian_info(cv):
    """maroon serif letters on the former Austrian post office (photos 145, citadel_east/B07)"""
    W, H = cv.W, cv.H
    boxes = [(W * 0.13, H * 0.03, W * 0.87, H * 0.30), (W * 0.01, H * 0.36, W * 0.99, H * 0.63),
             (W * 0.25, H * 0.69, W * 0.75, H * 0.96)]
    cutout(cv, ["CHRISTIAN", "INFORMATION", "CENTRE"], "roman_b", (0.56, 0.11, 0.10), tracking=0.04,
           line_boxes=boxes, fade=0.18, runs=0.3)


def sign_swedish_roof(cv):
    """free-standing dark letters along the roof-terrace railing (citadel_east/B01)"""
    cutout(cv, ["SWEDISH CHRISTIAN STUDY CENTRE"], "narrow_b", (0.16, 0.16, 0.17), tracking=0.12,
           line_boxes=[(cv.W * 0.005, cv.H * 0.04, cv.W * 0.995, cv.H * 0.96)], shadow=0.0, runs=0.0, bevel=0.3, rust=0.15)


def sign_swedish_facade(cv):
    """'SWEDISH CHRISTIAN CENTER' black letters on the smooth parapet panel facing the square (photo 144)"""
    cutout(cv, ["SWEDISH CHRISTIAN CENTER"], "century_b", (0.10, 0.10, 0.10), tracking=0.03,
           line_boxes=[(cv.W * 0.01, cv.H * 0.12, cv.W * 0.99, cv.H * 0.82)], shadow=0.45, runs=0.25)


def sign_versavee(cv):
    """'VERSAVEE' (bar-café in the Imperial Hotel arcade) dark capitals (photos 019, 039)"""
    cutout(cv, ["VERSAVEE"], "roman_b", (0.14, 0.13, 0.12), tracking=0.18,
           line_boxes=[(cv.W * 0.02, cv.H * 0.12, cv.W * 0.98, cv.H * 0.84)], runs=0.2)


def sign_welcome(cv):
    """'WELCOME TO THE OLD CITY' white letters on the dark balcony fascia (square_north/030)"""
    W, H = cv.W, cv.H
    cv.fill((0.21, 0.22, 0.23))
    cv.grain(0.03, 2)
    under = cv.rgb.copy()
    m, _ = cv.text_mask("WELCOME TO THE OLD CITY", "century_b", (W * 0.015, H * 0.2, W * 0.985, H * 0.8), sx=1.25,
                        tracking=0.08)
    cv.fill((0.93, 0.92, 0.88), m * (1 - 0.35 * smooth(0.5, 0.8, cv.noise(30, 3))))
    cv.peel(0.3, under, edge_m=0.04)
    cv.fill((0.70, 0.68, 0.64), cv.m_rect((0, 0, W, cv.p(0.01))), 0.5)
    cv.rust(0.4, edge_m=0.05)
    cv.streaks(0.35, (0.45, 0.38, 0.30), length=1.0)
    cv.grime(0.3)
    cv.dust(0.2)


# =============================================================================== NAMED PANELS
def sign_new_imperial(cv):
    W, H = cv.W, cv.H
    cream, green = (0.92, 0.88, 0.76), (0.10, 0.29, 0.22)
    cv.fill(green)
    cv.fill(cream, cv.m_rect((cv.p(0.025), cv.p(0.025), W - cv.p(0.025), H - cv.p(0.025)), cv.p(0.02)))
    cv.grain(0.015)
    cv.fill(green, cv.frame_mask((cv.p(0.045), cv.p(0.045), W - cv.p(0.045), H - cv.p(0.045)), cv.p(0.004), cv.p(0.012)))
    cv.text("NEW IMPERIAL HOTEL", "roman_b", cv.bx(0.06, 0.13, 0.94, 0.56), green, tracking=0.08)
    cv.fill(green, cv.m_rect(cv.bx(0.30, 0.615, 0.70, 0.625)))
    cx, cy, r = W * 0.5, H * 0.78, cv.p(0.016)
    cv.fill(green, cv.m_poly([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]))
    cv.text("מלון ניו אימפריאל", "he_serif_b", cv.bx(0.54, 0.68, 0.93, 0.88), green)
    cv.text("فندق نيو إمبريال", "ar_naskh_b", cv.bx(0.07, 0.66, 0.46, 0.90), green)
    cv.screws([(0.012, 0.15), (0.988, 0.15), (0.012, 0.85), (0.988, 0.85)], r_m=0.005)
    cv.fade(0.2)
    cv.chips(0.1, under=(0.3, 0.27, 0.25))
    cv.streaks(0.25, length=0.8)
    cv.grime(0.25)
    cv.dust(0.1)


def petra_vignette(cv, box):
    """small oval picture of Petra's rock-cut Treasury on the guest-house lightbox"""
    x0, y0, x1, y1 = box
    ov = cv.m_ellipse(box)
    w, h = x1 - x0, y1 - y0
    n = cv.noise(12, 4)
    rock = np.stack([0.78 + 0.12 * n, 0.50 + 0.1 * n, 0.40 + 0.08 * n], -1)
    cv.fill_rgb(rock, ov)
    fac = cv.m_rect((x0 + w * 0.3, y0 + h * 0.18, x1 - w * 0.3, y1 - h * 0.1))
    cv.fill((0.88, 0.62, 0.50), fac * ov)
    for k in range(4):
        cx = x0 + w * (0.34 + k * 0.105)
        cv.fill((0.45, 0.25, 0.20), cv.m_rect((cx, y0 + h * 0.5, cx + w * 0.025, y1 - h * 0.12)) * ov)
    cv.fill((0.45, 0.25, 0.20), cv.m_poly([(x0 + w * 0.32, y0 + h * 0.48), (x0 + w * 0.5, y0 + h * 0.33),
                                           (x1 - w * 0.32, y0 + h * 0.48)]) * ov, 0.8)
    cv.fill((0.30, 0.18, 0.15), cv.m_rect((x0 + w * 0.47, y0 + h * 0.66, x0 + w * 0.53, y1 - h * 0.1)) * ov)
    ring = np.clip(ov - erode(ov, max(1, int(cv.p(0.003)))), 0, 1)
    cv.fill((0.25, 0.2, 0.18), ring)


def sign_petra(cv):
    """'New PETRA Guest House' lightbox over the hotel door on David St. (square_north/013)"""
    W, H = cv.W, cv.H
    white, red, black = (0.95, 0.94, 0.91), (0.86, 0.12, 0.14), (0.10, 0.10, 0.10)
    cv.fill((0.20, 0.20, 0.21))
    face = cv.m_rect((cv.p(0.03), cv.p(0.03), W - cv.p(0.03), H - cv.p(0.03)))
    cv.fill(white, face)
    cv.grain(0.012)
    cv.text("NICE VIEW", "narrow_b", cv.bx(0.06, 0.12, 0.27, 0.28), red)
    cv.text("OLD CITY", "narrow_b", cv.bx(0.74, 0.12, 0.94, 0.28), red)
    petra_vignette(cv, cv.bx(0.10, 0.32, 0.23, 0.62))
    petra_vignette(cv, cv.bx(0.77, 0.32, 0.90, 0.62))
    cv.text("New", "sans_blk_i", cv.bx(0.42, 0.06, 0.58, 0.36), black)
    cv.text("Guest", "helv_b", cv.bx(0.06, 0.64, 0.26, 0.92), black)
    cv.text("House", "helv_b", cv.bx(0.74, 0.64, 0.94, 0.92), black)
    cv.text("PETRA", "narrow_b", cv.bx(0.31, 0.38, 0.69, 0.95), red, sx=1.05, outline=(black, cv.p(0.004)))
    cv.fill((0.55, 0.55, 0.56), cv.frame_mask((0, 0, W, H), cv.p(0.008)), 0.6)
    cv.fade(0.25)
    cv.streaks(0.3, (0.35, 0.3, 0.25), length=0.7)
    cv.grime(0.35, bottom=0.2)
    cv.dust(0.2)
    cv.scratches(15, (0.4, 0.4, 0.4), 0.25, 0.2)


def i_disc(cv, cx, cy, r, disc=(0.95, 0.95, 0.94), ink=(0.10, 0.12, 0.15)):
    d = cv.m_ellipse((cx - r, cy - r, cx + r, cy + r))
    cv.fill(disc, d)
    m, _ = cv.text_mask("i", "serif_blk", (cx - r * 0.5, cy - r * 0.72, cx + r * 0.5, cy + r * 0.66))
    cv.fill(ink, m)


def sign_tourist_info(cv):
    """Ministry of Tourism information office (design plausible; Jerusalem wayfinding palette)"""
    W, H = cv.W, cv.H
    dark, teal, white = (0.12, 0.15, 0.20), (0.05, 0.60, 0.58), (0.96, 0.96, 0.95)
    cv.fill(dark)
    cv.grain(0.012)
    cv.fill(teal, cv.m_rect((0, 0, W, H * 0.09)))
    cv.fill(teal, cv.m_rect((0, H - H * 0.04, W, H)))
    i_disc(cv, H * 0.52, H * 0.54, H * 0.32)
    x0 = H * 0.98
    cv.text("מידע לתיירים", "he_sans_b", (x0, H * 0.16, W * 0.96, H * 0.40), white, align="r")
    cv.text("معلومات سياحية", "ar_sans_b", (x0, H * 0.42, W * 0.96, H * 0.66), white, align="r")
    cv.text("Tourist Information", "sans_b", (x0, H * 0.68, W * 0.96, H * 0.90), white, align="r")
    metal_rim(cv, 0.008, color=(0.55, 0.56, 0.58))
    cv.dust(0.15, (0.6, 0.57, 0.5))
    cv.streaks(0.18, (0.45, 0.42, 0.36), length=0.6)
    cv.grime(0.12)


def sign_tower_of_david(cv):
    """vertical black totem at the citadel entrance: blue corner, text running bottom-to-top
    (citadel_east/A22): Hebrew / Arabic / English, small logo plate, red base band."""
    W, H = cv.W, cv.H
    black, blue, white, red = (0.08, 0.08, 0.09), (0.12, 0.30, 0.62), (0.95, 0.95, 0.94), (0.62, 0.10, 0.10)
    cv.fill(black)
    cv.grain(0.012)
    cv.fill(blue, cv.m_poly([(W * 0.45, 0), (W, 0), (W, H * 0.16)]))
    cv.fill(red, cv.m_rect((0, H * 0.94, W, H)))
    # lay the three lines out on a rotated canvas (length = H), then rotate 90 deg CCW
    L, S = H, W
    tmp = Image.new("L", (int(L), int(S)), 0)
    lines = [("מוזיאון מגדל דוד", "he_sans_b", 0.08, 0.34), ("متحف قلعة داود", "ar_sans_b", 0.38, 0.64),
             ("Tower of David Museum", "sans_b", 0.68, 0.92)]
    for text, key, a, b in lines:
        img = fit_text(text, key, L * 0.56, S * (b - a))
        tmp.paste(img, (int(L * 0.82 - img.width), int(S * a + (S * (b - a) - img.height) / 2)))
    rot = np.asarray(tmp.transpose(Image.ROTATE_90), np.float32) / 255.0
    cv.fill(white, rot[:H, :W])
    lg = cv.bx(0.10, 0.80, 0.34, 0.89)
    cv.fill((0.88, 0.88, 0.86), cv.m_rect(lg))
    cx, cy = (lg[0] + lg[2]) / 2, (lg[1] + lg[3]) / 2
    tw_, th_ = (lg[2] - lg[0]) * 0.32, (lg[3] - lg[1]) * 0.36
    tower = cv.m_rect((cx - tw_ / 2, cy - th_, cx + tw_ / 2, cy + th_ * 0.7))
    for k in range(3):
        mx = cx - tw_ / 2 + k * tw_ * 0.4
        tower = np.maximum(tower, cv.m_rect((mx, cy - th_ * 1.25, mx + tw_ * 0.2, cy - th_)))
    tower = np.maximum(tower, cv.m_rect((cx - tw_ * 1.2, cy + th_ * 0.2, cx + tw_ * 1.2, cy + th_ * 0.7)))
    cv.fill((0.32, 0.33, 0.36), tower)
    metal_rim(cv, 0.006, color=(0.22, 0.22, 0.24))
    cv.dust(0.2, (0.6, 0.57, 0.5))
    cv.scratches(25, (0.6, 0.6, 0.6), 0.2, 0.2)
    cv.streaks(0.2, (0.5, 0.46, 0.4), length=0.5)


def sign_ramparts_walk(cv):
    """hanging violet-blue sign at the Ramparts Walk ticket office next to the gate (gate/g40, g52)"""
    W, H = cv.W, cv.H
    blue, white = (0.24, 0.20, 0.55), (0.96, 0.96, 0.96)
    cv.fill((0.22, 0.22, 0.23))
    cv.fill(blue, cv.m_rect((cv.p(0.015), cv.p(0.015), W - cv.p(0.015), H - cv.p(0.015))))
    cv.grain(0.012)
    cv.text("טיילת", "he_sans_b", cv.bx(0.15, 0.08, 0.85, 0.27), white)
    cv.text("החומות", "he_sans_b", cv.bx(0.15, 0.30, 0.85, 0.49), white)
    cv.text("The Ramparts Walk", "narrow_b", cv.bx(0.08, 0.54, 0.92, 0.70), white)
    cv.text("متنزه الأسوار", "ar_sans_b", cv.bx(0.10, 0.73, 0.90, 0.92), white)
    cv.fade(0.12)
    cv.dust(0.12, (0.62, 0.58, 0.52))
    cv.streaks(0.18, (0.4, 0.38, 0.34), length=0.6)
    cv.grime(0.12)


def arrow_mask(cv, cx, cy, s, ang_deg, w=0.16):
    a = math.radians(ang_deg)
    ca, sa = math.cos(a), math.sin(a)
    pts = [(-0.5, -w / 2), (0.1, -w / 2), (0.1, -0.32), (0.5, 0), (0.1, 0.32), (0.1, w / 2), (-0.5, w / 2)]
    return cv.m_poly([(cx + (x * ca - y * sa) * s, cy + (x * sa + y * ca) * s) for x, y in pts])


def pictos(cv, cx, cy, r, kind, disc=(0.86, 0.86, 0.84), ink=(0.12, 0.12, 0.13)):
    d = cv.m_ellipse((cx - r, cy - r, cx + r, cy + r))
    cv.fill(disc, d)
    cv.fill(ink, np.clip(d - erode(d, max(1, int(r * 0.08))), 0, 1))
    if kind == "i":
        m, _ = cv.text_mask("i", "serif_blk", (cx - r * 0.4, cy - r * 0.6, cx + r * 0.4, cy + r * 0.6))
        cv.fill(ink, m)
    elif kind == "wc":
        for dx in (-0.32, 0.32):
            x = cx + dx * r
            cv.fill(ink, cv.m_ellipse((x - r * 0.1, cy - r * 0.55, x + r * 0.1, cy - r * 0.35)))
            if dx < 0:
                cv.fill(ink, cv.m_rect((x - r * 0.13, cy - r * 0.3, x + r * 0.13, cy + r * 0.55)))
            else:
                cv.fill(ink, cv.m_poly([(x, cy - r * 0.3), (x + r * 0.2, cy + r * 0.25), (x - r * 0.2, cy + r * 0.25)]))
                cv.fill(ink, cv.m_rect((x - r * 0.08, cy + r * 0.2, x + r * 0.08, cy + r * 0.55)))
        cv.fill(ink, cv.m_rect((cx - r * 0.02, cy - r * 0.55, cx + r * 0.02, cy + r * 0.55)))
    elif kind == "police":
        cv.fill(ink, cv.m_ellipse((cx - r * 0.25, cy - r * 0.25, cx + r * 0.25, cy + r * 0.2)))
        cv.fill(ink, cv.m_poly([(cx - r * 0.42, cy - r * 0.28), (cx + r * 0.42, cy - r * 0.28), (cx + r * 0.3, cy - r * 0.55),
                                (cx - r * 0.3, cy - r * 0.55)]))
        cv.fill(ink, cv.m_poly([(cx - r * 0.5, cy + r * 0.62), (cx - r * 0.38, cy + r * 0.28), (cx + r * 0.38, cy + r * 0.28),
                                (cx + r * 0.5, cy + r * 0.62)]))


def wayfinding_jaffa(cv):
    """top of the dark municipal wayfinding totem on the square (photo 098): teal cap, three rows
    with arrows, pictogram discs."""
    W, H = cv.W, cv.H
    dark, teal, white, grey = (0.17, 0.18, 0.19), (0.12, 0.60, 0.55), (0.95, 0.95, 0.94), (0.75, 0.80, 0.80)
    cv.fill(dark)
    cv.grain(0.02, 2)
    cv.fill(teal, cv.m_rect((W * 0.04, 0, W * 0.96, H * 0.04), cv.p(0.01)))
    rows = [(0.06, 0.37), (0.37, 0.68), (0.68, 0.98)]
    for y0, y1 in rows[1:]:
        cv.fill(teal, cv.m_rect((W * 0.02, H * y0 - cv.p(0.002), W * 0.98, H * y0 + cv.p(0.002))), 0.8)
    texts = [("שער יפו", "باب الخليل", "Jaffa Gate", -90), ("השער החדש", "الباب الجديد", "New Gate", 0)]
    for (he, ar, en, ang), (y0, y1) in zip(texts, rows):
        h = (y1 - y0) * H
        cv.text(he, "he_sans_b", (W * 0.3, H * y0 + h * 0.12, W * 0.74, H * y0 + h * 0.36), white, align="r")
        cv.text(ar, "ar_sans_b", (W * 0.3, H * y0 + h * 0.38, W * 0.74, H * y0 + h * 0.64), white, align="r")
        cv.text(en, "sans_b", (W * 0.3, H * y0 + h * 0.66, W * 0.74, H * y0 + h * 0.88), white, align="r")
        cv.fill(grey, arrow_mask(cv, W * 0.86, H * y0 + h * 0.4, h * 0.42, ang, 0.12))
    y0, y1 = rows[2]
    h = (y1 - y0) * H
    for k, kind in enumerate(("wc", "police", "i")):
        pictos(cv, W * (0.36 + k * 0.15), H * y0 + h * 0.4, h * 0.22, kind)
    cv.fill(grey, arrow_mask(cv, W * 0.86, H * y0 + h * 0.4, h * 0.42, 0, 0.12))
    cv.dust(0.25, (0.6, 0.57, 0.5))
    cv.streaks(0.4, (0.75, 0.73, 0.68), length=0.9, density=0.3)
    cv.scratches(40, (0.65, 0.65, 0.63), 0.3, 0.15)
    cv.grime(0.15)


# =============================================================================== TOURIST POINTERS
def pointer(cv, he, ar, en, color, right=True, icon=None, wear=1.0):
    """Ministry-of-Tourism style pointer: enamelled plate with a pointed end, white keyline,
    Hebrew / Arabic / English in white."""
    W, H = cv.W, cv.H
    tip = H * 0.42
    if right:
        pts = [(0, 0), (W - tip, 0), (W, H / 2), (W - tip, H), (0, H)]
    else:
        pts = [(tip, 0), (W, 0), (W, H), (tip, H), (0, H / 2)]
    shape = cv.m_poly(pts)
    cv.fill(color)
    cv.grain(0.015)
    k = cv.p(0.018)
    kw = cv.p(0.006)
    if right:
        inner = [(k, k), (W - tip - k * 0.4, k), (W - k * 1.35, H / 2), (W - tip - k * 0.4, H - k), (k, H - k)]
    else:
        inner = [(tip + k * 0.4, k), (W - k, k), (W - k, H - k), (tip + k * 0.4, H - k), (k * 1.35, H / 2)]
    key = np.clip(cv.m_poly(inner) - erode(cv.m_poly(inner), max(1, int(kw))), 0, 1)
    white = (0.96, 0.96, 0.94)
    cv.fill(white, key)
    tx0, tx1 = (k * 2.8, W - tip - k * 0.6) if right else (tip + k * 0.6, W - k * 2.8)
    if icon == "P":
        s = H - 2 * k - cv.p(0.03)
        ix0 = tx0 if right else tx1 - s
        ib = (ix0, (H - s) / 2, ix0 + s, (H + s) / 2)
        cv.fill(white, cv.m_rect(ib, s * 0.1))
        cv.fill((0.10, 0.30, 0.65), cv.m_rect((ib[0] + s * 0.06, ib[1] + s * 0.06, ib[2] - s * 0.06, ib[3] - s * 0.06), s * 0.07))
        cv.text("P", "helv_b", (ib[0] + s * 0.2, ib[1] + s * 0.16, ib[2] - s * 0.2, ib[3] - s * 0.16), white)
        if right:
            tx0 = ib[2] + cv.p(0.03)
        else:
            tx1 = ib[0] - cv.p(0.03)
    al = "l" if right else "r"
    rows = [(0.13, 0.38), (0.39, 0.64), (0.66, 0.87)]
    cv.text(he, "he_sans_b", (tx0, H * rows[0][0], tx1, H * rows[0][1]), white, align=al, max_h=H * 0.2)
    cv.text(ar, "ar_sans_b", (tx0, H * rows[1][0], tx1, H * rows[1][1]), white, align=al, max_h=H * 0.24)
    cv.text(en, "sans_b", (tx0, H * rows[2][0], tx1, H * rows[2][1]), white, align=al, max_h=H * 0.19)
    rx = (W - tip * 0.6) / W if right else (tip * 0.6) / W
    cv.screws([(0.025 if right else 0.975, 0.5), (rx, 0.5)], r_m=0.005, rust=0.5 * wear)
    cv.fade(0.25 * wear)
    cv.chips(0.2 * wear, under=(0.20, 0.19, 0.18))
    cv.streaks(0.25 * wear, length=0.7)
    cv.grime(0.2 * wear)
    cv.dust(0.12)
    cv.a = shape


MAROON = (0.40, 0.15, 0.11)
DKGREEN = (0.07, 0.29, 0.20)


def dir_holy_sepulchre(cv):
    pointer(cv, "כנסיית הקבר", "كنيسة القيامة", "Church of the Holy Sepulchre", MAROON, right=True)


def dir_western_wall(cv):
    pointer(cv, "הכותל המערבי", "الحائط الغربي", "Western Wall", MAROON, right=False, wear=1.2)


def dir_armenian_quarter(cv):
    pointer(cv, "הרובע הארמני", "حارة الأرمن", "Armenian Quarter", DKGREEN, right=False)


def dir_christian_quarter(cv):
    pointer(cv, "הרובע הנוצרי", "حارة النصارى", "Christian Quarter", DKGREEN, right=True, wear=1.3)


def dir_jaffa_gate_parking(cv):
    pointer(cv, "חניון שער יפו", "موقف سيارات باب الخليل", "Jaffa Gate Parking", MAROON, right=True, icon="P", wear=0.8)


# =============================================================================== MISC
def house_number(cv):
    W, H = cv.W, cv.H
    rim = cv.p(0.006)
    cv.fill(GLAZE)
    blue = (0.10, 0.22, 0.55)
    cv.fill(blue, cv.frame_mask((rim + cv.p(0.008), rim + cv.p(0.008), W - rim - cv.p(0.008), H - rim - cv.p(0.008)),
                                cv.p(0.005), cv.p(0.01)))
    cv.fill(blue, cv.frame_mask((rim + cv.p(0.016), rim + cv.p(0.016), W - rim - cv.p(0.016), H - rim - cv.p(0.016)),
                                cv.p(0.0018), cv.p(0.006)))
    for cx, cy in ((0.18, 0.22), (0.82, 0.22), (0.18, 0.78), (0.82, 0.78)):
        x, y, r = cx * W, cy * H, cv.p(0.006)
        cv.fill((0.05, 0.50, 0.50), cv.m_ellipse((x - r, y - r, x + r, y + r)))
    cv.text("23", "serif_b", cv.bx(0.26, 0.20, 0.74, 0.80), blue, wobble=0.3, cover=0.1)
    cv.crazing(0.4, scale=8)
    cv.streaks(0.2, (0.4, 0.36, 0.3), length=0.8)
    cv.grime(0.2, (0.36, 0.32, 0.26))
    mortar_rim(cv, rim)


def round_sign(cv, draw_face, wear=1.0):
    W, H = cv.W, cv.H
    disc = cv.m_ellipse((cv.p(0.004), cv.p(0.004), W - cv.p(0.004), H - cv.p(0.004)))
    cv.fill((0.70, 0.71, 0.72))
    draw_face(cv)
    rimm = np.clip(disc - erode(disc, max(1, int(cv.p(0.008)))), 0, 1)
    cv.fill((0.82, 0.83, 0.84), rimm)
    cv.grain(0.012)
    cv.fade(0.2 * wear, top_bias=0)
    cv.streaks(0.2 * wear, (0.35, 0.32, 0.28), length=0.6)
    cv.grime(0.15 * wear)
    cv.dust(0.12)
    cv.scratches(int(10 * wear), (0.9, 0.9, 0.9), 0.25, 0.08)
    cv.a = disc


def no_entry_vehicles(cv):
    """Israeli sign 401: closed to all vehicles (white disc, red ring)"""
    def face(c):
        W, H = c.W, c.H
        c.fill((0.80, 0.10, 0.10), c.m_ellipse((0, 0, W, H)))
        r = W * 0.5 * 0.76
        c.fill((0.96, 0.96, 0.95), c.m_ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r)))
    round_sign(cv, face)


def no_entry(cv):
    """Israeli sign 402: no entry (red disc, white bar)"""
    def face(c):
        W, H = c.W, c.H
        c.fill((0.80, 0.10, 0.10), c.m_ellipse((0, 0, W, H)))
        c.fill((0.96, 0.96, 0.95), c.m_rect((W * 0.18, H * 0.41, W * 0.82, H * 0.59)))
    round_sign(cv, face, 1.2)


def no_parking(cv):
    """no parking (blue disc, red ring and bar) as on the square (square_north/036)"""
    def face(c):
        W, H = c.W, c.H
        c.fill((0.80, 0.12, 0.12), c.m_ellipse((0, 0, W, H)))
        r = W * 0.5 * 0.78
        inner = c.m_ellipse((W / 2 - r, H / 2 - r, W / 2 + r, H / 2 + r))
        c.fill((0.10, 0.32, 0.70), inner)
        a = math.radians(45)
        bw = W * 0.075
        dx, dy = math.cos(a) * r, math.sin(a) * r
        bar = c.m_poly([(W / 2 - dx - bw * dy / r, H / 2 - dy + bw * dx / r), (W / 2 - dx + bw * dy / r, H / 2 - dy - bw * dx / r),
                        (W / 2 + dx + bw * dy / r, H / 2 + dy - bw * dx / r), (W / 2 + dx - bw * dy / r, H / 2 + dy + bw * dx / r)])
        c.fill((0.80, 0.12, 0.12), bar * inner)
    round_sign(cv, face, 1.3)


def plate_boarding(cv):
    """yellow supplementary plate under the no-parking sign (square_north/036)"""
    W, H = cv.W, cv.H
    yellow, black = (0.97, 0.80, 0.12), (0.08, 0.08, 0.08)
    cv.fill(black)
    cv.fill(yellow, cv.m_rect((cv.p(0.012), cv.p(0.012), W - cv.p(0.012), H - cv.p(0.012)), cv.p(0.012)))
    cv.text("מותרת העלאת", "he_sans_b", cv.bx(0.10, 0.04, 0.92, 0.135), black, align="r")
    cv.text("והורדת נוסעים בלבד", "he_sans_b", cv.bx(0.06, 0.145, 0.94, 0.245), black, align="r")
    cv.text("يسمح بتحميل وتنزيل", "ar_sans_b", cv.bx(0.10, 0.26, 0.92, 0.37), black, align="r")
    cv.text("الركاب فقط", "ar_sans_b", cv.bx(0.30, 0.375, 0.92, 0.47), black, align="r")
    cv.text("Boarding and", "sans_m", cv.bx(0.08, 0.50, 0.92, 0.61), black)
    cv.text("alighting only", "sans_m", cv.bx(0.08, 0.62, 0.92, 0.73), black)
    cv.fill(black, cv.m_rect(cv.bx(0.03, 0.765, 0.97, 0.775)))
    th = text_img("עד 07:00 למחרת", "alef_b", 160)
    mh = min(cv.H * 0.075, cv.W * 0.86 * th.height / th.width)
    cv.text("מ- 11:00", "alef_b", cv.bx(0.06, 0.785, 0.94, 0.875), black, align="r", max_h=mh)
    cv.text("עד 07:00 למחרת", "alef_b", cv.bx(0.06, 0.88, 0.94, 0.97), black, align="r", max_h=mh)
    cv.grain(0.012)
    cv.fade(0.2)
    cv.streaks(0.2, length=0.6)
    cv.grime(0.15)
    cv.dust(0.1)


def sign_police(cv):
    """small enamel 'Police' plate (design plausible)"""
    W, H = cv.W, cv.H
    blue, white = (0.06, 0.15, 0.38), (0.96, 0.96, 0.95)
    cv.fill(blue)
    cv.grain(0.012)
    cv.fill(white, cv.frame_mask((cv.p(0.012), cv.p(0.012), W - cv.p(0.012), H - cv.p(0.012)), cv.p(0.005), cv.p(0.015)))
    cx, cy, r = W * 0.21, H * 0.5, H * 0.25
    ring = cv.m_ellipse((cx - r, cy - r, cx + r, cy + r))
    cv.fill(white, np.clip(ring - erode(ring, max(1, int(cv.p(0.005)))), 0, 1))
    cv.fill(white, star_of_david(cv, cx, cy, r * 0.66, cv.p(0.006)))
    cv.text("משטרה", "he_sans_blk", cv.bx(0.40, 0.12, 0.92, 0.42), white)
    cv.text("شرطة", "ar_kufi_b", cv.bx(0.46, 0.43, 0.86, 0.68), white)
    cv.text("POLICE", "sans_blk", cv.bx(0.42, 0.70, 0.90, 0.88), white, tracking=0.15)
    cv.screws([(0.06, 0.5), (0.94, 0.5)], r_m=0.004, rust=0.4)
    cv.fade(0.15)
    cv.chips(0.15)
    cv.streaks(0.2, length=0.6)
    cv.grime(0.15)


# =============================================================================== registry
# name: (fn, w_m, h_m, kind, ppm, verified, note)
SIGNS = {
    # ---- shops (generic; the money changer follows the black boards on the square)
    "sign_souvenirs": (sign_souvenirs, 2.6, 0.60, "shop", 300, False, "painted steel, faded red"),
    "sign_exchange": (sign_exchange, 2.4, 0.60, "shop", 300, True, "style of the black money-changer boards (photo 141)"),
    "sign_ceramics": (sign_ceramics, 2.6, 0.60, "shop", 300, False, "glazed tile panel, cobalt letters"),
    "sign_jewelry": (sign_jewelry, 2.2, 0.50, "shop", 300, False, "black lacquer, gilt letters"),
    "sign_books": (sign_books, 2.4, 0.55, "shop", 300, False, "painted wood board, peeling"),
    "sign_cafe": (sign_cafe, 2.5, 0.60, "shop", 300, False, "enamel, rounded"),
    "sign_spices": (sign_spices, 2.4, 0.60, "shop", 300, False, "hand-painted sheet metal"),
    "sign_icons": (sign_icons, 2.4, 0.55, "shop", 300, False, "blue enamel, gilt"),
    "sign_photo": (sign_photo, 2.2, 0.55, "shop", 300, False, "1970s enamel, sun-bleached"),
    "sign_judaica": (sign_judaica, 2.4, 0.60, "shop", 300, False, "aluminium composite"),
    "sign_bakery": (sign_bakery, 2.0, 0.55, "shop", 300, False, "hand-painted whitewashed planks"),
    "sign_textiles": (sign_textiles, 2.6, 0.60, "shop", 300, False, "burgundy with kilim border"),
    "sign_atm_changer": (sign_atm_changer, 0.75, 1.30, "shop", 300, True, "New Petra entrance board (square_north/013)"),
    # ---- street plaques (Karakashian tiles, 15 cm)
    "plaque_omar": (plaque_omar, 0.75, 0.45, "plaque", 640, True, "on the gate's east face (photos 090, gate/g43)"),
    "plaque_david": (plaque_david, 0.45, 0.45, "plaque", 640, True, "citadel_east/C10"),
    "plaque_bazaar": (plaque_bazaar, 0.60, 0.45, "plaque", 640, True, "Suq el-Bazaar Rd. = David St. (citadel_east/C11)"),
    "plaque_latin": (plaque_latin, 0.75, 0.45, "plaque", 640, False, "tile design verified, wording from OSM"),
    "plaque_armenian": (plaque_armenian, 0.75, 0.45, "plaque", 640, False, "tile design verified, wording from OSM"),
    "plaque_greek": (plaque_greek, 0.90, 0.45, "plaque", 640, False, "tile design verified, wording from OSM"),
    "plaque_christian": (plaque_christian, 0.75, 0.45, "plaque", 640, False, "tile design verified; Arabic = Tariq Harat an-Nasara"),
    "plaque_jaffa_gate_info": (plaque_jaffa_gate_info, 0.42, 0.46, "plaque", 640, True, "heritage plaque under the tiles"),
    # ---- named
    "sign_jaffa_gate": (sign_jaffa_gate, 0.45, 0.48, "named", 640, True, "3x3 tiles, braid trim (photos 090, 105)"),
    "sign_imperial_letters": (sign_imperial_letters, 2.4, 0.32, "named", 260, True, "cutout metal letters"),
    "sign_new_imperial": (sign_new_imperial, 1.8, 0.45, "named", 300, False, "entrance plate"),
    "sign_petra": (sign_petra, 1.6, 0.42, "named", 340, True, "lightbox over the door (square_north/013)"),
    "sign_christian_info": (sign_christian_info, 1.7, 0.95, "named", 260, True, "cutout maroon letters (photo 145)"),
    "sign_swedish_roof": (sign_swedish_roof, 7.0, 0.45, "roof", 150, True, "free-standing letters on the roof railing (B01)"),
    "sign_swedish_facade": (sign_swedish_facade, 3.2, 0.26, "named", 220, True, "cutout letters on the parapet (photo 144)"),
    "sign_tourist_info": (sign_tourist_info, 1.5, 0.50, "named", 340, False, "plausible"),
    "sign_tower_of_david": (sign_tower_of_david, 0.50, 1.50, "named", 380, True, "entrance totem (citadel_east/A22)"),
    "sign_ramparts_walk": (sign_ramparts_walk, 0.60, 0.70, "tourist", 380, True, "gate/g40, g52"),
    "sign_versavee": (sign_versavee, 1.3, 0.24, "named", 260, True, "cutout letters, Imperial arcade"),
    "sign_welcome": (sign_welcome, 5.6, 0.34, "named", 170, True, "balcony fascia (square_north/030)"),
    "wayfinding_jaffa": (wayfinding_jaffa, 0.80, 1.10, "tourist", 340, True, "totem top on the square (photo 098)"),
    # ---- tourist pointers
    "dir_holy_sepulchre": (dir_holy_sepulchre, 1.15, 0.34, "tourist", 420, False, "pointing right"),
    "dir_western_wall": (dir_western_wall, 1.00, 0.34, "tourist", 420, False, "pointing left"),
    "dir_armenian_quarter": (dir_armenian_quarter, 1.00, 0.34, "tourist", 420, False, "pointing left"),
    "dir_christian_quarter": (dir_christian_quarter, 1.00, 0.34, "tourist", 420, False, "pointing right"),
    "dir_jaffa_gate_parking": (dir_jaffa_gate_parking, 1.15, 0.34, "tourist", 420, False, "pointing right"),
    # ---- misc
    "house_number": (house_number, 0.16, 0.13, "misc", 900, False, "ceramic number tile"),
    "no_entry_vehicles": (no_entry_vehicles, 0.60, 0.60, "misc", 420, False, "Israeli sign 401, round (alpha)"),
    "no_entry": (no_entry, 0.60, 0.60, "misc", 420, False, "Israeli sign 402, round (alpha)"),
    "no_parking": (no_parking, 0.60, 0.60, "misc", 420, True, "square_north/036, round (alpha)"),
    "plate_boarding": (plate_boarding, 0.55, 0.50, "misc", 420, True, "text as photographed (square_north/036)"),
    "police": (sign_police, 0.45, 0.30, "misc", 600, False, "plausible"),
}

CUTOUT = {"sign_imperial_letters", "sign_christian_info", "sign_swedish_roof", "sign_swedish_facade", "sign_versavee",
          "dir_holy_sepulchre", "dir_western_wall", "dir_armenian_quarter", "dir_christian_quarter",
          "dir_jaffa_gate_parking", "no_entry_vehicles", "no_entry", "no_parking"}


# =============================================================================== packing
def skyline_pack(sizes, W, H):
    sky = [(0, 0, W)]
    order = sorted(range(len(sizes)), key=lambda i: (-sizes[i][1], -sizes[i][0]))
    pos = [None] * len(sizes)
    for i in order:
        w, h = sizes[i]
        best = None
        for si in range(len(sky)):
            x = sky[si][0]
            if x + w > W:
                break
            y, wl, j = 0, w, si
            while wl > 0 and j < len(sky):
                y = max(y, sky[j][1])
                wl -= sky[j][2]
                j += 1
            if wl > 0 or y + h > H:
                continue
            if best is None or y < best[1] or (y == best[1] and x < best[0]):
                best = (x, y)
        if best is None:
            return None
        x, y = best
        pos[i] = best
        new = []
        for sx_, sy_, sw in sky:
            ex = sx_ + sw
            if ex <= x or sx_ >= x + w:
                new.append((sx_, sy_, sw))
                continue
            if sx_ < x:
                new.append((sx_, sy_, x - sx_))
            if ex > x + w:
                new.append((x + w, sy_, ex - (x + w)))
        new.append((x, y + h, w))
        new.sort()
        merged = []
        for s in new:
            if merged and merged[-1][1] == s[1] and merged[-1][0] + merged[-1][2] == s[0]:
                merged[-1] = (merged[-1][0], s[1], merged[-1][2] + s[2])
            else:
                merged.append(s)
        sky = merged
    return pos


def layout(k):
    names = list(SIGNS)
    px = {n: (max(8, int(round(SIGNS[n][1] * SIGNS[n][4] * k))), max(8, int(round(SIGNS[n][2] * SIGNS[n][4] * k))))
          for n in names}
    sizes = [(px[n][0] + 2 * PAD, px[n][1] + 2 * PAD) for n in names]
    pos = skyline_pack(sizes, ATLAS, ATLAS)
    if pos is None:
        return None
    return {n: (pos[i][0] + PAD, pos[i][1] + PAD, px[n][0], px[n][1]) for i, n in enumerate(names)}


def best_layout():
    lo, hi = 0.3, 3.0
    best = None
    for _ in range(22):
        mid = (lo + hi) / 2
        lay = layout(mid)
        if lay:
            best, lo = (mid, lay), mid
        else:
            hi = mid
    return best


# =============================================================================== colour bleed
def bleed(rgba):
    """push-pull: fill RGB of fully transparent texels with the average of nearby opaque colour"""
    rgb = rgba[..., :3].astype(np.float32)
    a = (rgba[..., 3] >= 12).astype(np.float32)
    levels = [(rgb * a[..., None], a)]
    while min(levels[-1][1].shape) > 1:
        c, w = levels[-1]
        H, W = w.shape
        H2, W2 = (H + 1) // 2, (W + 1) // 2
        cp = np.pad(c, ((0, H2 * 2 - H), (0, W2 * 2 - W), (0, 0)))
        wp = np.pad(w, ((0, H2 * 2 - H), (0, W2 * 2 - W)))
        c2 = cp.reshape(H2, 2, W2, 2, 3).sum((1, 3))
        w2 = wp.reshape(H2, 2, W2, 2).sum((1, 3))
        levels.append((c2, w2))
    fill = levels[-1][0] / np.maximum(levels[-1][1], 1e-6)[..., None]
    for c, w in reversed(levels[:-1]):
        H, W = w.shape
        up = np.repeat(np.repeat(fill, 2, 0), 2, 1)[:H, :W]
        own = c / np.maximum(w, 1e-6)[..., None]
        has = (w > 0)[..., None]
        fill = np.where(has, own * np.minimum(w, 1)[..., None] + up * (1 - np.minimum(w, 1))[..., None], up)
    out = rgba.copy()
    trans = rgba[..., 3] < 12
    out[..., :3][trans] = np.clip(fill[trans], 0, 255).astype(np.uint8)
    return out


# =============================================================================== preview
def stone_bg(W, H, seed=3):
    rng = np.random.default_rng(seed)
    n = fbm(rng, H, W, 40, 5)
    n2 = fbm(rng, H, W, 6, 3)
    base = np.array([0.80, 0.74, 0.63], np.float32)
    rgb = base * (0.88 + 0.16 * n[..., None]) * (0.95 + 0.08 * n2[..., None])
    course = 90
    img = (np.clip(rgb, 0, 1) * 255).astype(np.uint8)
    im = Image.fromarray(img)
    d = ImageDraw.Draw(im)
    for y in range(0, H, course):
        d.line([(0, y), (W, y)], fill=(176, 160, 136), width=2)
        off = (y // course) % 2 * 70
        for x in range(off, W, 140 + (y * 7) % 60):
            d.line([(x, y), (x, y + course)], fill=(176, 160, 136), width=2)
    return im


def preview(atlas, rects, path):
    pad, label_h = 18, 22
    maxw = 2600
    items = sorted(rects.items(), key=lambda kv: (SIGNS[kv[0]][3], -kv[1][3]))
    x = y = pad
    row_h = 0
    places = []
    for name, (rx, ry, rw, rh) in items:
        if x + rw + pad > maxw:
            x = pad
            y += row_h + label_h + pad
            row_h = 0
        places.append((name, x, y))
        x += rw + pad
        row_h = max(row_h, rh)
    H = y + row_h + label_h + pad
    bg = stone_bg(maxw, H).convert("RGBA")
    d = ImageDraw.Draw(bg)
    f = ImageFont.truetype(str(FONTS["sans_b"]), 14)
    for name, px_, py in places:
        rx, ry, rw, rh = rects[name]
        crop = atlas.crop((rx, ry, rx + rw, ry + rh))
        bg.alpha_composite(crop, (px_, py))
        d.text((px_, py + rh + 3), f"{name}  {SIGNS[name][1]:.2f}x{SIGNS[name][2]:.2f} m", font=f, fill=(40, 30, 20, 255))
    bg.convert("RGB").save(path)
    return bg


# =============================================================================== main
def render_sign(name, w_px, h_px):
    fn, w_m, h_m = SIGNS[name][:3]
    rng = np.random.default_rng(zlib.crc32(name.encode()))
    cv = Canvas(w_px * SS, h_px * SS, w_m, h_m, rng)
    fn(cv)
    # downsample in float with premultiplied alpha (no 8-bit rounding of faint edge colours)
    a = np.clip(cv.a, 0, 1).astype(np.float32)
    prem = np.clip(cv.rgb, 0, 1) * a[..., None]
    def rs(ch):
        return np.asarray(Image.fromarray(np.ascontiguousarray(ch, np.float32), "F").resize((w_px, h_px), Image.LANCZOS),
                          np.float32)
    a2 = np.clip(rs(a), 0, 1)
    rgb2 = np.stack([rs(prem[..., i]) for i in range(3)], -1) / np.maximum(a2, 1e-4)[..., None]
    out = np.dstack([np.clip(rgb2, 0, 1), a2[..., None]])
    out[a2 < 0.5 / 255] = 0
    return Image.fromarray((out * 255 + 0.5).astype(np.uint8), "RGBA")


def main():
    import sys
    only = set(sys.argv[1:])
    k, rects = best_layout()
    print(f"scale factor {k:.3f}: {len(rects)} signs")
    atlas = Image.new("RGBA", (ATLAS, ATLAS), (0, 0, 0, 0))
    for name, (x, y, w, h) in rects.items():
        if only and name not in only:
            continue
        im = render_sign(name, w, h)
        atlas.paste(im, (x, y))
        print(f"  {name:24s} {w:4d}x{h:<4d} px  {SIGNS[name][1]:.2f} x {SIGNS[name][2]:.2f} m")
    arr = bleed(np.asarray(atlas))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    PREVIEW_DIR.mkdir(parents=True, exist_ok=True)
    Image.fromarray(arr, "RGBA").save(OUT_DIR / "signs.png", optimize=True)
    meta = {"size": [ATLAS, ATLAS], "signs": {}}
    for name, (x, y, w, h) in rects.items():
        fn, w_m, h_m, kind, ppm, verified, note = SIGNS[name]
        meta["signs"][name] = {"rect": [x, y, w, h], "w_m": w_m, "h_m": h_m, "kind": kind,
                               "alpha": "cutout" if name in CUTOUT else ("edge" if kind in ("plaque",) or name in
                                                                          ("sign_jaffa_gate", "house_number") else "opaque"),
                               "verified": verified, "note": note}
    (OUT_DIR / "signs.json").write_text(json.dumps(meta, indent=1, ensure_ascii=False))
    preview(atlas, rects, PREVIEW_DIR / "preview.png")
    Image.fromarray(arr, "RGBA").convert("RGB").save(PREVIEW_DIR / "atlas_rgb.png")
    print("wrote", OUT_DIR / "signs.png", OUT_DIR / "signs.json", PREVIEW_DIR / "preview.png")


if __name__ == "__main__":
    main()

"""Manage the photo evaluation set: find candidate photos, download them from Commons, and
keep the camera poses in data/reference/eval_cams.json (mirrored to game/public/eval_cams.json).

    python3 pipeline/eval_set.py candidates [--near X,Y] [--radius R] [--sheet out.jpg]
    python3 pipeline/eval_set.py search "David Street Jerusalem" [--limit 40]
    python3 pipeline/eval_set.py category "David Street (Jerusalem)"
    python3 pipeline/eval_set.py fetch "File:David Street (20041).jpg" [...]   # -> data/photos_ref/eval/
    python3 pipeline/eval_set.py exif data/photos/087_124589152.jpg [...]       # focal length -> FOV
    python3 pipeline/eval_set.py add NAME PHOTO --x 60 --y 8 --heading 270 [--z_eye 1.6 --pitch 0 --fov 50]
    python3 pipeline/eval_set.py set NAME heading=272.5 fov=48 ...
    python3 pipeline/eval_set.py resect NAME --pt X,Y,Z,u,v --pt X,Y,u ... [--free x,y,heading,pitch] [--write]
    python3 pipeline/eval_set.py grid NAME            # photo with a 0..1 coordinate grid, for reading u, v
    python3 pipeline/eval_set.py list
    python3 pipeline/eval_set.py sync          # validate + copy to game/public/eval_cams.json

Local frame: x east, y north, metres from the Jaffa Gate OSM node; heading = compass degrees
(0 N, 90 E), pitch = degrees above the horizon, fov = VERTICAL field of view in degrees,
z_eye = camera height above the local ground under the camera. See docs/EVALUATION.md.

Plain Python 3 + Pillow (only for `candidates --sheet`); no other dependencies.
"""
import argparse
import html
import json
import math
import re
import shutil
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAMS = ROOT / "data/reference/eval_cams.json"
GAME_CAMS = ROOT / "game/public/eval_cams.json"
EVAL_DIR = ROOT / "data/photos_ref/eval"
PHOTO_DIRS = [ROOT / "data/photos"] + sorted(p for p in (ROOT / "data/photos_ref").glob("*") if p.is_dir()) \
    if (ROOT / "data/photos_ref").exists() else [ROOT / "data/photos"]
API = "https://commons.wikimedia.org/w/api.php"
UA = "old-city-walker-poc/0.2 (evaluation)"
DELAY = 1.5                     # seconds between Commons requests (be polite)

# lat/lon -> local metres (same constants as data/reference/hero_edges.md / pipeline/geo.py)
LAT0, LON0 = 31.7766282, 35.2275435
MX, MY = 94721.7, 110882.9

FIELDS = ("photo", "credit", "x", "y", "z_eye", "heading", "pitch", "fov")
OPTIONAL = ("roll", "shift_x", "shift_y", "z_ground", "covers", "notes", "pose_quality", "date")


# ---------------------------------------------------------------- helpers
def to_local(lat, lon):
    return (lon - LON0) * MX, (lat - LAT0) * MY


def strip_html(s):
    s = re.sub(r"<[^>]+>", "", s or "")
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def load_cams():
    if CAMS.exists():
        return json.loads(CAMS.read_text())
    return {"cams": {}}


def save_cams(d):
    CAMS.parent.mkdir(parents=True, exist_ok=True)
    CAMS.write_text(json.dumps(d, indent=1, ensure_ascii=False) + "\n")
    print("wrote", CAMS.relative_to(ROOT))


def all_photo_records():
    """Every downloaded photo with metadata, from data/photos/index.json and data/photos_ref/*/index.json."""
    out = []
    for d in PHOTO_DIRS:
        idx = d / "index.json"
        if not idx.exists():
            continue
        try:
            recs = json.loads(idx.read_text())
        except json.JSONDecodeError:
            continue
        if isinstance(recs, dict):
            recs = recs.get("photos") or recs.get("files") or list(recs.values())
        for r in recs:
            if not isinstance(r, dict) or not r.get("file") or not (d / r["file"]).exists():
                continue
            r = dict(r)
            r["path"] = str((d / r["file"]).relative_to(ROOT))
            if r.get("x") is None and r.get("lat") is not None and r.get("lon") is not None:
                r["x"], r["y"] = to_local(r["lat"], r["lon"])
            out.append(r)
    return out


def credit_for(photo_path):
    """'Author, licence, page url' for a photo path relative to the project root."""
    p = (ROOT / photo_path).resolve()
    for r in all_photo_records():
        if (ROOT / r["path"]).resolve() == p:
            author = r.get("author") or strip_html(r.get("artist", "")) or "unknown author"
            return "%s, %s, %s" % (author, r.get("licence") or "licence unknown", r.get("page") or r.get("title"))
    return None


# ---------------------------------------------------------------- Commons
def api(params):
    q = API + "?" + urllib.parse.urlencode({**params, "format": "json", "maxlag": 5})
    req = urllib.request.Request(q, headers={"User-Agent": UA})
    d = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            if "error" not in d:
                return d
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 0) + 2 ** attempt)
            continue
        time.sleep(2 ** attempt + DELAY)          # maxlag / transient error
    raise RuntimeError("Commons API: %s" % str(d)[:300])


def download(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    err = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                dest.write_bytes(r.read())
            return True
        except urllib.error.HTTPError as e:
            err = e
            if e.code != 429 and e.code < 500:
                break
            time.sleep(int(e.headers.get("Retry-After") or 0) + 2 ** attempt)
    print("  download failed", url, err)
    return False


def cmd_search(a):
    r = api({"action": "query", "list": "search", "srsearch": a.query, "srnamespace": 6,
             "srlimit": a.limit})
    for s in r["query"]["search"]:
        print(s["title"])


def record_for(photo):
    p = (ROOT / photo).resolve() if (ROOT / photo).exists() else None
    for r in all_photo_records():
        if (p and (ROOT / r["path"]).resolve() == p) or r.get("title") == photo:
            return r
    return None


def cmd_exif(a):
    """Camera model / focal length from Commons EXIF -> a first vertical-FOV estimate."""
    for photo in a.photos:
        r = record_for(photo)
        title = r["title"] if r else (photo if photo.startswith("File:") else None)
        if not title:
            print(photo, ": no Commons record")
            continue
        q = api({"action": "query", "titles": title, "prop": "imageinfo",
                 "iiprop": "commonmetadata|size"})
        time.sleep(DELAY)
        ii = next(iter(q["query"]["pages"].values())).get("imageinfo", [{}])[0]
        md = {m["name"]: m["value"] for m in ii.get("commonmetadata", []) if not isinstance(m["value"], list)}
        w, h = ii.get("width", 4), ii.get("height", 3)
        f35 = md.get("FocalLengthIn35mmFilm")
        line = "%s: %s %s f=%s f35=%s %dx%d" % (photo, md.get("Make", ""), md.get("Model", ""),
                                               md.get("FocalLength"), f35, w, h)
        if f35:
            # 35 mm equivalence is defined on the diagonal of the sensor's native frame: 4:3 for
            # phones / Micro Four Thirds, 3:2 otherwise. Assume the long side was not cropped.
            f35 = float(f35)
            make = (md.get("Make", "") + md.get("Model", "")).lower()
            native = 4 / 3 if any(k in make for k in ("samsung", "apple", "google", "xiaomi", "huawei",
                                                       "olympus", "panasonic", "oneplus", "sm-")) else 1.5
            long_mm = math.hypot(36, 24) * native / math.hypot(native, 1)
            t_long = long_mm / 2 / f35
            t_vert = t_long * (min(w, h) / max(w, h)) if w >= h else t_long
            line += "  -> vertical FOV ~%.1f deg (native %s, long side uncropped; fisheyes differ)" % (
                math.degrees(2 * math.atan(t_vert)), "4:3" if native < 1.4 else "3:2")
        print(line)


def project(params, pts, W, H):
    """Pinhole projection of world points with the eval-cam convention -> (u, v) pixels."""
    cx, cy, cz, hd, pt, fov = params
    h, p = math.radians(hd), math.radians(pt)
    F = (math.sin(h) * math.cos(p), math.cos(h) * math.cos(p), math.sin(p))
    R = (math.cos(h), -math.sin(h), 0.0)
    U = (-math.sin(h) * math.sin(p), -math.cos(h) * math.sin(p), math.cos(p))
    fpx = (H / 2) / math.tan(math.radians(fov) / 2)
    out = []
    for X, Y, Z in pts:
        d = (X - cx, Y - cy, Z - cz)
        xc = sum(a * b for a, b in zip(d, R))
        yc = sum(a * b for a, b in zip(d, U))
        zc = max(1e-3, sum(a * b for a, b in zip(d, F)))
        out.append((W / 2 + xc / zc * fpx, H / 2 - yc / zc * fpx))
    return out


def cmd_resect(a):
    """Solve camera x, y, (eye z), heading, pitch, (fov) from image positions of known points.

    --pt X,Y,Z,u,v   a 3D point (e.g. a building corner at ground level, Z = ground height,
                     or at the roof line, Z = known height) seen at pixel (u, v)
    --pt X,Y,u       a vertical edge (corner) at (X, Y) seen at column u; uses only u
    u, v in photo pixels (as displayed, after EXIF rotation) or as fractions 0..1.
    """
    d = load_cams()
    cam = d["cams"][a.name]
    from PIL import Image, ImageOps
    W, H = ImageOps.exif_transpose(Image.open(ROOT / cam["photo"])).size
    obs = []
    for s in a.pt:
        v = [float(t) for t in s.split(",")]
        if len(v) == 3:
            X, Y, u = v
            obs.append(((X, Y, None), (u, None)))
        elif len(v) == 5:
            obs.append(((v[0], v[1], v[2]), (v[3], v[4])))
        else:
            sys.exit("bad --pt %s" % s)
    frac = all(o[1][0] <= 1.5 and (o[1][1] is None or o[1][1] <= 1.5) for o in obs)
    if frac:
        obs = [(p, (u * W, None if v is None else v * H)) for p, (u, v) in obs]
    gz = float(cam.get("z_ground", a.ground))
    names = ["x", "y", "z_eye", "heading", "pitch", "fov"]
    free = [names.index(n) for n in a.free.split(",")]
    x = [cam["x"], cam["y"], cam["z_eye"], cam["heading"], cam.get("pitch", 0.0), cam["fov"]]

    def resid(x):
        params = [x[0], x[1], gz + x[2], x[3], x[4], x[5]]
        pts = [(X, Y, (gz + x[2]) if Z is None else Z) for (X, Y, Z), _ in obs]
        pr = project(params, pts, W, H)
        r = []
        for (pu, pv), (_p, (u, v)) in zip(pr, obs):
            r.append(pu - u)
            if v is not None:
                r.append(pv - v)
        return r

    if a.search:
        # coarse grid over (x, y) around the current guess; heading from the mean bearing offset.
        # Avoids the mirror solutions a local solver falls into with only 3-4 points.
        fpx = (H / 2) / math.tan(math.radians(x[5]) / 2)
        offs = [math.degrees(math.atan((u - W / 2) / fpx)) for _p, (u, _v) in obs]
        best = None
        n = int(a.search / 0.5)
        for i in range(-n, n + 1):
            for j in range(-n, n + 1):
                px, py = x[0] + i * 0.5, x[1] + j * 0.5
                hs = [(math.degrees(math.atan2(X - px, Y - py)) - o) for ((X, Y, _Z), _uv), o in zip(obs, offs)]
                c = sum(math.cos(math.radians(h)) for h in hs)
                s_ = sum(math.sin(math.radians(h)) for h in hs)
                hm = math.degrees(math.atan2(s_, c))
                err = sum(((h - hm + 180) % 360 - 180) ** 2 for h in hs)
                if any(math.hypot(X - px, Y - py) < 2 for (X, Y, _Z), _uv in obs):
                    continue
                if best is None or err < best[0]:
                    best = (err, px, py, hm % 360)
        x[0], x[1], x[3] = best[1], best[2], best[3]
        print("grid search: x %.1f y %.1f heading %.1f (rms %.2f deg)" % (x[0], x[1], x[3],
                                                                         math.sqrt(best[0] / len(obs))))
    lam = 1e-2
    cur = resid(x)
    cost = sum(t * t for t in cur)
    for _ in range(200):
        J = []
        for i in free:
            dx = list(x)
            eps = 1e-4 * max(1.0, abs(x[i]))
            dx[i] += eps
            J.append([(b - a_) / eps for a_, b in zip(cur, resid(dx))])
        # normal equations (J is stored transposed: one row per free parameter)
        n = len(free)
        A = [[sum(J[i][k] * J[j][k] for k in range(len(cur))) for j in range(n)] for i in range(n)]
        g = [sum(J[i][k] * cur[k] for k in range(len(cur))) for i in range(n)]
        for i in range(n):
            A[i][i] *= 1 + lam
        try:
            step = solve(A, [-t for t in g])
        except ZeroDivisionError:
            break
        nx = list(x)
        for i, s_ in zip(free, step):
            nx[i] += s_
        nr = resid(nx)
        ncost = sum(t * t for t in nr)
        if ncost < cost:
            x, cur, cost, lam = nx, nr, ncost, lam * 0.3
            if max(abs(s_) for s_ in step) < 1e-5:
                break
        else:
            lam *= 10
            if lam > 1e8:
                break
    rms = math.sqrt(cost / max(1, len(cur)))
    print("solution: x %.2f  y %.2f  z_eye %.2f  heading %.2f  pitch %.2f  fov %.2f   rms %.1f px (%d residuals, image %dx%d)"
          % (x[0], x[1], x[2], x[3] % 360, x[4], x[5], rms, len(cur), W, H))
    params = [x[0], x[1], gz + x[2], x[3], x[4], x[5]]
    for ((X, Y, Z), (u, v)), (pu, pv) in zip(obs, project(params, [(X, Y, (gz + x[2]) if Z is None else Z)
                                                                     for (X, Y, Z), _ in obs], W, H)):
        print("   pt (%.1f, %.1f, %s): observed u %.0f v %s  model u %.0f v %.0f" % (
            X, Y, "-" if Z is None else "%.1f" % Z, u, "-" if v is None else "%.0f" % v, pu, pv))
    if a.write:
        for i in free:
            cam[names[i]] = round(x[i] % 360 if names[i] == "heading" else x[i], 2)
        save_cams(d)


def cmd_grid(a):
    """Photo with a fractional coordinate grid -> renders/eval/<name>_grid.jpg (read u, v off it)."""
    from PIL import Image, ImageDraw, ImageOps
    cam = load_cams()["cams"][a.name]
    im = ImageOps.exif_transpose(Image.open(ROOT / cam["photo"])).convert("RGB")
    im.thumbnail((a.size, a.size))
    d = ImageDraw.Draw(im)
    W, H = im.size
    for k in range(1, 20):
        f = k / 20
        col = (255, 255, 0) if k % 2 == 0 else (0, 255, 255)
        d.line([(f * W, 0), (f * W, H)], fill=col, width=1)
        d.line([(0, f * H), (W, f * H)], fill=col, width=1)
        if k % 2 == 0:
            d.text((f * W + 2, 2), "%.1f" % f, fill=col)
            d.text((2, f * H + 2), "%.1f" % f, fill=col)
    out = ROOT / "renders/eval" / ("%s_grid.jpg" % a.name)
    out.parent.mkdir(parents=True, exist_ok=True)
    im.save(out, quality=88)
    print(out.relative_to(ROOT))


def solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        if abs(M[c][c]) < 1e-12:
            raise ZeroDivisionError
        for r in range(n):
            if r != c:
                f = M[r][c] / M[c][c]
                for k in range(c, n + 1):
                    M[r][k] -= f * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


def cmd_category(a):
    cat = a.name if a.name.startswith("Category:") else "Category:" + a.name
    cont = {}
    while True:
        r = api({"action": "query", "list": "categorymembers", "cmtitle": cat, "cmtype": "file",
                 "cmlimit": 200, **cont})
        for m in r["query"]["categorymembers"]:
            print(m["title"])
        if "continue" not in r:
            break
        cont = r["continue"]
        time.sleep(DELAY)


def cmd_fetch(a):
    EVAL_DIR.mkdir(parents=True, exist_ok=True)
    idx_path = EVAL_DIR / "index.json"
    idx = json.loads(idx_path.read_text()) if idx_path.exists() else []
    have = {r["title"]: r for r in idx}
    titles = [t if t.startswith("File:") else "File:" + t for t in a.titles]
    for i in range(0, len(titles), 40):
        chunk = titles[i:i + 40]
        r = api({"action": "query", "titles": "|".join(chunk), "prop": "imageinfo|coordinates",
                 "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1280, "coprimary": "all"})
        time.sleep(DELAY)
        for p in r["query"]["pages"].values():
            if "imageinfo" not in p:
                print("  not found:", p.get("title"))
                continue
            ii = p["imageinfo"][0]
            meta = ii.get("extmetadata", {})
            coords = p.get("coordinates") or []
            cam = next((c for c in coords if c.get("primary") is not None), coords[0] if coords else None)
            rec = {"file": "%d.jpg" % p["pageid"], "title": p["title"], "pageid": p["pageid"],
                   "page": ii.get("descriptionurl"),
                   "author": strip_html(meta.get("Artist", {}).get("value", ""))[:200],
                   "licence": meta.get("LicenseShortName", {}).get("value"),
                   "date": strip_html(meta.get("DateTimeOriginal", {}).get("value", ""))[:19],
                   "description": strip_html(meta.get("ImageDescription", {}).get("value", ""))[:300],
                   "orig_w": ii.get("width"), "orig_h": ii.get("height"),
                   "lat": cam and cam["lat"], "lon": cam and cam["lon"], "thumb": ii.get("thumburl")}
            if cam:
                rec["x"], rec["y"] = [round(v, 1) for v in to_local(cam["lat"], cam["lon"])]
            dest = EVAL_DIR / rec["file"]
            if not dest.exists():
                ok = download(ii.get("thumburl") or ii["url"], dest)
                time.sleep(DELAY)
                if not ok:
                    continue
            have[rec["title"]] = rec
            print("  %s -> %s  (%s, %s)" % (rec["title"], dest.relative_to(ROOT), rec["author"], rec["licence"]))
    idx_path.write_text(json.dumps(list(have.values()), indent=1, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- candidates
def cmd_candidates(a):
    recs = all_photo_records()
    if a.near:
        nx, ny = map(float, a.near.split(","))
        recs = [r for r in recs if r.get("x") is not None and math.hypot(r["x"] - nx, r["y"] - ny) <= a.radius]
        recs.sort(key=lambda r: math.hypot(r["x"] - nx, r["y"] - ny))
    if a.grep:
        rx = re.compile(a.grep, re.I)
        recs = [r for r in recs if rx.search(r.get("title", "") + " " + r.get("description", "") + " " + r["path"])]
    for r in recs:
        xy = "(%6.1f,%6.1f)" % (r["x"], r["y"]) if r.get("x") is not None else "(  no GPS   )"
        print("%-48s %s %-10s %s" % (r["path"], xy, str(r.get("date", ""))[:10], r.get("title", "")[5:80]))
    print(len(recs), "photos")
    if a.sheet:
        contact_sheet([r["path"] for r in recs], Path(a.sheet))


def contact_sheet(paths, out, cols=5, tw=400, th=300):
    from PIL import Image, ImageDraw, ImageOps
    rows = max(1, math.ceil(len(paths) / cols))
    sheet = Image.new("RGB", (cols * tw, rows * (th + 18)), "white")
    d = ImageDraw.Draw(sheet)
    for k, p in enumerate(paths):
        im = ImageOps.exif_transpose(Image.open(ROOT / p)).convert("RGB")
        im.thumbnail((tw, th))
        x, y = (k % cols) * tw, (k // cols) * (th + 18)
        sheet.paste(im, (x, y))
        d.text((x + 3, y + th + 3), p.split("/")[-2] + "/" + p.split("/")[-1][:40], fill="black")
    sheet.save(out, quality=82)
    print("contact sheet ->", out)


# ---------------------------------------------------------------- cams
def num(v):
    try:
        f = float(v)
        return int(f) if f.is_integer() and "." not in str(v) else f
    except ValueError:
        return v


def cmd_add(a):
    d = load_cams()
    photo = str(Path(a.photo).resolve().relative_to(ROOT)) if Path(a.photo).exists() else a.photo
    if not (ROOT / photo).exists():
        sys.exit("photo not found: %s" % photo)
    cam = d["cams"].get(a.name, {})
    cam.update({"photo": photo, "credit": a.credit or credit_for(photo) or cam.get("credit", ""),
                "x": a.x, "y": a.y, "z_eye": a.z_eye, "heading": a.heading, "pitch": a.pitch, "fov": a.fov})
    d["cams"][a.name] = cam
    save_cams(d)


def cmd_set(a):
    d = load_cams()
    cam = d["cams"].get(a.name)
    if cam is None:
        sys.exit("no cam %s" % a.name)
    for kv in a.pairs:
        k, v = kv.split("=", 1)
        if v == "":
            cam.pop(k, None)
        else:
            cam[k] = num(v)
    save_cams(d)


def validate(d):
    problems = []
    for name, c in d["cams"].items():
        for k in FIELDS:
            if k not in c:
                problems.append("%s: missing %s" % (name, k))
        if "photo" in c and not (ROOT / c["photo"]).exists():
            problems.append("%s: photo missing %s" % (name, c["photo"]))
        if not str(c.get("credit", "")).strip():
            problems.append("%s: no credit" % name)
        if not 1 <= float(c.get("fov", 50)) <= 140:
            problems.append("%s: odd fov %s" % (name, c.get("fov")))
    return problems


def cmd_list(a):
    d = load_cams()
    print("%-22s %7s %7s %5s %7s %6s %5s  %s" % ("name", "x", "y", "z", "heading", "pitch", "fov", "photo"))
    for n, c in d["cams"].items():
        print("%-22s %7.1f %7.1f %5.2f %7.1f %6.1f %5.1f  %s" % (
            n, c["x"], c["y"], c["z_eye"], c["heading"], c["pitch"], c["fov"], c["photo"]))
    for p in validate(d):
        print("WARNING", p)


def cmd_sync(a):
    d = load_cams()
    probs = validate(d)
    for p in probs:
        print("WARNING", p)
    GAME_CAMS.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(CAMS, GAME_CAMS)
    print("copied ->", GAME_CAMS.relative_to(ROOT), "(%d cams)" % len(d["cams"]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("candidates")
    s.add_argument("--near")
    s.add_argument("--radius", type=float, default=25)
    s.add_argument("--grep")
    s.add_argument("--sheet")
    s.set_defaults(f=cmd_candidates)
    s = sub.add_parser("search")
    s.add_argument("query")
    s.add_argument("--limit", type=int, default=40)
    s.set_defaults(f=cmd_search)
    s = sub.add_parser("category")
    s.add_argument("name")
    s.set_defaults(f=cmd_category)
    s = sub.add_parser("fetch")
    s.add_argument("titles", nargs="+")
    s.set_defaults(f=cmd_fetch)
    s = sub.add_parser("exif", help="focal length -> first FOV estimate")
    s.add_argument("photos", nargs="+", help="photo paths or File: titles")
    s.set_defaults(f=cmd_exif)
    s = sub.add_parser("add")
    s.add_argument("name")
    s.add_argument("photo")
    s.add_argument("--x", type=float, required=True)
    s.add_argument("--y", type=float, required=True)
    s.add_argument("--z_eye", type=float, default=1.6)
    s.add_argument("--heading", type=float, required=True)
    s.add_argument("--pitch", type=float, default=0.0)
    s.add_argument("--fov", type=float, default=50.0)
    s.add_argument("--credit")
    s.set_defaults(f=cmd_add)
    s = sub.add_parser("set")
    s.add_argument("name")
    s.add_argument("pairs", nargs="+", help="key=value (empty value removes the key)")
    s.set_defaults(f=cmd_set)
    s = sub.add_parser("resect", help="solve the pose from known points seen in the photo")
    s.add_argument("name")
    s.add_argument("--pt", action="append", required=True, help="X,Y,Z,u,v or X,Y,u")
    s.add_argument("--free", default="x,y,heading,pitch")
    s.add_argument("--ground", type=float, default=0.0, help="ground z under the camera")
    s.add_argument("--search", type=float, default=0.0,
                   help="grid-search x, y within this radius (m) of the current pose first")
    s.add_argument("--write", action="store_true")
    s.set_defaults(f=cmd_resect)
    s = sub.add_parser("grid", help="photo with a 0..1 grid for reading image coordinates")
    s.add_argument("name")
    s.add_argument("--size", type=int, default=1400)
    s.set_defaults(f=cmd_grid)
    sub.add_parser("list").set_defaults(f=cmd_list)
    sub.add_parser("sync").set_defaults(f=cmd_sync)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()

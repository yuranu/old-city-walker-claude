"""Walkable street-level terrain for the whole walled Old City (see docs/TERRAIN.md).

The open DEM (AWS Terrain Tiles, SRTM-derived, ~30 m effective) is a surface model: over the
dense Old City it sees roofs, not streets. This module builds a street-level model by

  1. a lower envelope of the DEM (morphological opening + Gaussian smoothing) as the regional trend,
  2. a Gaussian-process (kriging) correction through ~400 ground ANCHORS: spot heights and bench
     marks transcribed from the 1864-65 Ordnance Survey of Jerusalem 1:2500 (public domain, feet
     above the Mediterranean; data/raw/terrain/os1865_spot_heights.csv), plus modern anchors
     (Warren/Caspi Haram levels, the post-1967 Western Wall plaza),
  3. FLATS: polygons kept exactly level (Temple Mount esplanade, Western Wall prayer area and
     plaza) for the builder to bound with retaining walls.

Output data/terrain_street.json: regular grid in the local frame (x east, y north, metres from the
Jaffa Gate node), z relative to the street at the Jaffa Gate node (datum_asl = its height asl).
"z" has the flats burned in; "z_ground" is the continuous field without them (use it for the foot
of retaining walls). data/terrain_street.png is a hillshade + 2 m contour preview.

    python3 pipeline/terrain_street.py            # rebuild json + png, print validation
    from terrain_street import street_z           # street_z(x, y) -> metres rel. Jaffa Gate street
"""
import csv
import json
import math
import sys
import urllib.request
from pathlib import Path

import numpy as np
import shapely
from PIL import Image, ImageDraw, ImageFont
from shapely import contains_xy
from shapely.geometry import LineString, Point, Polygon, shape
from shapely.prepared import prep

sys.path.insert(0, str(Path(__file__).resolve().parent))
from osm_to_local import LAT0, LON0, M_PER_DEG_LAT, M_PER_DEG_LON  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT_JSON = ROOT / "data/terrain_street.json"
OUT_PNG = ROOT / "data/terrain_street.png"
TILE_DIR = ROOT / "data/raw/terrain"
OS_SPOTS = TILE_DIR / "os1865_spot_heights.csv"
OS_CPS = TILE_DIR / "os1865_control_points.csv"
OSM = ROOT / "data/osm_local.json"
POLY = ROOT / "data/oldcity_polygon.json"
SECTORS = ROOT / "data/sectors.json"

# Output grid (covers x -360..1008, y -508..852 at 4 m).
X0, Y0, STEP, NX, NY = -360.0, -508.0, 4.0, 343, 341

FT = 0.3048                      # metres per (British) foot
TZ = 15                          # terrain tile zoom
TILES_X = (19590, 19591)
TILES_Y = (13329, 13330, 13331)
TILE_URL = "https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"

# Method parameters (chosen by leave-one-out cross-validation, see explore()).
ENV_R = 10                       # opening half-width, cells (40 m -> 84 m window)
ENV_SIGMA = 4.0                  # smoothing of the envelope, cells (16 m)
GP_L = 45.0                      # Matern-3/2 length scale, m
GP_S = 4.0                       # GP prior std of the correction, m
SIG = {"S": 0.6, "B": 0.6, "out": 1.5, "edge": 0.3}     # anchor noise std, m
BM_OFFSET = None                 # bench mark height above ground, m; None = estimate from data

# ---------------------------------------------------------------------------------------------
# Modern / literature anchors. role: "flat" (sets a flat's level), "check" (validation only).
MODERN = [
    dict(name="Mughrabi Gate sill (Temple Mount)", x=659.7, y=-26.9, asl=736.5, sigma=0.3, role="check",
         source="Caspi survey value quoted in 'Table I. Elevations on Mount Moriah', templemount.org "
                "(Warren 1884, map XXXII: 2416 ft = 736.4 m)", conf="high"),
    dict(name="Gate of the Chain level", x=643.7, y=73.3, asl=737.3, sigma=0.3, role="check",
         source="Warren, map XXXIV (2419 ft) via templemount.org Table I", conf="high"),
    dict(name="Haram surface at the northern gates", x=760.0, y=378.0, asl=737.0, sigma=0.5, role="check",
         source="Wilson, Ordnance Survey of Jerusalem notes (1865): 'surface ground only 2,418 feet at "
                "the northern gates' (templemount.org/wilson1.html)", conf="high"),
    dict(name="Dome of the Rock upper court (not a flat here)", x=733.5, y=120.0, asl=742.0, sigma=0.5,
         role="info", source="Warren, map XII via templemount.org Table I; OS 1865 spots 2434-2439 ft",
         conf="high"),
    dict(name="Sakhra (Foundation Stone) summit", x=733.5, y=154.0, asl=743.7, sigma=0.2, role="info",
         source="Warren map XII; Wilson 1865 '2,440 feet above the level of the sea'", conf="high"),
    dict(name="Western Wall prayer area (post-1967)", x=632.0, y=8.0, asl=727.0, sigma=0.8, role="flat",
         source="OS 1865 Wailing Place 2391-2393 ft (728.8-729.4 m) minus the c. 2 m (two Herodian "
                "courses) lowering of 1967-68 (bibleplaces.com 'Then and Now: Western Wall Plaza'; "
                "Lancaster 1998; Encyclopedia.com 'Western Wall')", conf="medium"),
    dict(name="Western Wall plaza (main, behind the partition)", x=592.0, y=-20.0, asl=729.0, sigma=1.5,
         role="flat", source="Inferred: 1865 Mughrabi-quarter ground 2387-2404 ft (727.5-732.7 m, mean "
                             "730.6) graded in 1967; the elevator figure (26 m below Misgav Ladach St, "
                             "~756 m) gives ~730 at the plaza's west edge; real plaza slopes ~2-3 m "
                             "down towards the prayer area", conf="low"),
    dict(name="Western Wall elevator: Misgav Ladach St to plaza, 22-26 m", x=498.0, y=-60.0, asl=None,
         sigma=None, role="check", source="Hebrew Wikipedia 'מעלית הכותל' (c. 22 m); AP / Times of Israel "
                                          "(26 m, 85 ft)", conf="medium"),
    dict(name="New Gate (Wikipedia: 790 m)", x=-128.3, y=296.8, asl=790.0, sigma=3.0, role="check",
         source="en.wikipedia New Gate (uncited round figure)", conf="low"),
    dict(name="Herod's Gate (Wikipedia: 755 m)", x=588.0, y=705.0, asl=755.0, sigma=3.0, role="check",
         source="en.wikipedia Herod's Gate (uncited)", conf="low"),
]


# Street profiles pinned where a single-valued field would otherwise sag towards a lower level
# passing underneath: (x, y, m asl) vertices, densified to pseudo-anchors every 6 m.
PINNED = [
    dict(name="Chain Street east end (causeway over Al-Wad and Wilson's Arch)",
         pts=[(552.0, 40.0, 738.5), (566.0, 45.0, 738.0), (583.0, 50.0, 737.6), (601.0, 55.0, 737.3),
              (620.0, 63.0, 737.3), (640.0, 71.0, 737.3)],
         source="OS 1865 spots 2423 ft (554.7, 43.2) and 2419 ft (602.2, 53.6); Warren: Gate of the Chain 737.3"),
]

# Lower streets passing under another street: street_z() returns the UPPER level there.
UNDERPASSES = [
    dict(name="Al-Wad under Chain Street", osm_ways=[508241135, 277508274],
         pts=[[536.0, 110.0], [541.0, 81.0], [551.0, 65.0], [555.0, 34.0], [562.0, 18.0]],
         z_asl=[731.0, 730.8, 730.6, 730.2, 729.8],
         note="tunnel (OSM layer -1) c. 30 m long under the Chain Street causeway; the single-valued field "
              "rises towards Chain Street (~738) over the last ~45 m of Al-Wad. Lower level from the OS 1865 "
              "Al-Wad spots (2399-2400 ft at y~125-154) falling gently to the Western Wall plaza"),
]


# ---------------------------------------------------------------------------------------------
# DEM
def fetch_tiles():
    TILE_DIR.mkdir(parents=True, exist_ok=True)
    for tx in TILES_X:
        for ty in TILES_Y:
            f = TILE_DIR / ("%d_%d_%d.png" % (TZ, tx, ty))
            if not f.exists():
                url = TILE_URL.format(z=TZ, x=tx, y=ty)
                print("fetching", url)
                req = urllib.request.Request(url, headers={"User-Agent": "old-city-walker"})
                f.write_bytes(urllib.request.urlopen(req, timeout=60).read())


def dem_mosaic():
    fetch_tiles()
    mos = np.zeros((256 * len(TILES_Y), 256 * len(TILES_X)))
    for j, ty in enumerate(TILES_Y):
        for i, tx in enumerate(TILES_X):
            a = np.asarray(Image.open(TILE_DIR / ("%d_%d_%d.png" % (TZ, tx, ty))).convert("RGB")).astype(float)
            mos[j * 256:(j + 1) * 256, i * 256:(i + 1) * 256] = a[..., 0] * 256 + a[..., 1] + a[..., 2] / 256 - 32768
    return mos


def local_to_latlon(x, y):
    return LAT0 + np.asarray(y) / M_PER_DEG_LAT, LON0 + np.asarray(x) / M_PER_DEG_LON


def dem_sample(mos, x, y):
    lat, lon = local_to_latlon(x, y)
    n = 2 ** TZ
    X = ((lon + 180) / 360 * n - TILES_X[0]) * 256 - 0.5
    Y = ((1 - np.arcsinh(np.tan(np.radians(lat))) / math.pi) / 2 * n - TILES_Y[0]) * 256 - 0.5
    return bilinear(mos, X, Y)


def bilinear(a, X, Y):
    X = np.clip(X, 0, a.shape[1] - 1.001)
    Y = np.clip(Y, 0, a.shape[0] - 1.001)
    x0, y0 = np.floor(X).astype(int), np.floor(Y).astype(int)
    fx, fy = X - x0, Y - y0
    return ((a[y0, x0] * (1 - fx) + a[y0, x0 + 1] * fx) * (1 - fy) +
            (a[y0 + 1, x0] * (1 - fx) + a[y0 + 1, x0 + 1] * fx) * fy)


def grid_xy():
    xs = X0 + STEP * np.arange(NX)
    ys = Y0 + STEP * np.arange(NY)
    return np.meshgrid(xs, ys)          # arrays [NY, NX], row j = y, col i = x


# ---------------------------------------------------------------------------------------------
# image filters (numpy only)
def _rank1d(a, r, axis, fn):
    if r <= 0:
        return a
    pad = [(0, 0), (0, 0)]
    pad[axis] = (r, r)
    p = np.pad(a, pad, mode="edge")
    n = a.shape[axis]
    out = None
    for k in range(2 * r + 1):
        sl = [slice(None), slice(None)]
        sl[axis] = slice(k, k + n)
        v = p[tuple(sl)]
        out = v.copy() if out is None else fn(out, v)
    return out


def min_filter(a, r):
    return _rank1d(_rank1d(a, r, 0, np.minimum), r, 1, np.minimum)


def max_filter(a, r):
    return _rank1d(_rank1d(a, r, 0, np.maximum), r, 1, np.maximum)


def gauss(a, sigma):
    if sigma <= 0:
        return a
    r = int(math.ceil(3 * sigma))
    k = np.exp(-0.5 * (np.arange(-r, r + 1) / sigma) ** 2)
    k /= k.sum()
    out = a
    for axis in (0, 1):
        pad = [(0, 0), (0, 0)]
        pad[axis] = (r, r)
        p = np.pad(out, pad, mode="edge")
        acc = np.zeros_like(out)
        n = out.shape[axis]
        for i, w in enumerate(k):
            sl = [slice(None), slice(None)]
            sl[axis] = slice(i, i + n)
            acc += w * p[tuple(sl)]
        out = acc
    return out


def lower_envelope(dem, r=ENV_R, sigma=ENV_SIGMA):
    """Morphological opening (removes bumps narrower than ~2r cells: roofs, domes) + smoothing."""
    return gauss(max_filter(min_filter(dem, r), r), sigma)


# ---------------------------------------------------------------------------------------------
# anchors
def _read_csv(path):
    lines = [ln for ln in path.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    return list(csv.DictReader(lines))


def os1865_affine():
    cps = _read_csv(OS_CPS)
    P = np.array([[float(c["px"]), float(c["py"]), 1.0] for c in cps])
    L = np.array([[float(c["x"]), float(c["y"])] for c in cps])
    coef = np.linalg.lstsq(P, L, rcond=None)[0]
    res = P @ coef - L
    return coef, cps, res


def load_os1865():
    coef, _, _ = os1865_affine()
    out = []
    for r in _read_csv(OS_SPOTS):
        x, y = np.array([float(r["px"]), float(r["py"]), 1.0]) @ coef
        out.append(dict(x=float(x), y=float(y), ft=float(r["feet"]), asl=float(r["feet"]) * FT,
                        kind=r["kind"], cls=r["cls"], note=r["note"], px=int(r["px"]), py=int(r["py"])))
    return out


# ---------------------------------------------------------------------------------------------
# flats
def _osm():
    return json.loads(OSM.read_text())


def _way(osm, wid):
    for w in osm["ways"]:
        if w["id"] == wid:
            return w
    raise KeyError(wid)


def flats_polygons(osm=None):
    """Flats with z in metres asl. The Haram is ONE flat at esplanade level, including the area under
    the Dome of the Rock's upper platform (OSM w137725307), which blender/landmarks_haram.py builds
    as a solid on top (coordination note, 2026-10-19)."""
    osm = osm or _osm()
    poly = json.loads(POLY.read_text())
    haram = Polygon(poly["haram"]).buffer(0)
    plaza = Polygon(_way(osm, 26492734)["pts"]).buffer(0)
    # prayer area: between the partition wall (OSM barrier=wall w45081552 / fences) and the Western Wall
    prayer = Polygon([(620.0, -20.4), (656.0, -14.6), (656.0, 40.0), (625.6, 31.5), (624.9, 24.1),
                      (627.3, 18.0), (613.9, 15.7), (617.7, -7.3)]).intersection(plaza).buffer(0)
    main = plaza.difference(prayer)
    main = max(main.geoms, key=lambda g: g.area) if main.geom_type == "MultiPolygon" else main
    main = main.intersection(Polygon([(560, -62), (660, -62), (660, 40), (560, 40)])).buffer(0)
    esplanade = sum(s["asl"] for s in ESPLANADE_SPOTS) / len(ESPLANADE_SPOTS) if ESPLANADE_SPOTS else 737.0
    m = {a["name"]: a for a in MODERN}
    return [
        dict(name="haram_esplanade", polygon=haram, asl=round(esplanade, 2),
             source="mean of %d OS 1865 spot heights on the esplanade (2412-2423 ft); Warren: Chain Gate "
                    "737.3, Mughrabi Gate 736.4 (Caspi 736.5); real surface varies +-1.5 m (NW rock "
                    "c. 741, Golden Gate hollow c. 729-732)" % len(ESPLANADE_SPOTS)),
        dict(name="western_wall_prayer_area", polygon=prayer,
             asl=m["Western Wall prayer area (post-1967)"]["asl"],
             source=m["Western Wall prayer area (post-1967)"]["source"]),
        dict(name="western_wall_plaza", polygon=main,
             asl=m["Western Wall plaza (main, behind the partition)"]["asl"],
             source=m["Western Wall plaza (main, behind the partition)"]["source"]),
    ]


ESPLANADE_SPOTS = []   # filled in build()


# ---------------------------------------------------------------------------------------------
# Gaussian process (Matern 3/2) on the residual anchor - envelope
def matern32(d, l, s):
    a = math.sqrt(3.0) * d / l
    return s * s * (1 + a) * np.exp(-a)


def _pdist(A, B):
    return np.sqrt(((A[:, None, :] - B[None, :, :]) ** 2).sum(-1))


class GP:
    def __init__(self, xy, r, sig, l=GP_L, s=GP_S, mean=0.0):
        self.xy, self.l, self.s, self.mean = xy, l, s, mean
        K = matern32(_pdist(xy, xy), l, s) + np.diag(sig ** 2)
        self.Kinv = np.linalg.inv(K)
        self.alpha = self.Kinv @ (r - mean)

    def predict(self, q, chunk=8000):
        out = np.empty(len(q))
        for i in range(0, len(q), chunk):
            out[i:i + chunk] = self.mean + matern32(_pdist(q[i:i + chunk], self.xy), self.l, self.s) @ self.alpha
        return out

    def loo(self):
        """Closed-form leave-one-out residuals (prediction without anchor i minus anchor i)."""
        return -self.alpha / np.diag(self.Kinv)


# ---------------------------------------------------------------------------------------------
def anchor_set(spots, flats, bm_offset):
    """Anchors used in the GP fit: (x, y, asl, sigma, label)."""
    haram = prep(flats[0]["polygon"].buffer(2.0))
    plaza = prep(flats[1]["polygon"].union(flats[2]["polygon"]).buffer(3.0))
    A = []
    for s in spots:
        p = Point(s["x"], s["y"])
        if s["cls"] in ("haram", "haramupper", "court") or haram.contains(p):
            continue                       # the Haram is a flat; Omariya rock court is not a street
        if s["cls"] in ("wailing", "mughrabi"):
            continue                       # Mughrabi quarter: cleared and regraded in 1967
        if "doubt" in s["note"]:
            continue                       # digit not legible on the scan
        if plaza.contains(p):
            continue
        z = s["asl"] - (bm_offset if s["kind"] == "B" else 0.0)
        sig = SIG["out"] if s["cls"] == "out" else SIG[s["kind"]]
        A.append((s["x"], s["y"], z, sig, "os1865:%s:%s" % (s["cls"], s["ft"])))
    # pseudo-anchors along the Western Wall plaza flats' edges, except on the Haram wall and at the
    # prayer area's north end (under Wilson's Arch, below Chain Street)
    wall = flats[0]["polygon"].buffer(3.0)
    for f in flats[1:]:
        ring = f["polygon"].exterior
        for t in np.arange(0, ring.length, 8.0):
            q = ring.interpolate(t)
            if wall.contains(q) or (f["name"] == "western_wall_prayer_area" and q.y > 20):
                continue
            A.append((q.x, q.y, f["asl"], SIG["edge"], "flat-edge:" + f["name"]))
    for pin in PINNED:
        v = np.array(pin["pts"])
        line = LineString(v[:, :2])
        cum = np.r_[0, np.cumsum(np.hypot(*np.diff(v[:, :2], axis=0).T))]
        for t in np.arange(0, line.length + 0.1, 6.0):
            q = line.interpolate(t)
            A.append((q.x, q.y, float(np.interp(t, cum, v[:, 2])), SIG["edge"], "pinned:" + pin["name"]))
    return A


def build(verbose=True, env_r=ENV_R, env_sigma=ENV_SIGMA, l=GP_L, s=GP_S, bm_offset=BM_OFFSET):
    osm = _osm()
    mos = dem_mosaic()
    GX, GY = grid_xy()
    dem = dem_sample(mos, GX, GY)
    env = lower_envelope(dem, env_r, env_sigma)
    spots = load_os1865()
    ESPLANADE_SPOTS[:] = [sp for sp in spots if sp["cls"] == "haram" and "golden-gate-low" not in sp["note"]
                          and "nw-corner" not in sp["note"]
                          and "upper" not in sp["note"]]
    flats = flats_polygons(osm)

    def env_at(x, y):
        return bilinear(env, (np.asarray(x) - X0) / STEP, (np.asarray(y) - Y0) / STEP)

    # bench mark offset: GP on spot heights only, predict at the bench marks
    if bm_offset is None:
        A0 = anchor_set([sp for sp in spots if sp["kind"] == "S"], flats, 0.0)
        xy0 = np.array([(a[0], a[1]) for a in A0])
        r0 = np.array([a[2] for a in A0]) - env_at(xy0[:, 0], xy0[:, 1])
        sig0 = np.array([a[3] for a in A0])
        g0 = GP(xy0, r0, sig0, l, s, float(np.median(r0)))
        bms = [sp for sp in spots if sp["kind"] == "B" and sp["cls"] == "in"]
        qb = np.array([(b["x"], b["y"]) for b in bms])
        pred = env_at(qb[:, 0], qb[:, 1]) + g0.predict(qb)
        diff = np.array([b["asl"] for b in bms]) - pred
        bm_offset = float(np.median(diff))
        if verbose:
            print("bench marks: %d, median(BM - ground from spots) = %+.2f m (IQR %.2f..%.2f)" %
                  (len(bms), bm_offset, *np.percentile(diff, [25, 75])))
        bm_offset = float(np.clip(bm_offset, 0.0, 1.0))

    A = anchor_set(spots, flats, bm_offset)
    xy = np.array([(a[0], a[1]) for a in A])
    z_anchor = np.array([a[2] for a in A])
    sig = np.array([a[3] for a in A])
    r = z_anchor - env_at(xy[:, 0], xy[:, 1])
    out_mask = np.array([a[4].startswith("os1865:out") for a in A])
    mean = float(np.median(r[out_mask])) if out_mask.any() else float(np.median(r))
    gp = GP(xy, r, sig, l, s, mean)
    q = np.c_[GX.ravel(), GY.ravel()]
    zg = (env.ravel() + gp.predict(q)).reshape(GX.shape)

    fit = env_at(xy[:, 0], xy[:, 1]) + gp.predict(xy)
    loo = gp.loo()
    lab = [a[4] for a in A]
    is_in = np.array([t.startswith("os1865:in") for t in lab])
    stats = dict(n=len(A), n_in=int(is_in.sum()),
                 fit_rms_in=float(np.sqrt(np.mean((fit - z_anchor)[is_in] ** 2))),
                 fit_max_in=float(np.max(np.abs(fit - z_anchor)[is_in])),
                 loo_rms_in=float(np.sqrt(np.mean(loo[is_in] ** 2))),
                 loo_mad_in=float(np.median(np.abs(loo[is_in]))),
                 loo_p90_in=float(np.percentile(np.abs(loo[is_in]), 90)),
                 raw_dem_bias_in=float(np.median((dem_sample(mos, xy[:, 0], xy[:, 1]) - z_anchor)[is_in])),
                 env_bias_in=float(np.median(-r[is_in])),
                 env_rms_in=float(np.sqrt(np.mean((r[is_in] - np.median(r[is_in])) ** 2))),
                 bm_offset=bm_offset, gp_mean=mean)
    return dict(osm=osm, mos=mos, GX=GX, GY=GY, dem=dem, env=env, zg=zg, spots=spots, flats=flats,
                anchors=A, fit=fit, loo=loo, z_anchor=z_anchor, stats=stats, gp=gp)


def burn_flats(zg, flats, GX, GY):
    z = zg.copy()
    for f in flats:
        m = contains_xy(f["polygon"], GX, GY)
        z[m] = f["asl"]
    return z


# ---------------------------------------------------------------------------------------------
# runtime API
_RT = None


def _runtime():
    global _RT
    if _RT is None:
        d = json.loads(OUT_JSON.read_text())
        zg = np.array(d.get("z_ground", d["z"]), dtype=float)
        flats = [(Polygon(f["polygon"]), f["z"]) for f in d.get("flats", [])]
        unders = [(LineString(u["pts"]), np.array(u["z_asl"], float) - d["datum_asl"])
                  for u in d.get("underpasses", [])]
        _RT = (d, zg, flats, unders)
    return _RT


def street_z(x, y, under=False):
    """Walkable street level (m, relative to the street at the Jaffa Gate node) at local x, y.
    Flats take precedence; elsewhere bilinear on the continuous grid (clamped at its edge).
    under=True: within 3 m of a listed underpass (e.g. Al-Wad beneath Chain Street) return the lower
    street's level instead of the upper one. Accepts scalars or numpy arrays."""
    d, zg, flats, unders = _runtime()
    xa, ya = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
    z = bilinear(zg, (xa - d["x0"]) / d["step"], (ya - d["y0"]) / d["step"])
    for poly, fz in flats:
        z = np.where(contains_xy(poly, xa, ya), fz, z)
    if under:
        pts = shapely.points(xa, ya)
        for line, uz in unders:
            t = shapely.line_locate_point(line, pts, normalized=True)
            cum = np.r_[0, np.cumsum(np.hypot(*np.diff(np.array(line.coords), axis=0).T))] / line.length
            z = np.where(shapely.distance(line, pts) < 3.0, np.interp(t, cum, uz), z)
    return float(z) if np.ndim(z) == 0 else z


def street_z_asl(x, y, under=False):
    return street_z(x, y, under) + _runtime()[0]["datum_asl"]


# ---------------------------------------------------------------------------------------------
# validation helpers
def chain(osm, items):
    """Polyline from a sequence of OSM way ids (oriented to continue from the current end) and points."""
    ways = {w["id"]: w["pts"] for w in osm["ways"] if w.get("pts")}
    pts = []
    for it in items:
        if isinstance(it, int):
            w = ways[it]
            if pts and math.dist(pts[-1], w[-1]) < math.dist(pts[-1], w[0]):
                w = w[::-1]
            pts += [tuple(p) for p in w]
        else:
            pts.append(tuple(it))
    clean = [pts[0]]
    for p in pts[1:]:
        if math.dist(p, clean[-1]) > 0.05:
            clean.append(p)
    return LineString(clean)


# Transects along OSM street centrelines (way ids from data/osm_local.json; points bridge gaps).
TRANSECTS = {
    "A  Jaffa Gate - David St - Chain St - Gate of the Chain":
        [(0, 0), (48, 0), 279685572, 277508275, 26492743, 291836757],
    "B  Damascus Gate - Al-Wad - Western Wall plaza":
        [(268, 557), 616186087, 616186086, 26496070, 362057747, 362057745, 508241135, 277508274,
         (575, 0), (592, -20)],
    "C  Lions' Gate - Via Dolorosa - Holy Sepulchre":
        [288395746, 290986904, 744664057, 744664059, 26492728, 44830379, 582488415, 362057747,
         26506003, 616344390, 616344389, (321, 171), 256298883, 612045234],
    "D  New Gate - Jaffa Gate - Armenian Patriarchate Rd - Zion Gate":
        [(-128, 297), 26491282, 1548979886, 1548979887, 26491278, (5, 0), 265414845, 26506007, 44376249,
         44376240, 290669005, 26492736],
    "E  Zion Gate - Jewish Quarter - Dung Gate":
        [(221, -410), 496167694, 290677058, 290677070, 926204888, 496167693, 771909614, 290693162],
}


def transect(zfun, line, step=5.0):
    ts = np.arange(0, line.length + 1e-6, step)
    pts = np.array([line.interpolate(t).coords[0] for t in ts])
    return ts, pts, zfun(pts[:, 0], pts[:, 1])


# ---------------------------------------------------------------------------------------------
# rendering
def _marching_squares(Z, level):
    """Line segments (in grid index coords) where Z crosses level."""
    a, b, c, d = Z[:-1, :-1], Z[:-1, 1:], Z[1:, 1:], Z[1:, :-1]     # corners: (0,0) (1,0) (1,1) (0,1)
    segs = []
    jj, ii = np.mgrid[0:Z.shape[0] - 1, 0:Z.shape[1] - 1]

    def cross(v0, v1):
        with np.errstate(divide="ignore", invalid="ignore"):
            return np.clip((level - v0) / (v1 - v0), 0, 1)
    e_top = ((a < level) != (b < level))       # edge (0,0)-(1,0)
    e_right = ((b < level) != (c < level))     # (1,0)-(1,1)
    e_bot = ((d < level) != (c < level))       # (0,1)-(1,1)
    e_left = ((a < level) != (d < level))      # (0,0)-(0,1)
    pt = {
        "t": (ii + cross(a, b), jj + 0.0),
        "r": (ii + 1.0, jj + cross(b, c)),
        "b": (ii + cross(d, c), jj + 1.0),
        "l": (ii + 0.0, jj + cross(a, d)),
    }
    E = {"t": e_top, "r": e_right, "b": e_bot, "l": e_left}
    keys = ["t", "r", "b", "l"]
    for k1 in range(4):
        for k2 in range(k1 + 1, 4):
            m = E[keys[k1]] & E[keys[k2]]
            # cells with 4 crossings (saddles) produce extra segments; acceptable for a preview
            if m.any():
                x1, y1 = pt[keys[k1]]
                x2, y2 = pt[keys[k2]]
                segs.append(np.c_[x1[m], y1[m], x2[m], y2[m]])
    return np.vstack(segs) if segs else np.zeros((0, 4))


def render(res, z, path=OUT_PNG, scale=3):
    GX, GY, flats = res["GX"], res["GY"], res["flats"]
    datum = res["datum_asl"]
    zasl = z + datum
    H, W = z.shape
    # hillshade
    gy, gx = np.gradient(zasl, STEP)
    az, alt = math.radians(315), math.radians(40)
    slope = np.arctan(np.hypot(gx, gy) * 1.6)
    aspect = np.arctan2(-gx, gy)
    shade = np.sin(alt) * np.cos(slope) + np.cos(alt) * np.sin(slope) * np.cos(az - aspect)
    shade = np.clip(shade, 0, 1)
    lo, hi = 700.0, 795.0
    t = np.clip((zasl - lo) / (hi - lo), 0, 1)
    stops = np.array([[0.00, 46, 104, 92], [0.25, 120, 160, 96], [0.5, 214, 196, 128],
                      [0.75, 196, 140, 92], [1.0, 245, 240, 232]])
    rgb = np.stack([np.interp(t, stops[:, 0], stops[:, k]) for k in (1, 2, 3)], -1)
    rgb = rgb * (0.45 + 0.55 * shade[..., None])
    img = Image.fromarray(np.flipud(rgb).clip(0, 255).astype(np.uint8)).resize((W * scale, H * scale), Image.BILINEAR)
    dr = ImageDraw.Draw(img, "RGBA")

    def P(x, y):                                   # local -> image
        return ((x - X0) / STEP * scale, (H - 1 - (y - Y0) / STEP) * scale)

    # contours every 2 m (10 m bold)
    for lev in np.arange(math.ceil(zasl.min() / 2) * 2, zasl.max(), 2.0):
        segs = _marching_squares(zasl, lev)
        bold = abs(lev / 10 - round(lev / 10)) < 1e-6
        col = (40, 25, 10, 200) if bold else (40, 25, 10, 90)
        for x1, y1, x2, y2 in segs:
            dr.line([(x1 * scale, (H - 1 - y1) * scale), (x2 * scale, (H - 1 - y2) * scale)], fill=col,
                    width=2 if bold else 1)
    try:
        font = ImageFont.load_default(size=13)
        big = ImageFont.load_default(size=18)
    except TypeError:
        font = big = ImageFont.load_default()
    # sectors
    sec = json.loads(SECTORS.read_text())["sectors"]
    for s in sec:
        g = shape(s["geom"])
        for part in getattr(g, "geoms", [g]):
            dr.line([P(*p) for p in part.exterior.coords], fill=(255, 255, 255, 150), width=2)
        c = g.representative_point()
        dr.text(P(c.x, c.y), s["id"].split("_", 1)[1], fill=(255, 255, 255, 230), font=font, anchor="mm",
                stroke_width=2, stroke_fill=(0, 0, 0, 160))
    # walls
    poly = json.loads(POLY.read_text())
    dr.line([P(*p) for p in poly["ring"]], fill=(20, 20, 20, 255), width=4)
    # flats
    for f in flats:
        g = f["polygon"]
        dr.polygon([P(*p) for p in g.exterior.coords], outline=(0, 230, 255, 255), fill=(0, 230, 255, 40))
    # steps
    for w in res["osm"]["ways"]:
        if w["tags"].get("highway") == "steps" and w.get("pts") and not w["tags"].get("tunnel"):
            dr.line([P(*p) for p in w["pts"]], fill=(230, 20, 20, 255), width=3)
    # transects
    for name, (line, _ts, _zz) in res.get("transects", {}).items():
        dr.line([P(*p) for p in line.coords], fill=(255, 0, 255, 200), width=2)
        x, y = P(*line.coords[0])
        dr.text((x + 6, y + 6), name[0], fill=(255, 0, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    # anchors
    for a in res["anchors"]:
        if a[4].startswith("os1865"):
            x, y = P(a[0], a[1])
            col = (255, 255, 0, 255) if ":in:" in a[4] else (255, 160, 0, 255)
            dr.ellipse([x - 2, y - 2, x + 2, y + 2], fill=col)
    # gates
    for name, x, y in [("Jaffa", 0, 0), ("New", -128, 297), ("Damascus", 268, 557), ("Herod's", 588, 700),
                       ("Lions'", 889, 467), ("Dung", 628, -199), ("Zion", 204, -415)]:
        px, py = P(x, y)
        dr.text((px, py - 12), "%s %.0f" % (name, float(street_z_from(res, x, y)) + datum), fill=(255, 255, 255),
                font=font, anchor="mm", stroke_width=2, stroke_fill=(0, 0, 0))
    dr.text((10, 10), "Street-level terrain (m asl), contours 2 m (bold 10 m). z=0 at Jaffa Gate = %.1f m asl" % datum,
            fill=(255, 255, 255), font=big, stroke_width=2, stroke_fill=(0, 0, 0))
    dr.text((10, 34), "cyan: flats  red: OSM steps  yellow/orange dots: 1865 OS anchors in/outside walls",
            fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    # colour bar
    for k in range(200):
        tt = k / 199
        c = [int(np.interp(tt, stops[:, 0], stops[:, i])) for i in (1, 2, 3)]
        dr.line([(10 + k, 58), (10 + k, 70)], fill=tuple(c))
    dr.text((10, 74), "%d" % lo, fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    dr.text((185, 74), "%d" % hi, fill=(255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0))
    img.save(path)


def street_z_from(res, x, y):
    """street_z on an in-memory build result (relative to datum)."""
    z = bilinear(res["zg_rel"], (np.asarray(x, float) - X0) / STEP, (np.asarray(y, float) - Y0) / STEP)
    for f in res["flats_rel"]:
        z = np.where(contains_xy(f[0], np.asarray(x, float), np.asarray(y, float)), f[1], z)
    return z


# ---------------------------------------------------------------------------------------------
def explore():
    """Parameter search by leave-one-out RMS on inside-wall anchors."""
    print("env_r env_sigma  L    S   | env_rms  loo_rms  loo_mad  fit_max")
    for env_r, env_sigma in [(0, 0), (5, 3), (8, 4), (10, 4), (15, 5), (20, 6)]:
        for l, s in [(30, 4), (45, 4), (60, 4), (45, 8), (80, 6)]:
            st = build(False, env_r, env_sigma, l, s, 0.4)["stats"]
            print("%4d %6.1f %6.0f %4.0f  | %6.2f  %6.2f  %6.2f  %6.2f" % (
                env_r, env_sigma, l, s, st["env_rms_in"], st["loo_rms_in"], st["loo_mad_in"], st["fit_max_in"]))


def main():
    res = build()
    st = res["stats"]
    GX, GY = res["GX"], res["GY"]
    datum = float(bilinear(res["zg"], np.array((0 - X0) / STEP), np.array((0 - Y0) / STEP)))
    datum = round(datum, 2)
    res["datum_asl"] = datum
    z = burn_flats(res["zg"], res["flats"], GX, GY) - datum
    zg_rel = res["zg"] - datum
    res["zg_rel"] = zg_rel
    res["flats_rel"] = [(f["polygon"], f["asl"] - datum) for f in res["flats"]]

    print("\nanchors in GP: %d (%d inside-wall OS 1865)  BM offset %.2f m  GP mean %.2f m" %
          (st["n"], st["n_in"], st["bm_offset"], st["gp_mean"]))
    print("raw DEM minus street anchors (inside walls): median %+.1f m" % st["raw_dem_bias_in"])
    print("lower envelope minus anchors: median %+.1f m, rms about median %.1f m" % (st["env_bias_in"], st["env_rms_in"]))
    print("model fit at inside anchors: rms %.2f m, max %.2f m" % (st["fit_rms_in"], st["fit_max_in"]))
    print("leave-one-out (inside): rms %.2f m, median |err| %.2f m, 90%% %.2f m" %
          (st["loo_rms_in"], st["loo_mad_in"], st["loo_p90_in"]))
    print("datum: street at Jaffa Gate node = %.2f m asl" % datum)

    flats_out = []
    for f in res["flats"]:
        g = f["polygon"].simplify(0.3)
        flats_out.append(dict(name=f["name"], z=round(f["asl"] - datum, 2), z_asl=f["asl"],
                              area_m2=round(g.area), source=f["source"],
                              polygon=[[round(x, 2), round(y, 2)] for x, y in g.exterior.coords]))
    anchors_out = []
    for s, (x, y) in zip(res["spots"], [(sp["x"], sp["y"]) for sp in res["spots"]]):
        anchors_out.append(dict(x=round(x, 1), y=round(y, 1), asl=round(s["asl"], 2), ft=s["ft"],
                                kind=s["kind"], cls=s["cls"]))
    data = {
        "x0": X0, "y0": Y0, "step": STEP, "nx": NX, "ny": NY,
        "datum_asl": datum,
        "units": "metres; z relative to the street at the Jaffa Gate node (local 0,0); z[j][i] at "
                 "x = x0 + i*step, y = y0 + j*step",
        "z": [[round(float(v), 2) for v in row] for row in z],
        "z_ground": [[round(float(v), 2) for v in row] for row in zg_rel],
        "flats": flats_out,
        "underpasses": UNDERPASSES,
        "pinned_profiles": PINNED,
        "platforms_info": [dict(name="dome_of_the_rock_upper_platform", osm="w137725307",
                                z_asl_measured=742.2, z=round(742.2 - datum, 2),
                                note="NOT a flat here (built as a solid by blender/landmarks_haram.py); "
                                     "OS 1865 spots 2434-2439 ft and Warren 742.0 m put its top ~5 m above "
                                     "the esplanade")],
        "sources": [
            "AWS Terrain Tiles (terrarium z15, SRTM-derived DSM) - regional trend via lower envelope "
            "(opening %d m window, Gaussian %.0f m)" % ((2 * ENV_R + 1) * STEP, ENV_SIGMA * STEP),
            "Ordnance Survey of Jerusalem 1:2500, Wilson 1864-65 (public domain; Princeton University "
            "Library ark:/88435/p8418q700): %d spot heights / bench marks transcribed, "
            "data/raw/terrain/os1865_spot_heights.csv" % len(res["spots"]),
            "Warren 1884 / Caspi Haram levels (templemount.org 'Table I. Elevations on Mount Moriah')",
            "Western Wall plaza: 1865 level minus the 1967-68 lowering (~2 m, two Herodian courses)",
            "OSM (ODbL) polygons for flats, walls and the Haram",
        ],
        "method": "z_ground = lower_envelope(DEM) + GP(Matern-3/2, L=%.0f m) through anchors; flats burned "
                  "into z; street_z(): flats first, else bilinear on z_ground. Fit rms %.2f m at %d "
                  "inside-wall anchors, leave-one-out rms %.2f m." % (GP_L, st["fit_rms_in"], st["n_in"],
                                                                       st["loo_rms_in"]),
        "anchors_modern": [{k: v for k, v in a.items()} for a in MODERN],
        "anchors_os1865": anchors_out,
    }
    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")))
    print("wrote %s (%.1f MB)" % (OUT_JSON.relative_to(ROOT), OUT_JSON.stat().st_size / 1e6))
    global _RT
    _RT = None
    validate(res, datum)
    render(res, z)
    print("wrote", OUT_PNG.relative_to(ROOT))


def validate(res, datum):
    osm = res["osm"]
    zf = lambda x, y: street_z(x, y) + datum   # noqa: E731
    zfu = lambda x, y: street_z(x, y, under=True) + datum   # noqa: E731
    # modern anchors
    print("\nmodern / literature checks (model vs value, m asl):")
    for a in MODERN:
        if a["asl"] is None:
            continue
        print("  %-52s value %6.1f  model %6.1f  (%s)" % (a["name"][:52], a["asl"], zf(a["x"], a["y"]), a["role"]))
    # elevator
    # the elevator's 65 m tunnel runs east from Misgav Ladach (x~498) to the plaza's west edge (x~565),
    # so its top is on the stretch level with the plaza (y -62..-20)
    mz = np.mean([zf(498.0, yy) for yy in np.arange(-62, -19, 4.0)])
    print("  Misgav Ladach St (y -62..-20) %.1f  minus WW plaza %.1f = %.1f m (elevator: 22-26 m)" % (
        mz, zf(592, -20), mz - zf(592, -20)))
    print("\ngates: OS 1865 level vs model (m asl)")
    for s in res["spots"]:
        if s["note"].endswith(("gate-BM", "gate-jamb", "-inside", "-outside", "lions-gate", "near-dung-gate",
                               "chain-st-end")):
            print("  %-18s %-2s %7.2f   model %7.2f" % (s["note"], s["kind"], s["asl"], zf(s["x"], s["y"])))
    print("  Dome platform 742.2 - esplanade %.1f = %.1f m;  esplanade - WW prayer area = %.1f m" % (
        zf(760, 250), 742.2 - zf(760, 250), zf(760, 250) - zf(632, 8)))

    # steps vs other streets
    poly = json.loads(POLY.read_text())
    ring = prep(Polygon(poly["ring"]))
    gy, gx = np.gradient(res["zg"], STEP)
    grad = np.hypot(gx, gy)

    def grade_along(w):
        a = np.array(w["pts"])
        L = np.hypot(*np.diff(a, axis=0).T).sum()
        if L < 4:
            return None
        zz = zf(a[:, 0], a[:, 1])
        return L, abs(zz[-1] - zz[0]) / L, float(np.mean(bilinear(grad, (a[:, 0] - X0) / STEP, (a[:, 1] - Y0) / STEP)))
    st_steps, st_other = [], []
    for w in osm["ways"]:
        hw = w["tags"].get("highway")
        if not hw or not w.get("pts") or w["tags"].get("tunnel"):
            continue
        c = np.mean(w["pts"], axis=0)
        if not ring.contains(Point(*c)):
            continue
        g = grade_along(w)
        if g is None:
            continue
        if hw == "steps":
            st_steps.append(g)
        elif hw in ("pedestrian", "footway", "residential", "living_street", "service", "path", "unclassified"):
            st_other.append(g)
    ss, so = np.array(st_steps), np.array(st_other)
    print("\nOSM steps inside walls: %d ways; terrain gradient at steps: median %.1f%% (other streets %.1f%%);"
          " end-to-end grade median %.1f%% (others %.1f%%); steps with gradient > 6%%: %d%% (others %d%%)" % (
              len(ss), 100 * np.median(ss[:, 2]), 100 * np.median(so[:, 2]), 100 * np.median(ss[:, 1]),
              100 * np.median(so[:, 1]), 100 * np.mean(ss[:, 2] > 0.06), 100 * np.mean(so[:, 2] > 0.06)))

    # transects
    res["transects"] = {}
    for name, items in TRANSECTS.items():
        line = chain(osm, items)
        ts, pts, zz = transect(zfu if "Al-Wad" in name else zf, line, 5.0)   # B runs under Chain St
        ups = np.diff(zz)
        print("\n%s  (%.0f m)" % (name, line.length))
        print("   dist  " + " ".join("%6.0f" % t for t in ts[::10]) + " %6.0f" % ts[-1])
        print("   z asl " + " ".join("%6.1f" % v for v in zz[::10]) + " %6.1f" % zz[-1])
        print("   start %.1f  end %.1f  net %+.1f m; max 5 m-grade %.0f%%; total climb %.1f m, total descent %.1f m" % (
            zz[0], zz[-1], zz[-1] - zz[0], 100 * np.max(np.abs(ups)) / 5, ups[ups > 0].sum(), -ups[ups < 0].sum()))
        res["transects"][name] = (line, ts, zz)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "explore":
        explore()
    else:
        main()

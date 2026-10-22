"""Real photographs of the iconic places (data/qa/iconic.json) from Wikimedia Commons, for comparing the
model with what a visitor sees: geotagged files near the place plus a search by its name.

    python3 pipeline/fetch_iconic_photos.py [place id ...] [--n 12]

-> data/photos_ref/iconic/<place>/NN_<pageid>.jpg and index.json (title, page, licence, artist, x, y).
"""
import json
import math
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "old-city-walker-poc/0.2 (iconic reference photos)"
API = "https://commons.wikimedia.org/w/api.php"
ORIGIN = json.loads((ROOT / "data/osm_local.json").read_text())["origin"]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 0) + 2 ** attempt)
    raise RuntimeError("rate limited: " + url)


def api(**q):
    q.update(format="json")
    return json.loads(get(API + "?" + urllib.parse.urlencode(q)))


def to_latlon(x, y):
    lat = ORIGIN["lat"] + y / 111320.0
    lon = ORIGIN["lon"] + x / (111320.0 * math.cos(math.radians(ORIGIN["lat"])))
    return lat, lon


def to_xy(lat, lon):
    return ((lon - ORIGIN["lon"]) * 111320.0 * math.cos(math.radians(ORIGIN["lat"])), (lat - ORIGIN["lat"]) * 111320.0)


def info(titles):
    out = {}
    for i in range(0, len(titles), 40):
        r = api(action="query", titles="|".join(titles[i:i + 40]), prop="imageinfo|coordinates",
                iiprop="url|extmetadata|size|mime", iiurlwidth=800)
        for p in r.get("query", {}).get("pages", {}).values():
            ii = (p.get("imageinfo") or [{}])[0]
            if not ii.get("thumburl") or not str(ii.get("mime", "")).startswith("image/jpeg"):
                continue
            md = ii.get("extmetadata", {})
            c = (p.get("coordinates") or [{}])[0]
            xy = to_xy(c["lat"], c["lon"]) if "lat" in c else (None, None)
            out[p["title"]] = {"pageid": p["pageid"], "title": p["title"], "thumb": ii["thumburl"],
                               "page": ii.get("descriptionurl"), "w": ii.get("width"), "h": ii.get("height"),
                               "licence": md.get("LicenseShortName", {}).get("value"),
                               "artist": md.get("Artist", {}).get("value", "")[:200],
                               "x": None if xy[0] is None else round(xy[0], 1),
                               "y": None if xy[1] is None else round(xy[1], 1)}
    return out


def main():
    args = sys.argv[1:]
    n = 12
    if "--n" in args:
        n = int(args[args.index("--n") + 1])
        args = [a for i, a in enumerate(args) if a != "--n" and (i == 0 or args[i - 1] != "--n")]
    places = json.loads((ROOT / "data/qa/iconic.json").read_text())["places"]
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    for pl in places:
        if args and pl["id"] not in args:
            continue
        if "osm" in pl:
            b = next(b for b in osm["buildings"] if b["id"] == pl["osm"])
            xs = [p[0] for p in b["outer"][0]]
            ys = [p[1] for p in b["outer"][0]]
            cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        else:
            cx, cy = pl["at"]
        lat, lon = to_latlon(cx, cy)
        titles = []
        r = api(action="query", list="geosearch", gscoord="%f|%f" % (lat, lon), gsradius=max(60, pl.get("r", 25) * 3),
                gsnamespace=6, gslimit=40)
        titles += [g["title"] for g in r.get("query", {}).get("geosearch", [])]
        name = pl["name"].split(" and ")[0].split(" / ")[0]
        r = api(action="query", list="search", srsearch="%s Jerusalem" % name, srnamespace=6, srlimit=30)
        titles += [s["title"] for s in r.get("query", {}).get("search", [])]
        titles = list(dict.fromkeys(titles))
        meta = info(titles)
        out_dir = ROOT / "data/photos_ref/iconic" / pl["id"]
        out_dir.mkdir(parents=True, exist_ok=True)
        idx = []
        for k, t in enumerate([t for t in titles if t in meta][:n]):
            m = meta[t]
            fn = "%02d_%d.jpg" % (k, m["pageid"])
            if not (out_dir / fn).exists():
                (out_dir / fn).write_bytes(get(m["thumb"]))
                time.sleep(0.3)
            idx.append(dict(m, file=fn))
        (out_dir / "index.json").write_text(json.dumps(idx, indent=1, ensure_ascii=False))
        print("%-18s %2d photos (%d candidates)" % (pl["id"], len(idx), len(titles)))


if __name__ == "__main__":
    main()

"""Collect geotagged reference photos from Wikimedia Commons around the PoC area.

Uses the Commons geosearch API (no key), keeps camera position where available, licence and
author, and downloads ~1000 px thumbnails to data/photos/. Reference only: these are not used
as textures.

    python3 pipeline/fetch_photos.py [max_download]
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from osm_to_local import to_latlon, to_local  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data/photos"
API = "https://commons.wikimedia.org/w/api.php"
UA = "old-city-walker-poc/0.1 (personal research; yuranu)"
# sample points (local metres) along gate -> square -> David Street
CENTRES = [(0, 0), (40, 5), (80, 10), (120, 10), (60, -30)]
BOX = (-40, -70, 150, 60)


def api(params):
    q = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(q, headers={"User-Agent": UA})
    d = None
    for attempt in range(6):
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                d = json.load(r)
            if "query" in d:
                return d
        except urllib.error.HTTPError as e:   # 429: honour Retry-After
            if e.code != 429:
                raise
            time.sleep(int(e.headers.get("Retry-After") or 0) + 2 ** attempt)
            continue
        time.sleep(2 ** attempt)              # maxlag responses carry no "query"
    raise RuntimeError("Commons API: %s" % str(d)[:300])


def main():
    max_dl = int(sys.argv[1]) if len(sys.argv) > 1 else 120
    OUT.mkdir(parents=True, exist_ok=True)
    found = {}
    for cx, cy in CENTRES:
        lat, lon = to_latlon(cx, cy)
        r = api({"action": "query", "list": "geosearch", "gscoord": "%f|%f" % (lat, lon),
                 "gsradius": 60, "gsnamespace": 6, "gslimit": 500})
        for g in r["query"]["geosearch"]:
            found[g["pageid"]] = g
        time.sleep(1.5)
    print("unique geotagged files:", len(found))

    recs = []
    ids = list(found)
    for i in range(0, len(ids), 40):
        chunk = "|".join(map(str, ids[i:i + 40]))
        r = api({"action": "query", "pageids": chunk, "prop": "imageinfo|coordinates",
                 "iiprop": "url|extmetadata|size|mime", "iiurlwidth": 1280,
                 "coprop": "type|dim", "coprimary": "all"})
        for pid, p in r["query"]["pages"].items():
            ii = (p.get("imageinfo") or [{}])[0]
            if not ii.get("mime", "").startswith("image/jpeg"):
                continue
            meta = ii.get("extmetadata", {})
            cam = next((c for c in p.get("coordinates", []) if c.get("primary") is not None), None) \
                or found[int(pid)]
            x, y = to_local(cam["lat"], cam["lon"])
            if not (BOX[0] <= x <= BOX[2] and BOX[1] <= y <= BOX[3]):
                continue
            recs.append({"pageid": int(pid), "title": p["title"], "x": x, "y": y,
                         "thumb": ii.get("thumburl"), "page": ii.get("descriptionurl"),
                         "w": ii.get("width"), "h": ii.get("height"),
                         "date": meta.get("DateTimeOriginal", {}).get("value", "")[:10],
                         "licence": meta.get("LicenseShortName", {}).get("value"),
                         "artist": meta.get("Artist", {}).get("value", "")[:200]})
        time.sleep(1.5)
    # newest first: the square was repaved and buildings restored over the years
    recs.sort(key=lambda r: r["date"] or "0000", reverse=True)
    print("JPEGs with camera inside the PoC box:", len(recs))
    for n, rec in enumerate(recs[:max_dl]):
        fn = OUT / ("%03d_%d.jpg" % (n, rec["pageid"]))
        rec["file"] = fn.name
        if not fn.exists() and rec["thumb"]:
            req = urllib.request.Request(rec["thumb"], headers={"User-Agent": UA})
            for attempt in range(6):
                try:
                    with urllib.request.urlopen(req, timeout=60) as r:
                        fn.write_bytes(r.read())
                    break
                except urllib.error.HTTPError as e:          # 429s happen; back off
                    err = e
                    time.sleep(int(e.headers.get("Retry-After") or 0) + 2 ** attempt)
            else:
                print("  failed", rec["title"], err)
            time.sleep(1.0)
    (OUT / "index.json").write_text(json.dumps(recs, indent=1, ensure_ascii=False))
    print("downloaded", min(max_dl, len(recs)), "->", OUT)


if __name__ == "__main__":
    main()

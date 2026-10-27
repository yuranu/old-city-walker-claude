"""Re-download reference photographs listed in data/photos*/**/index.json.

The repository versions only the metadata (title, page, author, licence, local file name); the
images are restored with this script (./fetch_data.sh --photos runs it and checks the photos the
evaluation loop needs against data/inputs.sha256).

    python3 pipeline/fetch_ref_photos.py [dir ...]     # default: data/photos and data/photos_ref/*
"""
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
UA = "old-city-walker-poc/0.2 (reference restore)"
API = "https://commons.wikimedia.org/w/api.php"


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


def thumb_for(title, width=1280):
    q = API + "?" + urllib.parse.urlencode({"action": "query", "titles": title, "prop": "imageinfo",
                                            "iiprop": "url", "iiurlwidth": width, "format": "json"})
    pages = json.loads(get(q))["query"]["pages"]
    ii = next(iter(pages.values())).get("imageinfo") or [{}]
    return ii[0].get("thumburl")


def restore(d: Path):
    idx = json.loads((d / "index.json").read_text())
    items = idx if isinstance(idx, list) else idx.get("photos", [])
    n = 0
    for it in items:
        fn = it.get("file")
        if not fn or (d / fn).exists():
            continue
        url = it.get("thumb") or (thumb_for(it["title"]) if it.get("title") else None)
        if not url:
            continue
        (d / fn).write_bytes(get(url))
        n += 1
        time.sleep(1.2)
    print("%s: restored %d" % (d.relative_to(ROOT), n))


def main():
    dirs = [Path(a) for a in sys.argv[1:]] or [ROOT / "data/photos"] + sorted((ROOT / "data/photos_ref").glob("*/"))
    for d in dirs:
        if (d / "index.json").exists():
            restore(d)


if __name__ == "__main__":
    main()

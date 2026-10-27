"""CC0 PBR textures from Poly Haven: the originals are a versioned snapshot in data/raw/polyhaven/<id>/
(diff, nor, rough + info.json with the source URLs and size); this writes the tinted copies and
data/textures/manifest.json. Only a texture missing from the snapshot is downloaded (api.polyhaven.com).

    python3 pipeline/fetch_textures.py [res]      # res: 1k | 2k (default) | 4k, for new downloads
"""
import json
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data/raw/polyhaven"
OUT = ROOT / "data/textures"
UA = "old-city-walker-poc/0.1"

# role -> (Poly Haven id, metres per texture repeat, RGB tint). Chosen and tinted against the
# Commons reference photos: Jerusalem limestone is warm cream, the plaza paving is pale.
TEXTURES = {
    "ashlar": ("sandstone_blocks_08", 3.0, (1.08, 1.03, 0.94)),   # dressed stone: hotels, institutions
    "rubble": ("sandstone_blocks_05", 3.0, (1.10, 1.04, 0.95)),   # coursed rough blocks: older houses
    "fort": ("sandstone_blocks_08", 5.5, (1.04, 0.99, 0.91)),     # same ashlar, bigger blocks: walls, citadel
    "paving": ("square_cobblestone", 3.0, (1.40, 1.32, 1.15)),    # (legacy; plaza paving is generated)
    "dressed": ("sandstone_blocks_08", 1.6, (1.22, 1.17, 1.06)),  # lighter, finer dressed stone: frames, sills, cornices
}
MAPS = {"Diffuse": "diff", "nor_gl": "nor", "Rough": "rough"}


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def download(pid, res):
    """Snapshot one texture into data/raw/polyhaven/<pid>/ (add its files to data/inputs.sha256)."""
    files = json.loads(get("https://api.polyhaven.com/files/" + pid))
    info = json.loads(get("https://api.polyhaven.com/info/" + pid))
    d = RAW / pid
    d.mkdir(parents=True, exist_ok=True)
    meta = {"id": pid, "page": "https://polyhaven.com/a/" + pid, "licence": "CC0", "res": res,
            "dimensions_mm": info.get("dimensions", [2000, 2000]), "maps": {}}
    for key, short in MAPS.items():
        entry = files.get(key, {}).get(res, {}).get("jpg") or files.get(key, {}).get(res, {}).get("png")
        if not entry:
            print("  missing", pid, key)
            continue
        fn = d / ("%s.%s" % (short, entry["url"].rsplit(".", 1)[-1]))
        fn.write_bytes(get(entry["url"]))
        meta["maps"][short] = {"file": fn.name, "url": entry["url"], "md5": entry.get("md5")}
    (d / "info.json").write_text(json.dumps(meta, indent=1))
    return meta


def main():
    res = sys.argv[1] if len(sys.argv) > 1 else "2k"
    manifest = {}
    for role, (pid, tile, tint) in TEXTURES.items():
        src = RAW / pid
        meta = json.loads((src / "info.json").read_text()) if (src / "info.json").exists() else download(pid, res)
        manifest[role] = {"id": pid, "tile": tile, "tint": tint, "maps": {},
                          "size_m": [v / 1000 for v in meta["dimensions_mm"]]}
        for short, m in meta["maps"].items():
            fn = src / m["file"]
            if short == "diff":                    # tinted copy per role
                tfn = OUT / pid / ("diff_%s.jpg" % role)
                tfn.parent.mkdir(parents=True, exist_ok=True)
                im = Image.open(fn).convert("RGB")
                # desaturate towards warm grey-cream first (photo-matched evaluation: the real stone is
                # far less saturated than the raw textures), then tint
                grey = im.convert("L").convert("RGB")
                im = Image.blend(im, grey, 0.45)
                r, g, b = im.split()
                im = Image.merge("RGB", [ch.point(lambda v, k=k: min(255, int(v * k))) for ch, k in zip((r, g, b), tint)])
                im.save(tfn, quality=90)
                fn = tfn
            manifest[role]["maps"][short] = str(fn.relative_to(ROOT))
        print("%-7s %-28s tile %.1f m" % (role, pid, tile))
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=1))


if __name__ == "__main__":
    main()

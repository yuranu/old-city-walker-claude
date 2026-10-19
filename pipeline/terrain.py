"""Decode Terrarium elevation tiles (AWS open data, SRTM-derived in this region) into a local grid.

Writes data/terrain.json: a regular grid in the local frame (see osm_to_local.py), metres above
sea level, plus a PNG preview. 30 m source data: good for the overall slope, not for steps.

    python3 pipeline/terrain.py
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
from osm_to_local import to_latlon  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
Z = 15
TILES = ROOT / "data/raw/terrain"
_cache = {}


def tile_px(lat, lon):
    n = 2 ** Z
    x = (lon + 180) / 360 * n
    y = (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) / 2 * n
    return x, y


def elev_at_tilepx(tx, ty, px, py):
    key = (tx, ty)
    if key not in _cache:
        _cache[key] = Image.open(TILES / ("%d_%d_%d.png" % (Z, tx, ty))).convert("RGB").load()
    r, g, b = _cache[key][px, py]
    return r * 256 + g + b / 256 - 32768


def elevation(lat, lon):
    """Bilinear sample."""
    x, y = tile_px(lat, lon)
    X, Y = x * 256 - 0.5, y * 256 - 0.5
    x0, y0 = math.floor(X), math.floor(Y)
    fx, fy = X - x0, Y - y0

    def e(ix, iy):
        return elev_at_tilepx(ix // 256, iy // 256, ix % 256, iy % 256)
    return ((e(x0, y0) * (1 - fx) + e(x0 + 1, y0) * fx) * (1 - fy) +
            (e(x0, y0 + 1) * (1 - fx) + e(x0 + 1, y0 + 1) * fx) * fy)


def main():
    xmin, ymin, xmax, ymax, step = -150, -200, 300, 200, 5.0
    nx, ny = int((xmax - xmin) / step) + 1, int((ymax - ymin) / step) + 1
    grid = [[round(elevation(*to_latlon(xmin + i * step, ymin + j * step)), 2) for i in range(nx)] for j in range(ny)]
    (ROOT / "data/terrain.json").write_text(json.dumps(
        {"xmin": xmin, "ymin": ymin, "step": step, "nx": nx, "ny": ny, "z": grid,
         "source": "AWS Terrain Tiles (terrarium, z15), SRTM-derived"}))
    flat = [v for row in grid for v in row]
    lo, hi = min(flat), max(flat)
    img = Image.new("L", (nx, ny))
    img.putdata([int(255 * (grid[ny - 1 - j][i] - lo) / (hi - lo)) for j in range(ny) for i in range(nx)])
    img.resize((nx * 2, ny * 2)).save(ROOT / "data/terrain_preview.png")
    print("grid %dx%d  elev %.1f..%.1f m" % (nx, ny, lo, hi))
    for name, x, y in [("Jaffa Gate", 0, 0), ("square centre", 45, 5), ("David St @x=100", 100, 8),
                       ("David St @x=160", 160, 8), ("Citadel courtyard", 45, -60), ("Christ Church", 140, -60)]:
        print("  %-20s %.1f" % (name, elevation(*to_latlon(x, y))))


if __name__ == "__main__":
    main()

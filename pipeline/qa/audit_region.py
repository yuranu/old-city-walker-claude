"""Coplanar-overlap (flicker) audit across ALL parts (base + every sector, LOD excluded) for a region,
in one Blender scene, and convert the result into QA findings.

    .venv/bin/python pipeline/qa/audit_region.py <region> <out findings.json>
"""
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT, finding, region_geom  # noqa: E402


def main():
    reg = region_geom(sys.argv[1])
    out = Path(sys.argv[2])
    x0, y0, x1, y1 = reg.bounds
    idx = json.loads((ROOT / "data/spec/index.json").read_text())["sectors"]
    parts = ["base"] + [s["id"] for s in idx
                        if not (s["bounds"][2] < x0 - 60 or s["bounds"][0] > x1 + 60 or s["bounds"][3] < y0 - 60 or s["bounds"][1] > y1 + 60)]
    js = out.with_suffix(".audit.json")
    cmd = ["blender", "-b", "--factory-startup", "--python-exit-code", "1", "-P", str(ROOT / "build/audit_combo.py"), "--",
           "--parts", ",".join(parts), "--bbox", "%f,%f,%f,%f" % (x0, y0, x1, y1), "--top", "0", "--json", str(js), "--min-area", "0.03"]
    subprocess.run(cmd, cwd=ROOT, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    F = []
    if js.exists():
        d = json.loads(js.read_text())
        for it in d.get("overlaps", d if isinstance(d, list) else []):
            x, y, z = it["at"]
            if reg.contains(__import__("shapely.geometry", fromlist=["Point"]).Point(x, y)):
                F.append(finding("coplanar", 0, "high" if it["area"] > 0.3 else "medium", x, y, z,
                                 what="coplanar faces %s / %s (%.2f m2, %s/%s)" % (it["a"], it["b"], it["area"], it["mat_a"], it["mat_b"]),
                                 source="overlapping geometry: " + it["a"].split(":")[-1] + " vs " + it["b"].split(":")[-1]))
    out.write_text(json.dumps(F, indent=1))
    print("audit %s (%s): %d coplanar findings" % (sys.argv[1], ",".join(parts), len(F)))


if __name__ == "__main__":
    main()

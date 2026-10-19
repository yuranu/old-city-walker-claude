"""Write game/public/sectors.json: what the game streams.

    {"version": 1, "materials": "base/materials.glb", "always": [...base GLBs...],
     "sectors": [{"id", "name", "bounds": [x0, y0, x1, y1], "hi", "lo", "tris_hi", "tris_lo"}]}

Bounds are in the local frame (x east, y north, metres); in the game (three.js, y up) that is
x = x, z = -y. Only sectors whose GLBs exist are listed.
"""
import json
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "game/public"


def tris(path):
    """Triangle count of a GLB, counting each mesh once per node that uses it (instancing)."""
    b = path.read_bytes()
    jl = struct.unpack_from("<I", b, 12)[0]
    j = json.loads(b[20:20 + jl])
    per_mesh = []
    for m in j.get("meshes", []):
        n = 0
        for pr in m["primitives"]:
            acc = j["accessors"][pr["indices"]] if "indices" in pr else j["accessors"][pr["attributes"]["POSITION"]]
            n += acc["count"] // 3
        per_mesh.append(n)
    return sum(per_mesh[nd["mesh"]] for nd in j.get("nodes", []) if "mesh" in nd)


def main():
    idx = json.loads((ROOT / "data/spec/index.json").read_text())
    always = [p for p in ("base/ground.glb", "base/walls.glb", "base/context.glb") if (PUB / p).exists()]
    out = {"version": 1, "materials": "base/materials.glb", "always": always, "sectors": []}
    for s in idx["sectors"]:
        hi, lo = "sectors/%s.glb" % s["id"], "sectors/%s_lo.glb" % s["id"]
        if not (PUB / hi).exists():
            continue
        rec = {"id": s["id"], "name": s["name"], "bounds": s["bounds"], "hi": hi, "tris_hi": tris(PUB / hi)}
        if (PUB / lo).exists():
            rec.update(lo=lo, tris_lo=tris(PUB / lo))
        out["sectors"].append(rec)
    (PUB / "sectors.json").write_text(json.dumps(out, indent=1))
    tot = sum(s["tris_hi"] for s in out["sectors"])
    print("manifest: %d sectors, %.2fM tris at full detail, always %s" % (len(out["sectors"]), tot / 1e6,
                                                                          ", ".join(always)))
    for s in out["sectors"]:
        print("  %-16s hi %7d  lo %6d" % (s["id"], s["tris_hi"], s.get("tris_lo", 0)))


if __name__ == "__main__":
    main()

"""Write data/landmark_ids.json: the OSM ids every landmark module registers (blender/landmarks_*.py).

make_spec.py must not carve landmark footprints (wall slabs, covered passages) and needs the ids, but
the modules only import inside Blender (bpy, mathutils) and register many ids in loops, which a text
parse misses. build.sh runs this before make_spec:

    blender -b --factory-startup --python-exit-code 1 -P blender/dump_landmarks.py [-- out.json]

{"modules": {module: sorted ids, or null when it failed to import}, "ids": sorted union}. A module
that fails to import is left null, so make_spec falls back to parsing its source.
"""
import importlib
import json
import os
import sys
import traceback
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
ROOT = HERE.parent
MODULES = ("landmarks_haram", "landmarks_city", "landmarks_gates")


def main():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = Path(argv[0]) if argv else ROOT / "data/landmark_ids.json"
    mods = {}
    for m in MODULES:
        if not (HERE / (m + ".py")).exists():
            continue
        try:
            mods[m] = sorted(getattr(importlib.import_module(m), "LANDMARKS", {}))
        except Exception:  # noqa: BLE001
            print("dump_landmarks: %s failed to import, make_spec parses its source instead:" % m)
            traceback.print_exc()
            mods[m] = None
    ids = sorted({i for v in mods.values() if v for i in v})
    tmp = out.with_name(out.name + ".tmp%d" % os.getpid())
    tmp.write_text(json.dumps({"modules": mods, "ids": ids}, indent=1))
    os.replace(tmp, out)
    print("landmark ids: %d (%s) -> %s" % (len(ids), ", ".join("%s %s" % (k, len(v) if v is not None else "failed")
                                                            for k, v in mods.items()), out))


main()

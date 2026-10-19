"""Landmark registry: hand-modelled buildings that replace the generic facade builder.

Builders live in landmarks_haram.py (Temple Mount / Haram al-Sharif, Western Wall),
landmarks_gates.py (the city gates other than Jaffa Gate) and
landmarks_city.py (churches, synagogues, mosques and towers elsewhere inside the walls). Each
module exports LANDMARKS = {osm_id: fn}, with

    fn(mbs, bd, gen, place, lod=False)

* mbs   {"solid", "deco", "signs", "cables"} MeshBuilders (meshkit); "solid" collides,
        the others are nocol
* bd    the building record from the spec: ring (CCW, local metres), base, ground, top, tint, tags…
* gen   generated texture atlases (doors, cut, decal, signs)
* place prop placer: place(type, Vector(p), rot_rad, nocol, scale)
* lod   True for the distant massing LOD: same silhouette, a few hundred triangles, no openings.
        All four mbs entries are then the same builder.

A landmark is visible from far away, so its LOD keeps the silhouette (domes, towers, minarets).
"""
import importlib
import os
import traceback

# Landmark modules are written by parallel workers: a module that is missing, mid-edit or failing
# must not break everybody's build. Its buildings then fall back to the generic builder with a
# warning. LANDMARKS_STRICT=1 makes errors fatal (use it while working on a landmark).
STRICT = os.environ.get("LANDMARKS_STRICT") == "1"
REG = {}
for _m in ("landmarks_haram", "landmarks_city", "landmarks_gates"):
    try:
        REG.update(getattr(importlib.import_module(_m), "LANDMARKS", {}))
    except ModuleNotFoundError as e:
        if e.name != _m or STRICT:
            raise
    except Exception:  # noqa: BLE001
        if STRICT:
            raise
        print("LANDMARKS WARNING: %s failed to import, using generic buildings:" % _m)
        traceback.print_exc()


def build(mbs, bd, gen, place, lod=False):
    """Build bd with its landmark builder if it has one; True when handled."""
    fn = REG.get(bd.get("osm"))
    if fn is None:
        return False
    if STRICT:
        fn(mbs, bd, gen, place, lod=lod)
        return True
    try:
        fn(mbs, bd, gen, place, lod=lod)
    except Exception:  # noqa: BLE001
        print("LANDMARKS WARNING: %s (%s) failed, generic building instead:" % (bd.get("osm"), fn.__module__))
        traceback.print_exc()
        return False      # (geometry already added by the failed builder may remain)
    return True

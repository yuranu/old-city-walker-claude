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

REG = {}
for _m in ("landmarks_haram", "landmarks_city", "landmarks_gates"):
    try:
        REG.update(importlib.import_module(_m).LANDMARKS)
    except ModuleNotFoundError as e:
        if e.name != _m:
            raise


def build(mbs, bd, gen, place, lod=False):
    """Build bd with its landmark builder if it has one; True when handled."""
    fn = REG.get(bd.get("osm"))
    if fn is None:
        return False
    fn(mbs, bd, gen, place, lod=lod)
    return True

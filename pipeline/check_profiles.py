"""Validate the sector profiles data/reference/profiles/<sector>.json.

    .venv/bin/python pipeline/check_profiles.py [file ...]        exit code 1 on errors

A profile carries what a sector pass found that is not a single building's facade (those go in
data/reference/overrides/<osm>.json, with building settings under "settings"):

  {
    "sector": "s04_sepulchre",
    "sources": ["data/photos_ref/s04_sepulchre/012_....jpg", ...],
    "souq_streets":     {"<way id or OSM name:en>": [share of fronting facades that are shop rows 0-1,
                                                     canopy probability 0-1]},
    "covered_streets":  ["<way id or name:en>", ...],          vaulted (passages are carved and vaulted)
    "open_areas":       [{"ring": [[x, y], ...], "why": "..."}],   kept free of infill (gardens, yards, ruins)
    "manual_buildings": [{"id": "m_<sector>_<n>", "ring": [[x, y], ...] (CCW), "height": m,
                          "shops": bool, "name": "...", "why": "photos ..."}],   lowest priority: fill gaps only
    "remove_buildings": {"<osm id>": "why (photos)"},          OSM footprints that are not buildings
    "props":            [{"type": "<prop library type>", "p": [x, y], "rot": deg, "why": "..."}],
    "requests":         ["anything that needs code or the spec owner: flats, ground holes, new
                          facade features, wrong terrain levels (with values and sources)"]
  }

Coordinates: local metres, x east, y north from the Jaffa Gate OSM node. Every entry should cite
its evidence in "why".
"""
import json
import re
import sys
from pathlib import Path

from shapely.geometry import Point, Polygon

ROOT = Path(__file__).resolve().parent.parent
KEYS = {"sector", "sources", "souq_streets", "covered_streets", "open_areas", "manual_buildings",
        "remove_buildings", "props", "requests", "notes"}


def prop_types():
    src = (ROOT / "blender/props.py").read_text()
    m = re.search(r"^BUILDERS = \{(.*?)^\}", src, re.M | re.S)
    return set(re.findall(r'"(\w+)"\s*:', m.group(1))) if m else set()


def main():
    osm = json.loads((ROOT / "data/osm_local.json").read_text())
    oc = json.loads((ROOT / "data/oldcity_polygon.json").read_text())
    city = Polygon(oc["ring"]).buffer(30)
    ways = {str(w["id"]): w for w in osm["ways"]}
    names = {w["tags"].get("name:en") for w in osm["ways"] if w["tags"].get("highway")}
    bids = {b["id"] for b in osm["buildings"]}
    sectors = {s["id"] for s in json.loads((ROOT / "data/sectors.json").read_text())["sectors"]}
    ptypes = prop_types()
    files = [Path(a) for a in sys.argv[1:]] or sorted((ROOT / "data/reference/profiles").glob("*.json"))
    errors = warnings = 0

    def err(msg):
        nonlocal errors
        print("ERROR " + msg)
        errors += 1

    def warn(msg):
        nonlocal warnings
        print("warn  " + msg)
        warnings += 1

    def street_ok(tag, k):
        if str(k) in ways:
            if not ways[str(k)]["tags"].get("highway"):
                err("%s: way %s is not a street" % (tag, k))
        elif k not in names:
            err("%s: %r is neither a way id nor a street name:en" % (tag, k))

    def ring_ok(tag, ring, min_area=4.0):
        try:
            p = Polygon(ring)
        except Exception as e:  # noqa: BLE001
            err("%s: bad ring (%s)" % (tag, e))
            return None
        if len(ring) < 3 or not p.is_valid or p.area < min_area:
            err("%s: ring invalid or under %.0f m2" % (tag, min_area))
            return None
        if not city.contains(p.centroid):
            warn("%s: centroid outside the walled city" % tag)
        return p

    for fn in files:
        try:
            d = json.loads(fn.read_text())
        except json.JSONDecodeError as e:
            err("%s: invalid JSON: %s" % (fn.name, e))
            continue
        for k in d:
            if k not in KEYS:
                warn("%s: unknown key %r" % (fn.name, k))
        if d.get("sector") not in sectors or d.get("sector") != fn.stem:
            err("%s: 'sector' must be one of the sector ids and match the file name" % fn.name)
        for k, v in d.get("souq_streets", {}).items():
            street_ok("%s souq_streets" % fn.name, k)
            if not (isinstance(v, list) and len(v) == 2 and all(0 <= x <= 1 for x in v)):
                err("%s souq_streets %s: value must be [share 0-1, canopy 0-1]" % (fn.name, k))
        for k in d.get("covered_streets", []):
            street_ok("%s covered_streets" % fn.name, k)
        for i, oa in enumerate(d.get("open_areas", [])):
            ring_ok("%s open_areas[%d]" % (fn.name, i), oa.get("ring", []), 6.0)
            if not oa.get("why"):
                warn("%s open_areas[%d]: no 'why'" % (fn.name, i))
        for i, mb in enumerate(d.get("manual_buildings", [])):
            tag = "%s manual_buildings[%d]" % (fn.name, i)
            if not str(mb.get("id", "")).startswith("m_"):
                err("%s: id must start with m_" % tag)
            ring_ok(tag, mb.get("ring", []), 6.0)
            if not 2.0 <= float(mb.get("height", 0)) <= 40.0:
                err("%s: height must be 2-40 m" % tag)
            if not mb.get("why"):
                err("%s: 'why' (photos) is required" % tag)
        for k, why in d.get("remove_buildings", {}).items():
            if k not in bids:
                err("%s remove_buildings: %s is not an OSM building" % (fn.name, k))
            if not why:
                err("%s remove_buildings %s: give the evidence" % (fn.name, k))
        for i, pr in enumerate(d.get("props", [])):
            tag = "%s props[%d]" % (fn.name, i)
            if pr.get("type") not in ptypes:
                err("%s: unknown prop type %r (known: %s)" % (tag, pr.get("type"), ", ".join(sorted(ptypes))))
            p = pr.get("p", [])
            if len(p) < 2 or not city.contains(Point(p[:2])):
                err("%s: p must be [x, y] inside the walled city" % tag)
    print("checked %d profiles: %d errors, %d warnings" % (len(files), errors, warnings))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

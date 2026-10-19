"""Convert the raw OSM extract into a local metric frame.

Origin is the Jaffa Gate node (OSM node 561157424); +X east, +Y north, metres.
Writes data/osm_local.json with buildings (incl. multipolygon relations), ways
(highways, barriers, areas) and tagged nodes.

    python3 pipeline/osm_to_local.py
"""
import json
import math
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data/raw/osm_oldcity.osm"
DST = ROOT / "data/osm_local.json"

LAT0, LON0 = 31.7766282, 35.2275435          # Jaffa Gate node
_phi = math.radians(LAT0)
M_PER_DEG_LAT = 111132.92 - 559.82 * math.cos(2 * _phi) + 1.175 * math.cos(4 * _phi)
M_PER_DEG_LON = 111412.84 * math.cos(_phi) - 93.5 * math.cos(3 * _phi)


def to_local(lat, lon):
    return (round((lon - LON0) * M_PER_DEG_LON, 3), round((lat - LAT0) * M_PER_DEG_LAT, 3))


def to_latlon(x, y):
    return (LAT0 + y / M_PER_DEG_LAT, LON0 + x / M_PER_DEG_LON)


def tags_of(el):
    return {t.get("k"): t.get("v") for t in el.findall("tag")}


def join_rings(segments):
    """Join member way node lists into closed rings."""
    segs = [list(s) for s in segments if len(s) > 1]
    rings = []
    while segs:
        ring = segs.pop(0)
        changed = True
        while ring[0] != ring[-1] and changed:
            changed = False
            for i, s in enumerate(segs):
                if s[0] == ring[-1]:
                    ring += s[1:]
                elif s[-1] == ring[-1]:
                    ring += s[::-1][1:]
                elif s[-1] == ring[0]:
                    ring = s[:-1] + ring
                elif s[0] == ring[0]:
                    ring = s[::-1][:-1] + ring
                else:
                    continue
                segs.pop(i)
                changed = True
                break
        if ring[0] == ring[-1]:
            rings.append(ring)
    return rings


def main():
    root = ET.parse(SRC).getroot()
    nodes, tagged_nodes = {}, []
    for n in root.findall("node"):
        p = to_local(float(n.get("lat")), float(n.get("lon")))
        nodes[n.get("id")] = p
        t = tags_of(n)
        if t:
            tagged_nodes.append({"id": int(n.get("id")), "p": p, "tags": t})

    ways = {}
    for w in root.findall("way"):
        refs = [nd.get("ref") for nd in w.findall("nd")]
        ways[w.get("id")] = {"id": int(w.get("id")), "refs": refs, "tags": tags_of(w),
                             "pts": [nodes[r] for r in refs if r in nodes],
                             "closed": len(refs) > 2 and refs[0] == refs[-1]}

    out_ways, buildings = [], []
    for w in ways.values():
        if not w["pts"]:
            continue
        rec = {"id": w["id"], "tags": w["tags"], "pts": w["pts"], "closed": w["closed"],
               "nodes": [int(r) for r in w["refs"]]}
        if "building" in w["tags"] and w["closed"]:
            buildings.append({"id": "w%d" % w["id"], "tags": w["tags"], "outer": [w["pts"][:-1]], "inner": []})
        elif w["tags"]:
            out_ways.append(rec)

    for r in root.findall("relation"):
        t = tags_of(r)
        if t.get("type") != "multipolygon":
            continue
        members = [(m.get("ref"), m.get("role")) for m in r.findall("member") if m.get("type") == "way"]
        if any(ref not in ways for ref, _ in members):
            continue                      # relation crosses the bbox edge; skip
        outer = join_rings([ways[ref]["refs"] for ref, role in members if role == "outer"])
        inner = join_rings([ways[ref]["refs"] for ref, role in members if role == "inner"])
        poly = {"id": "r%s" % r.get("id"), "tags": t,
                "outer": [[nodes[n] for n in ring[:-1]] for ring in outer],
                "inner": [[nodes[n] for n in ring[:-1]] for ring in inner]}
        if "building" in t:
            buildings.append(poly)
        else:
            out_ways.append({"id": "r%s" % r.get("id"), "tags": t, "multipolygon": poly})

    DST.write_text(json.dumps({"origin": {"lat": LAT0, "lon": LON0, "node": 561157424},
                               "buildings": buildings, "ways": out_ways, "nodes": tagged_nodes}))
    print("buildings %d  ways %d  tagged nodes %d -> %s" % (len(buildings), len(out_ways), len(tagged_nodes), DST))


if __name__ == "__main__":
    main()

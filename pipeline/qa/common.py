"""Shared helpers for the QA system (pipeline/qa): regions, spec loading, findings."""
import json
import math
from pathlib import Path

from shapely import STRtree, make_valid
from shapely.geometry import Polygon, box, shape

ROOT = Path(__file__).resolve().parents[2]
SPEC = ROOT / "data/spec"


def region_geom(name):
    """A region: a sector id, 'pilot:<name>' from data/qa/regions.json, or 'x0,y0,x1,y1'."""
    if "," in name:
        return box(*map(float, name.split(",")))
    regs = json.loads((ROOT / "data/qa/regions.json").read_text()) if (ROOT / "data/qa/regions.json").exists() else {}
    if name in regs:
        return box(*regs[name])
    for s in json.loads((ROOT / "data/sectors.json").read_text())["sectors"]:
        if s["id"] == name:
            return shape(s["geom"])
    raise SystemExit("unknown region %s" % name)


def load_spec():
    base = json.loads((SPEC / "base.json").read_text())
    blds = list(base["buildings"])
    secs = {}
    for s in json.loads((SPEC / "index.json").read_text())["sectors"]:
        d = json.loads((SPEC / ("%s.json" % s["id"])).read_text())
        secs[s["id"]] = d
        blds += d["buildings"]
    return base, secs, blds


def building_index(blds):
    polys = [make_valid(Polygon(b["ring"])) for b in blds]
    return polys, STRtree(polys)


def finding(kind, level, severity, x, y, z=None, what="", evidence=None, source=None, view=None):
    return {"kind": kind, "level": level, "severity": severity, "at": [round(x, 1), round(y, 1)] + ([round(z, 1)] if z is not None else []),
            "what": what, "evidence": evidence or {}, "source": source, "view": view,
            "key": "%s@%d,%d" % (kind, math.floor(x / 4), math.floor(y / 4))}

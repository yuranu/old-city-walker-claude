"""Per-facade overrides for the hero zone, transcribed from photographs.

Each building that has been researched gets one JSON file in data/reference/overrides/
(written per building, so several people or agents can work in parallel):

  {
    "building": "w290812336",                    OSM id (way/relation) as used in the spec
    "name": "New Imperial Hotel",
    "sources": ["data/photos_ref/square_north/001_107933129.jpg", ...],
    "settings": {"height": 17.5, "tint": [1.0, 0.96, 0.88], "wall": "ashlar", "parapet": "balustrade",
                 "storey": 4.2},
    "facades": {"4": { ...facade override... }}  keyed by edge index of the current spec ring
  }

Edge indices move when footprint cleaning changes (where a ring starts, vertices merged or split).
Give every facade an anchor, "at": [x, y] = the midpoint of the edge in the local frame. When
present it wins: the facade goes to the ring edge whose midpoint is nearest (within 3 m and facing
the same way to within 45 deg), whatever its index; the key is then only a label (any string).
Without "at" the key must be the edge index.

Facade override keys understood by facades.layout():
  centres        bay centre positions along the edge (m from vertex a)
  shops          ground floor is a shop row (bool)
  ground_storey  / storey   storey heights (m)
  ground         list per bay: {"kind": shop|door|window|blind, "w", "h", "arch", "door", "sign"}
  floors         list per upper floor: {"centres", "w", "h", "arch", "pair", "balconies": [bay idx],
                 "balcony_w", "balcony_d"}
  balcony_bays   bays with a balcony on the first upper floor
  awning         true/false: canopy over the shop row
  bands / cornice  true / false: force string courses / cornice on or off (default: hero ashlar fronts)
  extra_signs    [{"u0", "u1", "z0", "cell"}]       sign atlas names: data/textures/gen/signs.json; z0 is
                 absolute, built as given (on a souq canopy facade keep it above the canopy)
  extra_fixtures [{"type": "sign", "cell", "u", "z", "w", "h"} | {"type": "wall_lantern"|"ac_unit", "u", "z"}]
  extra_decals / extra_awnings / extra_balconies   appended as given
  blank          no openings at all
  auto           false: no random elements at all (signs, posters, plaques, AC units, pipes, lanterns,
                 cables, awnings, balconies, blind bays, arches, shutters/grilles, door colours, rubble
                 jitter); only what the override lists. Bays and upper floors it does not list get the
                 plain defaults (glass windows, arch_up, no balcony); check_overrides.py warns about them
  ground[k]      also "sign": a sign atlas cell (built on any facade: hero or mid, souq or not, auto or
                 not; over the shop head, or above the souq canopy where there is one) or false (no
                 fascia sign), "sill" (window sill height), "lo", "grille",
                 "h" for doors (default 2.75)
  floors[f]      also "ws" / "hs" / "arches" (per bay), "sill" (window floor above the storey base,
                 default 0.9), "lo" (infill cell for every window, e.g. "glass", "shutter_green"),
                 "shutters" ("open" or null), "grille" (bool)
"""
import json
from pathlib import Path

OVR = Path(__file__).resolve().parent.parent / "data/reference/overrides"

FACADES = {}
ANCHORED = {}          # bid -> [(x, y, key, ov)] for facades with an "at" anchor (key: only a label)
BUILDING = {}
SOURCES = {}

for fn in sorted(OVR.glob("*.json")) if OVR.exists() else []:
    d = json.loads(fn.read_text())
    bid = d["building"]
    BUILDING[bid] = d.get("settings", {})
    SOURCES[bid] = d.get("sources", [])
    for edge, ov in d.get("facades", {}).items():
        if "at" in ov:
            ANCHORED.setdefault(bid, []).append((ov["at"][0], ov["at"][1], edge, ov))
            continue
        try:
            FACADES[(bid, int(edge))] = ov
        except ValueError:            # a bad file must not stop make_spec for everyone else
            print("override %s facade %r: no \"at\" anchor and the key is not an edge index; skipped" % (fn.name, edge))


def facades_for(bid, ring):
    """{edge index: override} for a building ring (CCW list of (x, y)), resolving anchors."""
    import math
    out = {e: ov for (b, e), ov in FACADES.items() if b == bid}
    n = len(ring)
    for x, y, key, ov in ANCHORED.get(bid, []):
        best, bd = None, 3.0
        for i in range(n):
            a, b = ring[i], ring[(i + 1) % n]
            d = math.dist(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), (x, y))
            if d < bd:
                best, bd = i, d
        if best is None:
            print("override %s facade %s: no edge near anchor (%.1f, %.1f)" % (bid, key, x, y))
            continue
        out[best] = ov
    return out

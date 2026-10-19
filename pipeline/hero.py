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

Facade override keys understood by facades.layout():
  centres        bay centre positions along the edge (m from vertex a)
  shops          ground floor is a shop row (bool)
  ground_storey  / storey   storey heights (m)
  ground         list per bay: {"kind": shop|door|window|blind, "w", "h", "arch", "door", "sign"}
  floors         list per upper floor: {"centres", "w", "h", "arch", "pair", "balconies": [bay idx],
                 "balcony_w", "balcony_d"}
  balcony_bays   bays with a balcony on the first upper floor
  awning         true/false: canopy over the shop row
  bands / cornice  force string courses / cornice
  extra_signs    [{"u0", "u1", "z0", "cell"}]       sign atlas names: data/textures/gen/signs.json
  extra_fixtures [{"type": "sign", "cell", "u", "z", "w", "h"} | {"type": "wall_lantern"|"ac_unit", "u", "z"}]
  extra_decals / extra_awnings / extra_balconies   appended as given
  blank          no openings at all
"""
import json
from pathlib import Path

OVR = Path(__file__).resolve().parent.parent / "data/reference/overrides"

FACADES = {}
BUILDING = {}
SOURCES = {}

for fn in sorted(OVR.glob("*.json")) if OVR.exists() else []:
    d = json.loads(fn.read_text())
    bid = d["building"]
    BUILDING[bid] = d.get("settings", {})
    SOURCES[bid] = d.get("sources", [])
    for edge, ov in d.get("facades", {}).items():
        FACADES[(bid, int(edge))] = ov

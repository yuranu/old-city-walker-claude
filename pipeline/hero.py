"""Per-facade overrides for the hero zone, transcribed from photographs.

Keys: (building id, edge index) -> dict understood by facades.layout():
  centres        bay centre positions along the edge (m from vertex a)
  shops          ground floor is a shop row (bool)
  ground_storey  / storey   storey heights (m)
  ground         list per bay: {"kind": shop|door|window|blind, "w", "h", "arch", "door", "sign"}
  floors         list per upper floor: {"centres", "w", "h", "arch", "pair", "balconies": [bay idx]}
  balcony_bays   bays with a balcony on the first upper floor
  bands / cornice  force string courses / cornice
  extra_signs / extra_fixtures / extra_decals / extra_awnings / extra_balconies  appended as given
  blank          no openings at all

BUILDING holds per-building settings: height, tint, wall, parapet ("solid"|"balustrade"|"railing").
Sources are cited per entry (photo file names in data/photos and data/photos_ref).
"""

FACADES = {}
BUILDING = {}

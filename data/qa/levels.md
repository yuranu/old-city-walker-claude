# QA levels

A region passes level N when the measurement suite and the vision critic report no open finding of
severity high or medium at level <= N, and nothing regressed. Fixes go to the generating rule
(make_spec, stairs, infill, facades, dressing, builders) wherever possible, so the whole city
improves at once; a region-specific data fix (profile, override) only for facts about that place.

## Level 0: broken (anything a player would call a bug)
- holes: sky or void visible through or under the ground, gaps between ground and steps/walls
- flicker: coplanar faces fighting (striped, mixed textures on one surface)
- broken geometry: spikes or pyramids in the ground, slabs or walls standing across walkways,
  steps crossing each other or running into walls, objects cut in half, inside-out faces
- floating or buried objects: props, steps, doors, thresholds not meeting the surface below
- blocked walkways: a street or passage closed by a building, wall or prop
- missing or wrong textures: flat untextured surfaces, stretched or wildly scaled textures
- absurd scale: doors/windows/props far too big or small, walls 1 cm thick
- streaming artefacts: pieces missing nearby, LOD visible up close

## Level 1: structurally plausible
- buildings: sensible heights and storeys, doors at street level, windows in rows, roofs closed
- streets: plausible widths, continuous street walls, steps where the street is steep, no dead
  walls facing a main street, thresholds meeting the paving
- landmarks: in the right place and orientation, not hidden or overlapped by generic buildings
- terrain: no unrealistic ramps; level changes handled by steps or retaining walls that make sense

## Level 2: character (reads as this place)
- street types right (souq shop rows vs residential lanes), materials and tints, shutters and
  doors, canopies, signage, domes and rooftop clutter, vegetation where it grows

## Level 3: photo match
- fixed photo viewpoints (docs/EVALUATION.md) match the real photographs in massing and detail

## Level 4: material and lighting realism
## Level 5+: towards photorealism (micro detail, clutter, legible signage, weathering)

"""Render named close-up views of a built .blend (quick visual critique).

    blender -b build/city.blend -P blender/render_views.py -- out_dir name:x,y,z:lx,ly,lz[:lens] ...
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:]
out = Path(argv[0])
out.mkdir(parents=True, exist_ok=True)
scn = bpy.context.scene
for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
    try:
        scn.render.engine = eng
        break
    except TypeError:
        continue
if not scn.world:
    scn.world = bpy.data.worlds.new("sky")
scn.world.use_nodes = True
bg = next(n for n in scn.world.node_tree.nodes if n.type == "BACKGROUND")
bg.inputs["Color"].default_value = (0.55, 0.68, 0.9, 1)
bg.inputs["Strength"].default_value = 0.8
if "sun" not in bpy.data.objects:
    sd = bpy.data.lights.new("sun", "SUN")
    sd.energy, sd.color, sd.angle = 4.5, (1.0, 0.93, 0.82), math.radians(1.0)
    sun = bpy.data.objects.new("sun", sd)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-130))
    scn.collection.objects.link(sun)
scn.render.resolution_x, scn.render.resolution_y = 1280, 800
try:
    scn.view_settings.view_transform = "AgX"
except TypeError:
    pass
for spec in argv[1:]:
    parts = spec.split(":")
    name, eye, look = parts[0], tuple(map(float, parts[1].split(","))), tuple(map(float, parts[2].split(",")))
    cd = bpy.data.cameras.new(name)
    cd.lens = float(parts[3]) if len(parts) > 3 else 20
    cam = bpy.data.objects.new("v_" + name, cd)
    cam.location = eye
    cam.rotation_euler = (Vector(look) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
    scn.collection.objects.link(cam)
    scn.camera = cam
    scn.render.filepath = str(out / ("%s.png" % name))
    bpy.ops.render.render(write_still=True)
    print("rendered", scn.render.filepath)

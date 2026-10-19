"""Render any part of the streamed city from the exported GLBs, as the game would load it:
base (ground, walls, context) + every sector whose bounds come within --radius of the cameras,
full detail, with textures re-attached from base/materials.glb by material name.

    blender -b --factory-startup -P blender/render_city.py -- --out renders/city/wad \
        --cam "wad:420,300,1.7:440,250,3" [--cam ...] [--radius 180] [--lo]

A camera is name:eye_x,eye_y,eye_z:look_x,look_y,look_z in the local frame (x east, y north);
the z values are heights above the ground at that point (streets drop ~35 m across the city),
unless --abs is given.
The sky, sun and look-at match blender/render_sector.py.
"""
import argparse
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parent.parent
PUB = ROOT / "game/public"


def args_():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--cam", action="append", default=[])
    p.add_argument("--radius", type=float, default=180.0)
    p.add_argument("--res", default="1280x720")
    p.add_argument("--lens", type=float, default=18)
    p.add_argument("--lo", action="store_true", help="sectors beyond the radius as LOD instead of nothing")
    p.add_argument("--abs", action="store_true", help="camera z values are absolute")
    return p.parse_args(argv)


def import_glb(path):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=str(path))
    return [o for o in bpy.data.objects if o not in before]


def main():
    a = args_()
    bpy.ops.wm.read_factory_settings(use_empty=True)
    cams = []
    for c in a.cam:
        name, e, l = c.split(":")
        cams.append((name, tuple(map(float, e.split(","))), tuple(map(float, l.split(",")))))
    man = json.loads((PUB / "sectors.json").read_text())
    lib = import_glb(PUB / man["materials"])
    libmats = {}
    for o in lib:
        for s in o.material_slots:
            if s.material:
                libmats[s.material.name] = s.material
        bpy.data.objects.remove(o)
    files = list(man["always"])

    def near(b):
        return min(math.hypot(max(b[0] - e[0], 0, e[0] - b[2]), max(b[1] - e[1], 0, e[1] - b[3]))
                   for _, e, _ in cams) < a.radius
    for s in man["sectors"]:
        if near(s["bounds"]):
            files.append(s["hi"])
        elif a.lo and s.get("lo"):
            files.append(s["lo"])
    print("loading", files)
    for f in files:
        for o in import_glb(PUB / f):
            for s in o.material_slots:
                m = s.material
                if m and m.name not in libmats:
                    base = m.name.split(".")[0]
                    if base in libmats:
                        s.material = libmats[base]
    # glTF is y-up: the importer converts to Blender's z-up, so the local frame is preserved
    scn = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
        try:
            scn.render.engine = eng
            break
        except TypeError:
            continue
    world = bpy.data.worlds.new("sky")
    scn.world = world
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (0.55, 0.68, 0.9, 1)
    bg.inputs["Strength"].default_value = 0.8
    sd = bpy.data.lights.new("sun", "SUN")
    sd.energy = 4.5
    sd.color = (1.0, 0.93, 0.82)
    sd.angle = math.radians(1.0)
    sun = bpy.data.objects.new("sun", sd)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-130))
    scn.collection.objects.link(sun)
    w, h = (int(v) for v in a.res.split("x"))
    scn.render.resolution_x, scn.render.resolution_y = w, h
    try:
        scn.view_settings.view_transform = "AgX"
    except TypeError:
        pass
    grounds = [o for o in scn.objects if o.type == "MESH" and o.get("ground")]
    bpy.context.view_layer.update()

    def zg(x, y):
        best = None
        for o in grounds:
            inv = o.matrix_world.inverted()
            org = inv @ Vector((x, y, 1000.0))
            dirn = (inv.to_3x3() @ Vector((0, 0, -1))).normalized()
            hit, loc, _, _ = o.ray_cast(org, dirn)
            if hit:
                z = (o.matrix_world @ loc).z
                best = z if best is None else max(best, z)
        return best or 0.0
    if not a.abs:
        cams = [(n, (e[0], e[1], e[2] + zg(e[0], e[1])), (l[0], l[1], l[2] + zg(l[0], l[1]))) for n, e, l in cams]
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, eye, look in cams:
        cd = bpy.data.cameras.new(name)
        cd.lens = a.lens if not name.startswith("aerial") else 28
        cd.clip_end = 3000
        cam = bpy.data.objects.new("cam_" + name, cd)
        cam.location = eye
        f = (Vector(look) - Vector(eye)).normalized()
        r = f.cross(Vector((0, 0, 1))).normalized()
        u = r.cross(f)
        cam.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()
        scn.collection.objects.link(cam)
        scn.camera = cam
        scn.render.filepath = str(out / ("%s.png" % name))
        bpy.ops.render.render(write_still=True)
        print("rendered", scn.render.filepath)


main()

"""Quick look at a built sector: open build/<sector>.blend (or any blend), add sky, sun and a
ground plane if there is none, render named viewpoints.

    blender -b build/s04_sepulchre.blend -P blender/render_sector.py -- --out renders/sectors/s04 \
        --cam "parvis:215,160,1.7:213,184,8" --cam "aerial:150,40,90:240,190,0"

A camera is name:eye_x,eye_y,eye_z:look_x,look_y,look_z in the local frame (x east, y north).
With no --cam an oblique aerial over the scene is rendered.
"""
import argparse
import math
import statistics
import sys
from pathlib import Path

import bpy
from mathutils import Matrix, Vector


def args_():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--cam", action="append", default=[])
    p.add_argument("--res", default="1280x720")
    p.add_argument("--lens", type=float, default=18)
    return p.parse_args(argv)


def bounds():
    xs, ys, zs = [], [], []
    for o in bpy.context.scene.objects:
        if o.type != "MESH" or o.name.startswith("material_library"):
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            xs.append(w.x)
            ys.append(w.y)
            zs.append(w.z)
    return min(xs), min(ys), max(xs), max(ys), zs


def main():
    a = args_()
    scn = bpy.context.scene
    for eng in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT", "BLENDER_WORKBENCH"):
        try:
            scn.render.engine = eng
            break
        except TypeError:
            continue
    x0, y0, x1, y1, zs = bounds()
    if not any(o.get("ground") for o in scn.objects):
        bases = sorted(zs)[: max(1, len(zs) // 10)]
        z = statistics.median(bases) - 0.03
        bpy.ops.mesh.primitive_plane_add(size=1, location=((x0 + x1) / 2, (y0 + y1) / 2, z))
        pl = bpy.context.active_object
        pl.scale = (x1 - x0 + 200, y1 - y0 + 200, 1)
        m = bpy.data.materials.get("paving")
        if m:
            pl.data.materials.append(m)
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
    cams = []
    for c in a.cam:
        name, e, l = c.split(":")
        cams.append((name, tuple(map(float, e.split(","))), tuple(map(float, l.split(",")))))
    if not cams:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        d = max(x1 - x0, y1 - y0)
        cams.append(("aerial", (cx - 0.35 * d, cy - 0.6 * d, 0.45 * d), (cx, cy, 0)))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, eye, look in cams:
        cd = bpy.data.cameras.new(name)
        cd.lens = a.lens if not name.startswith("aerial") else 28
        cd.clip_end = 3000
        cam = bpy.data.objects.new("cam_" + name, cd)
        cam.location = eye
        f = (Vector(look) - Vector(eye)).normalized()       # explicit look-at: no roll near the y axis
        r = f.cross(Vector((0, 0, 1))).normalized()
        u = r.cross(f)
        cam.rotation_euler = Matrix((r, u, -f)).transposed().to_euler()
        scn.collection.objects.link(cam)
        scn.camera = cam
        scn.render.filepath = str(out / ("%s.png" % name))
        bpy.ops.render.render(write_still=True)
        print("rendered", scn.render.filepath)


main()

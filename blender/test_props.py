"""Prop library test: build every prop, lay them out in labelled rows (roof props on a slab, wall props on a
wall), light with sun + sky and render a lineup plus close-ups to renders/props/.

  blender -b --factory-startup --python-exit-code 1 -P blender/test_props.py -- [--only lineup,street,...] [--fast]

The preview materials multiply the per-face vertex colour onto the base colour, as the game does.
"""
import json
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import materials  # noqa: E402
import props  # noqa: E402
from meshkit import MeshBuilder, box  # noqa: E402

OUT = ROOT / "renders/props"
ARGS = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
ONLY = None
if "--only" in ARGS:
    ONLY = set(ARGS[ARGS.index("--only") + 1].split(","))
FAST = "--fast" in ARGS
SAVE = ARGS[ARGS.index("--save") + 1] if "--save" in ARGS else None
NORENDER = "--norender" in ARGS

BUDGET = {**{k: 300 for k in props.MODERN}, "bollard": 60, "lamp_post": 300, "tree_olive": 200, "tree_ficus": 200, "cart": 250, "water_heater": 120,
          "water_tank": 80, "sat_dish": 80, "antenna": 80, "ac_unit": 60, **{k: 30 for k in props.LITTER}}
SUN_DIR = Vector((0.45, 0.8, 0.75)).normalized()      # towards the sun: front-left, high


def preview_materials(mats):
    """Mimic the game: base colour (or texture) x vertex colour 'Col'."""
    for m in set(mats.values()):
        nt = m.node_tree
        bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
        inp = bsdf.inputs["Base Color"]
        vc = nt.nodes.new("ShaderNodeVertexColor")
        vc.layer_name = "Col"
        mul = nt.nodes.new("ShaderNodeVectorMath")
        mul.operation = "MULTIPLY"
        if inp.is_linked:
            nt.links.new(inp.links[0].from_socket, mul.inputs[0])
        else:
            c = inp.default_value
            mul.inputs[0].default_value = (c[0], c[1], c[2])
        nt.links.new(vc.outputs["Color"], mul.inputs[1])
        nt.links.new(mul.outputs["Vector"], inp)
        if hasattr(m, "use_transparent_shadow"):
            m.use_transparent_shadow = True


def label_material():
    m = bpy.data.materials.new("label")
    m.use_nodes = True
    bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    bsdf.inputs["Base Color"].default_value = (0.01, 0.01, 0.012, 1)
    bsdf.inputs["Roughness"].default_value = 0.9
    return m


def add_label(text, x, y, size, col, mat):
    cu = bpy.data.curves.new("lbl_" + text, "FONT")
    cu.body = text
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "TOP"
    cu.materials.append(mat)
    ob = bpy.data.objects.new("lbl_" + text, cu)
    ob.location = (x, y, 0.004)
    ob.rotation_euler = (0, 0, math.pi)          # readable from the +Y camera
    col.objects.link(ob)
    return ob


def bounds(me):
    xs = [v.co.x for v in me.vertices]
    ys = [v.co.y for v in me.vertices]
    zs = [v.co.z for v in me.vertices]
    return (min(xs), max(xs)), (min(ys), max(ys)), (min(zs), max(zs))


def place(lib, name, x, y, z, col, yaw=0.0):
    ob = bpy.data.objects.new(name, lib[name])
    ob.location = (x, y, z)
    ob.rotation_euler = (0, 0, yaw)
    col.objects.link(ob)
    return ob


def row(lib, names, y, gap, col, lmat, lsize, yaw=None, labels=None):
    """Place props along -X (screen left -> right for the +Y camera), centred on x = 0."""
    yaw = yaw or {}
    widths = []
    for n in names:
        (x0, x1), (y0, y1), _ = bounds(lib[n])
        if n in yaw:                                   # rotated: projected width
            a = yaw[n]
            w = abs(math.cos(a)) * (x1 - x0) + abs(math.sin(a)) * (y1 - y0)
        else:
            w = x1 - x0
        widths.append(max(w, 0.05))
    total = sum(widths) + gap * (len(names) - 1)
    cur = total / 2
    obs = []
    for n, w in zip(names, widths):
        x = cur - w / 2
        ob = place(lib, n, x, y, 0.0, col, yaw.get(n, 0.0))
        (_, _), (y0, y1), _ = bounds(lib[n])
        lb = add_label(n, x, y + max(abs(y1), abs(y0)) + lsize * 0.6, lsize, col, lmat)
        if labels is not None:
            labels.append(lb)
        obs.append(ob)
        cur -= w + gap
    return obs


def grid(lib, names, cx, cy, ncol, dx, dy, col, lmat, lsize, labels):
    obs = []
    for i, n in enumerate(names):
        r, c = divmod(i, ncol)
        x = cx + (ncol - 1) * dx / 2 - c * dx
        y = cy - r * dy
        obs.append(place(lib, n, x, y, 0.0, col, 0.0))
        labels.append(add_label(n, x, y + 0.11, lsize, col, lmat))
    return obs


def stage_mesh(name, mats, tiles, fn, col):
    mb = MeshBuilder(tiles)
    fn(mb)
    ob = mb.to_object(name, mats, col)
    return ob


def setup_world(scene):
    world = bpy.data.worlds.new("sky")
    scene.world = world
    world.use_nodes = True
    nt = world.node_tree
    bg = next(n for n in nt.nodes if n.type == "BACKGROUND")
    sky = nt.nodes.new("ShaderNodeTexSky")
    types = [i.identifier for i in bpy.types.ShaderNodeTexSky.bl_rna.properties["sky_type"].enum_items]
    sky.sky_type = "MULTIPLE_SCATTERING" if "MULTIPLE_SCATTERING" in types else types[0]
    if hasattr(sky, "sun_disc"):
        sky.sun_disc = False
    if hasattr(sky, "sun_elevation"):
        sky.sun_elevation = math.asin(SUN_DIR.z)
    if hasattr(sky, "sun_rotation"):
        sky.sun_rotation = math.atan2(SUN_DIR.x, SUN_DIR.y)
    if hasattr(sky, "sun_direction"):
        sky.sun_direction = SUN_DIR
    if hasattr(sky, "turbidity"):
        sky.turbidity = 2.6
    if hasattr(sky, "ground_albedo"):
        sky.ground_albedo = 0.35
    nt.links.new(sky.outputs["Color"], bg.inputs["Color"])
    bg.inputs["Strength"].default_value = 0.32
    # the camera sees the sky; everything else is lit by a softer, neutral sky dome
    amb = nt.nodes.new("ShaderNodeBackground")
    amb.inputs["Color"].default_value = (0.62, 0.68, 0.78, 1)
    amb.inputs["Strength"].default_value = 0.85
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    out = next(n for n in nt.nodes if n.type == "OUTPUT_WORLD")
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(amb.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs["Surface"])

    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.4
    sun.angle = math.radians(1.2)
    sun.color = (1.0, 0.96, 0.9)
    ob = bpy.data.objects.new("sun", sun)
    ob.rotation_euler = SUN_DIR.to_track_quat("Z", "Y").to_euler()
    scene.collection.objects.link(ob)


def setup_render(scene, x, y):
    ok = False
    for e in ("BLENDER_EEVEE", "BLENDER_EEVEE_NEXT"):
        try:
            scene.render.engine = e
            ok = True
            break
        except TypeError:
            pass
    if not ok:
        scene.render.engine = "BLENDER_WORKBENCH"
    scene.render.resolution_x, scene.render.resolution_y = x, y
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    if hasattr(scene, "eevee"):
        scene.eevee.taa_render_samples = 16 if FAST else 48
        scene.eevee.use_shadows = True
        try:
            scene.eevee.use_raytracing = False
            scene.eevee.shadow_ray_count = 2
            scene.eevee.shadow_step_count = 6
        except AttributeError:
            pass
    scene.view_settings.view_transform = "AgX"
    try:
        scene.view_settings.look = "AgX - Base Contrast"
    except TypeError:
        pass


def frame(cam, scene, objs, direction, margin=0.92, lift=0.0):
    """Point the camera along -direction at the bounding box of objs and back off until it all fits."""
    bpy.context.view_layer.update()
    pts = []
    for ob in objs:
        for c in ob.bound_box:
            pts.append(ob.matrix_world @ Vector(c))
    lo = Vector((min(p.x for p in pts), min(p.y for p in pts), min(p.z for p in pts)))
    hi = Vector((max(p.x for p in pts), max(p.y for p in pts), max(p.z for p in pts)))
    ctr = (lo + hi) / 2 + Vector((0, 0, lift))
    d = direction.normalized()
    fwd = -d
    right = fwd.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(fwd)
    aspect = scene.render.resolution_x / scene.render.resolution_y
    th = math.tan(cam.data.angle_x / 2) if aspect >= 1 else math.tan(cam.data.angle_y / 2) * aspect
    tv = th / aspect

    def fits(D):
        eye = ctr + d * D
        for p in pts:
            v = p - eye
            z = v.dot(fwd)
            if z <= 0.05:
                return False
            if abs(v.dot(right)) / z > th * margin or abs(v.dot(up)) / z > tv * margin:
                return False
        return True
    a, b = 0.2, 400.0
    for _ in range(50):
        m = (a + b) / 2
        a, b = (a, m) if fits(m) else (m, b)
    cam.location = ctr + d * b
    cam.rotation_euler = fwd.to_track_quat("-Z", "Y").to_euler()


def render(scene, path):
    scene.render.filepath = str(path)
    try:
        bpy.ops.render.render(write_still=True)
    except RuntimeError as ex:                  # EEVEE unavailable (no GPU context): fall back to Workbench
        print("EEVEE failed (%s); falling back to Workbench" % ex)
        scene.render.engine = "BLENDER_WORKBENCH"
        scene.display.shading.light = "STUDIO"
        scene.display.shading.color_type = "MATERIAL"
        bpy.ops.render.render(write_still=True)
    print("wrote", path)


def main():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    mats, tiles, gen = materials.build(ROOT)
    lib = props.build_library(mats, tiles, gen)
    preview_materials(mats)

    # ---- triangle counts
    counts = {k: props.tri_count(me) for k, me in lib.items()}
    print("\n%-14s %5s  %-6s  %s" % ("prop", "tris", "kind", "budget"))
    for k in props.BUILDERS:
        b = BUDGET.get(k)
        flag = "" if b is None else ("ok (<= %d)" % b if counts[k] <= b else "OVER %d" % b)
        print("%-14s %5d  %-6s  %s" % (k, counts[k], props.KIND[k], flag))
    print("total %d tris for %d props\n" % (sum(counts.values()), len(counts)))
    missing = set(props.KIND) - set(lib)
    assert not missing, missing
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "tris.json").write_text(json.dumps(counts, indent=1))

    col = scene.collection
    lmat = label_material()
    stage_mesh("ground", mats, tiles,
               lambda mb: mb.poly([(-40, -30, 0), (40, -30, 0), (40, 12, 0), (-40, 12, 0)], "paving", (0, 0, 1)), col)

    groups, labels = {}, {}
    for g in ("litter", "clutter", "trees", "street", "wall", "roof"):
        labels[g] = []
    groups["litter"] = grid(lib, props.LITTER, 0.0, 2.4, 4, 0.42, 0.42, col, lmat, 0.04, labels["litter"])
    groups["clutter"] = row(lib, ["cart", "box_stack", "crate_stack", "crate_single", "stool_stack", "plant_pot",
                                  "weeds"], -0.6, 0.6, col, lmat, 0.13, yaw={"cart": math.radians(65)},
                            labels=labels["clutter"])
    lt = []
    street = row(lib, ["tree_olive", "tree_ficus", "lamp_post", "info_board", "dumpster", "bench", "bin_post",
                       "bollard"], -5.5, 0.8, col, lmat, 0.28, labels=lt)
    groups["shop"], labels["shop"] = groups["clutter"][:3], labels["clutter"][:3]
    groups["small"], labels["small"] = groups["clutter"][3:], labels["clutter"][3:]
    groups["trees"], labels["trees"] = street[:2], lt[:2]
    groups["street"], labels["street"] = street[2:], lt[2:]

    # ---- wall stage (wall face = XZ plane at y = -11.0, props stick out towards +Y), behind the street row
    wy, wx = -11.0, -2.6
    wall = stage_mesh("wall", mats, tiles,
                      lambda mb: box(mb, (wx, wy - 0.3), (1, 0, 0), (0, 1, 0), 5.2, 0.6, 0.0, 4.6, "ashlar"), col)
    wobs = [wall]
    for n, x, z in [("wall_lantern", -1.6, 3.1), ("ac_unit", 0.15, 2.3), ("spout", 1.75, 3.6), ("caper", 1.4, 1.4),
                    ("caper", -0.7, 1.1)]:
        wobs.append(place(lib, n, wx + x, wy, z, col))
    for n, x in [("wall_lantern", -1.6), ("ac_unit", 0.15), ("spout", 1.9), ("caper", -0.7)]:
        labels["wall"].append(add_label(n, wx + x, wy + 0.6, 0.22, col, lmat))
    groups["wall"] = wobs

    # ---- roof stage (flat slab 0.5 m high)
    rx, ry, rz = -11.2, -11.5, 0.5
    slab = stage_mesh("roof", mats, tiles,
                      lambda mb: box(mb, (rx, ry), (1, 0, 0), (0, 1, 0), 9.5, 4.6, 0.0, rz, "lime"), col)
    robs = [slab]
    for n, x, y in [("water_heater", 2.8, 0.2), ("water_tank", 0.6, -0.6), ("sat_dish", -1.3, 0.6),
                    ("antenna", -3.3, -0.4)]:
        robs.append(place(lib, n, rx + x, ry + y, rz, col))
        labels["roof"].append(add_label(n, rx + x, ry + 2.75, 0.22, col, lmat))
    groups["roof"] = robs
    # ---- present-day plaza furniture, back row
    labels["modern"] = []
    groups["modern"] = row(lib, props.MODERN, -17.5, 1.5, col, lmat, 0.2, labels=labels["modern"])
    for g, names in (("modern_lamps", ["lamp_modern", "lamp_modern_double", "lamp_disc", "banner_pole", "flagpole"]),
                     ("modern_small", ["bin_slatted", "bench_stone", "barrier_post"]),
                     ("modern_trees", ["palm", "tree_young"])):
        idx = [props.MODERN.index(n) for n in names]
        groups[g] = [groups["modern"][i] for i in idx]
        labels[g] = [labels["modern"][i] for i in idx]
    if SAVE:
        bpy.ops.wm.save_as_mainfile(filepath=SAVE)
        print("saved", SAVE)
    if NORENDER:
        return

    setup_world(scene)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    cam.data.lens = 35
    cam.data.clip_end = 500
    col.objects.link(cam)
    scene.camera = cam

    shots = [("lineup", None, Vector((0.1, 1.0, 0.68)), 1600, 1000)]
    for g, dirv in [("street", (0.35, 1.0, 0.38)), ("trees", (0.3, 1.0, 0.3)), ("shop", (0.35, 1.0, 0.55)),
                    ("small", (0.3, 1.0, 0.45)),
                    ("litter", (0.25, 1.0, 1.1)), ("wall", (0.45, 1.0, 0.15)), ("roof", (-0.4, 1.0, 0.7))]:
        shots.append((g, g, Vector(dirv), 1600, 1000))
    for g, dirv in [("modern_lamps", (0.75, 1.0, 0.22)), ("modern_small", (0.35, 1.0, 0.5)),
                    ("modern_trees", (0.3, 1.0, 0.3))]:
        shots.append((g, g, Vector(dirv), 1600, 1000))
    shots.append(("modern_lamps_back", "modern_lamps", Vector((-0.4, -1.0, 0.3)), 1600, 1000))
    shots.append(("roof_back", "roof", Vector((0.3, -1.0, 0.6)), 1600, 1000))
    shots.append(("street_back", "street", Vector((-0.4, -1.0, 0.4)), 1600, 1000))
    shots.append(("shop_back", "shop", Vector((-0.5, -1.0, 0.6)), 1600, 1000))
    every = [o for o in scene.objects if o.type == "MESH" and o.name != "ground"]
    for name, g, dirv, rx_, ry_ in shots:
        if ONLY and name not in ONLY:
            continue
        keep = None if g is None else set(groups[g]) | set(labels[g])
        for o in scene.objects:
            if o.type in ("MESH", "FONT") and o.name != "ground":
                o.hide_render = keep is not None and o not in keep
        setup_render(scene, rx_, ry_)
        frame(cam, scene, groups[g] if g else every, dirv, margin=0.95 if g else 0.98)
        render(scene, OUT / ("lineup.png" if name == "lineup" else "close_%s.png" % name))

main()

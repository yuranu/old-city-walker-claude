"""Render the photo-evaluation cameras from a built scene.

    blender -b build/city.blend --python-exit-code 1 -P blender/render_eval.py -- \
        [--cams data/reference/eval_cams.json] [--out renders/eval] [--only a,b] \
        [--long 1280] [--samples 32] [--fast] [--suffix _try] [--set cam.key=value ...] \
        [--variants variants.json]

For every camera in eval_cams.json it writes, into --out:
    <name>_model.png       the render (photo aspect, sky composited behind the geometry)
    <name>_mask.png        8-bit geometry mask (255 = model, 0 = sky) for the alignment score
    <name>_model.json      pose actually used (incl. ground z found under the camera) and the
                           image positions of visible labelled objects (for the compare sheet)

The .blend is opened read-only: nothing is ever saved. Works on any rebuild: the camera is
placed relative to whatever ground mesh is under (x, y) (objects with a truthy "ground" custom
property, or named ground*/terrain*/paving*/road*/kerbs*/steps*/*_steps but not cables/decals;
else the lowest surface hit), existing lights are hidden and
replaced by a warm afternoon sun from the south-west plus a sky fill.

Pose convention (local frame, x east, y north, metres): heading = compass degrees (0 N, 90 E),
pitch = degrees above horizon, roll = degrees (positive turns the image clockwise),
fov = vertical field of view in degrees, z_eye = eye height above the ground under the camera
(or z_ground to force the ground height). Optional shift_x/shift_y = Blender lens shift (for
cropped / perspective-corrected photos).

--variants FILE renders a list [{"cam": name, "out": "path.png", "set": {"heading": 271}}, ...]
(used by pipeline/eval_compare.py refine); --set overrides one cam's fields from the command line.
"""
import argparse
import json
import math
import os
import re
import sys
import time
from pathlib import Path

import bpy
from bpy_extras.object_utils import world_to_camera_view
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent.parent
GROUND_RX = re.compile(r"^(ground|terrain|paving|road|plaza|kerbs?|steps|stairs)|_(steps|stairs|ground)\b", re.I)
NOT_GROUND_RX = re.compile(r"cable|wire|lamp|awning|sign|decal|tree|prop", re.I)
DEFAULT_RENDER = {
    "sun_azimuth": 240.0,     # compass direction the sun is IN (SW = 225); afternoon
    "sun_elevation": 32.0,
    "sun_strength": 4.2,
    "sun_color": [1.0, 0.88, 0.72],
    "sky_color": [0.52, 0.68, 0.95],
    "sky_strength": 1.0,
    "sky_top": [0.36, 0.56, 0.86],     # composited background gradient (sRGB 0..1)
    "sky_horizon": [0.80, 0.86, 0.93],
}


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--cams", default=str(ROOT / "data/reference/eval_cams.json"))
    p.add_argument("--out", default=str(ROOT / "renders/eval"))
    p.add_argument("--only", default="", help="comma-separated cam names")
    p.add_argument("--long", type=int, default=1280, help="long side of the render in px")
    p.add_argument("--samples", type=int, default=32)
    p.add_argument("--fast", action="store_true", help="few samples, no labels (pose iteration)")
    p.add_argument("--suffix", default="", help="appended to output names, e.g. _try")
    p.add_argument("--set", action="append", default=[], help="cam.key=value override")
    p.add_argument("--variants", default="")
    p.add_argument("--no-labels", action="store_true")
    return p.parse_args(argv)


# ---------------------------------------------------------------- scene setup
def set_engine(scn):
    for eng in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
        try:
            scn.render.engine = eng
            return eng
        except TypeError:
            continue
    return scn.render.engine


def setup_lighting(scn, rs):
    for ob in scn.objects:
        if ob.type == "LIGHT":
            ob.hide_render = True
    world = bpy.data.worlds.new("eval_sky")
    world.use_nodes = True
    bg = next(n for n in world.node_tree.nodes if n.type == "BACKGROUND")
    bg.inputs["Color"].default_value = (*rs["sky_color"], 1)
    bg.inputs["Strength"].default_value = rs["sky_strength"]
    scn.world = world
    ld = bpy.data.lights.new("eval_sun", "SUN")
    ld.energy = rs["sun_strength"]
    ld.color = rs["sun_color"]
    ld.angle = math.radians(1.5)
    try:
        ld.use_shadow = True
    except AttributeError:
        pass
    sun = bpy.data.objects.new("eval_sun", ld)
    az, el = math.radians(rs["sun_azimuth"]), math.radians(rs["sun_elevation"])
    to_sun = Vector((math.sin(az) * math.cos(el), math.cos(az) * math.cos(el), math.sin(el)))
    sun.rotation_euler = (-to_sun).to_track_quat("-Z", "Y").to_euler()
    scn.collection.objects.link(sun)


def setup_render(scn, samples):
    set_engine(scn)
    ee = scn.eevee
    for attr, val in (("taa_render_samples", samples), ("use_shadows", True),
                      ("use_raytracing", True), ("use_gtao", True), ("shadow_ray_count", 2),
                      ("shadow_step_count", 8)):
        if hasattr(ee, attr):
            try:
                setattr(ee, attr, val)
            except (TypeError, AttributeError):
                pass
    scn.render.film_transparent = True
    scn.render.image_settings.file_format = "PNG"
    scn.render.image_settings.color_mode = "RGBA"
    scn.render.resolution_percentage = 100
    try:
        scn.view_settings.view_transform = "AgX"
        scn.view_settings.look = "AgX - Medium High Contrast"
    except TypeError:
        try:
            scn.view_settings.look = "None"
        except TypeError:
            pass


# ---------------------------------------------------------------- ground under the camera
class Ground:
    def __init__(self, scn):
        dg = bpy.context.evaluated_depsgraph_get()
        self.trees = []
        for ob in scn.objects:
            tagged = bool(ob.get("ground"))                       # build tags walkable ground
            named = GROUND_RX.search(ob.name) and not NOT_GROUND_RX.search(ob.name)
            if ob.type == "MESH" and (tagged or named) and not ob.hide_render:
                ev = ob.evaluated_get(dg)
                me = ev.to_mesh()
                verts = [ob.matrix_world @ v.co for v in me.vertices]
                polys = [tuple(p.vertices) for p in me.polygons]
                ev.to_mesh_clear()
                if polys:
                    self.trees.append((ob.name, BVHTree.FromPolygons(verts, polys, all_triangles=False)))
        self.scn, self.dg = scn, dg

    def z(self, x, y):
        """Highest ground-like surface under (x, y); else the lowest hit of anything."""
        best = None
        for _name, t in self.trees:
            hit = t.ray_cast(Vector((x, y, 300.0)), Vector((0, 0, -1)), 1000)
            if hit[0] is not None and (best is None or hit[0].z > best):
                best = hit[0].z
        if best is not None:
            return best, "ground mesh"
        lowest, z0 = None, 300.0
        for _ in range(50):
            ok, loc, _n, _i, _ob, _m = self.scn.ray_cast(self.dg, Vector((x, y, z0)), Vector((0, 0, -1)))
            if not ok:
                break
            lowest, z0 = loc.z, loc.z - 0.01
        return (lowest if lowest is not None else 0.0), "lowest hit"


# ---------------------------------------------------------------- camera
def photo_size(cam):
    p = ROOT / cam["photo"]
    if "photo_w" in cam and "photo_h" in cam:
        return cam["photo_w"], cam["photo_h"]
    try:
        from PIL import Image, ImageOps
        im = ImageOps.exif_transpose(Image.open(p))
        return im.size
    except Exception:  # noqa: BLE001  (no PIL in this Blender: use Blender's loader)
        img = bpy.data.images.load(str(p), check_existing=True)
        return tuple(img.size)


def cam_rotation(heading, pitch, roll):
    # Blender cameras look down -Z with +Y up. Rx(90+pitch) looks north and tilts up;
    # Rz(-heading) turns clockwise (compass); roll spins about the view axis.
    return (Matrix.Rotation(math.radians(-heading), 4, "Z")
            @ Matrix.Rotation(math.radians(90 + pitch), 4, "X")
            @ Matrix.Rotation(math.radians(roll), 4, "Z"))


def place_camera(scn, cam, ground, long_side):
    w, h = photo_size(cam)
    if w >= h:
        rw, rh = long_side, max(2, round(long_side * h / w))
    else:
        rw, rh = max(2, round(long_side * w / h)), long_side
    scn.render.resolution_x, scn.render.resolution_y = rw, rh
    if "z_ground" in cam:
        gz, how = float(cam["z_ground"]), "z_ground"
    else:
        gz, how = ground.z(cam["x"], cam["y"])
    ob = bpy.data.objects.get("eval_cam")
    if ob is None:
        cd = bpy.data.cameras.new("eval_cam")
        ob = bpy.data.objects.new("eval_cam", cd)
        scn.collection.objects.link(ob)
    cd = ob.data
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = 24.0
    cd.lens = 12.0 / math.tan(math.radians(cam["fov"]) / 2)
    cd.clip_start, cd.clip_end = 0.05, 3000
    cd.shift_x = float(cam.get("shift_x", 0))
    cd.shift_y = float(cam.get("shift_y", 0))
    ob.matrix_world = Matrix.Translation((cam["x"], cam["y"], gz + cam["z_eye"])) @ \
        cam_rotation(cam["heading"], cam.get("pitch", 0), cam.get("roll", 0))
    scn.camera = ob
    bpy.context.view_layer.update()
    return ob, (rw, rh), gz, how


# ---------------------------------------------------------------- labels
def visible_labels(scn, camob, size):
    """Image positions of labelled objects (custom property "label") visible from the camera.
    Objects sharing a label (building + its _deco/_cables parts) are merged."""
    dg = bpy.context.evaluated_depsgraph_get()
    eye = camob.matrix_world.translation
    groups = {}
    for ob in scn.objects:
        if ob.type == "MESH" and not ob.hide_render and ob.get("label") and len(ob.data.vertices):
            groups.setdefault(str(ob.get("label")), []).append(ob)
    out = []
    for label, obs in groups.items():
        members = set(obs)
        pts = []
        for ob in obs:
            me = ob.data
            n = len(me.vertices)
            step = max(1, n // 300)
            for i in range(0, n, step):
                wp = ob.matrix_world @ me.vertices[i].co
                uvz = world_to_camera_view(scn, camob, wp)
                if not (0.02 < uvz.x < 0.98 and 0.02 < uvz.y < 0.98 and uvz.z > 0.5):
                    continue
                d = wp - eye
                dist = d.length
                ok, loc, _n, _i, hit, _m = scn.ray_cast(dg, eye, d.normalized(), distance=dist + 0.5)
                if ok and hit is not None and hit.original in members and \
                        (loc - wp).length < max(1.5, 0.03 * dist):
                    pts.append((uvz.x, uvz.y, dist))
        if len(pts) < 3:
            continue
        us = sorted(p[0] for p in pts)
        vs = sorted(p[1] for p in pts)
        out.append({"text": label, "u": round(us[len(us) // 2], 4), "v": round(1 - vs[int(len(vs) * 0.75)], 4),
                    "dist": round(min(p[2] for p in pts), 1), "n": len(pts)})
    out.sort(key=lambda r: r["dist"])
    return out


# ---------------------------------------------------------------- compositing
def finish(rgba_path, model_path, mask_path, rs):
    """Composite the transparent render over a sky gradient; write the geometry mask."""
    try:
        from PIL import Image
        import numpy as np
    except ImportError:
        Path(rgba_path).replace(model_path)   # keep the RGBA render; compare handles alpha
        return
    im = Image.open(rgba_path).convert("RGBA")
    a = np.asarray(im).astype(np.float32) / 255.0
    h, w = a.shape[:2]
    t = np.linspace(0, 1, h, dtype=np.float32)[:, None, None]
    top, hor = np.array(rs["sky_top"], np.float32), np.array(rs["sky_horizon"], np.float32)
    sky = top * (1 - t) + hor * t
    alpha = a[..., 3:4]
    rgb = a[..., :3] * alpha + sky * (1 - alpha)   # Blender writes straight alpha
    Image.fromarray((rgb * 255 + 0.5).clip(0, 255).astype(np.uint8)).save(model_path)
    Image.fromarray(((alpha[..., 0] > 0.5) * 255).astype(np.uint8)).save(mask_path)
    Path(rgba_path).unlink()


# ---------------------------------------------------------------- main
def coerce(v):
    try:
        return float(v)
    except ValueError:
        return v


def main():
    args = parse_args()
    data = json.loads(Path(args.cams).read_text())
    cams = data["cams"]
    rs = dict(DEFAULT_RENDER, **data.get("render", {}))
    for s in args.set:
        k, v = s.split("=", 1)
        name, key = k.split(".", 1)
        cams[name][key] = coerce(v)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    scn = bpy.context.scene
    samples = 4 if args.fast else args.samples
    setup_render(scn, samples)
    setup_lighting(scn, rs)
    ground = Ground(scn)

    jobs = []
    if args.variants:
        for v in json.loads(Path(args.variants).read_text()):
            c = dict(cams[v["cam"]], **v.get("set", {}))
            jobs.append((v["cam"], c, Path(v["out"]), True))
    else:
        only = {s for s in args.only.split(",") if s}
        for name, c in cams.items():
            if only and name not in only:
                continue
            if "photo_w" not in c and not (ROOT / c["photo"]).exists():
                print("skip %s: photo missing (%s; ./fetch_data.sh --photos)" % (name, c["photo"]))
                continue
            jobs.append((name, c, out / ("%s_model%s.png" % (name, args.suffix)), args.fast or args.no_labels))

    for name, c, model_path, nolabels in jobs:
        t0 = time.time()
        camob, size, gz, how = place_camera(scn, c, ground, args.long)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        stem = model_path.with_suffix("")
        rgba = str(stem) + "_rgba.png"
        mask = str(stem).replace("_model", "_mask") + ".png" if "_model" in stem.name else str(stem) + "_mask.png"
        scn.render.filepath = rgba
        bpy.ops.render.render(write_still=True)
        finish(rgba, str(model_path), mask, rs)
        info = {"cam": name, "pose": {k: c[k] for k in c if k not in ("credit",)},
                "ground_z": round(gz, 3), "ground_from": how, "eye_z": round(gz + c["z_eye"], 3),
                "size": size, "blend": bpy.data.filepath,
                "blend_mtime": time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(os.path.getmtime(bpy.data.filepath)))
                if bpy.data.filepath and os.path.exists(bpy.data.filepath) else None,
                "render_s": round(time.time() - t0, 1)}
        if not nolabels:
            info["labels"] = visible_labels(scn, camob, size)
        Path(str(stem) + ".json").write_text(json.dumps(info, indent=1))
        if gz < -1.5:
            print("EVAL WARNING %s: ground under the camera is at z %.2f (moat/pit in the model?); "
                  "move the camera or set z_ground" % (name, gz))
        print("EVAL rendered %s -> %s  (%dx%d, ground z %.2f via %s, %.1fs)" % (
            name, model_path, size[0], size[1], gz, how, time.time() - t0))


if __name__ == "__main__":
    main()

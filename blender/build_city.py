"""Build the Jaffa Gate scene from data/scene_spec.json and export it for the game.

    blender -b --factory-startup -P blender/build_city.py -- \
        [--out game/public/city.glb] [--blend build/city.blend] [--preview renders] [--no-export]

Local frame: +X east, +Y north, Z up, metres; origin = Jaffa Gate (OSM node 561157424).
Objects carry a custom property nocol=1 when the game must not collide with them (exported as
glTF node extras). Props are linked duplicates of library meshes (blender/props.py).
"""
import argparse
import json
import math
import sys
import zlib
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import facade_build as fb  # noqa: E402
import fortifications  # noqa: E402
import landmarks  # noqa: E402
import materials  # noqa: E402
import meshkit as mk  # noqa: E402

try:
    import props as proplib  # noqa: E402
except Exception as e:  # noqa: BLE001
    print("props library unavailable:", e)
    proplib = None

ROOT = HERE.parent
UP = Vector((0, 0, 1))


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--spec", default=str(ROOT / "data/scene_spec.json"))
    p.add_argument("--out", default=str(ROOT / "game/public/city.glb"))
    p.add_argument("--blend", default=str(ROOT / "build/city.blend"))
    p.add_argument("--preview", default=str(ROOT / "renders"))
    p.add_argument("--no-export", action="store_true")
    p.add_argument("--part", default=None, help="base | <sector id>; default: legacy single scene (base + s00)")
    return p.parse_args(argv)


# ---------------------------------------------------------------- buildings
def obb(ring):
    best = None
    for i in range(len(ring)):
        a, b = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        t = b - a
        if t.length < 0.5:
            continue
        t.normalize()
        s = Vector((-t.y, t.x))
        us = [Vector(p).dot(t) for p in ring]
        vs = [Vector(p).dot(s) for p in ring]
        A = (max(us) - min(us)) * (max(vs) - min(vs))
        if best is None or A < best[0]:
            c = t * (max(us) + min(us)) / 2 + s * (max(vs) + min(vs)) / 2
            lu, lv = max(us) - min(us), max(vs) - min(vs)
            best = (A, c, t, s, lu, lv) if lu >= lv else (A, c, s, t, lv, lu)
    return best[1:]


def roof_flat(mb, bd, wall_mat, col, gen=None):
    ring = [tuple(p) for p in bd["ring"]]
    top = bd["top"]
    rz = top - 0.9
    if bd["style"].get("parapet") == "balustrade" and bd["tier"] == "hero" and gen:
        return roof_balustrade(mb, bd, wall_mat, col, gen)
    roofs = bd.get("roof") or []
    if not roofs:
        fl, ft = mk.tess2d([ring])
        mb.tris([(p[0], p[1], top) for p in fl], ft, "lime", UP)
        return []
    holes = [r["ext"] for r in roofs]
    try:
        fl, ft = mk.tess2d([ring] + holes)
        mb.tris([(p[0], p[1], top) for p in fl], ft, wall_mat, UP, col=col)
    except Exception:  # noqa: BLE001
        pass
    for r in roofs:
        ext = r["ext"]
        for i in range(len(ext)):
            a, b = ext[i], ext[(i + 1) % len(ext)]
            mb.poly([(a[0], a[1], rz), (b[0], b[1], rz), (b[0], b[1], top), (a[0], a[1], top)], wall_mat,
                    Vector((-(b[1] - a[1]), b[0] - a[0], 0)), col=col)
        fl, ft = mk.tess2d([ext] + r["holes"])
        mb.tris([(p[0], p[1], rz) for p in fl], ft, "lime", UP)
    return roofs


def roof_balustrade(mb, bd, wall_mat, col, gen):
    """Stone balustrade parapet (hotels on the square): plinth, balusters (cut-out card), coping."""
    ring = [tuple(p) for p in bd["ring"]]
    top = bd["top"]
    rz = top - 0.9
    plinth = rz + 0.18
    roofs = bd.get("roof") or []
    holes = [r["ext"] for r in roofs]
    try:
        fl, ft = mk.tess2d([ring] + holes)
        mb.tris([(p[0], p[1], plinth) for p in fl], ft, wall_mat, UP, col=col)
    except Exception:  # noqa: BLE001
        pass
    rect = mk.atlas_rect(gen["cutout"]["grid"], gen["cutout"]["cells"]["balustrade"])
    for i in range(len(ring)):
        a, b = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        t = b - a
        L = t.length
        if L < 0.3:
            continue
        t.normalize()
        nin = Vector((-t.y, t.x))
        c = (a + b) / 2 + nin * 0.16
        k = max(1, round(L / 1.2))
        for j in range(k):
            p0, p1 = a + t * (L * j / k), a + t * (L * (j + 1) / k)
            mk.card(mb, ((p0 + p1) / 2 + nin * 0.16).to_3d() + UP * plinth, t.to_3d(), UP, (p1 - p0).length,
                    top - 0.14 - plinth, "cut", rect, col=STONE, double=True)
        dz = 0.002 * (i % 2)
        mk.box(mb, c, t, nin, L, 0.34, top - 0.14 + dz, top + dz, "dressed", bottom=True, col=STONE)
        n_posts = max(1, round(L / 3.0))
        for j in range(n_posts + 1):
            p = a + t * (L * j / n_posts) + nin * 0.16
            mk.box(mb, p, t, nin, 0.3, 0.3, plinth, top - 0.14, "dressed", col=STONE)
    for r in roofs:
        ext = r["ext"]
        for i in range(len(ext)):
            a, b = ext[i], ext[(i + 1) % len(ext)]
            mb.poly([(a[0], a[1], rz), (b[0], b[1], rz), (b[0], b[1], plinth), (a[0], a[1], plinth)], wall_mat,
                    Vector((-(b[1] - a[1]), b[0] - a[0], 0)), col=col)
        fl, ft = mk.tess2d([ext] + r["holes"])
        mb.tris([(p[0], p[1], rz) for p in fl], ft, "lime", UP)
    return roofs


STONE = (1.0, 1.0, 1.0)


def roof_hipped(mb, ring, top):
    c, t, s, ll, ls = obb(ring)
    ov = 0.35
    ll, ls = ll + 2 * ov, ls + 2 * ov
    hr = ls / 2 * 0.5
    c3 = Vector((c.x, c.y, top))
    t3, s3 = Vector((t.x, t.y, 0)), Vector((s.x, s.y, 0))
    cs = [c3 - t3 * ll / 2 - s3 * ls / 2, c3 + t3 * ll / 2 - s3 * ls / 2,
          c3 + t3 * ll / 2 + s3 * ls / 2, c3 - t3 * ll / 2 + s3 * ls / 2]
    r0 = c3 - t3 * (ll / 2 - ls / 2) + UP * hr
    r1 = c3 + t3 * (ll / 2 - ls / 2) + UP * hr
    mb.poly([cs[0], cs[1], r1, r0], "roof_tiles", -s3 + UP)
    mb.poly([cs[2], cs[3], r0, r1], "roof_tiles", s3 + UP)
    mb.poly([cs[1], cs[2], r1], "roof_tiles", t3 + UP)
    mb.poly([cs[3], cs[0], r0], "roof_tiles", -t3 + UP)
    for k in range(4):                                     # eaves underside
        mb.poly([cs[k], cs[(k + 1) % 4], cs[(k + 1) % 4] - UP * 0.05, cs[k] - UP * 0.05], "roof_tiles",
                (cs[k] + cs[(k + 1) % 4]) / 2 - c3)
    fl, ft = mk.tess2d([ring])
    mb.tris([(p[0], p[1], top) for p in fl], ft, "lime", -UP)


def add_domes(mb, roofs, rz, count):
    for r in roofs[:1]:
        ext = r["ext"]
        c, t, s, ll, ls = obb(ext)
        rad = min(2.6, 0.24 * ls)
        if rad < 0.9:
            return
        spots = [c] if count == 1 else [c - t * ll / 4, c + t * ll / 4]
        for p in spots:
            if all(mk.point_in((p.x + math.cos(a) * rad * 1.1, p.y + math.sin(a) * rad * 1.1), ext)
                   for a in [k * math.pi / 4 for k in range(8)]):
                mk.dome(mb, p.x, p.y, rz, rad, "lime", drum=0.6)


def vernacular_domes(mb, bd, z, seg=12, rings=4, limit=None):
    """Field of shallow lime domes from the spec (pipeline/roofscape.py)."""
    for i, d in enumerate(bd.get("dome_list", [])[:limit]):
        g = 0.9 + 0.1 * ((i * 37 + len(bd["id"])) % 7) / 6
        mk.dome(mb, d["c"][0], d["c"][1], z - 0.05, d["r"], "lime", drum=d["drum"], seg=seg, rings=rings,
                rise=d["rise"], col=(g, g, g * 0.98))


def context_windows(mb, bd, gen):
    """Flat window cards on context buildings (positions from the spec): windows at distance for 2 tris."""
    ring = [tuple(p) for p in bd["ring"]]
    for wdw in bd.get("cwin", []):
        i = wdw["edge"]
        a, b = Vector(ring[i]), Vector(ring[(i + 1) % len(ring)])
        t = (b - a).normalized()
        n = Vector((t.y, -t.x))
        rect = mk.atlas_rect(gen["doors"]["grid"], gen["doors"]["cells"][wdw["cell"]])
        c = (a + t * wdw["u"] + n * 0.05).to_3d() + UP * wdw["z"]     # 5 cm: safe for depth precision far away
        mk.card(mb, c, t.to_3d(), UP, 1.0, 1.5, "doors", rect)


def build_building(mbs, bd, gen, signs, place):
    ring = [tuple(p) for p in bd["ring"]]
    st = bd["style"]
    wall = st["wall"]
    col = tuple(min(1.0, c / 1.06) for c in bd["tint"])
    mb = mbs["solid"]
    fac = {f["edge"]: f for f in bd.get("facades", [])}
    key = bd["id"]
    if bd["tier"] == "context":
        context_windows(mbs["deco"], bd, gen)
    for i in range(len(ring)):
        a, b = ring[i], ring[(i + 1) % len(ring)]
        f = fac.get(i)
        z_top = bd["top"] - 0.72 if st.get("parapet") == "balustrade" and bd["tier"] == "hero" else bd["top"]
        fb.wall_panel(mb, a, b, bd["base"], z_top, f["openings"] if f else [], wall, col, gen, key + str(i))
        if f:
            fb.facade_extras(mbs, a, b, f, gen, signs, place, col)
    if st["roof"] == "hipped" and bd["tier"] != "context":
        roof_hipped(mb, ring, bd["top"])
        return
    roofs = roof_flat(mb, bd, wall, col, gen)
    rz = bd["top"] - 0.9
    for rm in bd.get("roof_rooms", []):
        rr = [tuple(p) for p in rm["ring"]]
        lens = [math.dist(rr[i], rr[(i + 1) % len(rr)]) for i in range(len(rr))]
        door_edge = lens.index(max(lens))
        for i in range(len(rr)):
            if i == door_edge:
                continue
            a, b = rr[i], rr[(i + 1) % len(rr)]
            fb.wall_panel(mb, a, b, rz, rz + rm["h"], [], "rubble" if wall == "rubble" else "ashlar", col, gen)
        if rm["roof"] == "tiles":
            roof_hipped(mb, rr, rz + rm["h"])
        else:
            fl, ft = mk.tess2d([rr])
            mb.tris([(p[0], p[1], rz + rm["h"]) for p in fl], ft, "lime", UP)
        i = door_edge                                       # a door on the longest side
        L = lens[i]
        fb.wall_panel(mb, rr[i], rr[(i + 1) % len(rr)], rz, rz + rm["h"],
                      [{"kind": "door", "u0": L / 2 - 0.45, "u1": L / 2 + 0.45, "v0": rz + 0.05, "v1": rz + 2.1,
                        "arch": None, "depth": 0.15, "lo": "door_green"}],
                      "rubble" if wall == "rubble" else "ashlar", col, gen)
    if st["domes"] and roofs:
        add_domes(mb, roofs, rz, st["domes"])
    vernacular_domes(mb, bd, rz)


# ---------------------------------------------------------------- ground
def build_ground(mbs, spec):
    mat_of = {"paving": "paving", "setts": "setts", "moat": "rubble", "grass": "grass", "kerb_band": "dressed"}
    for g in spec["ground"]:
        mb = mbs["ground"]
        mat = mat_of.get(g["mat"], "paving")
        col = (0.9, 0.88, 0.84) if g["mat"] == "kerb_band" else None
        for t in g["tris"]:
            mb.poly(t, mat, UP, col=col)
    for k in spec["kerbs"]:
        a, b = k["a"], k["b"]
        q = [(a[0], a[1], k["z0"] - 0.02), (b[0], b[1], k["z0"] - 0.02), (b[0], b[1], k["z1"]), (a[0], a[1], k["z1"])]
        n = Vector((b[1] - a[1], -(b[0] - a[0]), 0))
        mbs["ground"].poly(q, "dressed", n, col=(0.85, 0.83, 0.8))
    for s in spec["steps"]:
        ext = s["poly"]["ext"]
        try:
            fl, ft = mk.tess2d([ext] + s["poly"]["holes"])
        except Exception:  # noqa: BLE001
            continue
        dx_, dy_ = s.get("dir", [1, 0])
        tile = 4.0
        mbs["ground"].tris([(p[0], p[1], s["top"]) for p in fl], ft, "paving", UP,
                           uvfn=lambda p, dx_=dx_, dy_=dy_: ((p[0] * -dy_ + p[1] * dx_) / tile, (p[0] * dx_ + p[1] * dy_) / tile))
        for i in range(len(ext)):
            a, b = ext[i], ext[(i + 1) % len(ext)]
            q = [(a[0], a[1], s["bottom"]), (b[0], b[1], s["bottom"]), (b[0], b[1], s["top"]), (a[0], a[1], s["top"])]
            mbs["ground"].poly(q, "ashlar", Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=(0.82, 0.8, 0.76))


# ---------------------------------------------------------------- props
class Placer:
    def __init__(self, lib, col):
        self.lib, self.col = lib or {}, col
        self.count, self.missing = {}, {}

    def __call__(self, ty, pos, yaw, nocol=True, scale=1.0):
        me = self.lib.get(ty)
        if me is None:
            self.missing[ty] = self.missing.get(ty, 0) + 1
            return
        ob = bpy.data.objects.new("%s.%d" % (ty, self.count.get(ty, 0)), me)
        ob.location = pos
        ob.rotation_euler = (0, 0, yaw)
        ob.scale = (scale, scale, scale)
        if nocol:
            ob["nocol"] = 1
        self.col.objects.link(ob)
        self.count[ty] = self.count.get(ty, 0) + 1


def cable_curve(a, b, sag, n=12):
    A, B = Vector(a), Vector(b)
    return [A.lerp(B, i / n) - UP * (sag * 4 * (i / n) * (1 - i / n)) for i in range(n + 1)]


# ---------------------------------------------------------------- scene, export, preview
def setup_preview(outdir: Path):
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
    sun_d = bpy.data.lights.new("sun", "SUN")
    sun_d.energy = 4.5
    sun_d.color = (1.0, 0.93, 0.82)
    sun_d.angle = math.radians(1.0)
    sun = bpy.data.objects.new("sun", sun_d)
    sun.rotation_euler = (math.radians(52), 0, math.radians(-130))
    scn.collection.objects.link(sun)
    scn.render.resolution_x, scn.render.resolution_y = 1280, 720
    try:
        scn.view_settings.view_transform = "AgX"
    except TypeError:
        pass
    cams = {
        "outside_gate": ((-24, 4, 1.7), (3, -4, 5)),
        "square_west": ((22, -2, 1.7), (80, 14, 7)),
        "square_east": ((92, 2, 1.7), (20, -2, 6)),
        "david_street": ((104, 8.5, 1.7), (150, 8.5, -2)),
        "aerial": ((-40, -70, 70), (55, 5, 0)),
    }
    for name, (eye, look) in cams.items():
        cd = bpy.data.cameras.new(name)
        cd.lens = 18 if name != "aerial" else 28
        cam = bpy.data.objects.new("cam_" + name, cd)
        cam.location = eye
        cam.rotation_euler = (Vector(look) - Vector(eye)).to_track_quat("-Z", "Y").to_euler()
        scn.collection.objects.link(cam)
        scn.camera = cam
        scn.render.filepath = str(outdir / ("%s.png" % name))
        try:
            bpy.ops.render.render(write_still=True)
            print("rendered", scn.render.filepath)
        except Exception as e:  # noqa: BLE001
            print("render failed", name, e)
    bpy.data.objects.remove(sun)


def build_steps(mb, steps):
    for s in steps:
        ext = s["poly"]["ext"]
        try:
            fl, ft = mk.tess2d([ext] + s["poly"]["holes"])
        except Exception:  # noqa: BLE001
            continue
        dx_, dy_ = s.get("dir", [1, 0])
        tile = 4.0
        mb.tris([(p[0], p[1], s["top"]) for p in fl], ft, "paving", UP,
                uvfn=lambda p, dx_=dx_, dy_=dy_: ((p[0] * -dy_ + p[1] * dx_) / tile, (p[0] * dx_ + p[1] * dy_) / tile))
        for i in range(len(ext)):
            a, b = ext[i], ext[(i + 1) % len(ext)]
            q = [(a[0], a[1], s["bottom"]), (b[0], b[1], s["bottom"]), (b[0], b[1], s["top"]), (a[0], a[1], s["top"])]
            mb.poly(q, "ashlar", Vector((b[1] - a[1], -(b[0] - a[0]), 0)), col=(0.82, 0.8, 0.76))


def build_walls_generic(mb, walls):
    """OSM wall circuit outside the hand-modelled Jaffa Gate stretch: stepped, crenellated."""
    for w in walls:
        mk.thick_wall(mb, [tuple(w["a"]), tuple(w["b"])], w["z0"], w["z1"], w["thick"], "fort",
                      merlons=(0.9, 0.75, 1.4, 0.6), outside="right")


def build_lod(mb, bd, gen):
    """Cheap massing for distant sectors: plain walls, flat or hipped roof, window cards, domes."""
    ring = [tuple(p) for p in bd["ring"]]
    col = tuple(min(1.0, c / 1.06) for c in bd["tint"])
    wall = bd["style"]["wall"]
    for i in range(len(ring)):
        fb.wall_panel(mb, ring[i], ring[(i + 1) % len(ring)], bd["base"], bd["top"], [], wall, col, gen)
    if bd["style"]["roof"] == "hipped":
        roof_hipped(mb, ring, bd["top"])
    else:
        fl, ft = mk.tess2d([ring])
        mb.tris([(p[0], p[1], bd["top"]) for p in fl], ft, "lime", UP)
    context_windows(mb, bd, gen)
    vernacular_domes(mb, bd, bd["top"], seg=8, rings=2, limit=4)
    if bd["style"]["domes"]:
        c, t, s, ll, ls = obb(ring)
        r = min(2.6, 0.24 * ls)
        if r > 0.9:
            mk.dome(mb, c.x, c.y, bd["top"], r, "lime", drum=0.4, seg=8, rings=3)


def material_library(mats, tiles, collection):
    """One small quad per material: the textured materials every sector GLB refers to by name."""
    mb = mk.MeshBuilder(tiles)
    for i, name in enumerate(sorted(mats)):
        x = (i % 8) * 2.0
        y = -2000.0 - (i // 8) * 2.0
        mb.poly([Vector((x, y, -50)), Vector((x + 1, y, -50)), Vector((x + 1, y + 1, -50)), Vector((x, y + 1, -50))],
                name, UP, uv=[(0, 0), (1, 0), (1, 1), (0, 1)])
    ob = mb.to_object("material_library", mats, collection)
    ob["nocol"] = 1
    return ob


def export_glb(path, collections, images=True):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    for o in bpy.context.scene.objects:
        o.select_set(False)
    n = 0
    for c in collections:
        for o in c.all_objects:
            o.select_set(True)
            n += 1
    if not n:
        print("nothing to export for", path)
        return
    kw = dict(filepath=str(path), export_format="GLB", export_extras=True, export_yup=True, use_selection=True,
              export_apply=True, export_image_format="WEBP" if images else "NONE", export_texcoords=True,
              export_image_quality=85)
    try:
        bpy.ops.export_scene.gltf(**kw, export_vertex_color="ACTIVE")
    except TypeError:
        bpy.ops.export_scene.gltf(**kw)
    print("exported", path, n, "objects")


def main():
    args = parse_args()
    part = args.part
    if part == "base":
        spec = json.loads((ROOT / "data/spec/base.json").read_text())
    elif part:
        spec = json.loads((ROOT / ("data/spec/%s.json" % part)).read_text())
    else:
        spec = json.loads(Path(args.spec).read_text())
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mats, tiles, gen = materials.build(ROOT)
    sj = ROOT / "data/textures/gen/signs.json"
    signs = json.loads(sj.read_text()) if sj.exists() and "signs" in mats else None
    cols = {}

    def col(name):
        if name not in cols:
            cols[name] = bpy.data.collections.new(name)
            bpy.context.scene.collection.children.link(cols[name])
        return cols[name]
    lib = proplib.build_library(mats, tiles, gen) if proplib else {}
    place = Placer(lib, col("props"))

    def mbset():
        return {"solid": mk.MeshBuilder(tiles), "deco": mk.MeshBuilder(tiles), "signs": mk.MeshBuilder(tiles),
                "cables": mk.MeshBuilder(tiles)}

    def flush(mbs, name, collection, label=None):
        for p_, mb in mbs.items():
            if mb.empty():
                continue
            ob = mb.to_object(name if p_ == "solid" else "%s_%s" % (name, p_), mats, collection)
            if p_ != "solid":
                ob["nocol"] = 1
            if label:
                ob["label"] = label

    detailed = [b for b in spec["buildings"] if b["tier"] in ("hero", "mid")]
    context = [b for b in spec["buildings"] if b["tier"] == "context"]
    hi = col("city")
    for bd in detailed:                                     # sector detail (or legacy scene)
        mbs = mbset()
        if not landmarks.build(mbs, bd, gen, place):
            build_building(mbs, bd, gen, signs, place)
        flush(mbs, "bld_%s" % bd["id"], hi, bd["tags"].get("name:en") or bd["tags"].get("name") or bd["id"])
    if context:
        mbs = mbset()
        for bd in context:
            build_building(mbs, bd, gen, signs, place)
        flush(mbs, "context_massing", col("context"))
    if part in (None, "base"):
        fmbs = {k: mk.MeshBuilder(tiles) for k in ("jaffa_gate", "city_wall", "citadel")}
        fortifications.build(fmbs, spec, gen, place)
        for k, mb in fmbs.items():
            mb.to_object(k, mats, col("walls"))
        wg = mk.MeshBuilder(tiles)
        build_walls_generic(wg, spec.get("walls_generic", []))
        if not wg.empty():
            wg.to_object("city_walls_osm", mats, col("walls"))
        gmbs = {"ground": mk.MeshBuilder(tiles)}
        build_ground(gmbs, dict(spec, steps=[]))
        gmbs["ground"].to_object("ground", mats, col("ground"))["ground"] = 1
    st = mk.MeshBuilder(tiles)
    build_steps(st, spec.get("steps", []))
    if not st.empty():
        st.to_object("steps", mats, hi)
    gd = mk.MeshBuilder(tiles)
    for dcl in spec.get("ground_decals", []):
        cell = gen["decal"]["cells"].get(dcl["type"])
        if not cell:
            continue
        rect = mk.atlas_rect(gen["decal"]["grid"], cell, size_px=1024)
        a = math.radians(dcl["rot"])
        right = Vector((math.cos(a), -math.sin(a), 0))
        fwd = Vector((math.sin(a), math.cos(a), 0))
        c = Vector(dcl["p"]) - fwd * dcl["h"] / 2
        q = [c - right * dcl["w"] / 2, c + right * dcl["w"] / 2, c + right * dcl["w"] / 2 + fwd * dcl["h"],
             c - right * dcl["w"] / 2 + fwd * dcl["h"]]
        u0, v0, u1, v1 = rect
        gd.poly(q, "decal", UP, uv=[(u0, v0), (u1, v0), (u1, v1), (u0, v1)])
    if not gd.empty():
        gd.to_object("ground_decals", mats, col("ground") if part == "base" else hi)["nocol"] = 1
    bm_ = mk.MeshBuilder(tiles)
    for bmz in spec.get("beams", []):
        mk.tube(bm_, [bmz["a"], bmz["b"]], 0.05, "metal_green", sides=6, col=fb.GREEN)
    if not bm_.empty():
        bm_.to_object("street_beams", mats, hi)["nocol"] = 1
    cab = mk.MeshBuilder(tiles)
    for c in spec.get("cables", []):
        mk.tube(cab, cable_curve(c["a"], c["b"], c["sag"]), c.get("r", 0.012), "iron")
    if not cab.empty():
        cab.to_object("street_cables", mats, hi)["nocol"] = 1
    for p in spec.get("props", []):
        place(p["type"], Vector(p["p"]), -math.radians(p["rot"]), not p.get("col", False), p.get("s", 1.0))
    if part not in (None, "base") and detailed:             # massing LOD for this sector
        lo = mk.MeshBuilder(tiles)
        lo4 = {"solid": lo, "deco": lo, "signs": lo, "cables": lo}
        for bd in detailed:
            if not landmarks.build(lo4, bd, gen, place, lod=True):
                build_lod(lo, bd, gen)
        lo.to_object("lod_%s" % part, mats, col("lod"))

    for name, c in cols.items():
        print("collection %-8s objects %5d faces %8d" % (name, len(c.all_objects),
                                                          sum(len(o.data.polygons) for o in c.all_objects if o.type == "MESH")))
    print("missing prop types %s" % place.missing)
    pub = ROOT / "game/public"
    if not args.no_export:
        if part == "base":
            # textures live once in materials.glb; every other GLB refers to materials by name
            material_library(mats, tiles, col("materials"))
            export_glb(pub / "base/materials.glb", [col("materials")])
            export_glb(pub / "base/ground.glb", [col("ground")], images=False)
            export_glb(pub / "base/walls.glb", [col("walls")], images=False)
            export_glb(pub / "base/context.glb", [col("context"), col("props")], images=False)
        elif part:
            export_glb(pub / ("sectors/%s.glb" % part), [hi, col("props")], images=False)
            export_glb(pub / ("sectors/%s_lo.glb" % part), [col("lod")], images=False)
        else:
            export_glb(args.out, [c for n, c in cols.items() if n != "lod"])
    if args.preview and not part:
        out = Path(args.preview)
        out.mkdir(parents=True, exist_ok=True)
        setup_preview(out)
    blend = args.blend if not part else str(ROOT / ("build/%s.blend" % part))
    Path(blend).parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("saved", blend)


if __name__ == "__main__":
    main()

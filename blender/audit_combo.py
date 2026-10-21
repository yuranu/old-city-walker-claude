import bpy, sys, runpy
from mathutils import Vector
# load the parts one at a time, keeping only objects that reach the --bbox (+5 m): memory stays at about one
# part's size instead of the sum of all (the full-city audit of 5 parts needed 14 GB and was OOM-killed)
parts = sys.argv[sys.argv.index("--parts") + 1].split(",")
bb = [float(v) for v in sys.argv[sys.argv.index("--bbox") + 1].split(",")] if "--bbox" in sys.argv else None
bpy.ops.wm.read_factory_settings(use_empty=True)


def reaches(o):
    if bb is None:
        return True
    cs = [o.matrix_world @ Vector(c) for c in o.bound_box]
    return not (max(c.x for c in cs) < bb[0] - 5 or min(c.x for c in cs) > bb[2] + 5 or
                max(c.y for c in cs) < bb[1] - 5 or min(c.y for c in cs) > bb[3] + 5)


for p in parts:
    with bpy.data.libraries.load("build/%s.blend" % p, link=False) as (src, dst):
        dst.objects = [n for n in src.objects if not n.startswith("lod_") and not n.startswith("cam")]
    for o in dst.objects:
        if o is None:
            continue
        if o.type == "MESH" and reaches(o):
            o.name = p + ":" + o.name
            bpy.context.scene.collection.objects.link(o)
        else:
            bpy.data.objects.remove(o)
    bpy.data.orphans_purge(do_recursive=True)
sys.argv = [a for a in sys.argv if a != "--parts" and a not in [",".join(parts)]]
runpy.run_path("blender/audit.py", run_name="__main__")

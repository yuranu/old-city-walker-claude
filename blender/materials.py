"""Materials for the city build. glTF-exportable; names are a contract with the game:

  stone (tinted per face by vertex colour, game adds macro variation + ground grime):
      ashlar, rubble, fort, dressed (frames, sills, cornices), paving, setts; grass (moat lawn)
  atlases:  doors (closed shop doors / shutters / windows, + normal map)
            cut   (RGBA cut-outs: grilles, railings, fan lights, foliage) -> alpha test, double sided
            decal (RGBA streaks, rust, posters, manholes)                  -> alpha blend, polygon offset
            signs (RGBA sign atlas)                                        -> alpha test
  flat:     see FLAT below (props tint them further with vertex colours)
"""
import json
from pathlib import Path

import bpy

FLAT = {   # base colour (linear), roughness, metallic
    "lime": ((0.74, 0.71, 0.65), 0.9, 0.0),        # whitewashed roofs and domes
    "roof_tiles": ((0.42, 0.11, 0.05), 0.7, 0.0),
    "lead": ((0.30, 0.31, 0.32), 0.55, 0.6),       # awnings, dome sheeting
    "iron": ((0.018, 0.018, 0.018), 0.55, 0.6),    # railings, lamp posts, cables, brackets
    "metal_grey": ((0.16, 0.16, 0.155), 0.6, 0.5),  # pipes, electrical boxes
    "metal_green": ((0.05, 0.16, 0.08), 0.55, 0.3),
    "metal_dark": ((0.06, 0.06, 0.06), 0.6, 0.4),
    "plastic": ((0.85, 0.85, 0.85), 0.5, 0.0),     # tinted by vertex colour
    "wood": ((0.30, 0.18, 0.09), 0.75, 0.0),
    "cardboard": ((0.50, 0.36, 0.20), 0.9, 0.0),
    "solar": ((0.02, 0.03, 0.06), 0.15, 0.3),
    "glass_lamp": ((0.75, 0.70, 0.55), 0.2, 0.0),
    "bark": ((0.20, 0.15, 0.11), 0.9, 0.0),

    "void": ((0.01, 0.01, 0.012), 0.9, 0.0),       # darkness behind grilles
}


def _img(path, non_color=False):
    im = bpy.data.images.load(str(path), check_existing=True)
    if non_color:
        im.colorspace_settings.name = "Non-Color"
    return im


def _textured(name, diff, nor=None, rough=0.88, alpha=False):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tex = nt.nodes.new("ShaderNodeTexImage")
    tex.image = _img(diff)
    nt.links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
    if alpha == "mask":                                    # glTF alphaMode MASK, cutoff 0.5
        gt = nt.nodes.new("ShaderNodeMath")
        gt.operation = "GREATER_THAN"
        gt.inputs[1].default_value = 0.5
        nt.links.new(tex.outputs["Alpha"], gt.inputs[0])
        nt.links.new(gt.outputs[0], bsdf.inputs["Alpha"])
        m.use_backface_culling = False
    elif alpha:
        nt.links.new(tex.outputs["Alpha"], bsdf.inputs["Alpha"])
        m.use_backface_culling = True
    else:
        m.use_backface_culling = True                      # closed shells: single-sided in glTF
    if nor:
        tn = nt.nodes.new("ShaderNodeTexImage")
        tn.image = _img(nor, non_color=True)
        nm = nt.nodes.new("ShaderNodeNormalMap")
        nt.links.new(tn.outputs["Color"], nm.inputs["Color"])
        nt.links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = rough
    return m


def build(root: Path):
    mats, tiles = {}, {}
    man = json.loads((root / "data/textures/manifest.json").read_text())
    for role in ("ashlar", "rubble", "fort", "dressed"):
        info = man[role]
        mats[role] = _textured(role, root / info["maps"]["diff"], root / info["maps"].get("nor"))
        tiles[role] = info.get("tile", info["size_m"][0])
    gen = json.loads((root / "data/textures/gen/manifest.json").read_text())
    for role in ("paving", "setts", "grass"):
        mats[role] = _textured(role, root / gen[role]["diff"], root / gen[role]["nor"], rough=0.8)
        tiles[role] = gen[role]["tile"]
    # canopies / awnings: corrugated sheet (keeps the material name "awning" for the game contract)
    mats["awning"] = _textured("awning", root / gen["corrugated"]["diff"], root / gen["corrugated"]["nor"], rough=0.6)
    tiles["awning"] = gen["corrugated"]["tile"]
    mats["doors"] = _textured("doors", root / gen["doors"]["diff"], root / gen["doors"]["nor"], rough=0.6)
    mats["cut"] = _textured("cut", root / gen["cutout"]["img"], alpha="mask", rough=0.7)
    mats["decal"] = _textured("decal", root / gen["decal"]["img"], alpha=True, rough=0.9)
    signs = root / "data/textures/gen/signs.png"
    if signs.exists():
        mats["signs"] = _textured("signs", signs, alpha="mask", rough=0.6)
    if "lime" in gen:                         # lime plaster: roofs, bollards, benches (a flat colour read as untextured)
        mats["lime"] = _textured("lime", root / gen["lime"]["diff"], root / gen["lime"]["nor"], rough=0.9)
        tiles["lime"] = gen["lime"]["tile"]
    if "bark" in gen:                         # trunks: generated bark (a flat colour read as untextured)
        mats["bark"] = _textured("bark", root / gen["bark"]["diff"], root / gen["bark"]["nor"], rough=0.9)
        tiles["bark"] = gen["bark"]["tile"]
    for name, (col, rough, metal) in FLAT.items():
        if name in mats:
            continue
        m = bpy.data.materials.new(name)
        m.use_nodes = True
        bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
        bsdf.inputs["Base Color"].default_value = (*col, 1.0)
        bsdf.inputs["Roughness"].default_value = rough
        bsdf.inputs["Metallic"].default_value = metal
        m.use_backface_culling = True
        mats[name] = m
        tiles[name] = 2.0
    # ---- append-only: Haram landmark materials (blender/landmarks_haram.py, textures from
    # pipeline/gen_landmark_textures.py): gold (gilded dome, metallic), leaddome (lead sheeting,
    # metallic), herodian (Western Wall ashlar), faience (Dome of the Rock tile/marble atlas; its UV
    # rects are exposed to the builders as gen["landmarks"]["faience"]["cells"])
    lm = root / "data/textures/gen/landmarks/manifest.json"
    if lm.exists():
        lmj = json.loads(lm.read_text())
        for name, info in lmj.items():
            m = _textured(name, root / info["diff"], root / info["nor"], rough=info.get("rough", 0.8))
            bsdf = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
            bsdf.inputs["Metallic"].default_value = info.get("metallic", 0.0)
            mats[name] = m
            tiles[name] = info["tile"]
        gen["landmarks"] = lmj
    return mats, tiles, gen

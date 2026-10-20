"""Validate data/reference/overrides/*.json against the current spec and sign atlas.

    .venv/bin/python pipeline/check_overrides.py [file ...]      exit code 1 on errors

Checks: building id exists and is in the hero/mid tier, edge exists (resolved from the "at" anchor
when present, as make_spec does) and is exposed, bay centres and opening widths fit the edge,
the floors listed are the floors built (facades.storeys_for on the facade's own ground), sign
cells exist, extra signs clear the souq canopy, ground list length matches the bays. Reads every
sector spec (data/spec, or $SPEC_DIR); run make_spec.py first.
"""
import json
import math
import os
import sys
from pathlib import Path

import facades

ROOT = Path(__file__).resolve().parent.parent
GROUND_KINDS = {"shop", "door", "window", "blind"}


def main():
    sdir = Path(os.environ["SPEC_DIR"]) if os.environ.get("SPEC_DIR") else ROOT / "data/spec"
    blds = {}
    for fn_ in sorted(sdir.glob("*.json")):
        if fn_.name in ("index.json",) or fn_.name.startswith("scene_spec"):
            continue
        for b_ in json.loads(fn_.read_text()).get("buildings", []):
            if b_["osm"] not in blds or b_["id"] == b_["osm"]:
                blds[b_["osm"]] = b_
    sj = ROOT / "data/textures/gen/signs.json"
    atlas = json.loads(sj.read_text())["signs"] if sj.exists() else {}
    cells = set(atlas)
    files = [Path(a) for a in sys.argv[1:]] or sorted((ROOT / "data/reference/overrides").glob("*.json"))
    errors = warnings = 0
    for fn in files:
        try:
            d = json.loads(fn.read_text())
        except json.JSONDecodeError as e:
            print("%s: invalid JSON: %s" % (fn.name, e))
            errors += 1
            continue
        bid = d.get("building")
        b = blds.get(bid)
        if not b:
            print("%s: unknown building %r" % (fn.name, bid))
            errors += 1
            continue
        if b["tier"] == "context":
            print("%s: %s is context tier; facades are not built" % (fn.name, bid))
            warnings += 1
        r = b["ring"]
        h = d.get("settings", {}).get("height", b["top"] - b["ground"])
        top = b["top"] if abs(b["top"] - b["ground"] - h) < 0.005 else b["ground"] + h    # spec older than the file
        for e, ov in d.get("facades", {}).items():
            tag = "%s edge %s" % (fn.name, e)
            if "at" in ov:                                 # resolve the anchor like hero.facades_for
                best, bd_ = None, 3.0
                for k in range(len(r)):
                    a_, b2 = r[k], r[(k + 1) % len(r)]
                    dd = math.dist(((a_[0] + b2[0]) / 2, (a_[1] + b2[1]) / 2), ov["at"])
                    if dd < bd_:
                        best, bd_ = k, dd
                if best is None:
                    print("%s: anchor %s is not within 3 m of any edge midpoint" % (tag, ov["at"]))
                    errors += 1
                    continue
                i = best
            else:
                try:
                    i = int(e)
                except ValueError:
                    print("%s: no \"at\" anchor and the key is not an edge index; facade is skipped" % tag)
                    errors += 1
                    continue
            if not 0 <= i < len(r):
                print("%s: edge out of range (ring has %d edges)" % (tag, len(r)))
                errors += 1
                continue
            L = math.dist(r[i], r[(i + 1) % len(r)])
            if not b["exposed"][i]:
                print("%s: edge is not exposed (party wall); facade will not be built" % tag)
                warnings += 1
            cs = ov.get("centres")
            if cs:
                if any(c < 0.4 or c > L - 0.4 for c in cs):
                    print("%s: centres %s outside 0.4..%.1f m" % (tag, cs, L - 0.4))
                    errors += 1
                if sorted(cs) != cs:
                    print("%s: centres not sorted" % tag)
                    errors += 1
            g = ov.get("ground")
            if g is not None:
                if cs and len(g) != len(cs):
                    print("%s: ground has %d entries but %d centres" % (tag, len(g), len(cs)))
                    warnings += 1
                for k, gg in enumerate(g):
                    if gg.get("kind") not in GROUND_KINDS:
                        print("%s: ground[%d] kind %r" % (tag, k, gg.get("kind")))
                        errors += 1
                    if gg.get("sign") and gg["sign"] not in cells:
                        print("%s: ground[%d] sign %r not in atlas" % (tag, k, gg["sign"]))
                        errors += 1
            # floors: counted exactly as facades.layout builds them, from this facade's own ground
            # (lower than the building's on a sloping lot, so more floors fit)
            gs, st = facades.storey_heights(b["style"], ov)
            eg = b["edge_ground"][i]
            built = len(facades.storeys_for({"top": top}, eg, gs, st))
            nfl = len(ov.get("floors", []))
            auto = ov.get("auto", True)
            if not ov.get("blank") and (nfl or not auto) and nfl != built:
                if nfl > built:
                    print("%s: %d floors listed but only %d fit under the roof (top %.1f, facade ground %.1f, "
                          "ground storey %.1f + %.1f per floor); floors %d.. are not built" %
                          (tag, nfl, built, top, eg, gs, st, built + 1))
                else:
                    print("%s: %d floors listed but %d are built (top %.1f, facade ground %.1f, ground storey "
                          "%.1f + %.1f per floor); floors %d.. get %s windows" %
                          (tag, nfl, built, top, eg, gs, st, nfl + 1,
                           "random" if auto else "plain default"))
                warnings += 1
            for key in ("extra_signs",):
                for sg in ov.get(key, []):
                    if sg.get("cell") not in cells:
                        print("%s: %s cell %r not in atlas" % (tag, key, sg.get("cell")))
                        errors += 1
                    if sg.get("u0", 0) < 0 or sg.get("u1", 0) > L:
                        print("%s: sign %s spans %.1f..%.1f beyond edge length %.1f" %
                              (tag, sg.get("cell"), sg.get("u0", 0), sg.get("u1", 0), L))
                        errors += 1
            # souq canopy (in the spec): its brackets reach the wall 0.75 m under the sheet, which meets
            # the wall at z_wall. layout() lifts named ground signs above it; extra_signs stay as given
            fac = next((f_ for f_ in b.get("facades", []) if f_["edge"] == i), None)
            for cp in (fac or {}).get("canopies", []):
                for sg in ov.get("extra_signs", []):
                    rect = atlas.get(sg.get("cell"), {}).get("rect")
                    if not rect or "z0" not in sg:
                        continue
                    z1 = sg["z0"] + min(1.1, (sg.get("u1", 0) - sg.get("u0", 0)) * rect[3] / rect[2])   # as built
                    if sg["z0"] < cp["z_wall"] + 0.05 and z1 > cp["z_wall"] - 0.75:
                        print("%s: extra sign %s (z %.2f..%.2f) runs into the souq canopy (sheet meets the wall at "
                              "z %.2f, brackets from %.2f); put z0 above %.2f" %
                              (tag, sg.get("cell"), sg["z0"], z1, cp["z_wall"], cp["z_wall"] - 0.75, cp["z_wall"] + 0.1))
                        warnings += 1
            for fx in ov.get("extra_fixtures", []):
                if fx.get("type") == "sign" and fx.get("cell") not in cells:
                    print("%s: fixture sign %r not in atlas" % (tag, fx.get("cell")))
                    errors += 1
    print("checked %d files: %d errors, %d warnings" % (len(files), errors, warnings))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

"""Validate data/reference/overrides/*.json against the current spec and sign atlas.

    .venv/bin/python pipeline/check_overrides.py [file ...]      exit code 1 on errors

Checks: building id exists and is in the hero/mid tier, edge exists and is exposed, bay centres
and opening widths fit the edge, floors fit under the roof, sign cells exist, ground list
length matches the bays. Run make_spec.py first so the spec reflects the current OSM cleanup.
"""
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GROUND_KINDS = {"shop", "door", "window", "blind"}


def main():
    spec = json.loads((ROOT / "data/scene_spec.json").read_text())
    blds = {b["osm"]: b for b in spec["buildings"]}
    sj = ROOT / "data/textures/gen/signs.json"
    cells = set(json.loads(sj.read_text())["signs"]) if sj.exists() else set()
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
        for e, ov in d.get("facades", {}).items():
            i = int(e)
            tag = "%s edge %s" % (fn.name, e)
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
            gs = ov.get("ground_storey", 4.8 if ov.get("shops", b["style"]["shops"]) else b["style"]["storey"])
            st = ov.get("storey", b["style"]["storey"])
            nfl = len(ov.get("floors", []))
            if nfl:
                fit = int(max(0, (h - 1.0 - gs - 2.6) // st) + 1)
                if nfl > fit:
                    print("%s: %d floors listed but only %d fit under %.1f m (ground %.1f + %.1f per floor)" %
                          (tag, nfl, fit, h, gs, st))
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
            for fx in ov.get("extra_fixtures", []):
                if fx.get("type") == "sign" and fx.get("cell") not in cells:
                    print("%s: fixture sign %r not in atlas" % (tag, fx.get("cell")))
                    errors += 1
    print("checked %d files: %d errors, %d warnings" % (len(files), errors, warnings))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()

"""Findings ledger: merge a QA run's findings for a region into data/qa/ledger.json and report what is
new, still open, fixed, or REGRESSED (fixed before, back now). Fixes must never regress anything.

    .venv/bin/python pipeline/qa/ledger.py <region> <level> <findings.json> [...]
"""
import json
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import ROOT  # noqa: E402

LEDGER = ROOT / "data/qa/ledger.json"


def main():
    region, level = sys.argv[1], int(sys.argv[2])
    found = []
    for f in sys.argv[3:]:
        if Path(f).exists():
            found += json.loads(Path(f).read_text())
    found = [f for f in found if f["level"] <= level]
    led = json.loads(LEDGER.read_text()) if LEDGER.exists() else {"entries": {}}
    E = led["entries"]
    now = time.strftime("%Y-%m-%d %H:%M")
    seen = {}
    for f in found:
        k = "%s|%s" % (region, f["key"])
        seen.setdefault(k, f)
    stats = Counter()
    for k, f in seen.items():
        e = E.get(k)
        if e is None:
            E[k] = {"region": region, "first": now, "last": now, "status": "open", "finding": f}
            stats["new"] += 1
        else:
            if e["status"] == "fixed":
                e["status"] = "regressed"
                stats["REGRESSED"] += 1
            elif e["status"] == "regressed":
                stats["REGRESSED"] += 1
            else:
                stats["still open"] += 1
            e["last"], e["finding"] = now, f
    for k, e in E.items():
        if e["region"] == region and e["finding"]["level"] <= level and k not in seen and e["status"] in ("open", "regressed"):
            e["status"], e["fixed"] = "fixed", now
            stats["fixed"] += 1
    LEDGER.write_text(json.dumps(led, indent=1))
    opened = Counter(e["finding"]["kind"] for e in E.values() if e["region"] == region and e["status"] != "fixed")
    print("ledger %s L%d: %s | open by kind: %s" % (region, level, dict(stats), dict(opened)))
    if stats["REGRESSED"]:
        print("REGRESSIONS:")
        for k, e in E.items():
            if e["status"] == "regressed" and e["region"] == region:
                print("  ", k, e["finding"]["what"])


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Compare lab/production SVG richness to Pursuit reference (same course_id)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from figure_richness import metrics_from_path, pursuit_gate  # noqa: E402
from figure_tiers import resolve  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: compare_pursuit_richness.py COURSE_ID [tier]", file=sys.stderr)
        return 2
    cid = sys.argv[1]
    lab_tier = sys.argv[2] if len(sys.argv) > 2 else "production"
    ref = resolve(cid, "pursuit")
    lab = resolve(cid, lab_tier)
    if ref is None or lab is None:
        print(json.dumps({"error": "missing ref or lab path", "ref": str(ref), "lab": str(lab)}))
        return 1
    gate = pursuit_gate(ref, lab, same_file_is_pass=False)
    ref_m = metrics_from_path(ref).to_dict()
    lab_m = metrics_from_path(lab).to_dict()
    out = {
        "course_id": cid,
        "pursuit": str(ref.relative_to(ROOT)),
        "lab": str(lab.relative_to(ROOT)),
        "pursuit_metrics": ref_m,
        "lab_metrics": lab_m,
        "gaps": {k: ref_m[k] - lab_m[k] for k in ref_m if isinstance(ref_m[k], int)},
        "gate": gate.to_dict(),
    }
    print(json.dumps(out, indent=2))
    return 0 if gate.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

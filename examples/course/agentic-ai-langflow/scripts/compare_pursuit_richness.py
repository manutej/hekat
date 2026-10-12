#!/usr/bin/env python3
"""Compare lab/production SVG richness to Pursuit reference (same course_id)."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))
from figure_tiers import resolve  # noqa: E402


def metrics(svg: str) -> dict:
    view_h = 0
    m = re.search(r'viewBox="[^"]*\s+(\d+(?:\.\d+)?)"', svg)
    if m:
        view_h = int(float(m.group(1)))
    texts = re.findall(r"<text[^>]*>", svg)
    annot = len(re.findall(r'data-kind="annot"', svg))
    panels = len(re.findall(r'data-role="block"', svg))
    components = len(set(re.findall(r'data-component="([^"]+)"', svg)))
    return {
        "viewBox_height": view_h,
        "text_elements": len(texts),
        "annot_nodes": annot,
        "block_nodes": panels,
        "data_components": components,
        "bytes": len(svg.encode("utf-8")),
    }


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
    ref_m = metrics(ref.read_text(encoding="utf-8"))
    lab_m = metrics(lab.read_text(encoding="utf-8"))
    out = {
        "course_id": cid,
        "pursuit": str(ref.relative_to(ROOT)),
        "lab": str(lab.relative_to(ROOT)),
        "pursuit_metrics": ref_m,
        "lab_metrics": lab_m,
        "gaps": {k: ref_m[k] - lab_m[k] for k in ref_m if isinstance(ref_m[k], int)},
    }
    print(json.dumps(out, indent=2))
    # Heuristic: lab is "thin" if far below Pursuit on annotations or height
    thin = lab_m["annot_nodes"] < max(3, ref_m["annot_nodes"] // 2) or lab_m["viewBox_height"] < ref_m["viewBox_height"] * 0.6
    return 1 if thin else 0


if __name__ == "__main__":
    raise SystemExit(main())

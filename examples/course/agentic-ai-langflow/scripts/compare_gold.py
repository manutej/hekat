#!/usr/bin/env python3
"""Compare production SVG component sets to gold reference SVGs."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def components(svg_text: str) -> set[str]:
    found = set(re.findall(r'component="([^"]+)"', svg_text))
    # Also data-component on blocks
    found.update(re.findall(r'data-component="([^"]+)"', svg_text))
    return {c.strip() for c in found if c.strip()}


def jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 1.0
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main() -> int:
    if len(sys.argv) < 3:
        print("usage: compare_gold.py PRODUCTION.svg GOLD.svg", file=sys.stderr)
        return 2
    prod = Path(sys.argv[1]).read_text(encoding="utf-8")
    gold = Path(sys.argv[2]).read_text(encoding="utf-8")
    cp, cg = components(prod), components(gold)
    score = jaccard(cp, cg)
    out = {
        "production": sorted(cp),
        "gold": sorted(cg),
        "jaccard": round(score, 3),
        "only_in_production": sorted(cp - cg),
        "only_in_gold": sorted(cg - cp),
    }
    print(json.dumps(out, indent=2))
    return 0 if score >= 0.85 or (not cg and cp) else 1


if __name__ == "__main__":
    raise SystemExit(main())

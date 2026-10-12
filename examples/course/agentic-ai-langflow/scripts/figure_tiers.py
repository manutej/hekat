"""Resolve Module 1 SVG paths: Pursuit bar > course gold > FigTree production."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
COURSE_MODULE = Path(__file__).resolve().parents[1] / "module-01"
PURSUIT_DIR = ROOT / "examples/figtree/langflow/pursuit/module-01/figures"
PURSUIT_MANIFEST = ROOT / "examples/figtree/langflow/pursuit/module-01/manifest.json"
GOLD = COURSE_MODULE / "gold"

Tier = str  # "pursuit" | "gold" | "production"


def _pursuit_by_course_id() -> dict[str, Path]:
    if not PURSUIT_MANIFEST.exists():
        return {}
    data = json.loads(PURSUIT_MANIFEST.read_text(encoding="utf-8"))
    out: dict[str, Path] = {}
    for row in data.get("figures", []):
        cid = row.get("course_id")
        fname = row.get("file")
        if cid and fname:
            path = PURSUIT_DIR / fname
            if path.exists():
                out[cid] = path
    return out


def resolve(course_id: str, tier: Tier = "pursuit") -> Path | None:
    prod = COURSE_MODULE / f"{course_id}.svg"
    gold = GOLD / f"{course_id}.svg"
    pursuit = _pursuit_by_course_id().get(course_id)
    if tier == "pursuit" and pursuit:
        return pursuit
    if tier == "gold" and gold.exists():
        return gold
    if tier == "production" and prod.exists():
        return prod
    if tier == "pursuit":
        if gold.exists():
            return gold
        return prod if prod.exists() else None
    return None

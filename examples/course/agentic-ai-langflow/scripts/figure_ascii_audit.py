#!/usr/bin/env python3
"""ASCII topology audit: compare diagram briefs to SVG component sets and canvas fit."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODULE = Path(__file__).resolve().parents[1] / "module-01"
DIAGRAMS = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams"
ASCII_DIR = MODULE / "ascii"
ADV = ROOT / "examples/figtree/langflow/adversarial"
sys.path.insert(0, str(ADV))
sys.path.insert(0, str(ROOT))

from figtree.program import load_program  # noqa: E402
from figtree.rubrics import RUBRICS  # noqa: E402


def expected_from_md(text: str) -> list[str]:
    found: list[str] = []
    for line in text.splitlines():
        if "->" not in line:
            continue
        parts = re.split(r"\s*->\s*", line.strip())
        for p in parts:
            name = p.strip()
            if name and name not in found:
                found.append(name)
    return found


def components_in_svg(svg: str) -> set[str]:
    return set(re.findall(r'data-component="([^"]+)"', svg))


def _arrow_groups(text: str) -> list[list[str]]:
    groups: list[list[str]] = []
    run: list[str] = []
    for raw in text.splitlines():
        line = raw.strip()
        if "->" in line:
            run.append(line)
            continue
        if run:
            groups.append(run)
            run = []
    if run:
        groups.append(run)
    return groups


def _stitch_chain(run: list[str]) -> list[str]:
    ordered: list[str] = []
    for seg in run:
        parts = [p.strip() for p in re.split(r"\s*->\s*", seg.strip())]
        if not ordered:
            ordered.extend(parts)
        elif ordered[-1] == parts[0]:
            ordered.extend(parts[1:])
        else:
            ordered.extend(parts)
    return ordered


def chain_lines_from_md(text: str) -> list[str]:
    """Stitched main flow from the first blank-separated arrow group."""
    groups = _arrow_groups(text)
    if not groups:
        return []
    return ["  ->  ".join(f"[{n}]" for n in _stitch_chain(groups[0]))]


def side_flows(text: str) -> list[tuple[str, str]]:
    """Edges from groups after the first (e.g. Knowledge Base side feed)."""
    groups = _arrow_groups(text)
    flows: list[tuple[str, str]] = []
    for run in groups[1:]:
        for seg in run:
            parts = [p.strip() for p in re.split(r"\s*->\s*", seg.strip())]
            for i in range(len(parts) - 1):
                flows.append((parts[i], parts[i + 1]))
    return flows


def canvas_audit(svg_path: Path) -> dict:
    margin = int(RUBRICS["teaching"].margin)
    prog = load_program(svg_path.read_text(encoding="utf-8"))
    cb = prog.content_bbox()
    if cb is None:
        return {"canvas_w": prog.width, "canvas_h": prog.height, "clipped": True, "margin_ok": False}
    clipped = cb.x < 0 or cb.y < 0 or cb.x2 > prog.width or cb.y2 > prog.height
    margin_ok = (
        cb.x >= margin
        and cb.y >= margin
        and cb.x2 <= prog.width - margin
        and cb.y2 <= prog.height - margin
    )
    return {
        "canvas_w": prog.width,
        "canvas_h": prog.height,
        "bbox": [round(cb.x), round(cb.y), round(cb.x2), round(cb.y2)],
        "clipped": clipped,
        "margin_ok": margin_ok,
    }


def to_ascii(title: str, components: list[str], chains: list[str], side: list[tuple[str, str]]) -> str:
    lines = [f"# {title}", ""]
    if chains:
        lines.append("Primary chain(s):")
        for chain in chains:
            lines.append(f"  {chain}")
    if side:
        lines.append("")
        lines.append("Side feeds:")
        for a, b in side:
            lines.append(f"  [{a}] --> [{b}]")
    lines.append("")
    lines.append("Components expected: " + ", ".join(components))
    return "\n".join(lines) + "\n"


def main() -> int:
    ASCII_DIR.mkdir(parents=True, exist_ok=True)
    manifest = json.loads((MODULE / "manifest.json").read_text(encoding="utf-8"))
    report: list[dict] = []
    ok = True
    for fig in manifest["figures"]:
        fid = fig["id"]
        md_path = DIAGRAMS / f"{fid}.md"
        svg_path = MODULE / f"{fid}.svg"
        md = md_path.read_text(encoding="utf-8")
        expected = expected_from_md(md)
        chains = chain_lines_from_md(md)
        side = side_flows(md)
        ascii_text = to_ascii(fig.get("title") or fid, expected, chains, side)
        (ASCII_DIR / f"{fid}.txt").write_text(ascii_text, encoding="utf-8")
        present = components_in_svg(svg_path.read_text(encoding="utf-8")) if svg_path.exists() else set()
        missing = [c for c in expected if c not in present]
        extra = sorted(present - set(expected))
        canvas = canvas_audit(svg_path) if svg_path.exists() else {"clipped": True, "margin_ok": False}
        row = {
            "id": fid,
            "expected_count": len(expected),
            "present_count": len(present),
            "missing": missing,
            "extra": extra,
            "canvas": canvas,
        }
        report.append(row)
        if missing:
            ok = False
            print(f"FAIL {fid}: missing {missing}")
        elif canvas.get("clipped"):
            ok = False
            print(f"FAIL {fid}: content clipped outside canvas")
        else:
            print(f"OK   {fid}: {len(present)} components, canvas {canvas.get('canvas_w')}x{canvas.get('canvas_h')}")
    (MODULE / "ascii-audit.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

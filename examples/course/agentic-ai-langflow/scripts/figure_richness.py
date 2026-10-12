"""Shared SVG richness metrics and Pursuit-relative gate."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class RichnessMetrics:
    viewbox_height: int
    text_elements: int
    annot_nodes: int
    block_nodes: int
    data_components: int
    bytes: int

    def to_dict(self) -> dict[str, int]:
        return {
            "viewBox_height": self.viewbox_height,
            "text_elements": self.text_elements,
            "annot_nodes": self.annot_nodes,
            "block_nodes": self.block_nodes,
            "data_components": self.data_components,
            "bytes": self.bytes,
        }


def metrics_from_text(svg: str) -> RichnessMetrics:
    view_h = 0
    m = re.search(r'viewBox="[^"]*\s+(\d+(?:\.\d+)?)"', svg)
    if m:
        view_h = int(float(m.group(1)))
    return RichnessMetrics(
        viewbox_height=view_h,
        text_elements=len(re.findall(r"<text[^>]*>", svg)),
        annot_nodes=len(re.findall(r'data-kind="annot"', svg)),
        block_nodes=len(re.findall(r'data-role="block"', svg)),
        data_components=len(set(re.findall(r'data-component="([^"]+)"', svg))),
        bytes=len(svg.encode("utf-8")),
    )


def metrics_from_path(path: Path) -> RichnessMetrics:
    return metrics_from_text(path.read_text(encoding="utf-8"))


def _ratio(ref: int, cand: int, *, skip_if_ref_zero: bool = True) -> float | None:
    if ref <= 0:
        return None if skip_if_ref_zero else (1.0 if cand <= 0 else float("inf"))
    return cand / ref


@dataclass
class PursuitGateResult:
    ok: bool
    reasons: list[str]
    ratios: dict[str, float | None]
    reference: dict[str, int]
    candidate: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "reasons": self.reasons,
            "ratios": self.ratios,
            "reference": self.reference,
            "candidate": self.candidate,
        }


def pursuit_gate(
    reference: Path,
    candidate: Path,
    *,
    min_height_ratio: float = 0.55,
    min_text_ratio: float = 0.45,
    min_annot_ratio: float = 0.45,
    min_block_ratio: float = 0.5,
    same_file_is_pass: bool = True,
) -> PursuitGateResult:
    if same_file_is_pass and reference.resolve() == candidate.resolve():
        ref_m = metrics_from_path(reference)
        return PursuitGateResult(True, [], {}, ref_m.to_dict(), ref_m.to_dict())

    ref_m = metrics_from_path(reference)
    cand_m = metrics_from_path(candidate)
    ref = ref_m.to_dict()
    cand = cand_m.to_dict()
    ratios = {
        "height": _ratio(ref["viewBox_height"], cand["viewBox_height"]),
        "text": _ratio(ref["text_elements"], cand["text_elements"]),
        "annot": _ratio(ref["annot_nodes"], cand["annot_nodes"]),
        "blocks": _ratio(ref["block_nodes"], cand["block_nodes"]),
    }
    reasons: list[str] = []
    if ratios["height"] is not None and ratios["height"] < min_height_ratio:
        reasons.append(
            f"viewBox height ratio {ratios['height']:.2f} < {min_height_ratio} "
            f"({cand['viewBox_height']} vs ref {ref['viewBox_height']})"
        )
    if ratios["text"] is not None and ratios["text"] < min_text_ratio:
        reasons.append(
            f"text element ratio {ratios['text']:.2f} < {min_text_ratio} "
            f"({cand['text_elements']} vs ref {ref['text_elements']})"
        )
    if ref["annot_nodes"] > 0 and ratios["annot"] is not None and ratios["annot"] < min_annot_ratio:
        reasons.append(
            f"annotation ratio {ratios['annot']:.2f} < {min_annot_ratio} "
            f"({cand['annot_nodes']} vs ref {ref['annot_nodes']})"
        )
    if ratios["blocks"] is not None and ratios["blocks"] < min_block_ratio:
        reasons.append(
            f"block ratio {ratios['blocks']:.2f} < {min_block_ratio} "
            f"({cand['block_nodes']} vs ref {ref['block_nodes']})"
        )
    return PursuitGateResult(not reasons, reasons, ratios, ref, cand)

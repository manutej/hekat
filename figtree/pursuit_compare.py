"""Optional Pursuit-style reference comparison for course-narrative scoring."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ReferenceGap:
    check_id: str
    dimension: str
    severity: str
    visual_description: str
    penalty: float

    def to_issue_dict(self) -> dict:
        return {
            "check_id": self.check_id,
            "dimension": self.dimension,
            "severity": self.severity,
            "visual_description": self.visual_description,
            "code_anchor": "svg",
            "fix_instruction": "match Pursuit reference richness (panels, annotations, canvas height)",
            "penalty": self.penalty,
            "auto_edit": None,
        }


def _metrics(svg: str) -> dict[str, int]:
    view_h = 0
    m = re.search(r'viewBox="[^"]*\s+(\d+(?:\.\d+)?)"', svg)
    if m:
        view_h = int(float(m.group(1)))
    return {
        "viewBox_height": view_h,
        "text_elements": len(re.findall(r"<text[^>]*>", svg)),
        "annot_nodes": len(re.findall(r'data-kind="annot"', svg)),
        "block_nodes": len(re.findall(r'data-role="block"', svg)),
    }


def gaps_vs_reference(reference_svg: str, candidate_svg: str) -> List[ReferenceGap]:
    ref = _metrics(reference_svg)
    cand = _metrics(candidate_svg)
    out: List[ReferenceGap] = []
    if ref["viewBox_height"] > 0:
        ratio = cand["viewBox_height"] / ref["viewBox_height"]
        if ratio < 0.55:
            out.append(
                ReferenceGap(
                    "narrative.ref_height",
                    "medium_fit",
                    "warning",
                    f"canvas height {ratio:.0%} of reference ({cand['viewBox_height']}px vs {ref['viewBox_height']}px)",
                    1.0,
                )
            )
    if ref["annot_nodes"] > 0:
        ratio = cand["annot_nodes"] / ref["annot_nodes"]
        if ratio < 0.45:
            out.append(
                ReferenceGap(
                    "narrative.ref_annot",
                    "semantic_coverage",
                    "warning",
                    f"annotation count {ratio:.0%} of reference ({cand['annot_nodes']} vs {ref['annot_nodes']})",
                    1.2,
                )
            )
    if ref["text_elements"] > 0:
        ratio = cand["text_elements"] / ref["text_elements"]
        if ratio < 0.45:
            out.append(
                ReferenceGap(
                    "narrative.ref_text",
                    "text_quality",
                    "warning",
                    f"text element count {ratio:.0%} of reference ({cand['text_elements']} vs {ref['text_elements']})",
                    0.8,
                )
            )
    return out

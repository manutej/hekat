#!/usr/bin/env python3
"""Turn Pursuit richness gaps into figtree refine --request prose (no LLM)."""

from __future__ import annotations

from figure_richness import PursuitGateResult, pursuit_gate


def requests_from_gate(gate: PursuitGateResult, *, fig_title: str) -> list[str]:
    """One refine request per round, ordered for course-narrative improvement."""
    out: list[str] = []
    ratios = gate.ratios
    if ratios.get("height") is not None and ratios["height"] < 0.55:
        out.append(
            f"Expand the canvas vertically to at least match a tall course panel figure for "
            f"'{fig_title}'. Stack Chat Input above Knowledge Base on the left; use full-width "
            f"panels with icons, section title, and inner example text areas (data-kind=annot)."
        )
    if ratios.get("annot") is not None and ratios["annot"] < 0.45:
        out.append(
            "Add grounded annotation lines (data-kind=annot, 11–13px, #5B6B7C) inside each major "
            "panel describing what that component holds, plus a short member quote in a nested white "
            "example rect. Do not remove any labelled components or arrows."
        )
    if ratios.get("text") is not None and ratios["text"] < 0.45:
        out.append(
            "Add a section title (font-weight 600, data-kind=title) and supporting labels; preserve "
            "topology and all data-component names from the brief."
        )
    if not out:
        out.append(
            "Polish panel spacing and annotation alignment to match a Pursuit-style course figure; "
            "keep all components and flows."
        )
    return out[:3]


def gate_for_course_id(course_id: str) -> tuple[PursuitGateResult | None, str]:
    from figure_tiers import resolve

    ref = resolve(course_id, "pursuit")
    lab = resolve(course_id, "production")
    if ref is None or lab is None:
        return None, course_id
    return pursuit_gate(ref, lab, same_file_is_pass=False), course_id

"""Image-space judge: the paper's fine-grained diagnostic evaluator, on this session's login.

The judge reads the rendered PNG (through the Claude Code CLI's Read tool) and the rubric's
dimensions with their 1-10 anchors, and returns a score, a justification and tags per
dimension.  ``calibrate`` compares judged scores with the measured scores over a set of
figures, so the two evaluators can be checked against each other: a measured 10 that the judge
scores 6 is a blind spot of the rubric; a judged 10 the rubric scores 6 is a rule to reconsider.
"""

from __future__ import annotations

import json
import os
import subprocess
import shutil
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from figtree.quality import QualityCritic
from figtree.render import render_png
from figtree.rubric_spec import ANCHORS, JUDGE_QUESTIONS, VETOES, spec_for
from figtree.rubrics import DIMENSIONS

JUDGE_SYSTEM = (
    "You are an expert evaluator of figure quality. Rate the rendered figure on a 1-10 scale per dimension. "
    "Use the FULL range: 5 is average/mediocre, 1-2 completely broken, 9-10 near-perfect and reserved. Judge the "
    "output AS RENDERED: what you see matters. Cite concrete visual evidence in each justification (1-2 sentences) and "
    "give 1-4 diagnostic tags. Apply the veto rules: a veto caps the affected dimension at 4. Do not reward attractive "
    "figures that are wrong, hallucinated or unreadable. Respond only with JSON."
)

JUDGE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["scores", "vetoes", "overall_comment"],
    "properties": {
        "scores": {
            "type": "object",
            "additionalProperties": False,
            "required": list(DIMENSIONS),
            "properties": {d: {"type": "object", "additionalProperties": False, "required": ["score", "justification", "tags"],
                               "properties": {"score": {"type": "integer", "minimum": 1, "maximum": 10}, "justification": {"type": "string"}, "tags": {"type": "array", "items": {"type": "string"}}}} for d in DIMENSIONS},
        },
        "vetoes": {"type": "array", "items": {"type": "string"}},
        "overall_comment": {"type": "string"},
    },
}


@dataclass
class Judgement:
    rubric: str
    scores: Dict[str, int]
    justifications: Dict[str, str]
    tags: Dict[str, List[str]]
    vetoes: List[str]
    comment: str
    png: Optional[str] = None
    cost_usd: float = 0.0

    @property
    def overall(self) -> float:
        return round(sum(self.scores.values()) / len(self.scores), 2)

    def to_dict(self) -> Dict[str, Any]:
        return {"rubric": self.rubric, "overall": self.overall, "scores": self.scores, "justifications": self.justifications, "tags": self.tags, "vetoes": self.vetoes, "comment": self.comment, "png": self.png, "cost_usd": self.cost_usd}


def _prompt(rubric: str, png_path: str, source_text: Optional[str], svg_excerpt: str) -> str:
    spec = spec_for(rubric)
    dims = "\n".join(f"### {d}\n{JUDGE_QUESTIONS[d]}\nAnchors: " + "; ".join(f"{k}: {v}" for k, v in ANCHORS[d].items()) for d in DIMENSIONS)
    vetoes = "\n".join(f"- {k}: {v['description']}" for k, v in VETOES.items())
    src = f"\n## Source text (the authority for coverage and hallucination)\n{source_text[:4000]}\n" if source_text else "\n(No source text: score semantic_coverage and hallucination_control from internal consistency only.)\n"
    return (
        f"## Medium\n{spec['medium']} — {spec['description']}\n## Rendered figure\nRead the image file at: {png_path}\n"
        f"Use the Read tool to view it. Then also consider the SVG source excerpt below for element-level evidence.\n{src}"
        f"## Dimensions\n{dims}\n## Veto rules\n{vetoes}\n## SVG source (excerpt)\n{svg_excerpt[:6000]}\n\nOutput the JSON now."
    )


def judge(svg_text: str, rubric: str, source_text: Optional[str] = None, render_dir: Optional[str] = None, model: Optional[str] = None, timeout: int = 600) -> Judgement:
    exe = shutil.which("claude")
    if exe is None:
        raise RuntimeError("the `claude` CLI is required for the image judge")
    out_dir = render_dir or tempfile.mkdtemp(prefix="figtree-judge-")
    png = render_png(svg_text, out_dir, "judge")
    if png is None:
        raise RuntimeError("no renderer available for the image judge")
    cmd = [exe, "-p", _prompt(rubric, png, source_text, svg_text), "--output-format", "json", "--json-schema", json.dumps(JUDGE_SCHEMA),
           "--system-prompt", JUDGE_SYSTEM, "--tools", "Read", "--allowedTools", "Read", "--no-session-persistence", "--add-dir", out_dir]
    if model:
        cmd += ["--model", model]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=out_dir)
    data = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
    if data.get("is_error") or not isinstance(data.get("structured_output"), dict):
        raise RuntimeError(f"judge failed: {str(data.get('result'))[:200]}")
    so = data["structured_output"]
    scores = {d: int(so["scores"][d]["score"]) for d in DIMENSIONS}
    return Judgement(rubric, scores, {d: so["scores"][d]["justification"] for d in DIMENSIONS}, {d: so["scores"][d]["tags"] for d in DIMENSIONS}, so.get("vetoes", []), so.get("overall_comment", ""), png, float(data.get("total_cost_usd") or 0))


@dataclass
class CalibrationRow:
    name: str
    rubric: str
    measured: Dict[str, Optional[float]]
    judged: Dict[str, int]
    measured_overall: float
    judged_overall: float

    def to_dict(self) -> Dict[str, Any]:
        gaps = {d: (None if self.measured.get(d) is None else round(self.judged[d] - self.measured[d], 2)) for d in DIMENSIONS}
        return {"name": self.name, "rubric": self.rubric, "measured": self.measured, "judged": self.judged, "measured_overall": self.measured_overall, "judged_overall": self.judged_overall, "gap_overall": round(self.judged_overall - self.measured_overall, 2), "gaps": gaps}


def calibrate(items: List[Dict[str, str]], render_dir: Optional[str] = None) -> Dict[str, Any]:
    """``items``: [{"name", "svg": path, "rubric", "source"?: path}] -> rows + blind spots."""
    rows: List[CalibrationRow] = []
    cost = 0.0
    for it in items:
        with open(it["svg"], encoding="utf-8") as fh:
            svg = fh.read()
        src = None
        if it.get("source"):
            with open(it["source"], encoding="utf-8") as fh:
                src = fh.read()
        report = QualityCritic(it["rubric"]).review(svg, src)
        j = judge(svg, it["rubric"], src, render_dir)
        cost += j.cost_usd
        rows.append(CalibrationRow(it["name"], it["rubric"], report.scores, j.scores, report.overall, j.overall))
    blind: List[Dict[str, Any]] = []
    for r in rows:
        for d in DIMENSIONS:
            m = r.measured.get(d)
            if m is not None and m >= 9 and r.judged[d] <= 6:
                blind.append({"name": r.name, "dimension": d, "measured": m, "judged": r.judged[d], "kind": "rubric blind spot"})
            if m is not None and m <= 6 and r.judged[d] >= 9:
                blind.append({"name": r.name, "dimension": d, "measured": m, "judged": r.judged[d], "kind": "rule to reconsider"})
    gaps = [r.judged_overall - r.measured_overall for r in rows]
    return {"rows": [r.to_dict() for r in rows], "mean_gap": round(sum(gaps) / len(gaps), 2) if gaps else None, "findings": blind, "cost_usd": round(cost, 3)}

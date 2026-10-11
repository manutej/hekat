"""Probe harness: measure the evaluators themselves.

A *probe* is a minimal SVG with a known verdict: which checks must fire (a defect probe), which
must stay silent (a clean probe), or a *gaming* case (a figure that satisfies every measurable
check yet is bad, so a judge must catch it) or a *false-positive* case (a good figure the critic
wrongly flags).  ``figtree eval`` runs every probe for a rubric and reports recall and precision
per check.  Seed probes are generated here; adversarial probes live under
``examples/figtree/probes/<rubric>/<id>.svg`` with a sibling ``<id>.json``.
"""

from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

from figtree.quality import QualityCritic
from figtree.rubric_spec import CHECKS

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" font-family="Times New Roman">'
BG = '<rect id="bg" width="{w}" height="{h}" fill="#FFFFFF"/>'
MARKER = '<defs><marker id="a" markerWidth="5" markerHeight="3.5" refX="5" refY="1.75" orient="auto" markerUnits="userSpaceOnUse"><path d="M0,0 L5,1.75 L0,3.5 z" fill="#333"/></marker></defs>'


def block(i: int, x: int, y: int, w: int = 96, h: int = 32, fill: str = "#7BA3C9", label: str = "Block", size: int = 12, font: Optional[str] = None, text_fill: str = "#333333", extra: str = "") -> str:
    ff = f' font-family="{font}"' if font else ""
    return (f'<rect id="b{i}" x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="#333" stroke-width="1.2" data-role="block" rx="4"{extra}/>'
            f'<text id="t{i}" x="{x + w // 2}" y="{y + h // 2}" font-size="{size}" text-anchor="middle" dominant-baseline="middle" fill="{text_fill}" data-kind="label"{ff}>{label}</text>')


def arrow(i: int, d: str, flow: str = "data") -> str:
    dash = ' stroke-dasharray="4 2"' if flow != "data" else ""
    return f'<path id="f{i}" d="{d}" fill="none" stroke="#333" stroke-width="1.2" data-flow="{flow}"{dash} marker-end="url(#a)"/>'


def doc(body: str, w: int = 320, h: int = 96) -> str:
    return HEAD.format(w=w, h=h) + BG.format(w=w, h=h) + MARKER + body + "</svg>"


CLEAN_DIAGRAM = doc(block(1, 24, 32, label="Source", size=14) + block(2, 200, 32, label="Model", size=14) + arrow(1, "M120,48 H200"))


@dataclass
class Probe:
    id: str
    rubric: str
    kind: str  # defect | clean | gaming | false_positive
    svg: str
    expect_fire: List[str] = field(default_factory=list)
    expect_silent: List[str] = field(default_factory=list)
    rationale: str = ""
    source: str = "seed"

    def to_dict(self) -> Dict[str, object]:
        return {"id": self.id, "rubric": self.rubric, "kind": self.kind, "expect_fire": self.expect_fire, "expect_silent": self.expect_silent, "rationale": self.rationale, "source": self.source}


def seed_probes() -> List[Probe]:
    P: List[Probe] = []
    T = "teaching"
    P.append(Probe("clean.diagram", T, "clean", CLEAN_DIAGRAM, expect_silent=[c.id for c in CHECKS], rationale="two compliant blocks, one arrow, 24px margins: nothing may fire"))
    P.append(Probe("defect.min_font", T, "defect", doc(block(1, 24, 32, label="Tiny", size=8) + block(2, 200, 32, label="Model", size=14) + arrow(1, "M120,48 H200")), ["text.min_font"]))
    P.append(Probe("defect.contrast", T, "defect", doc(block(1, 24, 32, label="Grey", size=14, text_fill="#9A9A9A", fill="#D5D5D5") + block(2, 200, 32, label="Model", size=14) + arrow(1, "M120,48 H200")), ["text.contrast"]))
    P.append(Probe("defect.gradient", T, "defect", doc('<defs><linearGradient id="g"><stop offset="0" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient></defs>' + block(1, 24, 32, label="Grad", size=14, fill="url(#g)") + block(2, 200, 32, label="Model", size=14) + arrow(1, "M120,48 H200")), ["polish.gradient_fill", "text.gradient_host"]))
    P.append(Probe("defect.neon_fill", T, "defect", doc(block(1, 24, 32, label="Neon", size=14, fill="#FF00FF") + block(2, 200, 32, label="Model", size=14) + arrow(1, "M120,48 H200")), ["polish.neon"]))
    P.append(Probe("defect.neon_stroke", T, "defect", doc(block(1, 24, 32, label="A", size=14) + block(2, 200, 32, label="B", size=14) + '<path id="f1" d="M120,48 H200" fill="none" stroke="#00FF66" stroke-width="1.2" data-flow="data" marker-end="url(#a)"/>'), ["polish.neon"]))
    P.append(Probe("defect.overflow_label", T, "defect", doc(block(1, 24, 32, w=64, label="A very long label indeed", size=14) + block(2, 200, 32, label="B", size=14) + arrow(1, "M88,48 H200")), ["text.overflow"]))
    P.append(Probe("defect.overlap", T, "defect", doc(block(1, 24, 32, label="Alpha", size=14) + '<text id="t9" x="80" y="48" font-size="14" text-anchor="middle" dominant-baseline="middle" fill="#333" data-kind="label">Beta</text>' + block(2, 200, 32, label="B", size=14) + arrow(1, "M120,48 H200")), ["text.overlap"]))
    P.append(Probe("defect.two_fonts", T, "defect", doc(block(1, 24, 32, label="Serif", size=14) + block(2, 200, 32, label="Sans", size=14, font="Arial") + arrow(1, "M120,48 H200")), ["polish.font_families"]))
    P.append(Probe("defect.through_block", T, "defect", doc(block(1, 24, 16, label="A", size=14) + block(2, 112, 48, label="Mid", size=14) + block(3, 200, 80, label="C", size=14) + arrow(1, "M120,32 H160 V96 H200"), h=128), ["flow.through_block"]))
    P.append(Probe("defect.crossing", T, "defect", doc(block(1, 24, 16, label="A", size=14) + block(2, 24, 80, label="B", size=14) + block(3, 200, 16, label="C", size=14) + block(4, 200, 80, label="D", size=14) + arrow(1, "M120,32 H152 V96 H200") + arrow(2, "M120,96 H168 V32 H200"), h=128), ["flow.crossings"]))
    P.append(Probe("defect.diagonal", T, "defect", doc(block(1, 24, 16, label="A", size=14) + block(2, 200, 80, label="B", size=14) + '<path id="f1" d="M120,32 L200,96" fill="none" stroke="#333" stroke-width="1.2" data-flow="data" marker-end="url(#a)"/>', h=128), ["flow.diagonal"]))
    P.append(Probe("defect.short_shaft", T, "defect", doc(block(1, 24, 32, label="A", size=14) + block(2, 136, 32, label="B", size=14) + arrow(1, "M120,48 H136")), ["flow.short_shaft"]))
    P.append(Probe("defect.reading_order", T, "defect", doc(block(1, 24, 32, label="A", size=14) + block(2, 200, 32, label="B", size=14) + arrow(1, "M200,48 H120")), ["flow.reading_order"]))
    P.append(Probe("defect.blank_margin", T, "defect", doc(block(1, 24, 32, label="A", size=14) + block(2, 200, 32, label="B", size=14) + arrow(1, "M120,48 H200"), w=800, h=160), ["compactness.blank_margin"]))
    P.append(Probe("defect.overflow_canvas", T, "defect", doc(block(1, 24, 32, label="A", size=14) + block(2, 280, 32, label="B", size=14) + arrow(1, "M120,48 H280"), w=320, h=160), ["compactness.overflow"]))
    P.append(Probe("defect.black_bg", T, "defect", HEAD.format(w=320, h=96) + '<rect id="bg" width="320" height="96" fill="#111111"/>' + MARKER + block(1, 24, 32, label="A", size=14, text_fill="#FFFFFF") + block(2, 200, 32, label="B", size=14, text_fill="#FFFFFF") + arrow(1, "M120,48 H200") + "</svg>", ["medium.black_background"]))
    P.append(Probe("defect.corner_radius", T, "defect", doc(block(1, 24, 32, label="A", size=14, extra="").replace('rx="4"', 'rx="24"', 1) + block(2, 200, 32, label="B", size=14) + arrow(1, "M120,48 H200")), ["polish.corner_radius"]))
    P.append(Probe("defect.long_label", T, "defect", doc(block(1, 24, 32, w=272, label="this label runs to eleven words which is far too many", size=14)), ["text.words_per_label"]))
    P.append(Probe("defect.palette", T, "defect", doc("".join(block(i, 24 + (i - 1) * 56, 32, w=48, label=str(i), size=14, fill=c) for i, c in enumerate(["#7BA3C9", "#F4A460", "#C97BA3", "#A3C97B", "#C9A37B", "#7BC9A3"], 1)), w=400), ["polish.palette_size"]))
    P.append(Probe("defect.no_connectors", T, "defect", doc(block(1, 24, 16, label="A", size=14) + block(2, 200, 16, label="B", size=14) + block(3, 24, 80, label="C", size=14), h=128), ["flow.no_connectors"]))
    # data-figure
    D = "data-figure"
    chart = (HEAD.format(w=320, h=200) + BG.format(w=320, h=200) + '<line id="x" x1="40" y1="160" x2="300" y2="160" stroke="#333"/><line id="y" x1="40" y1="24" x2="40" y2="160" stroke="#333"/>'
             '<rect id="r1" x="60" y="80" width="40" height="80" fill="#7BA3C9"/><rect id="r2" x="140" y="40" width="40" height="120" fill="#7BA3C9"/>'
             '<text id="tt" x="170" y="16" font-size="12" text-anchor="middle" fill="#333">{title}</text>{axes}</svg>')
    axes_ok = '<text id="xl" x="170" y="190" font-size="11" text-anchor="middle" fill="#333" data-role="axis-label">Epoch</text><text id="yl" x="14" y="92" font-size="11" text-anchor="middle" fill="#333" data-role="axis-label" transform="rotate(-90 14 92)">Accuracy (%)</text>'
    P.append(Probe("clean.chart", D, "clean", chart.format(title="Accuracy rises with epochs", axes=axes_ok), expect_silent=["coverage.axis_labels", "coverage.title", "text.min_font"]))
    P.append(Probe("defect.no_axis_labels", D, "defect", chart.format(title="Accuracy rises with epochs", axes=""), ["coverage.axis_labels"]))
    P.append(Probe("defect.title_not_finding", D, "defect", chart.format(title="Results", axes=axes_ok), ["coverage.title"]))
    # icon
    I = "icon"
    icon = '<svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="#333" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</svg>'
    P.append(Probe("clean.icon", I, "clean", icon.format(body='<circle cx="12" cy="12" r="8"/><path d="M8 12h8"/>'), expect_silent=["medium.icon_text", "medium.square", "polish.stroke_widths"]))
    P.append(Probe("defect.icon_text", I, "defect", icon.format(body='<circle cx="12" cy="12" r="8"/><text x="12" y="13" font-size="6" text-anchor="middle">go</text>'), ["medium.icon_text"]))
    P.append(Probe("defect.icon_not_square", I, "defect", icon.replace('height="48"', 'height="36"').replace("0 0 24 24", "0 0 24 18").format(body='<circle cx="12" cy="9" r="6"/>'), ["medium.square"]))
    P.append(Probe("defect.icon_strokes", I, "defect", icon.format(body='<circle cx="12" cy="12" r="8"/><path d="M8 12h8" stroke-width="4"/>'), ["polish.stroke_widths"]))
    # slide
    S = "slide"
    slide = HEAD.format(w=640, h=360) + BG.format(w=640, h=360) + MARKER + "{body}</svg>"
    P.append(Probe("clean.slide", S, "clean", slide.format(body=block(1, 96, 152, w=160, h=56, label="Collect", size=20) + block(2, 384, 152, w=160, h=56, label="Model", size=20) + arrow(1, "M256,180 H384")), expect_silent=["text.min_font", "compactness.aspect", "text.words_per_label"]))
    P.append(Probe("defect.slide_small_font", S, "defect", slide.format(body=block(1, 96, 152, w=160, h=56, label="Collect", size=12) + block(2, 384, 152, w=160, h=56, label="Model", size=12) + arrow(1, "M256,180 H384")), ["text.min_font"]))
    return P


def load_probes(directory: str) -> List[Probe]:
    out: List[Probe] = []
    for meta in sorted(glob.glob(os.path.join(directory, "**", "*.json"), recursive=True)):
        svg_path = meta[:-5] + ".svg"
        if not os.path.exists(svg_path):
            continue
        with open(meta, encoding="utf-8") as fh:
            d = json.load(fh)
        with open(svg_path, encoding="utf-8") as fh:
            svg = fh.read()
        out.append(Probe(d["id"], d["rubric"], d.get("kind", "defect"), svg, d.get("expect_fire", []), d.get("expect_silent", []), d.get("rationale", ""), d.get("source", os.path.basename(os.path.dirname(meta)) or "external")))
    return out


@dataclass
class EvalResult:
    rubric: str
    per_check: Dict[str, Dict[str, int]]  # check -> {tp, fn, fp, tn}
    probe_results: List[Dict[str, object]]

    def recall(self, check: str) -> Optional[float]:
        c = self.per_check.get(check, {})
        n = c.get("tp", 0) + c.get("fn", 0)
        return None if n == 0 else c["tp"] / n

    def precision(self, check: str) -> Optional[float]:
        c = self.per_check.get(check, {})
        n = c.get("tp", 0) + c.get("fp", 0)
        return None if n == 0 else c["tp"] / n

    def summary(self) -> Dict[str, object]:
        tp = sum(c.get("tp", 0) for c in self.per_check.values())
        fn = sum(c.get("fn", 0) for c in self.per_check.values())
        fp = sum(c.get("fp", 0) for c in self.per_check.values())
        return {"rubric": self.rubric, "probes": len(self.probe_results), "expected_fires": tp + fn, "caught": tp, "missed": fn, "false_positives": fp,
                "recall": round(tp / (tp + fn), 3) if tp + fn else None, "precision": round(tp / (tp + fp), 3) if tp + fp else None,
                "failing_probes": [p["id"] for p in self.probe_results if not p["passed"]]}

    def to_dict(self) -> Dict[str, object]:
        return {"summary": self.summary(), "per_check": self.per_check, "probes": self.probe_results}


def evaluate(probes: Sequence[Probe], rubric: Optional[str] = None) -> EvalResult:
    per: Dict[str, Dict[str, int]] = {}
    rows: List[Dict[str, object]] = []
    for p in probes:
        if rubric and p.rubric != rubric:
            continue
        report = QualityCritic(p.rubric).review(p.svg)
        fired = {i.check_id for i in report.issues if i.check_id}
        missed = [c for c in p.expect_fire if c not in fired]
        wrong = [c for c in p.expect_silent if c in fired]
        for c in p.expect_fire:
            per.setdefault(c, {"tp": 0, "fn": 0, "fp": 0, "tn": 0})["tp" if c in fired else "fn"] += 1
        for c in p.expect_silent:
            per.setdefault(c, {"tp": 0, "fn": 0, "fp": 0, "tn": 0})["fp" if c in fired else "tn"] += 1
        passed = not missed and not wrong
        if p.kind == "gaming":
            passed = report.overall >= 9.0  # by definition the measurable critic is fooled; recorded for the judge
        rows.append({"id": p.id, "rubric": p.rubric, "kind": p.kind, "source": p.source, "overall": report.overall, "fired": sorted(fired), "missed": missed, "false_positive": wrong, "passed": passed})
    return EvalResult(rubric or "all", per, rows)

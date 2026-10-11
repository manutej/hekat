"""Tests for the iterative refinement layer: addressable programs, edit scripts, rubric
critic and the refine loop (the paper's iterative-editing evaluation as a tool)."""

from __future__ import annotations

import json
import os

import pytest

from figtree.editability import element_diff
from figtree.edits import apply_edits
from figtree.program import contrast_ratio, load_program, normalize_svg, parse_color
from figtree.quality import QualityCritic
from figtree.refine import Refiner
from figtree.rubrics import DIMENSIONS, RUBRICS, get_rubric

HERE = os.path.dirname(os.path.abspath(__file__))
TEACHING = os.path.join(os.path.dirname(HERE), "examples", "figtree", "teaching")


def read(name: str) -> str:
    with open(os.path.join(TEACHING, name), encoding="utf-8") as fh:
        return fh.read()


class TestProgram:
    def test_every_element_gets_a_stable_id(self):
        svg, assigned = normalize_svg(read("bar-chart.svg"))
        assert assigned > 0
        again, assigned2 = normalize_svg(svg)
        assert assigned2 == 0 and element_diff(svg, again) == []

    def test_inherited_typography_and_rotated_bbox(self):
        prog = load_program(read("slide-pipeline.svg"))
        t = next(e for e in prog.texts() if e.text == "Clean")
        assert t.font_family == "Arial" and t.font_size == 12
        rotated = '<svg xmlns="http://www.w3.org/2000/svg" width="100" height="100"><text x="18" y="50" font-size="12" text-anchor="middle" transform="rotate(-90 18 50)">Accuracy (%)</text></svg>'
        box = load_program(rotated).texts()[0].bbox
        assert box.x >= 0 and box.h > box.w

    def test_colour_helpers(self):
        assert parse_color("#fff") == (255, 255, 255) and parse_color("rgb(0, 0, 0)") == (0, 0, 0)
        assert round(contrast_ratio((0, 0, 0), (255, 255, 255))) == 21


class TestEdits:
    def test_each_operation_is_local(self):
        svg, _ = normalize_svg(read("bar-chart.svg"))
        ops = [
            {"op": "set_attr", "id": "e10-text", "attr": "font-size", "value": "12"},
            {"op": "recolor", "id": "e7-rect", "fill": "#7BA3C9"},
            {"op": "set_text", "id": "e3-text", "text": "Variant B wins"},
            {"op": "translate", "id": "e9-rect", "dx": 8, "dy": 0},
            {"op": "delete", "id": "e15-text"},
        ]
        for op in ops:
            res = apply_edits(svg, [op])
            assert res.failed == [], op
            assert len(element_diff(svg, res.svg)) == 1, op

    def test_insert_and_failures_are_reported(self):
        svg, _ = normalize_svg(read("bar-chart.svg"))
        res = apply_edits(svg, [{"op": "insert", "parent_id": "", "svg": '<text x="10" y="10" font-size="12">New</text>'}, {"op": "delete", "id": "missing"}])
        assert len(res.applied) == 1 and len(res.failed) == 1
        assert "New" in res.svg and len(element_diff(svg, res.svg)) == 1
        prog = load_program(res.svg)
        ids = [e.id for e in prog.elements]
        assert len(ids) == len(set(ids))


class TestRubricsAndCritic:
    def test_profiles_cover_the_media(self):
        assert {"methodology", "teaching", "slide", "data-figure", "dashboard", "icon"} <= set(RUBRICS)
        assert set(get_rubric("teaching").to_dict()["dimensions"]) == set(DIMENSIONS)
        with pytest.raises(KeyError):
            get_rubric("poster")

    def test_data_figure_defects_are_found_and_anchored(self):
        report = QualityCritic("data-figure").review(read("bar-chart.svg"))
        descs = " | ".join(i.visual_description for i in report.issues)
        for needle in ("font size 8px", "contrast", "gradient", "neon", "axis label", "font families", "stroke widths"):
            assert needle in descs, needle
        assert all(i.code_anchor for i in report.issues)
        assert report.overall < 7.5  # mediocre, in the paper's sense
        assert report.scores["hallucination_control"] is None  # no source text given
        assert any(i.auto_edit for i in report.issues) and any(i.auto_edit is None for i in report.issues)

    def test_icon_and_slide_rules(self):
        icon = QualityCritic("icon").review(read("process-icon.svg"))
        descs = " | ".join(i.visual_description for i in icon.issues)
        assert "not square" in descs and "text element" in descs and "stroke width" in descs
        slide = QualityCritic("slide").review(read("slide-pipeline.svg"))
        descs = " | ".join(i.visual_description for i in slide.issues)
        assert "10 words" in descs and "overflows" in descs and "font size 12px" in descs

    def test_source_grounding_checks(self):
        svg = read("slide-pipeline.svg")
        report = QualityCritic("teaching").review(svg, source_text="Collect, clean and model the sensor data.", plan_terms=["Collect", "Clean", "Model", "Deploy"])
        assert report.scores["hallucination_control"] is not None and report.metrics["coverage"] == 0.75
        assert any("Deploy" in i.visual_description for i in report.issues)


class TestRefiner:
    def test_trajectory_improves_and_terminates(self):
        res = Refiner("data-figure", render=False).run(read("bar-chart.svg"))
        assert res.final.overall > res.initial.overall
        assert res.trajectory[0].round == 0 and len(res.trajectory) <= 9
        assert res.stop_reason
        assert all(r.edits_failed == 0 for r in res.trajectory)
        # content decisions are handed back as requests, never guessed
        assert any("axis label" in r["visual_description"] for r in res.requests_remaining)

    def test_external_edit_requests_resolve_content_issues(self):
        with open(os.path.join(TEACHING, "bar-chart.edits.json"), encoding="utf-8") as fh:
            edits = json.load(fh)
        res = Refiner("data-figure", render=False).run(read("bar-chart.svg"), edits)
        assert not any("axis label" in r["visual_description"] for r in res.requests_remaining)
        assert not any("title" in r["visual_description"] for r in res.requests_remaining)
        assert res.final.overall >= 9.0

    def test_request_callable_and_no_auto(self):
        calls = []

        def ask(rnd, svg, report):
            calls.append(rnd)
            return [{"op": "set_canvas", "width": 48, "height": 48}] if rnd == 1 else None

        res = Refiner("icon", render=False, max_rounds=3).run(read("process-icon.svg"), ask, auto=False)
        assert calls == [1, 2] and res.trajectory[1].edits_applied == 1
        assert not any("not square" in r["visual_description"] for r in res.requests_remaining)

    def test_generated_figure_through_the_teaching_rubric(self):
        from figtree import FigTree

        src = open(os.path.join(os.path.dirname(TEACHING), "figtree-spec.md"), encoding="utf-8").read()
        result = FigTree(render=False).run(src)
        res = Refiner("teaching", render=False).run(result.final_svg, source_text=src, plan_terms=result.content_plan.component_names())
        assert res.final.scores["text_quality"] >= 9  # fonts raised to the teaching minimum
        assert res.final.metrics["coverage"] == 1.0
        assert 1.0 <= res.final.metrics["aspect"] <= 3.2  # no banner: rows were used

    def test_cli_refine_and_score(self, tmp_path, capsys):
        from figtree.cli import main

        out = tmp_path / "out.svg"
        traj = tmp_path / "traj.json"
        assert main(["refine", os.path.join(TEACHING, "bar-chart.svg"), "--rubric", "data-figure", "-o", str(out), "--trajectory", str(traj), "--no-render"]) == 0
        data = json.loads(traj.read_text())
        assert data["improvement"] > 0 and out.exists()
        assert main(["score", str(out), "--rubric", "data-figure"]) == 0
        assert "overall" in capsys.readouterr().out

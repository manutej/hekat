"""Tests for the digest batch mode: plan (unit manifest), one unit generation, gallery."""

from __future__ import annotations

import glob
import json
import os

import pytest

from figtree.digest import Manifest, collect_inputs, gallery, generate_unit, plan, run_all, split_sections, style_for

HERE = os.path.dirname(os.path.abspath(__file__))
EXAMPLES = os.path.join(os.path.dirname(HERE), "examples", "figtree")
DOCS = sorted(glob.glob(os.path.join(EXAMPLES, "*.md")))


class TestPlan:
    def test_split_sections_h1_h2_and_preamble(self):
        lines = ["intro line", "", "# Title", "body", "## Part A", "a", "a", "### not a unit boundary", "## Part B", "b"]
        secs = split_sections(lines)
        assert secs == [("intro line", 1, 2), ("Title", 3, 4), ("Part A", 5, 8), ("Part B", 9, 10)]

    def test_collect_inputs_walks_directories(self):
        files = collect_inputs([EXAMPLES])
        assert set(DOCS) <= set(files) and all(f.endswith((".md", ".txt", ".markdown", ".rst")) for f in files)

    def test_plan_over_examples_writes_manifest(self, tmp_path):
        m = plan(DOCS, str(tmp_path), rubric="teaching")
        assert os.path.exists(m.path)
        data = json.loads(open(m.path, encoding="utf-8").read())
        ids = [u["id"] for u in data["units"]]
        assert len(ids) == len(set(ids)) and {"loop", "figtree-spec", "transformer-method"} <= set(ids)
        for u in data["units"]:
            assert u["est_components"] >= 3 and u["span"][0] >= 1 and u["span"][1] >= u["span"][0] and u["chars"] > 0
            assert os.path.exists(u["source"])
        assert data["style"] == "teaching"
        # a round trip through the file keeps the units addressable
        again = Manifest.load(str(tmp_path))
        assert again.unit("loop").title == "The FigTree loop"
        with pytest.raises(KeyError):
            again.unit("no-such-unit")

    def test_small_file_is_one_unit_and_thin_sections_are_skipped_with_reason(self, tmp_path):
        doc = tmp_path / "doc.md"
        doc.write_text("# Big doc\n\nprose only\n\n## Pipeline\n\nReader → Parser → Printer → Logger\n\n## Thin\n\nnothing here\n" + "x" * 3000, encoding="utf-8")
        m = plan([str(doc)], str(tmp_path / "out"))
        assert [u.id for u in m.units] == ["doc--pipeline"]
        assert any(s["title"] == "Thin" and "grounded component" in s["reason"] for s in m.skipped)
        small = tmp_path / "small.md"
        small.write_text("# Small\n\nA → B → C\n", encoding="utf-8")
        m2 = plan([str(small)], str(tmp_path / "out2"))
        assert [u.id for u in m2.units] == ["small"] and m2.units[0].span == [1, 3]

    def test_style_mapping(self):
        assert style_for("teaching") == "teaching" and style_for("slide") == "slide"
        assert style_for("methodology") == "paper" and style_for("data-figure") == "paper"
        assert style_for("teaching", "paper") == "paper"


class TestUnit:
    def test_generate_one_unit_writes_svg_report_and_score(self, tmp_path):
        m = plan([os.path.join(EXAMPLES, "loop.md")], str(tmp_path))
        score = generate_unit(m, "loop", render=False)
        for suffix in ("svg", "report.json", "score.json"):
            assert os.path.exists(tmp_path / f"loop.{suffix}")
        assert score["unit"] == "loop" and 1 <= score["overall"] <= 10 and score["rubric"] == "teaching"
        assert all("check_id" in i and "code_anchor" in i for i in score["issues"])
        svg = (tmp_path / "loop.svg").read_text(encoding="utf-8")
        assert svg.startswith("<svg") and "Grounder" in svg
        report = json.loads((tmp_path / "loop.report.json").read_text(encoding="utf-8"))
        assert report["unit"]["id"] == "loop" and report["content_plan"]["components"]

    def test_rubric_override_changes_style(self, tmp_path):
        m = plan([os.path.join(EXAMPLES, "loop.md")], str(tmp_path), rubric="teaching")
        score = generate_unit(m, "loop", rubric="methodology", render=False)
        assert score["style"] == "paper" and score["rubric"] == "methodology"


class TestAll:
    def test_run_all_writes_gallery(self, tmp_path):
        m = plan([os.path.join(EXAMPLES, "loop.md"), os.path.join(EXAMPLES, "adversarial.md")], str(tmp_path))
        summary = run_all(m, render=False, log=lambda *_: None)
        index = tmp_path / "index.html"
        assert index.exists() and summary["index"] == str(index) and not summary["failed"]
        page = index.read_text(encoding="utf-8")
        assert "<svg" in page and "The FigTree loop" in page and "class=\"score" in page
        assert {u["id"] for u in summary["units"]} == {"loop", "adversarial"}
        assert all(u["status"] in ("ok", "needs-refine") for u in summary["units"])
        assert (tmp_path / "digest.json").exists()

    def test_gallery_tolerates_missing_svg(self, tmp_path):
        m = Manifest(str(tmp_path), "teaching", "teaching")
        path = gallery(m, [{"id": "x", "title": "X", "source": "x.md", "svg": str(tmp_path / "missing.svg"), "overall": 5.0, "issues": 0, "critical": 0}])
        assert "(no figure)" in open(path, encoding="utf-8").read()

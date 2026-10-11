"""Tests for the evaluation layer: rubric specs, check classification, probes and the judge schema."""

from __future__ import annotations

import json

from figtree.judge import JUDGE_SCHEMA, _prompt
from figtree.probes import evaluate, seed_probes
from figtree.quality import QualityCritic
from figtree.rubric_spec import CHECKS, VETOES, all_specs, classify, spec_for
from figtree.rubrics import DIMENSIONS, RUBRICS


class TestRubricSpecs:
    def test_every_rubric_has_a_spec_with_all_dimensions(self):
        specs = all_specs()
        assert set(specs) == set(RUBRICS)
        for name, spec in specs.items():
            assert set(spec["dimensions"]) == set(DIMENSIONS)
            for d in spec["dimensions"].values():
                assert set(d["anchors"]) == {"1-2", "3-4", "5-6", "7-8", "9-10"} and d["judge"]
            assert spec["checks"] and spec["vetoes"] and spec["scoring"]

    def test_check_ids_are_unique_and_classifiable(self):
        ids = [c.id for c in CHECKS]
        assert len(ids) == len(set(ids))
        assert classify("e3-text font size 8px below the chart minimum 10px") == "text.min_font"
        assert classify("f1 arrow shaft shorter than 20px") == "flow.short_shaft"
        assert classify("something new") is None

    def test_vetoes_reference_existing_checks(self):
        ids = {c.id for c in CHECKS}
        for v in VETOES.values():
            assert set(v["checks"]) <= ids

    def test_media_filter(self):
        assert any(c["id"] == "coverage.axis_labels" for c in spec_for("data-figure")["checks"])
        assert not any(c["id"] == "coverage.axis_labels" for c in spec_for("teaching")["checks"])


class TestProbes:
    def test_seed_probes_all_pass(self):
        res = evaluate(seed_probes())
        s = res.summary()
        assert s["failing_probes"] == [], s
        assert s["recall"] == 1.0 and s["precision"] == 1.0

    def test_issues_carry_check_ids(self):
        probes = {p.id: p for p in seed_probes()}
        report = QualityCritic("teaching").review(probes["defect.neon_fill"].svg)
        assert "polish.neon" in {i.check_id for i in report.issues}

    def test_gaming_probe_is_recorded_not_failed(self):
        from figtree.probes import CLEAN_DIAGRAM, Probe

        res = evaluate([Probe("gaming.x", "teaching", "gaming", CLEAN_DIAGRAM, ["proposed.nothing"], rationale="fooled")])
        row = res.probe_results[0]
        assert row["missed"] == ["proposed.nothing"] and row["passed"] is True


class TestJudge:
    def test_schema_and_prompt_cover_the_dimensions(self):
        assert set(JUDGE_SCHEMA["properties"]["scores"]["required"]) == set(DIMENSIONS)
        p = _prompt("teaching", "/tmp/x.png", "Source text here", "<svg/>")
        for d in DIMENSIONS:
            assert f"### {d}" in p
        assert "Veto rules" in p and "/tmp/x.png" in p
        json.dumps(JUDGE_SCHEMA)

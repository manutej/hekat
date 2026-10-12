"""The generative-UI contract: SVG -> FigureProgram -> SVG, schema validation, design swap."""
from __future__ import annotations

import json
import os

import pytest

from figtree.contract import HouseRenderer, program_from_svg, render_program, validate_program
from figtree.quality import QualityCritic

EX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "examples", "figtree")
SEED = os.path.join(EX, "design", "figtree-spec.teaching.svg")


def _read(p: str) -> str:
    with open(p, encoding="utf-8") as fh:
        return fh.read()


@pytest.fixture(scope="module")
def program():
    return program_from_svg(_read(SEED), title="FigTree loop", source="figtree-spec.md")


def test_export_is_valid_against_schema(program):
    assert validate_program(program) == []
    assert program["version"] == 1
    assert program["canvas"]["width"] > 0 and program["canvas"]["preset"] == "teaching"


def test_export_keeps_ids_labels_icons_and_hierarchy(program):
    nodes = {n["id"]: n for n in program["nodes"]}
    assert nodes["n2"]["label"] == "Grounder" and nodes["n2"]["icon"] == "search"
    assert nodes["n6"]["parent"] == "n3"
    conts = {c["id"] for c in program["containers"]}
    assert {"n3", "n4", "n5"} <= conts
    assert all(f["from"] in nodes or f["from"] in conts for f in program["flows"])


def test_flows_are_absolute_polylines(program):
    f = next(f for f in program["flows"] if f["id"] == "n4.arrow0")
    assert f["from"] == "n8" and f["to"] == "n9"
    assert f["points"][0][0] < f["points"][-1][0]  # left to right in canvas coordinates
    assert all(0 <= x <= program["canvas"]["width"] for x, _ in f["points"])


def test_render_round_trip_keeps_ids_and_scores_close(program):
    svg = render_program(program)
    for n in program["nodes"]:
        assert f'id="{n["id"]}"' in svg and f'id="{n["id"]}.label"' in svg
    for f in program["flows"]:
        assert f'id="{f["id"]}"' in svg
    before = QualityCritic("teaching").review(_read(SEED)).overall
    after = QualityCritic("teaching").review(svg).overall
    assert after >= before - 1.0
    # the rendered program is itself a program: exporting it again gives the same structure
    again = program_from_svg(svg)
    assert [n["id"] for n in again["nodes"]] == [n["id"] for n in program["nodes"]]
    assert len(again["flows"]) == len(program["flows"])


def test_validate_reports_dangling_references():
    bad = {"version": 1, "canvas": {"width": 100, "height": 100}, "nodes": [{"id": "a", "label": "A", "bbox": {"x": 0, "y": 0, "w": 10, "h": 10}}],
           "flows": [{"id": "f", "from": "a", "to": "zzz", "points": [[0, 0], [5, 5]]}]}
    probs = validate_program(bad)
    assert any("zzz" in p for p in probs)
    bad["version"] = 2
    assert any("version" in p for p in validate_program(bad))


class UpperCaseDesign(HouseRenderer):
    """A swapped design: same contract, different rendering decisions."""

    def node(self, n):
        return super().node({**n, "label": n["label"].upper(), "tone": "attention"})


def test_design_swap_changes_only_rendering(program):
    svg = render_program(program, UpperCaseDesign("slide"))
    assert "GROUNDER" in svg and 'id="n2"' in svg
    again = program_from_svg(svg)
    assert [n["id"] for n in again["nodes"]] == [n["id"] for n in program["nodes"]]
    assert all(n["tone"] == "attention" for n in again["nodes"])


def test_cli_round_trip(tmp_path):
    from figtree.cli import main

    out = tmp_path / "p.json"
    assert main(["contract", "export", SEED, "-o", str(out)]) == 0
    assert main(["contract", "validate", str(out)]) == 0
    svg = tmp_path / "r.svg"
    assert main(["contract", "render", str(out), "-o", str(svg), "--preset", "paper"]) == 0
    assert "Times" in _read(str(svg))
    json.loads(out.read_text())

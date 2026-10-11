"""Tests for element kinds, icons, the animation layer, the icon smith and the CLI backend parser."""

from __future__ import annotations

import json
import os
import re

from figtree import FigTree
from figtree.agents.claude_code import _parse_loose_json
from figtree.animate import animate_svg
from figtree.elements import kind_for, shape_path
from figtree.generator import RuleBasedGenerator
from figtree.icons import ICONS, icon_for, icons_used, standalone_icon, symbol_defs
from figtree.iconsmith import IconSmith, IconSpec, compose_icon, sheet
from figtree.program import load_program
from figtree.quality import QualityCritic
from figtree.svgmodel import parse_svg

HERE = os.path.dirname(os.path.abspath(__file__))
SPEC = os.path.join(os.path.dirname(HERE), "examples", "figtree", "figtree-spec.md")


def spec_text() -> str:
    with open(SPEC, encoding="utf-8") as fh:
        return fh.read()


class TestElementsAndIcons:
    def test_kind_matching_uses_word_boundaries(self):
        assert kind_for("render") == "block"  # not "end"
        assert kind_for("Memory store") == "store" and kind_for("Input") == "terminal"
        assert kind_for("Convergence Check") == "decision" and kind_for("User") == "actor"

    def test_shape_paths_are_closed_and_sized(self):
        for kind in ("store", "document", "decision", "terminal", "process", "actor"):
            d = shape_path(kind, 96, 32)
            assert d.startswith("M") and (kind == "actor" or "Z" in d)

    def test_icon_lookup_and_symbols(self):
        assert icon_for("Critic Agent") == "eye" and icon_for("Grounder") == "search" and icon_for("xyz") is None
        defs = symbol_defs(["eye", "search", "eye"])
        assert defs.count("<symbol") == 2 and 'id="icon-eye"' in defs
        for name, inner in ICONS.items():
            parse_svg(standalone_icon(name, inner))

    def test_generated_figure_with_icons_and_shapes_passes_the_critic(self):
        gen = RuleBasedGenerator(icons=True, shapes=True)
        result = FigTree(render=False, generator=gen).run(spec_text())
        svg = result.final_svg
        assert icons_used(svg) and "<symbol" in svg and 'data-role="icon"' in svg
        defects = [d for d in result.residual_defects if d.code_anchor != "no-vision"]
        assert defects == [], [d.to_dict() for d in defects]
        assert result.editability_proof.passed
        report = QualityCritic("teaching").review(svg)
        assert all("overflow" not in i.visual_description for i in report.issues)


class TestAnimation:
    def test_animation_layer_is_deterministic_and_guarded(self):
        result = FigTree(render=False).run(spec_text())
        svg, css = animate_svg(result.final_svg)
        again, css2 = animate_svg(result.final_svg)
        assert css == css2 and svg == again
        assert "prefers-reduced-motion" in css and "@keyframes ft-reveal" in css and "offset-path" in css
        parse_svg(svg)
        assert svg.count('data-role="pulse"') == len(result.content_plan.flows)
        # the animated document is still an addressable program the critic can read
        prog = load_program(svg)
        assert len([e for e in prog.elements if e.el.get("data-role") == "block"]) == len(result.content_plan.components)

    def test_modes_can_be_limited(self):
        result = FigTree(render=False).run(spec_text())
        svg, css = animate_svg(result.final_svg, modes=("reveal",), inline_style=False)
        assert "offset-path" not in css and "<style>" not in svg and "ft-reveal" in css


class TestIconSmith:
    def test_rule_based_draughtsman_and_loop(self):
        spec = IconSpec("critic-loop", "review and repair cycle", "arrows in a cycle")
        res = IconSmith().design(spec)
        assert res.svg.startswith("<svg") and res.score >= 9 and res.trajectory[0]["round"] == 0
        assert '<text' not in res.inner
        doc = sheet([res])
        parse_svg(doc)
        assert 'id="icon-critic-loop"' in doc

    def test_compose_prefers_library_base(self):
        assert compose_icon(IconSpec("eye2", "look", base="eye")) == ICONS["eye"]
        assert "<path" in compose_icon(IconSpec("x", "a page with a magnifier"))

    def test_icon_structural_rules_catch_tiny_and_margin_violations(self):
        from figtree.iconsmith import icon_structural_issues

        tiny = standalone_icon("t", '<circle cx="12" cy="12" r="2"/>')
        issues = icon_structural_issues(tiny, IconSpec("t", "dot"))
        assert any("vanish" in i.visual_description for i in issues)
        edge = standalone_icon("e", '<path d="M0 0h24v24"/>')
        issues = icon_structural_issues(edge, IconSpec("e", "edge"))
        assert any("safe margin" in i.visual_description for i in issues)


class TestClaudeCodeBackendParsing:
    def test_loose_json_parsing(self):
        assert _parse_loose_json('```json\n{"a": 1}\n```') == {"a": 1}
        assert _parse_loose_json('Here: {"edits": []} done') == {"edits": []}
        try:
            _parse_loose_json("no json here")
        except ValueError:
            pass
        else:
            raise AssertionError("expected ValueError")

    def test_backend_selection_prefers_cli_without_api_key(self, monkeypatch):
        from figtree.agents import llm
        from figtree.agents.claude_code import ClaudeCodeBackend

        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
        if ClaudeCodeBackend.available():
            assert isinstance(llm.default_backend(), ClaudeCodeBackend)

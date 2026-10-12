"""Spec-mode grounding and satellite grouping in the generator."""
from __future__ import annotations

from figtree.generator import RuleBasedGenerator, _satellites
from figtree.grounder import RuleBasedGrounder
from figtree.schemas import Flow

SPEC = """# An agent calling tools

A Langflow Agent component receives a Chat Input message and answers it with tools.

## Components
- **Chat Input** (kind: terminal, icon: user): the message enters here.
- **Agent** (kind: block, icon: gear): the actor.
- **Web Search** (kind: block, icon: search): a tool.
- **URL** (kind: block, icon: document): a tool.
- **Calculator** (kind: block, icon: wrench): a tool.
- **Chat Output** (kind: terminal, icon: text): the answer leaves here.

## Flows
Chat Input → Agent → Chat Output
Agent → Web Search (control): tool call.
Agent → URL (control): tool call.
Agent → Calculator (control): tool call.
"""


def test_spec_mode_draws_only_declared_components():
    out = RuleBasedGrounder().ground(SPEC)
    names = [c.name for c in out.content_plan.components]
    assert "Langflow" not in names and "Chat Input message" not in names
    assert set(names) == {"Chat Input", "Agent", "Web Search", "URL", "Calculator", "Chat Output"}
    assert any("spec mode" in r.visual_description for r in out.residuals)


def test_satellites_are_control_sinks_of_one_source():
    comps = ["A", "B", "T1", "T2", "C"]
    flows = [Flow("A", "B"), Flow("B", "C"), Flow("B", "T1", "control"), Flow("B", "T2", "control")]
    assert _satellites(comps, flows) == [("B", ["T1", "T2"])]
    # a data flow or an outgoing flow disqualifies a target
    assert _satellites(comps, flows + [Flow("T1", "C")]) == []
    assert _satellites(comps, [Flow("B", "T1", "control")]) == []  # one target is not a group


def test_agent_tools_become_their_own_child_and_score_well():
    from figtree.orchestrator import FigTree, Limits
    from figtree.quality import QualityCritic
    from figtree.styles import get_preset
    from figtree.worker import Worker

    ft = FigTree(limits=Limits(), render=False, generator=RuleBasedGenerator(icons=True, shapes=True),
                 worker=Worker(spacing_iterations=Limits().spacing_iterations, max_aspect=2.4))
    ft.style_override = get_preset("teaching").style
    result = ft.run(SPEC)
    svg = result.final_svg
    assert 'data-label="Web Search, URL, Calculator"' in svg
    report = QualityCritic("teaching").review(svg)
    assert report.overall >= 9.0
    assert not any(i.severity == "critical" for i in report.issues)

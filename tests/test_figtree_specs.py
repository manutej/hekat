"""Spec docs: parsing, the mechanical check against a corpus, and grounding of the annotations."""
from __future__ import annotations

import os

from figtree.grounder import RuleBasedGrounder
from figtree.specs import check_spec, parse_spec

SPEC = """# An agent calling tools

A user chats with an Agent that answers from tools.

## Components
- **Chat Input** (kind: terminal, icon: user): where the message enters.
- **Agent** (kind: block, icon: gear): the actor.
- **Web Search** (kind: block, icon: search): a tool.

## Flows
Chat Input → Agent
Agent → Web Search (control): the Toolset port connects to the Tools port.

## Steps
1. Add an Agent component.
2. Enable Tool Mode on the tool.

```evidence
Chat Input: "Add [**Chat Input** and **Chat Output** components](/chat-input-and-output) to your flow" (page.mdx)
Agent: "The Agent component is the main actor" (page.mdx)
Web Search: "Enable **Tool Mode** in the **Web Search**" (page.mdx)
Agent → Web Search: "Connect the Toolset port" (page.mdx)
```
"""

PAGE = """Some intro. Add [**Chat Input** and **Chat Output** components](/chat-input-and-output) to your flow.
The Agent component is the main actor. Enable **Tool Mode** in the **Web Search**, **URL** components.
Connect the Toolset port for each tool to the Tools port.
"""


def test_parse_spec_reads_every_section():
    s = parse_spec(SPEC)
    assert s["title"] == "An agent calling tools"
    assert [c["name"] for c in s["components"]] == ["Chat Input", "Agent", "Web Search"]
    assert s["components"][0]["kind"] == "terminal" and s["components"][1]["icon"] == "gear"
    assert s["flows"] == [{"from": "Chat Input", "to": "Agent", "type": "data"}, {"from": "Agent", "to": "Web Search", "type": "control"}]
    assert len(s["steps"]) == 2 and len(s["evidence"]) == 4


def test_check_against_corpus_normalises_markdown(tmp_path):
    (tmp_path / "page.mdx").write_text(PAGE, encoding="utf-8")
    r = check_spec(SPEC, str(tmp_path))
    assert r["evidence_missing"] == []
    assert r["components_without_evidence"] == []
    assert r["grounded_components"] == 3 and r["grounded_flows"] == 2
    assert r["flows_by_type"] == {"data": 1, "control": 1}
    assert r["ok"] is True


def test_check_reports_problems(tmp_path):
    (tmp_path / "page.mdx").write_text(PAGE, encoding="utf-8")
    bad = SPEC.replace('Agent: "The Agent component is the main actor"', 'Agent: "The Agent component is the main hero"')
    bad = bad.replace("Agent → Web Search (control)", "Agent → Web Search (control)\nWeb Search → Agent")
    r = check_spec(bad, str(tmp_path))
    assert any("main hero" in m for m in r["evidence_missing"])
    assert r["contradictions"] == ["agent <-> web-search"]
    assert r["ok"] is False


def test_grounder_honours_flow_type_and_hints():
    plan = RuleBasedGrounder().ground(SPEC).content_plan
    by = {c.name: c for c in plan.components}
    assert by["Chat Input"].kind == "terminal" and by["Chat Input"].icon == "user"
    assert by["Agent"].icon == "gear"
    types = {(f.src, f.dst): f.type for f in plan.flows}
    assert types[("Agent", "Web Search")] == "control"
    assert types[("Chat Input", "Agent")] == "data"
    # the evidence fence is not parsed as prose: no spurious component from the quotes
    assert "The" not in by and "Chat Output" not in by


def test_generate_uses_hints(tmp_path):
    from figtree.cli import main

    src = tmp_path / "spec.md"
    src.write_text(SPEC, encoding="utf-8")
    out = tmp_path / "fig.svg"
    assert main([str(src), "-o", str(out), "--style", "teaching", "--no-render"]) == 0
    svg = out.read_text(encoding="utf-8")
    assert 'data-kind="terminal"' in svg and 'href="#icon-gear"' in svg and 'href="#icon-search"' in svg


def test_sample_spec_in_repo_is_ok():
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    corpus = os.path.join(root, "examples", "figtree", "langflow", "corpus")
    specs = os.path.join(root, "examples", "figtree", "langflow", "specs")
    if not os.path.isdir(specs):
        return
    for f in os.listdir(specs):
        if f.endswith(".md") and not f.startswith("_"):
            with open(os.path.join(specs, f), encoding="utf-8") as fh:
                r = check_spec(fh.read(), corpus)
            assert r["ok"], (f, r["evidence_missing"], r["not_grounded"], r["flows_not_grounded"], r["contradictions"])

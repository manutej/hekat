#!/usr/bin/env python3
"""HEKAT Orchestration Mapping Workflow.

Runs a suite of multi-agent orchestration DSL queries through the full HEKAT
pipeline (lexer -> parser -> type-checker -> DAG builder -> compiler) and emits
an *explicit mapping* of every orchestration:

  - per-query execution plan (pattern, L1-L7 complexity, token budget, phases)
  - the explicit execution DAG: nodes + dependency edges (dep -> node)
  - parallel-phase grouping (which agents run concurrently)
  - an aggregate cross-query map of agent usage and agent-to-agent hand-offs

Outputs:
  - ORCHESTRATION_MAP.md   (human-readable report)
  - orchestration_map.json (machine-readable mapping)
  - a concise summary table to stdout
"""

import json
from collections import Counter, defaultdict

from hekat_compiler import HEKATCompiler, CompileError
from hekat_lexer import Lexer
from hekat_parser import (
    Parser, SimpleNode, SkilledNode, CommandedNode, EnsembleNode,
)
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder


# ---------------------------------------------------------------------------
# Orchestration suite: realistic multi-agent workflows across all 8 patterns.
# Every agent/skill/command is drawn from the type-checker registry so each
# query validates cleanly.
# ---------------------------------------------------------------------------
WORKFLOWS = [
    ("api-delivery-pipeline",
     'deep-researcher -> api-architect -> practical-programmer -> test-engineer '
     ': "design and ship a REST API"'),

    ("fullstack-fanout",
     '(frontend-architect || api-architect || test-engineer) '
     ': "build a full-stack feature in parallel"'),

    ("db-system-mixed",
     'deep-researcher -> (api-architect || debug-detective) -> practical-programmer '
     '-> test-engineer : "design and validate a database system"'),

    ("prod-deploy-fallback",
     'deployment-orchestrator ? devops-github-expert ? practical-programmer '
     ': "deploy the service to production"'),

    ("user-service-skilled",
     'api-architect + fastapi + postgresql : "design the user service API"'),

    ("research-consensus-ensemble",
     'deep-researcher^3 ; merge ; synthesize '
     ': "reach consensus on system architecture"'),

    ("docs-commanded",
     '@ctx7(deep-researcher) : "fetch the latest framework documentation"'),

    ("end-to-end-product",
     'deep-researcher -> (api-architect || frontend-architect || test-engineer) '
     '-> (practical-programmer || code-craftsman) -> deployment-orchestrator '
     ': "end-to-end product build"'),

    ("mercurio-synthesis",
     'mercurio-orchestrator -> (deep-researcher || api-architect) '
     '-> practical-programmer : "multi-dimensional synthesis and build"'),
]


def agent_label(expr) -> str:
    """Human-readable label for a DAG node's expression."""
    if isinstance(expr, SimpleNode):
        return expr.name
    if isinstance(expr, SkilledNode):
        return f"{expr.agent}+{'+'.join(expr.skills)}"
    if isinstance(expr, CommandedNode):
        agents = ",".join(expr.agents) if expr.agents else "?"
        return f"@{expr.command}({agents})"
    if isinstance(expr, EnsembleNode):
        return f"{expr.base}^{expr.count}"
    return "unknown"


def build_dag_view(dsl: str) -> dict:
    """Re-run lexer/parser/typecheck/DAG to extract the explicit graph."""
    tokens = Lexer(dsl).tokenize()
    ast = Parser(tokens).parse()
    validation = TypeChecker().validate(ast)
    dag = DAGBuilder().build(ast.expression)

    nodes = {
        nid: {
            "id": nid,
            "label": agent_label(node.expr),
            "is_fallback": node.is_fallback,
            "fallback_of": node.fallback_of,
        }
        for nid, node in dag.nodes.items()
    }

    # Explicit edges: each dependency is an incoming edge (dep -> node).
    edges = []
    for nid, node in dag.nodes.items():
        for dep in sorted(node.dependencies):
            edges.append({
                "from": dep,
                "to": nid,
                "from_label": nodes[dep]["label"],
                "to_label": nodes[nid]["label"],
            })

    phases = {
        str(phase): [nodes[nid]["label"] for nid in sorted(node_ids)]
        for phase, node_ids in sorted(dag.parallel_phases.items())
    }

    return {
        "valid": validation["valid"],
        "warnings": validation["warnings"],
        "nodes": nodes,
        "edges": edges,
        "phases": phases,
        "execution_order": dag.execution_order,
    }


def main() -> None:
    compiler = HEKATCompiler()

    mapping = {"workflows": [], "aggregate": {}}
    agent_usage = Counter()          # agent -> times it appears across workflows
    handoffs = Counter()             # (from_label, to_label) -> count

    for name, dsl in WORKFLOWS:
        entry = {"name": name, "query": dsl}
        try:
            plan = compiler.compile(dsl)
            dag = build_dag_view(dsl)

            entry.update({
                "pattern": plan.pattern_type,
                "complexity": plan.complexity_level,
                "total_tokens": plan.total_tokens,
                "metadata": plan.metadata,
                "plan_phases": [
                    {
                        "num": p.num,
                        "agents": p.agents,
                        "token_budget": p.token_budget,
                        "parallel": p.can_parallelize,
                        "skills": p.skills,
                    }
                    for p in plan.phases
                ],
                "dag": dag,
            })

            for node in dag["nodes"].values():
                agent_usage[node["label"]] += 1
            for edge in dag["edges"]:
                handoffs[(edge["from_label"], edge["to_label"])] += 1

        except CompileError as exc:
            entry["error"] = str(exc)

        mapping["workflows"].append(entry)

    mapping["aggregate"] = {
        "agent_usage": dict(agent_usage.most_common()),
        "handoffs": {f"{a} -> {b}": c for (a, b), c in handoffs.most_common()},
        "total_workflows": len(WORKFLOWS),
        "compiled_ok": sum(1 for w in mapping["workflows"] if "error" not in w),
    }

    # ---- JSON artifact -----------------------------------------------------
    with open("orchestration_map.json", "w") as fh:
        json.dump(mapping, fh, indent=2)

    # ---- Markdown artifact -------------------------------------------------
    md = _render_markdown(mapping)
    with open("ORCHESTRATION_MAP.md", "w") as fh:
        fh.write(md)

    # ---- stdout summary ----------------------------------------------------
    print("=" * 78)
    print("HEKAT ORCHESTRATION MAPPING WORKFLOW")
    print("=" * 78)
    agg = mapping["aggregate"]
    print(f"Workflows run : {agg['total_workflows']}   "
          f"compiled OK: {agg['compiled_ok']}\n")
    print(f"{'WORKFLOW':<28}{'PATTERN':<12}{'LVL':<5}{'NODES':<7}"
          f"{'EDGES':<7}{'PHASES':<7}{'TOKENS':<7}")
    print("-" * 78)
    for w in mapping["workflows"]:
        if "error" in w:
            print(f"{w['name']:<28}ERROR: {w['error']}")
            continue
        print(f"{w['name']:<28}{w['pattern']:<12}{w['complexity']:<5}"
              f"{len(w['dag']['nodes']):<7}{len(w['dag']['edges']):<7}"
              f"{len(w['dag']['phases']):<7}{w['total_tokens']:<7}")
    print("-" * 78)
    print("\nMost-used agents across all orchestrations:")
    for agent, count in list(agg["agent_usage"].items())[:8]:
        print(f"  {count}x  {agent}")
    print("\nArtifacts: ORCHESTRATION_MAP.md, orchestration_map.json")


def _render_markdown(mapping: dict) -> str:
    lines = ["# HEKAT Orchestration Map\n",
             "_Explicit mapping of multiple agentic orchestrations, generated by "
             "`build_orchestration_map.py`._\n"]

    agg = mapping["aggregate"]
    lines.append(f"- **Workflows:** {agg['total_workflows']}  "
                 f"(**{agg['compiled_ok']}** compiled successfully)\n")

    lines.append("\n## Summary\n")
    lines.append("| Workflow | Pattern | Level | Nodes | Edges | Phases | Tokens |")
    lines.append("|---|---|---|---|---|---|---|")
    for w in mapping["workflows"]:
        if "error" in w:
            lines.append(f"| {w['name']} | — | — | — | — | — | ERROR |")
            continue
        lines.append(
            f"| {w['name']} | {w['pattern']} | {w['complexity']} | "
            f"{len(w['dag']['nodes'])} | {len(w['dag']['edges'])} | "
            f"{len(w['dag']['phases'])} | {w['total_tokens']} |")

    for w in mapping["workflows"]:
        lines.append(f"\n## `{w['name']}`\n")
        lines.append(f"```hekat\n{w['query']}\n```\n")
        if "error" in w:
            lines.append(f"> **Compile error:** {w['error']}\n")
            continue
        lines.append(f"- **Pattern:** {w['pattern']}  ·  "
                     f"**Complexity:** {w['complexity']}  ·  "
                     f"**Tokens:** {w['total_tokens']}")
        meta = w["metadata"]
        lines.append(f"- **Agents:** {meta['total_agents']}  ·  "
                     f"**Depth:** {meta['execution_depth']}  ·  "
                     f"**Parallel:** {meta['has_parallelism']}  ·  "
                     f"**Fallback:** {meta['has_fallback']}\n")

        lines.append("**Execution phases (concurrent agents grouped):**\n")
        for phase, agents in w["dag"]["phases"].items():
            tag = " _(parallel)_" if len(agents) > 1 else ""
            lines.append(f"- Phase {phase}: {', '.join(agents)}{tag}")

        lines.append("\n**Explicit DAG edges (dependency → dependent):**\n")
        if w["dag"]["edges"]:
            for e in w["dag"]["edges"]:
                lines.append(f"- `{e['from_label']}` → `{e['to_label']}`")
        else:
            lines.append("- _(single node — no internal hand-offs)_")

        lines.append("\n**Mermaid graph:**\n")
        lines.append("```mermaid")
        lines.append("graph LR")
        node_ids = w["dag"]["nodes"]
        if w["dag"]["edges"]:
            for e in w["dag"]["edges"]:
                lines.append(f"  n{e['from']}[\"{e['from_label']}\"] "
                             f"--> n{e['to']}[\"{e['to_label']}\"]")
        else:
            for nid, n in node_ids.items():
                lines.append(f"  n{nid}[\"{n['label']}\"]")
        lines.append("```")

    lines.append("\n## Aggregate cross-workflow map\n")
    lines.append("**Agent usage (appearances across all orchestrations):**\n")
    for agent, count in agg["agent_usage"].items():
        lines.append(f"- `{agent}`: {count}")
    lines.append("\n**Agent hand-offs (edges aggregated across workflows):**\n")
    if agg["handoffs"]:
        for edge, count in agg["handoffs"].items():
            lines.append(f"- {edge}: {count}")
    else:
        lines.append("- _(none)_")

    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    main()

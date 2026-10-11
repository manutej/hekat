"""Command line: ``python -m figtree SOURCE.md -o figure.svg [--tree tree.json] [--backend rule|claude]``."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict, Optional

from figtree.orchestrator import FigTree, Limits


def _parse_edit(spec: Optional[str]) -> Optional[Dict[str, Any]]:
    if not spec:
        return None
    if spec.startswith("{"):
        return json.loads(spec)
    # "arrow:Critic>Generator" or "recolor:Critic=#F4A460"
    kind, _, rest = spec.partition(":")
    if kind == "arrow":
        a, _, b = rest.partition(">")
        return {"op": "add_dashed_arrow", "from": a.strip(), "to": b.strip()}
    if kind == "recolor":
        comp, _, fill = rest.partition("=")
        return {"op": "recolor", "component": comp.strip(), "fill": fill.strip() or "#F4A460"}
    raise SystemExit(f"unknown edit spec {spec!r}")


def main(argv: Optional[list] = None) -> int:
    ap = argparse.ArgumentParser(prog="figtree", description="FigTree-style recursive SVG methodology figure generator")
    ap.add_argument("source", help="paper, skill.md or methodology document")
    ap.add_argument("-o", "--output", default="figure.svg")
    ap.add_argument("--tree", help="write the layout tree (sheaf graph) as JSON")
    ap.add_argument("--report", help="write residuals, proof and content plan as JSON")
    ap.add_argument("--edit", help='editability test edit: "arrow:A>B", "recolor:A=#hex" or JSON')
    ap.add_argument("--backend", choices=["rule", "claude"], default="rule")
    ap.add_argument("--model", default=None, help="model id for the claude backend")
    ap.add_argument("--no-render", action="store_true", help="skip raster rendering for the critic")
    ap.add_argument("--max-nodes", type=int, default=32)
    ap.add_argument("--max-depth", type=int, default=8)
    args = ap.parse_args(argv)

    with open(args.source, encoding="utf-8") as fh:
        source = fh.read()
    limits = Limits(max_nodes=args.max_nodes, max_depth=args.max_depth)
    grounder = critic = None
    if args.backend == "claude":
        from figtree.agents.llm import ClaudeCritic, ClaudeGrounder, DEFAULT_MODEL

        model = args.model or DEFAULT_MODEL
        grounder, critic = ClaudeGrounder(model), ClaudeCritic(model)
    ft = FigTree(grounder=grounder, critic=critic, limits=limits, render=not args.no_render)
    result = ft.run(source, edit=_parse_edit(args.edit))
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(result.final_svg)
    if args.tree:
        with open(args.tree, "w", encoding="utf-8") as fh:
            json.dump(result.layout_tree.to_dict(), fh, indent=2)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(result.to_dict(), fh, indent=2)
    crit = sum(1 for r in result.residual_defects if r.severity == "critical")
    print(f"wrote {args.output}: {result.node_count} nodes, {len(result.content_plan.components)} components, "
          f"{len(result.content_plan.flows)} flows, {len(result.residual_defects)} residuals ({crit} critical), "
          f"editability {'PASS' if result.editability_proof.passed else 'FAIL'} "
          f"(diff={result.editability_proof.diff_element_count})")
    if result.faithfulness_failures:
        print("faithfulness failures:", ", ".join(result.faithfulness_failures), file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Command line.

    python -m figtree [generate] SOURCE.md -o figure.svg [--tree tree.json] [--backend rule|claude]
    python -m figtree refine FIG.svg --rubric teaching -o out.svg --trajectory t.json [--edits edits.json]
    python -m figtree score FIG.svg --rubric slide
"""

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


def _refine_main(argv: list) -> int:
    from figtree.refine import Refiner
    from figtree.rubrics import RUBRICS

    ap = argparse.ArgumentParser(prog="figtree refine", description="Iteratively refine any SVG against a rubric")
    ap.add_argument("svg")
    ap.add_argument("-o", "--output", default="refined.svg")
    ap.add_argument("--rubric", choices=sorted(RUBRICS), default="teaching")
    ap.add_argument("--rounds", type=int, default=8)
    ap.add_argument("--edits", help="JSON file: a list of edit scripts, one per round (external edit requests)")
    ap.add_argument("--source", help="source text for coverage / hallucination checks")
    ap.add_argument("--trajectory", help="write the score trajectory + remaining requests as JSON")
    ap.add_argument("--no-auto", action="store_true", help="apply only external edit requests")
    ap.add_argument("--no-render", action="store_true")
    ap.add_argument("--render-dir", help="keep the per-round PNG renders here")
    args = ap.parse_args(argv)
    with open(args.svg, encoding="utf-8") as fh:
        svg = fh.read()
    requests = None
    if args.edits:
        with open(args.edits, encoding="utf-8") as fh:
            requests = json.load(fh)
    source = None
    if args.source:
        with open(args.source, encoding="utf-8") as fh:
            source = fh.read()
    ref = Refiner(args.rubric, max_rounds=args.rounds, render=not args.no_render, render_dir=args.render_dir)
    res = ref.run(svg, requests, source_text=source, auto=not args.no_auto)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(res.svg)
    if args.trajectory:
        with open(args.trajectory, "w", encoding="utf-8") as fh:
            json.dump(res.to_dict(), fh, indent=2)
    print(f"{args.rubric}: {res.initial.overall} -> {res.final.overall} over {len(res.trajectory) - 1} round(s) ({res.stop_reason}); "
          f"{len(res.requests_remaining)} request(s) need a content decision; wrote {args.output}")
    for r in res.trajectory:
        print(f"  round {r.round}: overall {r.overall:5.2f}  issues {r.issues:2d} (critical {r.critical})  edits {r.edits_applied}  diff {r.diff_elements}  {r.note}")
    for req in res.requests_remaining:
        print(f"  request [{req['dimension']}] {req['visual_description']} -> {req['fix_instruction']} (anchor {req['code_anchor']})")
    return 0


def _score_main(argv: list) -> int:
    from figtree.quality import QualityCritic
    from figtree.rubrics import RUBRICS

    ap = argparse.ArgumentParser(prog="figtree score", description="Score an SVG against a rubric")
    ap.add_argument("svg")
    ap.add_argument("--rubric", choices=sorted(RUBRICS), default="teaching")
    ap.add_argument("--source")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    with open(args.svg, encoding="utf-8") as fh:
        svg = fh.read()
    source = open(args.source, encoding="utf-8").read() if args.source else None
    report = QualityCritic(args.rubric).review(svg, source)
    if args.json:
        print(json.dumps(report.to_dict(), indent=2))
        return 0
    print(f"{args.rubric}: overall {report.overall}")
    for k, v in report.scores.items():
        print(f"  {k:22s} {'  n/a' if v is None else f'{v:5.2f}'}")
    for i in report.issues:
        print(f"  [{i.severity}] {i.dimension}: {i.visual_description} -> {i.fix_instruction} ({'auto' if i.auto_edit else 'request'})")
    return 0


def main(argv: Optional[list] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "refine":
        return _refine_main(argv[1:])
    if argv and argv[0] == "score":
        return _score_main(argv[1:])
    if argv and argv[0] == "generate":
        argv = argv[1:]
    ap = argparse.ArgumentParser(prog="figtree", description="FigTree-style recursive SVG methodology figure generator (subcommands: generate, refine, score)")
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
    ap.add_argument("--max-aspect", type=float, default=3.0, help="fold wide layouts into rows above this width/height ratio")
    args = ap.parse_args(argv)

    with open(args.source, encoding="utf-8") as fh:
        source = fh.read()
    limits = Limits(max_nodes=args.max_nodes, max_depth=args.max_depth)
    grounder = critic = None
    if args.backend == "claude":
        from figtree.agents.llm import ClaudeCritic, ClaudeGrounder, DEFAULT_MODEL

        model = args.model or DEFAULT_MODEL
        grounder, critic = ClaudeGrounder(model), ClaudeCritic(model)
    from figtree.worker import Worker

    ft = FigTree(grounder=grounder, critic=critic, limits=limits, render=not args.no_render, worker=Worker(spacing_iterations=limits.spacing_iterations, max_aspect=args.max_aspect))
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

"""Command line.

    python -m figtree [generate] SOURCE.md -o figure.svg [--tree tree.json] [--backend rule|claude]
    python -m figtree refine FIG.svg --rubric teaching -o out.svg --trajectory t.json [--edits edits.json]
    python -m figtree score FIG.svg --rubric slide
    python -m figtree animate FIG.svg -o FIG.animated.svg [--modes reveal,draw,pulse]
    python -m figtree icon "name: concept | metaphor" ... -o icons/ [--backend claude] [--sheet sheet.svg]
"""

from __future__ import annotations

import argparse
import json
import os
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
    ap.add_argument("--request", action="append", default=[], help="prose edit request(s), one per round, turned into edit scripts by Claude (OAuth of this Claude Code session, or an API key)")
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
    if args.request:
        from figtree.agents.llm import ClaudeEditor

        editor = ClaudeEditor()
        prose = list(args.request)
        file_requests = requests or []

        def requests(rnd, current_svg, report):  # noqa: F811 - per-round prose requests, then any file scripts
            ops = []
            if rnd - 1 < len(prose):
                ops.extend(editor.propose(current_svg, prose[rnd - 1], [i.to_dict() for i in report.requests()], args.rubric))
                print(f"  request {rnd}: {prose[rnd - 1]!r} -> {len(ops)} edit op(s)")
            if rnd - 1 < len(file_requests):
                ops.extend(file_requests[rnd - 1])
            return ops or None

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


def _animate_main(argv: list) -> int:
    from figtree.animate import Timeline, animate_svg

    ap = argparse.ArgumentParser(prog="figtree animate", description="Add reveal / draw / pulse animation to a figure")
    ap.add_argument("svg")
    ap.add_argument("-o", "--output", default="animated.svg")
    ap.add_argument("--modes", default="reveal,draw,pulse")
    ap.add_argument("--css", help="write the stylesheet separately (for pages that inline the SVG)")
    ap.add_argument("--step", type=float, default=0.35)
    args = ap.parse_args(argv)
    with open(args.svg, encoding="utf-8") as fh:
        svg = fh.read()
    out, css = animate_svg(svg, tuple(m.strip() for m in args.modes.split(",") if m.strip()), Timeline(step=args.step), inline_style=not args.css)
    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(out)
    if args.css:
        with open(args.css, "w", encoding="utf-8") as fh:
            fh.write(css)
    print(f"wrote {args.output} ({len(css.splitlines())} animation rules)")
    return 0


def _icon_main(argv: list) -> int:
    from figtree.iconsmith import IconSmith, IconSpec, sheet

    ap = argparse.ArgumentParser(prog="figtree icon", description="Design custom icons with the generate -> critique -> refine loop")
    ap.add_argument("specs", nargs="+", help='"name: concept | metaphor" (metaphor optional)')
    ap.add_argument("-o", "--out-dir", default="icons")
    ap.add_argument("--backend", choices=["rule", "claude"], default="rule")
    ap.add_argument("--rounds", type=int, default=3)
    ap.add_argument("--sheet", help="write a contact sheet SVG")
    ap.add_argument("--report", help="write scores and trajectories as JSON")
    args = ap.parse_args(argv)
    os.makedirs(args.out_dir, exist_ok=True)
    draughtsman = None
    if args.backend == "claude":
        from figtree.agents.llm import ClaudeDraughtsman

        draughtsman = ClaudeDraughtsman()
    smith = IconSmith(draughtsman, rounds=args.rounds)
    results = []
    for spec_text in args.specs:
        name, _, rest = spec_text.partition(":")
        concept, _, metaphor = rest.partition("|")
        spec = IconSpec(name.strip(), concept.strip(), metaphor.strip())
        res = smith.design(spec)
        results.append(res)
        with open(os.path.join(args.out_dir, f"{spec.name}.svg"), "w", encoding="utf-8") as fh:
            fh.write(res.svg)
        status = "accepted" if res.accepted else "needs work"
        print(f"{spec.name:16s} {res.score:5.2f} {status}: " + "; ".join(i["visual_description"] for i in res.issues[:3]))
    if args.sheet:
        with open(args.sheet, "w", encoding="utf-8") as fh:
            fh.write(sheet(results))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump([r.to_dict() for r in results], fh, indent=2)
    return 0


def _eval_main(argv: list) -> int:
    from figtree.probes import evaluate, load_probes, seed_probes
    from figtree.rubric_spec import CHECKS

    ap = argparse.ArgumentParser(prog="figtree eval", description="Measure the evaluators: recall and precision of every check on probes")
    ap.add_argument("--rubric", default=None)
    ap.add_argument("--probes", default="examples/figtree/probes", help="directory of adversarial probes (<id>.svg + <id>.json)")
    ap.add_argument("--report", help="write the evaluation as JSON")
    ap.add_argument("--specs", help="also write the rubric specs to this directory")
    args = ap.parse_args(argv)
    probes = seed_probes() + (load_probes(args.probes) if os.path.isdir(args.probes) else [])
    res = evaluate(probes, args.rubric)
    s = res.summary()
    print(f"{s['probes']} probes, recall {s['recall']}, precision {s['precision']}, missed {s['missed']}, false positives {s['false_positives']}")
    for r in res.probe_results:
        if not r["passed"]:
            print(f"  FAIL {r['id']} ({r['kind']}, {r['source']}): missed {r['missed']} false {r['false_positive']} overall {r['overall']}")
    covered = {c for c in res.per_check}
    uncovered = [c.id for c in CHECKS if c.id not in covered]
    if uncovered:
        print("  checks without probes:", ", ".join(uncovered))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(res.to_dict(), fh, indent=2)
    if args.specs:
        from figtree.rubric_spec import write_specs

        write_specs(args.specs)
    return 0 if not s["failing_probes"] else 1


def _judge_main(argv: list) -> int:
    from figtree.judge import calibrate, judge

    ap = argparse.ArgumentParser(prog="figtree judge", description="Image-space judge (Claude reads the rendered PNG) and calibration against the measured scores")
    ap.add_argument("svg", nargs="?")
    ap.add_argument("--rubric", default="teaching")
    ap.add_argument("--source")
    ap.add_argument("--calibrate", help="JSON list of {name, svg, rubric, source?}")
    ap.add_argument("--report")
    args = ap.parse_args(argv)
    if args.calibrate:
        with open(args.calibrate, encoding="utf-8") as fh:
            items = json.load(fh)
        res = calibrate(items)
        for r in res["rows"]:
            print(f"  {r['name']:28s} measured {r['measured_overall']:5.2f}  judged {r['judged_overall']:5.2f}  gap {r['gap_overall']:+.2f}")
        print(f"mean gap {res['mean_gap']}, findings {len(res['findings'])}, cost ${res['cost_usd']}")
        for f in res["findings"]:
            print(f"  {f['kind']}: {f['name']} / {f['dimension']} measured {f['measured']} judged {f['judged']}")
        if args.report:
            with open(args.report, "w", encoding="utf-8") as fh:
                json.dump(res, fh, indent=2)
        return 0
    with open(args.svg, encoding="utf-8") as fh:
        svg = fh.read()
    src = open(args.source, encoding="utf-8").read() if args.source else None
    j = judge(svg, args.rubric, src)
    print(f"{args.rubric}: judged overall {j.overall} (${j.cost_usd:.3f})")
    for d, sc in j.scores.items():
        print(f"  {d:22s} {sc:2d}  {j.justifications[d][:110]}")
    if j.vetoes:
        print("  vetoes:", ", ".join(j.vetoes))
    if args.report:
        with open(args.report, "w", encoding="utf-8") as fh:
            json.dump(j.to_dict(), fh, indent=2)
    return 0


def main(argv: Optional[list] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if argv and argv[0] == "eval":
        return _eval_main(argv[1:])
    if argv and argv[0] == "judge":
        return _judge_main(argv[1:])
    if argv and argv[0] == "refine":
        return _refine_main(argv[1:])
    if argv and argv[0] == "score":
        return _score_main(argv[1:])
    if argv and argv[0] == "animate":
        return _animate_main(argv[1:])
    if argv and argv[0] == "icon":
        return _icon_main(argv[1:])
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
    ap.add_argument("--adopt-style", action="store_true", help="claude backend: use the model's global style instead of the paper's")
    ap.add_argument("--critic-scope", choices=["none", "root", "internal", "all"], default="root", help="claude backend: which nodes the model critic reviews")
    ap.add_argument("--no-render", action="store_true", help="skip raster rendering for the critic")
    ap.add_argument("--max-nodes", type=int, default=32)
    ap.add_argument("--max-depth", type=int, default=8)
    ap.add_argument("--max-aspect", type=float, default=3.0, help="fold wide layouts into rows above this width/height ratio")
    ap.add_argument("--icons", action="store_true", help="place a library icon inside each block")
    ap.add_argument("--shapes", action="store_true", help="draw stores, documents, decisions, terminals and actors with their silhouettes")
    args = ap.parse_args(argv)

    with open(args.source, encoding="utf-8") as fh:
        source = fh.read()
    limits = Limits(max_nodes=args.max_nodes, max_depth=args.max_depth)
    grounder = critic = None
    if args.backend == "claude":
        from figtree.agents.llm import ClaudeCritic, ClaudeGrounder, default_backend

        backend = default_backend(args.model)
        grounder = ClaudeGrounder(backend=backend, adopt_style=args.adopt_style)
        critic = ClaudeCritic(backend=backend, scope=args.critic_scope)
    from figtree.worker import Worker

    from figtree.generator import RuleBasedGenerator

    ft = FigTree(grounder=grounder, critic=critic, limits=limits, render=not args.no_render,
                 generator=RuleBasedGenerator(max_depth=limits.max_depth, icons=args.icons, shapes=args.shapes),
                 worker=Worker(spacing_iterations=limits.spacing_iterations, max_aspect=args.max_aspect))
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

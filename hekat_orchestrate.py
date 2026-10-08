#!/usr/bin/env python3
"""hekat_orchestrate — one entrypoint: HEKAT query → classify → gate → triage → durable run.

Uses the live TypeSafe model and Temporal worker tree when configured
(TYPESAFE_API_KEY / TEMPORAL_ADDRESS), and the local classifier + in-process
tape otherwise. Same command either way — going live is purely a config change.

Usage:
  python3 hekat_orchestrate.py '<dsl query>' [--allow c1,c2] [--forbid c3] [--json]
  python3 hekat_orchestrate.py --status

Examples:
  python3 hekat_orchestrate.py 'deep-researcher -> api-architect -> practical-programmer : "ship API"'
  python3 hekat_orchestrate.py 'deep-researcher -> deployment-orchestrator : "audit"' --forbid action
"""

import argparse
import json
import sys

from hekat_lexer import Lexer
from hekat_parser import Parser
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder
from hekat_jev import COLOR_META
from hekat_jev_config import load_config
from hekat_jev_typesafe import make_color_fn
from hekat_jev_tape import get_runner, GATE_WORD


def _colors(csv):
    return set(x.strip() for x in csv.split(",") if x.strip()) if csv else None


def orchestrate(dsl, allowed=None, forbidden=None, run_id="run"):
    cfg = load_config()
    tokens = Lexer(dsl).tokenize()
    ast = Parser(tokens).parse()
    validation = TypeChecker().validate(ast)
    if not validation["valid"]:
        raise ValueError(f"invalid query: {validation['errors']}")
    dag = DAGBuilder().build(ast.expression)

    color_fn = make_color_fn(cfg)                 # live model if keyed, else None
    runner = get_runner(cfg, color_fn=color_fn)   # Temporal if configured, else in-process
    record = runner.start(ast, dag, allowed=allowed, forbidden=forbidden, run_id=run_id)
    return cfg, record


def main(argv=None):
    p = argparse.ArgumentParser(description="Classify + gate + run a HEKAT orchestration")
    p.add_argument("query", nargs="?", help="HEKAT DSL query")
    p.add_argument("--allow", help="comma-separated allowed JEV colors")
    p.add_argument("--forbid", help="comma-separated forbidden (toxin) JEV colors")
    p.add_argument("--json", action="store_true", help="emit JSON")
    p.add_argument("--status", action="store_true", help="show backend config and exit")
    args = p.parse_args(argv)

    cfg = load_config()
    if args.status:
        print(cfg.banner())
        return 0
    if not args.query:
        p.error("a query is required (or use --status)")

    cfg, record = orchestrate(args.query, _colors(args.allow), _colors(args.forbid))
    clf = record.classification

    if args.json:
        print(json.dumps(record.summary(), indent=2))
        return 0

    print(f"[{cfg.banner()}]")
    print(f"query   : {args.query}")
    print(f"colors  : " + "  ".join(
        f"{lbl}[{COLOR_META[c]['short']}]" for lbl, c in clf.node_colors))
    for e in clf.edges:
        print(f"  γ {'✓' if e.ok else '✗'} {e.src_label}({e.src_color}) → "
              f"{e.dst_label}({e.dst_color})")
    print(f"cohorts : " + " | ".join(
        f"P{c.phase}:{'+'.join(c.workers)}" for c in record.cohorts))
    print(f"VERDICT : {clf.score.verdict}  →  gate={record.gate.upper()}  "
          f"triage={record.triage.upper()}")
    print(f"reasons : {'; '.join(clf.score.reasons)}")
    if clf.score.verdict == "RED":
        print("action  : fail closed — re-route via HEKAT '?' fallback operator")
    elif clf.score.verdict == "AMBER":
        print("action  : hold — signal a human verdict (runner.signal)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

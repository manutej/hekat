#!/usr/bin/env python3
"""Demo: classify + gate HEKAT orchestrations with the JEV bridge.

Runs several orchestration queries — including ones using the new ~color
classification modifier — through the compiler and the JEV gate, printing:
per-node color, γ edge seams, the fail-closed verdict (GREEN/AMBER/RED),
the triage branch (compose/escalate/refuse), and the durable tape.
"""

from hekat_lexer import Lexer
from hekat_parser import Parser
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder
from hekat_jev import classify_orchestration, replay, COLOR_META


QUERIES = [
    # grounded + actionable pipeline → expect GREEN / compose
    ('deep-researcher -> api-architect -> practical-programmer -> test-engineer '
     ': "design and ship a REST API"', None, None),

    # pure-idea speculation → not allowed on its own → AMBER/RED / escalate|refuse
    ('mercurio-orchestrator -> project-orchestrator : "brainstorm a strategy"', None, None),

    # ~color modifier overrides the lexicon: force research to read as evidence
    ('deep-researcher~evidence -> api-architect~concept -> practical-programmer~action '
     ': "classified pipeline via ~color modifier"', None, None),

    # fail-closed constraint: forbid `action` for a read-only / dry-run audit
    ('deep-researcher -> debug-detective -> deployment-orchestrator '
     ': "audit only, no changes"', {"entity", "concept", "evidence"}, {"action"}),
]


def run(dsl, allowed, forbidden):
    tokens = Lexer(dsl).tokenize()
    ast = Parser(tokens).parse()
    validation = TypeChecker().validate(ast)
    if not validation["valid"]:
        print(f"  ✗ invalid: {validation['errors']}")
        return
    dag = DAGBuilder().build(ast.expression)

    kwargs = {}
    if allowed is not None:
        kwargs["allowed"] = allowed
    if forbidden is not None:
        kwargs["forbidden"] = forbidden
    res = classify_orchestration(ast, dag, **kwargs)

    print(f"  prompt        : {ast.prompt!r}")
    if allowed is not None or forbidden is not None:
        print(f"  policy        : allowed={sorted(allowed or [])} forbidden={sorted(forbidden or [])}")
    colors = "  ".join(f"{lbl}[{COLOR_META[c]['short']}]" for lbl, c in res.node_colors)
    print(f"  classified    : {colors}")
    print(f"  color counts  : {{" + ", ".join(f'{c}:{n}' for c, n in res.color_counts.items() if n) + "}}")
    for e in res.edges:
        mark = "✓" if e.ok else "✗"
        print(f"    γ {mark} {e.src_label}({e.src_color}) → {e.dst_label}({e.dst_color}): {e.reason}")
    print(f"  VERDICT       : {res.score.verdict}   (allowed={res.score.allowed_mass:.2f}, "
          f"toxin={res.score.toxin_mass:.2f})")
    print(f"  triage        : {res.triage.upper()}")
    print(f"  reasons       : {'; '.join(res.score.reasons)}")
    print(f"  tape          : {replay(res.tape)}")


def main():
    print("=" * 78)
    print("HEKAT × JEV — orchestration classification & fail-closed gate")
    print("=" * 78)
    for dsl, allowed, forbidden in QUERIES:
        print(f"\n{'─' * 78}\nQUERY: {dsl}")
        run(dsl, allowed, forbidden)
    print("\n" + "=" * 78)


if __name__ == "__main__":
    main()

"""Golden-file: root lexer is SFT oracle; package lexer is drift telemetry.

See docs/sft/COMPILER_CANONICAL_SPEC.md
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from hekat_lexer import Lexer as RootLexer
from hekat.compiler.lexer import Lexer as PkgLexer

GOLDEN_DSL = [
    'api-architect : "design REST API"',
    'practical-programmer + fastapi + postgresql : "build API"',
    'deep-researcher -> api-architect -> practical-programmer : "design API"',
    '(frontend-architect || practical-programmer || devops-github-expert) : "chat mvp"',
    'deep-researcher -> (api-architect || debug-detective) -> practical-programmer : "fix"',
    'deployment-orchestrator ? devops-github-expert ? unix-bash-expert : "deploy"',
    '@ctx7(api-architect) : "docs-assisted design"',
]

OUT = ROOT / "reports/architecture/lexer_golden.json"
# Root token-type sequences that must not regress (names from hekat_lexer.TokenType).
ORACLE_TYPES = {
    'api-architect : "design REST API"': [
        "IDENTIFIER", "COLON", "STRING", "EOF"
    ],
}


def _root_types(dsl: str):
    return [t.type.name for t in RootLexer(dsl).tokenize()]


def _pkg_types(dsl: str):
    return [t.type.name for t in PkgLexer(dsl).tokenize()]


def main() -> int:
    rows = []
    oracle_fail = []
    for dsl in GOLDEN_DSL:
        root = _root_types(dsl)
        try:
            pkg = _pkg_types(dsl)
            pkg_err = None
        except Exception as e:  # package lexer may reject production strings
            pkg = []
            pkg_err = str(e)
        expected = ORACLE_TYPES.get(dsl)
        if expected and root != expected:
            oracle_fail.append({"dsl": dsl, "got": root, "expected": expected})
        rows.append(
            {
                "dsl": dsl,
                "root_types": root,
                "package_types": pkg,
                "package_error": pkg_err,
                "root_n": len(root),
                "package_n": len(pkg) if pkg else None,
                "diverges": root != pkg,
            }
        )
    report = {
        "canonical": "hekat_lexer.py (root)",
        "package": "hekat.compiler.lexer",
        "oracle_failures": oracle_fail,
        "n_divergent": sum(1 for r in rows if r["diverges"]),
        "rows": rows,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({"oracle_failures": len(oracle_fail), "n_divergent": report["n_divergent"]}, indent=2))
    return 1 if oracle_fail else 0


if __name__ == "__main__":
    raise SystemExit(main())

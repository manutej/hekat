"""Adversarial improvement lane: mutate DSL / tags and ensure validators catch failures."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/sft/build"))

from hekat_compiler import CompileError, HEKATCompiler
from hekat_type_checker import TypeChecker
from pack_record import pack_record
from validate_dataset import validate_row

OUT = ROOT / "reports/adversarial/report.json"
SCHEMA = ROOT / "datasets/hekat-orchestration-sft/schema/record.schema.json"

ATTACKS: List[Dict[str, Any]] = [
    {
        "name": "unknown_agent",
        "dsl": 'not-a-real-agent : "should fail"',
        "expect_compile_fail": True,
    },
    {
        "name": "empty_prompt",
        "dsl": 'api-architect : ""',
        "expect_compile_fail": True,
    },
    {
        "name": "missing_logic_tag",
        "dsl": 'api-architect : "ok"',
        "strip_logic": True,
        "expect_validation_substrings": ["missing_tag:logic"],
    },
    {
        "name": "answer_dsl_mismatch",
        "dsl": 'api-architect : "canonical artifacts dsl"',
        "answer_dsl": 'practical-programmer : "lying answer fence"',
        "expect_validation_substrings": ["answer_dsl_mismatch"],
    },
    {
        "name": "missing_pseudocode_tag",
        "dsl": 'api-architect : "ok"',
        "strip_pseudocode": True,
        "expect_validation_substrings": ["missing_tag:pseudocode"],
    },
    {
        "name": "invalid_operator_soup",
        "dsl": 'api-architect || -> ? : "bad"',
        "expect_compile_fail": True,
    },
    {
        "name": "unknown_skill",
        "dsl": 'api-architect+fake-skill-xyz : "x"',
        "expect_compile_fail": True,
    },
    {
        "name": "whitespace_only_logic",
        "dsl": 'api-architect : "ok"',
        "logic": "   \n\t  ",
        "expect_validation_substrings": ["missing_tag:logic"],
    },
]


def _replace_answer_fence(content: str, new_dsl: str) -> str:
    def repl(match: re.Match[str]) -> str:
        return f"{match.group(1)}{new_dsl.strip()}\n{match.group(3)}"

    return re.sub(
        r"(<answer>\s*```(?:hekat)?\s*)(.*?)(```)",
        repl,
        content,
        count=1,
        flags=re.DOTALL | re.IGNORECASE,
    )


def _apply_mutations(row: Dict[str, Any], atk: Dict[str, Any]) -> None:
    content = row["messages"][-1]["content"]
    if atk.get("strip_logic"):
        content = content.replace("<logic>\nfn probe(): pass\n</logic>\n\n", "")
    if atk.get("strip_pseudocode"):
        content = content.replace("<pseudocode>\nPROBE\n</pseudocode>\n\n", "")
    if atk.get("answer_dsl"):
        content = _replace_answer_fence(content, atk["answer_dsl"])
    row["messages"][-1]["content"] = content


def _validation_caught(errs: List[str], expect_substrings: List[str]) -> bool:
    joined = "\n".join(errs)
    return all(sub in joined for sub in expect_substrings)


def main() -> int:
    compiler = HEKATCompiler()
    registry = TypeChecker()
    schema = None
    if SCHEMA.exists():
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    try:
        import jsonschema  # noqa: F401
    except ImportError:
        schema = None

    results = []
    for atk in ATTACKS:
        dsl = atk["dsl"]
        compile_failed = False
        try:
            compiler.compile(dsl)
        except CompileError:
            compile_failed = True

        logic = atk.get("logic", "fn probe(): pass")
        row, _ = pack_record(
            record_id=f"adv-{atk['name']}",
            natural_language="adversarial probe",
            scenario_category="adversarial",
            pattern_type="Simple",
            operators=[":"],
            dsl=dsl,
            pseudocode="PROBE",
            logic=logic,
            generator_model="adversarial",
            source="adversarial",
        )
        _apply_mutations(row, atk)

        validation_errs = validate_row(row, schema, compiler, registry)

        caught = True
        detail: Dict[str, Any] = {
            "name": atk["name"],
            "compile_failed": compile_failed,
            "validation_errors": validation_errs,
        }

        if "expect_compile_fail" in atk:
            caught = compile_failed == atk["expect_compile_fail"]
            detail["expect_compile_fail"] = atk["expect_compile_fail"]

        if atk.get("expect_validation_substrings"):
            val_ok = _validation_caught(validation_errs, atk["expect_validation_substrings"])
            caught = caught and val_ok
            detail["expect_validation_substrings"] = atk["expect_validation_substrings"]

        detail["caught_as_expected"] = caught
        results.append(detail)

    n = len(results)
    caught_n = sum(1 for r in results if r["caught_as_expected"])
    summary = {
        "n": n,
        "caught": caught_n,
        "catch_rate": round(caught_n / n, 4) if n else 0.0,
        "results": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if caught_n == n else 1


if __name__ == "__main__":
    raise SystemExit(main())

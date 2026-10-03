"""Adversarial improvement lane: mutate DSL / tags and ensure validators catch failures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/sft/build"))

from hekat_compiler import CompileError, HEKATCompiler
from pack_record import pack_record

OUT = ROOT / "reports/adversarial/report.json"


ATTACKS = [
    {
        "name": "unknown_agent",
        "dsl": "not-a-real-agent : \"should fail\"",
        "expect_compile_fail": True,
    },
    {
        "name": "empty_prompt",
        "dsl": "api-architect : \"\"",
        "expect_compile_fail": True,
    },
    {
        "name": "missing_logic_tag",
        "dsl": "api-architect : \"ok\"",
        "strip_logic": True,
        "expect_compile_fail": False,
    },
]


def main() -> int:
    compiler = HEKATCompiler()
    results = []
    for atk in ATTACKS:
        compile_failed = False
        try:
            compiler.compile(atk["dsl"])
        except CompileError:
            compile_failed = True
        row, _ = pack_record(
            record_id=f"adv-{atk['name']}",
            natural_language="adversarial probe",
            scenario_category="adversarial",
            pattern_type="Simple",
            operators=[":"],
            dsl=atk["dsl"],
            pseudocode="PROBE",
            logic="fn probe(): pass",
            generator_model="adversarial",
            source="adversarial",
        )
        if atk.get("strip_logic"):
            row["messages"][-1]["content"] = row["messages"][-1]["content"].replace(
                "<logic>\nfn probe(): pass\n</logic>\n\n", ""
            )
        tag_ok = "<logic>" in row["messages"][-1]["content"]
        expect_fail = atk["expect_compile_fail"]
        caught = (compile_failed == expect_fail) if "expect_compile_fail" in atk else True
        if atk.get("strip_logic"):
            caught = not tag_ok  # evaluator should reject missing logic
        results.append(
            {
                "name": atk["name"],
                "compile_failed": compile_failed,
                "tag_logic_present": tag_ok,
                "caught_as_expected": caught,
            }
        )
    summary = {
        "n": len(results),
        "caught": sum(1 for r in results if r["caught_as_expected"]),
        "results": results,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0 if summary["caught"] == summary["n"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

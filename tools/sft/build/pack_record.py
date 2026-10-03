"""Pack HEKAT SFT records: DSL + dual traces + compiler artifacts → MessagesList row."""

from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parents[3]
import sys

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from hekat_compiler import CompileError, HEKATCompiler
from hekat_dag_builder import DAGBuilder
from hekat_lexer import Lexer
from hekat_parser import Parser

SYSTEM_PROMPT = (
    "You are a HEKAT orchestration planner. Reason in pseudocode, then in <logic> "
    "using coding constructs, then emit a valid HEKAT DSL query and structured plan."
)

TAG_RE = {
    "pseudocode": re.compile(r"<pseudocode>(.*?)</pseudocode>", re.DOTALL | re.IGNORECASE),
    "logic": re.compile(r"<logic>(.*?)</logic>", re.DOTALL | re.IGNORECASE),
    "answer": re.compile(r"<answer>(.*?)</answer>", re.DOTALL | re.IGNORECASE),
}


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def has_tags(text: str) -> Dict[str, bool]:
    return {name: bool(rx.search(text) and rx.search(text).group(1).strip()) for name, rx in TAG_RE.items()}


def extract_answer_dsl(answer_body: str) -> Optional[str]:
    fence = re.search(r"```(?:hekat)?\s*(.*?)```", answer_body, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    for line in answer_body.splitlines():
        if ":" in line and any(op in line for op in (":", "->", "→", "||", "?", "+")):
            return line.strip().strip("`")
    return None


def serialize_dag(dsl: str) -> Dict[str, Any]:
    tokens = Lexer(dsl).tokenize()
    ast = Parser(tokens).parse()
    dag = DAGBuilder().build(ast.expression)
    edges: List[List[int]] = []
    for nid, node in dag.nodes.items():
        for dep in node.dependencies:
            edges.append([dep, nid])
    return {
        "nodes": [
            {
                "id": nid,
                "agent": str(getattr(node.expr, "name", None)
                             or getattr(node.expr, "agent", None)
                             or getattr(node.expr, "base", "unknown")),
                "deps": list(node.dependencies),
            }
            for nid, node in dag.nodes.items()
        ],
        "edges": edges,
        "parallel_phases": {str(k): v for k, v in dag.parallel_phases.items()},
        "execution_order": list(dag.execution_order),
    }


def serialize_plan(plan) -> Dict[str, Any]:
    return {
        "pattern_type": plan.pattern_type,
        "complexity_level": plan.complexity_level,
        "total_tokens": plan.total_tokens,
        "prompt": plan.prompt,
        "phases": [
            {
                "num": p.num,
                "agents": p.agents,
                "token_budget": p.token_budget,
                "can_parallelize": p.can_parallelize,
                "skills": p.skills,
            }
            for p in plan.phases
        ],
        "metadata": plan.metadata,
    }


def build_assistant_content(pseudocode: str, logic: str, dsl: str, plan_summary: str) -> str:
    return (
        f"<pseudocode>\n{pseudocode.strip()}\n</pseudocode>\n\n"
        f"<logic>\n{logic.strip()}\n</logic>\n\n"
        f"<answer>\n```hekat\n{dsl.strip()}\n```\n\n{plan_summary.strip()}\n</answer>"
    )


def pack_record(
    *,
    record_id: str,
    natural_language: str,
    scenario_category: str,
    pattern_type: str,
    operators: List[str],
    dsl: str,
    pseudocode: str,
    logic: str,
    generator_model: str = "template-mvp",
    source: str = "synthetic-template",
) -> Tuple[Dict[str, Any], Optional[str]]:
    compiler = HEKATCompiler()
    compile_ok = False
    plan_obj = None
    err = None
    try:
        plan_obj = compiler.compile(dsl)
        compile_ok = True
    except CompileError as e:
        err = str(e)

    dag = {}
    execution_plan: Dict[str, Any] = {}
    complexity = "L1"
    if compile_ok and plan_obj is not None:
        dag = serialize_dag(dsl)
        execution_plan = serialize_plan(plan_obj)
        complexity = plan_obj.complexity_level
        plan_summary = (
            f"**pattern:** {plan_obj.pattern_type}\n"
            f"**level:** {plan_obj.complexity_level}\n"
            f"**phases:** {len(plan_obj.phases)}\n"
            f"**total_tokens:** {plan_obj.total_tokens}"
        )
    else:
        plan_summary = f"**pattern:** {pattern_type}\n**compile_error:** {err}"

    assistant = build_assistant_content(pseudocode, logic, dsl, plan_summary)
    tags = has_tags(assistant)

    record = {
        "id": record_id,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": natural_language},
            {"role": "assistant", "content": assistant},
        ],
        "task": {
            "natural_language": natural_language,
            "scenario_category": scenario_category,
            "pattern_type": pattern_type,
            "complexity_level": complexity if compile_ok else "L1",
            "operators": operators,
        },
        "artifacts": {
            "dsl": dsl,
            "compile_ok": compile_ok,
            "dag": dag,
            "execution_plan": execution_plan,
        },
        "meta": {
            "source": source,
            "generator_model": generator_model,
            "hekat_compiler_version": "root-pipeline",
            "license": "Apache-2.0",
            "created_at": _now(),
            "quality": {
                "schema_valid": False,  # set by validator
                "compile_valid": compile_ok,
                "has_pseudocode": tags["pseudocode"],
                "has_logic": tags["logic"],
                "has_answer": tags["answer"],
            },
            "content_hash": hashlib.sha256(
                f"{natural_language}\n{dsl}".encode("utf-8")
            ).hexdigest()[:16],
        },
    }
    return record, err


def write_jsonl(path: Path, rows: List[Dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

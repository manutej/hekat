"""
Blind evaluation harness.

INFORMATION FIREWALL: This module must not import tools.sft.build.* generators,
scenario seeds, or BUILD_SPEC content. It only reads:
  - PRODUCT_SPEC thresholds (hardcoded constants mirroring docs/sft/PRODUCT_SPEC.md)
  - dataset JSONL + schema
  - HEKATCompiler public compile API

Forbidden imports (enforced by convention + CI later):
  tools.sft.build.*, docs/sft/BUILD_SPEC.md, enrichment prompts, adversarial recipes.
"""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/sft"))

from hekat_compiler import CompileError, HEKATCompiler
from hekat_type_checker import TypeChecker
from common.tags import extract_answer_dsl, normalize_dsl, tags_ok

# Mirrors docs/sft/PRODUCT_SPEC.md — keep in sync manually; do not import BUILD_SPEC.
THRESHOLDS = {
    "pass_rate": 0.90,
    "tag_completeness": 1.0,
    "compile_recheck": 0.95,
    "dsl_answer_match": 0.95,
    "registry_ok": 0.95,
}

DATA = ROOT / "datasets/hekat-orchestration-sft/data"
OUT = ROOT / "reports/eval/scorecard.json"

_FORBIDDEN_MODULE_PREFIX = "tools.sft.build"


def assert_information_firewall() -> None:
    """Fail fast if build-lane modules were imported before blind eval runs."""
    leaked = [
        name
        for name in sys.modules
        if name == _FORBIDDEN_MODULE_PREFIX or name.startswith(f"{_FORBIDDEN_MODULE_PREFIX}.")
    ]
    if leaked:
        raise RuntimeError(
            "Information firewall violation: build modules loaded in eval process: "
            + ", ".join(sorted(leaked))
        )


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def _phase_agents_in_registry(plan, registry: TypeChecker) -> bool:
    for phase in plan.phases:
        for agent in phase.agents:
            # Commanded labels look like ctx7(api-architect)
            if "(" in agent and agent.endswith(")"):
                cmd, rest = agent.split("(", 1)
                inner = rest[:-1]
                if cmd not in registry.commands:
                    return False
                if inner and inner not in registry.agents:
                    return False
                continue
            if agent not in registry.agents:
                return False
    return True


def eval_split(
    rows: List[Dict[str, Any]],
    compiler: HEKATCompiler,
    registry: TypeChecker,
) -> Dict[str, Any]:
    n = len(rows) or 1
    tag_pass = 0
    compile_pass = 0
    match_pass = 0
    registry_pass = 0
    full_pass = 0
    by_pattern = Counter()
    fail_ids = []
    for row in rows:
        asst = row["messages"][-1]["content"]
        t_ok = tags_ok(asst)
        c_ok = False
        r_ok = False
        plan = None
        try:
            plan = compiler.compile(row["artifacts"]["dsl"])
            c_ok = True
            r_ok = _phase_agents_in_registry(plan, registry)
        except CompileError:
            c_ok = False
            r_ok = False
        a_ok = normalize_dsl(extract_answer_dsl(asst) or "") == normalize_dsl(row["artifacts"]["dsl"])
        if t_ok:
            tag_pass += 1
        if c_ok:
            compile_pass += 1
        if a_ok:
            match_pass += 1
        if r_ok:
            registry_pass += 1
        ok = (
            t_ok
            and c_ok
            and a_ok
            and r_ok
            and bool(row["artifacts"].get("compile_ok"))
        )
        if ok:
            full_pass += 1
            by_pattern[row["task"]["pattern_type"]] += 1
        else:
            fail_ids.append(row["id"])
    metrics = {
        "n": len(rows),
        "pass_rate": full_pass / n,
        "tag_completeness": tag_pass / n,
        "compile_recheck": compile_pass / n,
        "dsl_answer_match": match_pass / n,
        "registry_ok": registry_pass / n,
        "pass_by_pattern": dict(by_pattern),
        "fail_ids": fail_ids,
    }
    metrics["thresholds_met"] = {
        k: metrics[k] >= THRESHOLDS[k]
        for k in THRESHOLDS
    }
    metrics["mvp_green"] = all(metrics["thresholds_met"].values())
    return metrics


def main() -> int:
    assert_information_firewall()
    compiler = HEKATCompiler()
    registry = TypeChecker()
    report = {"thresholds": THRESHOLDS, "splits": {}}
    for split in ("train", "validation"):
        path = DATA / f"{split}.jsonl"
        if not path.exists():
            report["splits"][split] = {"error": "missing"}
            continue
        report["splits"][split] = eval_split(load_jsonl(path), compiler, registry)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    # PRODUCT_SPEC gates MVP on the validation split only.
    val = report["splits"].get("validation", {})
    green = bool(val.get("mvp_green"))
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())

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
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from hekat_compiler import CompileError, HEKATCompiler

# Mirrors docs/sft/PRODUCT_SPEC.md — keep in sync manually; do not import BUILD_SPEC.
THRESHOLDS = {
    "pass_rate": 0.90,
    "tag_completeness": 1.0,
    "compile_recheck": 0.95,
    "dsl_answer_match": 0.95,
}

TAG_RE = {
    "pseudocode": re.compile(r"<pseudocode>(.*?)</pseudocode>", re.DOTALL | re.IGNORECASE),
    "logic": re.compile(r"<logic>(.*?)</logic>", re.DOTALL | re.IGNORECASE),
    "answer": re.compile(r"<answer>(.*?)</answer>", re.DOTALL | re.IGNORECASE),
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


def normalize_dsl(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().replace("→", "->"))


def tags_ok(content: str) -> bool:
    for rx in TAG_RE.values():
        m = rx.search(content)
        if not m or not m.group(1).strip():
            return False
    return True


def answer_dsl(content: str) -> str:
    m = TAG_RE["answer"].search(content)
    if not m:
        return ""
    fence = re.search(r"```(?:hekat)?\s*(.*?)```", m.group(1), re.DOTALL | re.IGNORECASE)
    return fence.group(1).strip() if fence else ""


def eval_split(rows: List[Dict[str, Any]], compiler: HEKATCompiler) -> Dict[str, Any]:
    n = len(rows) or 1
    tag_pass = 0
    compile_pass = 0
    match_pass = 0
    full_pass = 0
    by_pattern = Counter()
    fail_ids = []
    for row in rows:
        asst = row["messages"][-1]["content"]
        t_ok = tags_ok(asst)
        c_ok = False
        try:
            compiler.compile(row["artifacts"]["dsl"])
            c_ok = True
        except CompileError:
            c_ok = False
        a_ok = normalize_dsl(answer_dsl(asst)) == normalize_dsl(row["artifacts"]["dsl"])
        if t_ok:
            tag_pass += 1
        if c_ok:
            compile_pass += 1
        if a_ok:
            match_pass += 1
        ok = t_ok and c_ok and a_ok and bool(row["artifacts"].get("compile_ok"))
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
    report = {"thresholds": THRESHOLDS, "splits": {}}
    for split in ("train", "validation"):
        path = DATA / f"{split}.jsonl"
        if not path.exists():
            report["splits"][split] = {"error": "missing"}
            continue
        report["splits"][split] = eval_split(load_jsonl(path), compiler)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    val = report["splits"].get("validation", {})
    train = report["splits"].get("train", {})
    green = bool(val.get("mvp_green") or train.get("mvp_green"))
    return 0 if green else 1


if __name__ == "__main__":
    raise SystemExit(main())

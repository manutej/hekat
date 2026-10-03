"""Quantify complexity/token stats for math reviewer."""

from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from hekat_compiler import HEKATCompiler

DATA = ROOT / "datasets/hekat-orchestration-sft/data"


def main() -> int:
    compiler = HEKATCompiler()
    mismatches = []
    levels = Counter()
    tokens = []
    seq_levels = Counter()
    for split in ("train.jsonl", "validation.jsonl"):
        for line in (DATA / split).read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            row = json.loads(line)
            plan = compiler.compile(row["artifacts"]["dsl"])
            levels[plan.complexity_level] += 1
            tokens.append(plan.total_tokens)
            if row["task"]["pattern_type"] == "Sequential":
                seq_levels[plan.complexity_level] += 1
            if plan.complexity_level != row["task"]["complexity_level"]:
                mismatches.append(row["id"])
    report = {
        "mismatches": mismatches,
        "levels": dict(levels),
        "sequential_levels": dict(seq_levels),
        "token_min": min(tokens) if tokens else None,
        "token_max": max(tokens) if tokens else None,
        "token_zero_or_neg": sum(1 for t in tokens if t <= 0),
        "l2_count": levels.get("L2", 0),
    }
    out = ROOT / "reports/math/stats.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not mismatches and report["token_zero_or_neg"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Math/metrics sanity checks for HEKAT orchestration SFT dataset."""

from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from hekat_compiler import HEKATCompiler  # noqa: E402

DATA = ROOT / "datasets/hekat-orchestration-sft/data"


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> int:
    compiler = HEKATCompiler()
    rows = load_jsonl(DATA / "train.jsonl") + load_jsonl(DATA / "validation.jsonl")

    mismatches: list[tuple] = []
    totals: list[int] = []
    phase_bad = 0
    token_drift = 0

    for row in rows:
        dsl = row["artifacts"]["dsl"]
        plan = compiler.compile(dsl)
        task_level = row["task"]["complexity_level"]
        plan_level = row["artifacts"]["execution_plan"]["complexity_level"]
        if plan.complexity_level != task_level or plan.complexity_level != plan_level:
            mismatches.append((row["id"], task_level, plan_level, plan.complexity_level))

        ep = row["artifacts"]["execution_plan"]
        totals.append(ep["total_tokens"])
        if plan.total_tokens != ep["total_tokens"]:
            token_drift += 1
        for ph in ep["phases"]:
            if ph["token_budget"] <= 0:
                phase_bad += 1

    levels = Counter(r["task"]["complexity_level"] for r in rows)
    seq = [r for r in rows if r["task"]["pattern_type"] == "Sequential"]
    seq_l4 = sum(1 for r in seq if r["task"]["complexity_level"] == "L4")

    random.seed(42)
    spot = random.sample(rows, min(15, len(rows)))
    spot_ok = 0
    for r in spot:
        if compiler.compile(r["artifacts"]["dsl"]).complexity_level == r["task"]["complexity_level"]:
            spot_ok += 1

    print(f"n_total={len(rows)}")
    print(f"levels={dict(sorted(levels.items()))}")
    print(f"complexity_mismatches={len(mismatches)}")
    print(f"spot_check_15_ok={spot_ok}/15")
    print(f"token_total_min={min(totals)} max={max(totals)} mean={sum(totals)/len(totals):.1f}")
    print(f"token_total_nonpositive={sum(1 for t in totals if t <= 0)} phase_budget_nonpositive={phase_bad}")
    print(f"token_drift_vs_recompile={token_drift}")
    print(f"L2_count={levels.get('L2', 0)} ({100*levels.get('L2', 0)/len(rows):.1f}%)")
    if seq:
        print(
            f"sequential_n={len(seq)} L4={seq_l4} "
            f"sequential_L4_rate={100*seq_l4/len(seq):.1f}%"
        )
    return 0 if not mismatches and phase_bad == 0 and all(t > 0 for t in totals) else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Monitoring agent: dataset health snapshot (counts, patterns, gate signals)."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "datasets/hekat-orchestration-sft/data"
OUT = ROOT / "reports/monitor/snapshot.json"
EVAL = ROOT / "reports/eval/scorecard.json"


def load_jsonl(path: Path):
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows


def main() -> int:
    train = load_jsonl(DATA / "train.jsonl")
    val = load_jsonl(DATA / "validation.jsonl")
    all_rows = train + val
    patterns = Counter(r["task"]["pattern_type"] for r in all_rows)
    levels = Counter(r["task"]["complexity_level"] for r in all_rows)
    compile_ok = sum(1 for r in all_rows if r["artifacts"].get("compile_ok"))
    alarms = []
    if len(all_rows) < 20:
        alarms.append("LOW_VOLUME")
    if compile_ok < len(all_rows):
        alarms.append("COMPILE_GAPS")
    if len(patterns) < 4:
        alarms.append("LOW_PATTERN_DIVERSITY")
    scorecard = {}
    if EVAL.exists():
        scorecard = json.loads(EVAL.read_text(encoding="utf-8"))
        # PRODUCT_SPEC gates on validation; train is diagnostic only.
        if not scorecard.get("splits", {}).get("validation", {}).get("mvp_green", False):
            alarms.append("EVAL_NOT_GREEN")
    snap = {
        "n_train": len(train),
        "n_validation": len(val),
        "n_total": len(all_rows),
        "compile_ok": compile_ok,
        "patterns": dict(patterns),
        "levels": dict(levels),
        "alarms": alarms,
        "eval_mvp_green_validation": scorecard.get("splits", {}).get("validation", {}).get("mvp_green"),
        "eval_mvp_green_train": scorecard.get("splits", {}).get("train", {}).get("mvp_green"),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(snap, indent=2), encoding="utf-8")
    print(json.dumps(snap, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""Deterministic dual-trace generator for MVP when Composer agents are unavailable."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from pack_record import pack_record, write_jsonl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCENARIOS = HERE / "scenarios" / "pilot_scenarios.json"
OUT_DIR = ROOT / "datasets" / "hekat-orchestration-sft" / "data"


def make_pseudocode(scenario: Dict[str, Any]) -> str:
    ops = ", ".join(scenario["operators"])
    return (
        f"GOAL = {scenario['pattern_type'].lower()}_orchestration\n"
        f"NL = {scenario['natural_language']!r}\n"
        f"PATTERN = {scenario['pattern_type']}\n"
        f"OPS = [{ops}]\n"
        "STEPS:\n"
        "  1. parse intent from NL\n"
        "  2. select registry agents matching intent\n"
        "  3. compose DSL with OPS\n"
        "  4. attach prompt from NL\n"
        "  5. validate via typecheck + compile\n"
        "RETURN dsl"
    )


def make_logic(scenario: Dict[str, Any], dsl: str) -> str:
    return (
        "fn plan(task: str) -> DslQuery:\n"
        f"  pattern = {scenario['pattern_type']!r}\n"
        "  requirements = decompose(task)\n"
        "  agents = select_agents(requirements, registry)\n"
        "  if pattern == \"Simple\":\n"
        "    dsl = Sequential([agents[0]]).with_prompt(task)\n"
        "  elif pattern == \"Skilled\":\n"
        "    dsl = Skilled(agents[0], skills).with_prompt(task)\n"
        "  elif pattern == \"Sequential\":\n"
        "    dsl = Sequential(agents).with_prompt(task)\n"
        "  elif pattern == \"Parallel\":\n"
        "    dsl = Parallel(agents).with_prompt(task)\n"
        "  elif pattern == \"Mixed\":\n"
        "    dsl = Sequential([agents[0], Parallel(agents[1:-1]), agents[-1]]).with_prompt(task)\n"
        "  elif pattern == \"Fallback\":\n"
        "    dsl = Fallback(agents).with_prompt(task)\n"
        "  elif pattern == \"Commanded\":\n"
        "    dsl = Commanded(cmd, agents).with_prompt(task)\n"
        "  else:\n"
        "    raise UnsupportedPattern(pattern)\n"
        "  assert typecheck(dsl).valid\n"
        f"  # concrete: {dsl}\n"
        "  return dsl"
    )


def expand_dsl(scenario: Dict[str, Any]) -> str:
    nl = scenario["natural_language"].replace('"', '\\"')
    return scenario["dsl_template"].format(nl=nl)


def generate(scenarios: List[Dict[str, Any]] | None = None) -> List[Dict[str, Any]]:
    if scenarios is None:
        scenarios = json.loads(SCENARIOS.read_text(encoding="utf-8"))
    rows: List[Dict[str, Any]] = []
    errors: List[str] = []
    for sc in scenarios:
        dsl = expand_dsl(sc)
        pc = make_pseudocode(sc)
        logic = make_logic(sc, dsl)
        row, err = pack_record(
            record_id=f"hekat-{sc['id']}",
            natural_language=sc["natural_language"],
            scenario_category=sc["scenario_category"],
            pattern_type=sc["pattern_type"],
            operators=sc["operators"],
            dsl=dsl,
            pseudocode=pc,
            logic=logic,
            generator_model="template-mvp",
            source="synthetic-template",
        )
        if err:
            errors.append(f"{sc['id']}: {err}")
        if row["artifacts"]["compile_ok"]:
            rows.append(row)
    if errors:
        print("Compile failures:")
        for e in errors:
            print(" -", e)
    return rows


def split_rows(rows: List[Dict[str, Any]], val_ratio: float = 0.15):
    # Stratify lightly by pattern_type
    by_pat: Dict[str, List[Dict[str, Any]]] = {}
    for r in rows:
        by_pat.setdefault(r["task"]["pattern_type"], []).append(r)
    train, val = [], []
    for pat, items in by_pat.items():
        n_val = max(1, int(round(len(items) * val_ratio))) if len(items) > 3 else (1 if len(items) > 1 else 0)
        val.extend(items[:n_val])
        train.extend(items[n_val:])
    return train, val


def main() -> int:
    rows = generate()
    train, val = split_rows(rows)
    write_jsonl(OUT_DIR / "train.jsonl", train)
    write_jsonl(OUT_DIR / "validation.jsonl", val)
    print(f"Wrote {len(train)} train / {len(val)} val (from {len(rows)} compile-ok)")
    return 0 if rows else 1


if __name__ == "__main__":
    raise SystemExit(main())

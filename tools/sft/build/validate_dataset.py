"""Hard gates G1–G6 for HEKAT SFT JSONL."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools/sft"))

from hekat_compiler import CompileError, HEKATCompiler
from hekat_type_checker import TypeChecker
from common.tags import TAG_RE, extract_answer_dsl, extract_tag, normalize_dsl

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

SCHEMA = ROOT / "datasets/hekat-orchestration-sft/schema/record.schema.json"
DATA = ROOT / "datasets/hekat-orchestration-sft/data"

def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def validate_row(row: Dict[str, Any], schema: Dict[str, Any] | None, compiler: HEKATCompiler, registry: TypeChecker) -> List[str]:
    errs: List[str] = []
    if schema is not None and jsonschema is not None:
        try:
            jsonschema.validate(row, schema)
            row["meta"]["quality"]["schema_valid"] = True
        except jsonschema.ValidationError as e:
            errs.append(f"schema: {e.message}")
            row["meta"]["quality"]["schema_valid"] = False

    asst = row["messages"][-1]["content"]
    for name in TAG_RE:
        if not extract_tag(asst, name):
            errs.append(f"missing_tag:{name}")

    dsl = row["artifacts"]["dsl"]
    try:
        plan = compiler.compile(dsl)
        if not row["artifacts"]["compile_ok"]:
            errs.append("compile_ok_flag_false_but_compiles")
        # G4: phase agents/commands ⊆ public registry
        for phase in plan.phases:
            for agent in phase.agents:
                if "(" in agent and agent.endswith(")"):
                    cmd, rest = agent.split("(", 1)
                    inner = rest[:-1]
                    if cmd not in registry.commands:
                        errs.append(f"registry: unknown command '{cmd}'")
                    elif inner and inner not in registry.agents:
                        errs.append(f"registry: unknown agent '{inner}'")
                elif agent not in registry.agents:
                    errs.append(f"registry: unknown agent '{agent}'")
    except CompileError as e:
        errs.append(f"compile: {e}")

    adsl = extract_answer_dsl(asst) or ""
    if adsl and normalize_dsl(adsl) != normalize_dsl(dsl):
        errs.append("answer_dsl_mismatch")

    return errs


def main() -> int:
    schema = json.loads(SCHEMA.read_text(encoding="utf-8")) if SCHEMA.exists() else None
    if jsonschema is None:
        print("WARN: jsonschema not installed; skipping formal schema validate")
    compiler = HEKATCompiler()
    registry = TypeChecker()
    all_errs: List[Tuple[str, str, List[str]]] = []
    hashes = set()
    dupes = 0
    total = 0
    for split in ("train.jsonl", "validation.jsonl"):
        path = DATA / split
        if not path.exists():
            print(f"MISSING {path}")
            return 1
        rows = load_jsonl(path)
        total += len(rows)
        for row in rows:
            h = row.get("meta", {}).get("content_hash") or row["id"]
            if h in hashes:
                dupes += 1
            hashes.add(h)
            errs = validate_row(row, schema, compiler, registry)
            if errs:
                all_errs.append((split, row["id"], errs))
    print(f"rows={total} dupes={dupes} failing={len(all_errs)}")
    for split, rid, errs in all_errs[:50]:
        print(f"FAIL {split} {rid}: {errs}")
    return 1 if all_errs or dupes else 0


if __name__ == "__main__":
    raise SystemExit(main())

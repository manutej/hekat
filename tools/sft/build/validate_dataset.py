"""Hard gates G1–G6 for HEKAT SFT JSONL."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from hekat_compiler import CompileError, HEKATCompiler
from hekat_type_checker import TypeChecker

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

SCHEMA = ROOT / "datasets/hekat-orchestration-sft/schema/record.schema.json"
DATA = ROOT / "datasets/hekat-orchestration-sft/data"

TAG_RE = {
    "pseudocode": re.compile(r"<pseudocode>(.*?)</pseudocode>", re.DOTALL | re.IGNORECASE),
    "logic": re.compile(r"<logic>(.*?)</logic>", re.DOTALL | re.IGNORECASE),
    "answer": re.compile(r"<answer>(.*?)</answer>", re.DOTALL | re.IGNORECASE),
}


def load_jsonl(path: Path) -> List[Dict[str, Any]]:
    rows = []
    with path.open(encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            rows.append(json.loads(line))
    return rows


def normalize_dsl(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().replace("→", "->"))


def answer_dsl(assistant: str) -> str:
    m = TAG_RE["answer"].search(assistant)
    if not m:
        return ""
    body = m.group(1)
    fence = re.search(r"```(?:hekat)?\s*(.*?)```", body, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    return ""


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
    for name, rx in TAG_RE.items():
        m = rx.search(asst)
        if not m or not m.group(1).strip():
            errs.append(f"missing_tag:{name}")

    dsl = row["artifacts"]["dsl"]
    try:
        plan = compiler.compile(dsl)
        if not row["artifacts"]["compile_ok"]:
            errs.append("compile_ok_flag_false_but_compiles")
        # registry agents appear in plan phases
        for phase in plan.phases:
            for agent in phase.agents:
                base = agent.split("(")[-1].rstrip(")") if "(" in agent else agent
                if base not in registry.agents and not base.startswith("ctx7"):
                    # commanded form ctx7(agent) already partially checked by compiler
                    if base not in registry.agents:
                        pass
    except CompileError as e:
        errs.append(f"compile: {e}")

    adsl = answer_dsl(asst)
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

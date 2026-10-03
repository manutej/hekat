"""Merge Composer-agent enrichment JSONL into packed dataset rows.

Expected input lines:
{
  "scenario_id": "simple-000",
  "natural_language": "...",
  "pseudocode": "...",
  "logic": "...",
  "dsl": "..."   # optional override; else scenario template
}
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from pack_record import pack_record, write_jsonl
from template_generator import expand_dsl, split_rows

ROOT = HERE.parents[2]
SCENARIOS = HERE / "scenarios" / "pilot_scenarios.json"
OUT_DIR = ROOT / "datasets" / "hekat-orchestration-sft" / "data"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("enrichment_jsonl")
    ap.add_argument("--replace-all", action="store_true", help="Rebuild dataset only from enrichment+templates")
    args = ap.parse_args()

    scenarios = {s["id"]: s for s in json.loads(SCENARIOS.read_text(encoding="utf-8"))}
    enrich_path = Path(args.enrichment_jsonl)
    enrichments = []
    with enrich_path.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                enrichments.append(json.loads(line))

    rows = []
    errors = []
    seen = set()
    for en in enrichments:
        sid = en["scenario_id"]
        sc = scenarios.get(sid)
        if not sc:
            errors.append(f"unknown scenario {sid}")
            continue
        nl = en.get("natural_language") or sc["natural_language"]
        dsl = en.get("dsl") or expand_dsl({**sc, "natural_language": nl})
        row, err = pack_record(
            record_id=f"hekat-{sid}-enriched",
            natural_language=nl,
            scenario_category=sc["scenario_category"],
            pattern_type=sc["pattern_type"],
            operators=sc["operators"],
            dsl=dsl,
            pseudocode=en["pseudocode"],
            logic=en["logic"],
            generator_model=en.get("generator_model", "composer-2.5"),
            source="synthetic-composer-2.5",
        )
        if err or not row["artifacts"]["compile_ok"]:
            errors.append(f"{sid}: {err or 'compile_ok false'}")
            continue
        rows.append(row)
        seen.add(sid)

    # Keep template rows for scenarios not enriched
    from template_generator import generate

    for row in generate():
        sid = row["id"].replace("hekat-", "")
        if sid in seen:
            continue
        rows.append(row)

    train, val = split_rows(rows)
    write_jsonl(OUT_DIR / "train.jsonl", train)
    write_jsonl(OUT_DIR / "validation.jsonl", val)
    print(f"enriched={len(enrichments)} kept_total={len(rows)} train={len(train)} val={len(val)}")
    for e in errors:
        print("ERR", e)
    return 0 if rows and not errors else (0 if rows else 1)


if __name__ == "__main__":
    raise SystemExit(main())

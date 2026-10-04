#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../../.." && pwd)"
cd "$ROOT"

echo "== generate (template) =="
python3 tools/sft/build/template_generator.py

echo "== validate =="
python3 tools/sft/build/validate_dataset.py

echo "== blind eval =="
python3 tools/sft/eval/blind_eval.py >/dev/null
python3 -c "import json;d=json.load(open('reports/eval/scorecard.json'));print('validation_mvp_green=', d['splits']['validation']['mvp_green'])"

echo "== adversarial =="
python3 tools/sft/ops/adversarial/attack_suite.py >/dev/null

echo "== monitor =="
python3 tools/sft/ops/monitor/snapshot.py

echo "== lexer golden (root oracle) =="
python3 tools/sft/ops/lexer_golden.py >/dev/null

echo "ALL GATES DONE"

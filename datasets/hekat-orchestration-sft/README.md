---
pretty_name: HEKAT Orchestration SFT
task_categories:
  - text-generation
language:
  - en
license: apache-2.0
size_categories:
  - n<1K
tags:
  - hekat
  - dsl
  - agent-orchestration
  - reasoning
  - sft
  - messages
configs:
  - config_name: sft
    data_files:
      - split: train
        path: data/train.jsonl
      - split: validation
        path: data/validation.jsonl
---

# HEKAT Orchestration SFT

MessagesList fine-tuning dataset for mapping natural-language orchestration intents to **HEKAT DSL**, with dual structured reasoning:

1. `<pseudocode>` — imperative sketch  
2. `<logic>` — coding-construct reasoning  
3. `<answer>` — final DSL + short plan summary  

Sidecar columns include compiler artifacts (DAG, execution plan) for research and filtering. Default TRL training should use the `messages` column only.

## Load

```python
from datasets import load_dataset
ds = load_dataset("json", data_files={
    "train": "data/train.jsonl",
    "validation": "data/validation.jsonl",
})
```

## Intended use
Supervised fine-tuning of chat models for agent orchestration planning (L1–L4 HEKAT patterns).

## Limitations
- Synthetic traces (template + Composer enrichment); early rows can be stylistically repetitive.
- Token budgets are heuristic; not measured billing costs.
- `complexity_level` follows compiler metrics (agent count / depth / parallelism / fallback), not human “task difficulty.” **L2 is sparse** in the pilot.
- L5–L7 research patterns are out of MVP scope.

See `docs/sft/PRODUCT_SPEC.md` in the source repo for the eval contract.

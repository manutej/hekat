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

## Format
Assistant turns always use **dual-track** XML (see `docs/sft/DUAL_REASONING_SPEC.md`):

1. `<pseudocode>` — imperative sketch  
2. `<logic>` — coding-construct re-encoding of the *same* plan (`fn`, constructors, `assert`)  
3. `<answer>` — fenced HEKAT DSL + short summary  

Default TRL training should use the `messages` column only.

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
- Synthetic traces (Composer-enriched); some logic blocks still share constructor skeletons.
- Token budgets are heuristic; not measured billing costs.
- `complexity_level` follows compiler metrics (agent count / depth / parallelism / fallback), not human “task difficulty.” **L2 is sparse**; 3-agent sequential often labels **L4**.
- Two lexers exist in-repo; **root** `hekat_lexer.py` is SFT ground truth. Package lexer (`hekat.compiler.lexer`) is CLI/experimental and may diverge.
- L5–L7 research patterns are out of MVP scope.
- Dual-track `<logic>` style is a soft vocabulary gate until promoted.

See `docs/sft/PRODUCT_SPEC.md` for the eval contract.

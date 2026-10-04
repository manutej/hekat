# Research notes — dual-track reasoning & HF packaging

**Date:** 2026-10-04  
**Purpose:** Cite prior art and record why HEKAT uses dual XML lanes instead of `<think>` alone.

## Hugging Face / TRL (packaging)

- Conversational SFT default: `messages: [{role, content}, …]` ([TRL dataset formats](https://huggingface.co/docs/trl/main/en/dataset_formats)).
- TRL’s own SFT example embeds reasoning **inside assistant content** as `<think>…</think>` then the answer ([SFT Trainer](https://huggingface.co/docs/trl/main/en/sft_trainer)).
- Community Hub datasets variously use `<think>`, `reasoning_content` columns, or Alpaca `output` wrapping. We stay on MessagesList + tags in `content` so Unsloth/TRL/Axolotl work without adapters.
- Dataset cards: YAML tags (`task_categories`, `license`, `size_categories`) + structure/limitations ([dataset card guide](https://huggingface.co/docs/datasets/dataset_card)).

## Structured reasoning families

| Work | Mechanism | Takeaway for HEKAT |
|------|-----------|--------------------|
| Wei et al. 2022 CoT | NL steps | Necessary but insufficient for operator graphs |
| Chen et al. 2023 PoT / Gao et al. 2023 PAL | Generate **runnable** programs; interpreter executes | We generate **non-runnable** logic + **runnable** DSL via HEKAT compiler |
| Li et al. 2024 Chain of Code | Code + LM-emulated semantic functions | Closest cousin; we emulate *planning constructors*, not sarcasm detectors |
| Logic-of-Thought (NAACL 2025) | Propositional expansions in context | Different object language (FOL vs orchestration AST) |
| Highlighted CoT (2025) | XML around facts | XML as **lanes**, not fact IDs |
| Fin-R1-Data / reasoning SFT mixes | Custom XML + format rewards | Confirms tagged traces train well if well-formedness is gated |

## Design choice

Train the model to **re-encode** a plan: imperative list → constructor program → DSL. The second encoding is the “ordered neural” constraint requested for HEKAT (coding constructs inside `<logic>`). Execution/type safety is delegated to `HEKATCompiler`, analogous to PAL’s interpreter split, but the intermediate program is a *thinking format*, not a runtime.

Full contracts: [`DUAL_REASONING_SPEC.md`](DUAL_REASONING_SPEC.md), [`COMPILER_CANONICAL_SPEC.md`](COMPILER_CANONICAL_SPEC.md), [`PRODUCT_SPEC.md`](PRODUCT_SPEC.md).

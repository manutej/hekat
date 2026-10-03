# Architecture Review Pass 1

## Strengths
- Clear firewall: `tools/sft/eval/blind_eval.py` does not import build generators.
- Single compiler ground truth for artifacts.
- MessagesList + sidecar artifacts matches HF/TRL norms.

## Drift / anti-patterns spotted
1. **Template traces are uniform** — logic blocks share near-identical skeletons; risk of model memorizing template rather than planning. Needs Composer-2.5 enrichment diversity.
2. **Root dual-pipeline still exists** (`hekat/compiler/lexer.py` vs root) — out of MVP scope but high long-term drift risk.
3. **Scenario NL is sometimes meta** ("Sequential workflow 3") — weak linguistic diversity; enrich with naturalistic prompts.
4. Do not open PR until Composer enrichment or explicit acceptance of template-quality MVP.

## Verdict
Scaffold architecture is sound for MVP. Blockers for "comprehensively working" are **trace diversity** and **naturalistic NL**, not packing/eval plumbing.

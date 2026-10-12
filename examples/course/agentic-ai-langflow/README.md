# Agentic AI with Langflow — course figures

FigTree-backed SVG pipeline for the **Agentic AI with Langflow** course companion.

| Path | Purpose |
|------|---------|
| [`Agentic_AI_with_Langflow.html`](Agentic_AI_with_Langflow.html) | Full six-module companion (source shell) |
| [`VISUAL-SPEC.md`](VISUAL-SPEC.md) | Course visual acceptance profile |
| [`docs/course/.../COURSE-NARRATIVE-STRATEGY.md`](../../docs/course/agentic-ai-langflow/COURSE-NARRATIVE-STRATEGY.md) | Pursuit bar + dual-rubric strategy |
| [`module-01/`](module-01/) | Module 1 figures, gold references, preview |
| [`examples/figtree/langflow/pursuit/module-01/`](../../figtree/langflow/pursuit/module-01/) | Canonical Pursuit figure bar (01–07) |
| [`scripts/extract_module_figures.py`](scripts/extract_module_figures.py) | Extract `#m1` inventory from HTML |
| [`scripts/compare_gold.py`](scripts/compare_gold.py) | Gold structural compare (`data-component` Jaccard) |

## Learner-facing pipeline (narrative tier)

```bash
python3 examples/course/agentic-ai-langflow/module-01/build_course_narrative.py
```

Ships `module-01/narrative/*.svg` (Pursuit baseline; m1b/m1-capstone pilots try `course-narrative` generate when they beat Pursuit richness). Score lab SVGs against Pursuit: `figtree score ... --reference pursuit/figures/....svg`.

## Lab / generator loop (teaching rubric)

```bash
python3 examples/course/agentic-ai-langflow/module-01/build_figures.py
python3 examples/figtree/langflow/adversarial/run_module_adversarial.py \
  examples/course/agentic-ai-langflow/module-01 \
  docs/course/agentic-ai-langflow/module-01/diagrams \
  --gold examples/course/agentic-ai-langflow/module-01/gold
python3 examples/course/agentic-ai-langflow/module-01/build_module_html.py
python3 examples/course/agentic-ai-langflow/module-01/build_index.py
```

# Agentic AI with Langflow — course figures

FigTree-backed SVG pipeline for the **Agentic AI with Langflow** course companion.

| Path | Purpose |
|------|---------|
| [`Agentic_AI_with_Langflow.html`](Agentic_AI_with_Langflow.html) | Full six-module companion (source shell) |
| [`VISUAL-SPEC.md`](VISUAL-SPEC.md) | Course visual acceptance profile |
| [`module-01/`](module-01/) | Module 1 figures, gold references, preview |
| [`scripts/extract_module_figures.py`](scripts/extract_module_figures.py) | Extract `#m1` inventory from HTML |
| [`scripts/compare_gold.py`](scripts/compare_gold.py) | Gold structural compare (`data-component` Jaccard) |

## One-command Module 1 loop

```bash
python3 examples/course/agentic-ai-langflow/module-01/build_figures.py
python3 examples/figtree/langflow/adversarial/run_module_adversarial.py \
  examples/course/agentic-ai-langflow/module-01 \
  docs/course/agentic-ai-langflow/module-01/diagrams \
  --gold examples/course/agentic-ai-langflow/module-01/gold
python3 examples/course/agentic-ai-langflow/module-01/build_module_html.py
python3 examples/course/agentic-ai-langflow/module-01/build_index.py
```

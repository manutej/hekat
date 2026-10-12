# Langflow agentic workflows — documentation-first FigTree run

This directory is the **documentation-first** reference run: figures are grounded in
[`docs/research/langflow-agentic-workflows/`](../../../docs/research/langflow-agentic-workflows/)
(Langflow official docs, October 2026), not in Figma `.fig` files.

## Artifacts

| File | Description |
|------|-------------|
| [`index.html`](index.html) | Digest gallery (8 teaching figures + skipped list) |
| [`digest.json`](digest.json) | Measured scores per unit |
| [`manifest.json`](manifest.json) | Digest plan (8 units, 2 skipped intro/bibliography) |
| [`icons/sheet.svg`](icons/sheet.svg) | Langflow concept icon family |
| [`research-workflow.refined.svg`](research-workflow.refined.svg) | Refine pass on meta research pipeline (9.09 → 9.23) |

## Regenerate

```bash
python3 -m figtree digest --plan docs/research/langflow-agentic-workflows/ \
  -o examples/figtree/langflow/ --rubric teaching --style teaching
python3 -m figtree digest --all -o examples/figtree/langflow/ --rubric teaching --no-render
```

## Adversarial three-layer pass

See [`adversarial/ITERATION-LOG.md`](adversarial/ITERATION-LOG.md) and
[`adversarial/ADVERSARY-LANGFLOW.md`](adversarial/ADVERSARY-LANGFLOW.md). Re-run:

```bash
python3 examples/figtree/langflow/adversarial/run_three_layer_eval.py
```

After the pass, two figures score **10.0** (single-agent tool loop, multi-tool coordination).

## Quality notes

- All units scored **≥ 8.0** on the `teaching` rubric (measured `figtree score`).
- `figtree judge` (image panel) requires the local `claude` CLI; it was not run in cloud CI.
  Use measured scores in `*.score.json` and optional local judge for faithfulness review.

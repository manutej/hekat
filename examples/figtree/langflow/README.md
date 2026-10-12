# Langflow agentic workflows — documentation-first FigTree run

This directory is the **documentation-first** reference run: figures are grounded in
[`docs/research/langflow-agentic-workflows/`](../../../docs/research/langflow-agentic-workflows/)
(Langflow official docs, October 2026), not in Figma `.fig` files.

## Artifacts

| File | Description |
|------|-------------|
| [`index.html`](index.html) | Digest gallery (SOURCE sections + research meta figures) |
| [`digest.json`](digest.json) | Measured scores per unit |
| [`manifest.json`](manifest.json) | Digest plan (SOURCE H2 units; bibliography skipped) |
| [`icons/sheet.svg`](icons/sheet.svg) | Langflow concept icon family |
| [`research-documentation-pipeline.svg`](research-documentation-pipeline.svg) | Meta pipeline (split from monolithic workflow; **10.0**) |
| [`research-verification-workflow.svg`](research-verification-workflow.svg) | Verification chain (**10.0**) |

## Regenerate

```bash
python3 -m figtree digest --plan docs/research/langflow-agentic-workflows/ \
  -o examples/figtree/langflow/ --rubric teaching --style teaching
python3 -m figtree digest --all -o examples/figtree/langflow/ --rubric teaching --no-render
```

## Module depth

- **Module 01 — flow topology:** [`modules/01-flow-topology/index.html`](modules/01-flow-topology/index.html) (7 diagrams, **10.0** each after compact trim)
- **Module 02 — tool loop:** [`modules/02-single-agent-tool-loop/index.html`](modules/02-single-agent-tool-loop/index.html) (4 diagrams, **10.0**)
- Hub: [`modules/index.html`](modules/index.html)

## Adversarial three-layer pass

See [`adversarial/ITERATION-LOG.md`](adversarial/ITERATION-LOG.md) and
[`adversarial/ADVERSARY-LANGFLOW.md`](adversarial/ADVERSARY-LANGFLOW.md). Re-run:

```bash
python3 examples/figtree/langflow/adversarial/run_three_layer_eval.py
python3 examples/figtree/langflow/adversarial/run_module_adversarial.py examples/figtree/langflow/modules/01-flow-topology
```

Layer 2 applies `figtree refine` then **`compact_trim`** when blank margins remain (leading edges refine cannot auto-shrink).

## Quality notes

- All units scored **≥ 8.0** on the `teaching` rubric (measured `figtree score`).
- `figtree judge` (image panel) requires the local `claude` CLI; it was not run in cloud CI.
  Use measured scores in `*.score.json` and optional local judge for faithfulness review.

# Module 01 — Langflow flow topology

Deep teaching figures for how a Langflow **flow** is wired before tools and MCP.

## Diagram set

| File | Topic |
|------|--------|
| [`diagrams/01-flow-canvas.md`](diagrams/01-flow-canvas.md) | Canvas, components, ports |
| [`diagrams/02-minimal-chat-flow.md`](diagrams/02-minimal-chat-flow.md) | Chat Input → Agent → Chat Output + Language Model |
| [`diagrams/03-model-providers.md`](diagrams/03-model-providers.md) | Model Providers → Agent |
| [`diagrams/06-custom-language-model-port.md`](diagrams/06-custom-language-model-port.md) | Custom LM component port |
| [`diagrams/04-playground-path.md`](diagrams/04-playground-path.md) | Playground run path |
| [`diagrams/05-simple-agent-template.md`](diagrams/05-simple-agent-template.md) | Simple Agent template |

Aggregated narrative: [`SOURCE.md`](SOURCE.md).

## Regenerate figures

```bash
OUT=examples/figtree/langflow/modules/01-flow-topology
for f in docs/research/langflow-agentic-workflows/modules/01-flow-topology/diagrams/*.md; do
  base=$(basename "$f" .md)
  python3 -m figtree generate "$f" -o "$OUT/${base}.svg" --style teaching --icons --shapes --max-aspect 2.4 --no-render
  python3 -m figtree refine "$OUT/${base}.svg" --rubric teaching -o "$OUT/${base}.svg" --source "$f" --rounds 3 --no-render
done
cp "$OUT/02-minimal-chat-flow.svg" "$OUT/overview.svg"
python3 "$OUT/build_index.py"
```

Gallery: [`examples/figtree/langflow/modules/01-flow-topology/index.html`](../../../../examples/figtree/langflow/modules/01-flow-topology/index.html)

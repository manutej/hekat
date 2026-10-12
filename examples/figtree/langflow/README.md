# Agentic workflows in Langflow: a documentation-driven run

The first concept space built from **documentation rather than a paper**, end to end by the
workflows with Sonnet researchers and Haiku checkers (`args.model: 'sonnet', cheap_model: 'haiku'`).

| Stage | What ran | Result |
|---|---|---|
| Corpus | 49 pages from `langflow-ai/langflow` `docs/docs` (`corpus/SOURCES.md`) | 552 KB |
| Research | `figtree-research`: 9 topics, 20 agents, 4.3 min, 1.5 M subagent tokens | 9 specs + overview, all `figtree spec check` ok on the first pass |
| Figures | `figtree digest --all --rubric teaching` over `specs/` | 10 figures, 8.9 to 10.0, no critical issue |
| Icons | `figtree-icon-family`: 8 briefs proposed from the specs, drawn with `--backend claude`, cold-eye reviewed at 16/24/48 px, one repair round | 8 icons (`icons/`), reviewer still below 9.5 on most: see `docs/FAILURE-MODES.md` row 13 |
| Animation | `figtree animate` on the overview | `figures/overview.animated.svg` |
| Page | `figtree page` | `index.html` (191 KB, self-contained) |

## Figures

| id | title | score |
|---|---|---|
| 00-overview | How Langflow agent workflows coordinate | 9.71 |
| a2a-agents | Agents talking to agents over A2A | 9.71 |
| agent-as-tool | A manager agent delegating to other agents | 10.00 |
| agent-with-tools | An agent calling tools | 9.86 |
| human-in-the-loop | Pausing a Flow for a Human | 8.90 |
| loops-and-routing | Branching, looping and sub-flows inside a flow | 10.00 |
| mcp-client | An agent using an MCP server's tools | 9.86 |
| mcp-server | Flows exposed as tools to MCP clients | 9.19 |
| memory-and-sessions | Conversation memory across turns and sessions | 9.86 |
| run-flow-api | Running a Flow from an Application through the API | 9.86 |

## What this run changed in the method

Five failure modes appeared and were folded back (`docs/FAILURE-MODES.md` rows 1-11): arrows
through blocks and labels (now routed around with a halo and a grid router), fan-in arrows
sharing a shaft, prose mentions drawn as components (spec mode), a component named "Loop"
swallowed as a loop marker, specs split into section figures, independent mechanisms tangled in
one layer stack (now separate sub-figures), an agent's tools chunked into the chain (now a
satellite group), and actor silhouettes colliding with their labels.

## Reproduce

```bash
Workflow({ name: 'figtree-research', args: { corpus_dir: 'examples/figtree/langflow/corpus', out_dir: 'examples/figtree/langflow/specs', model: 'sonnet', cheap_model: 'haiku', max_topics: 9 } })
python -m figtree digest --plan examples/figtree/langflow/specs -o examples/figtree/langflow/figures --rubric teaching
python -m figtree digest --all -o examples/figtree/langflow/figures --rubric teaching
python -m figtree animate examples/figtree/langflow/figures/00-overview.svg -o examples/figtree/langflow/figures/overview.animated.svg --css examples/figtree/langflow/figures/overview.animation.css
python -m figtree page --title "Agentic workflows in Langflow" --specs examples/figtree/langflow/specs --digest examples/figtree/langflow/figures/digest.json --icons-dir examples/figtree/langflow/icons --sheet examples/figtree/langflow/icons/sheet.svg --animated examples/figtree/langflow/figures/overview.animated.svg -o examples/figtree/langflow/index.html
```

Or the whole chain: `Workflow({ scriptPath: '.claude/workflows/figtree-pipeline.js', args: { title, corpus_dir, out_dir, model: 'sonnet', cheap_model: 'haiku' } })`.

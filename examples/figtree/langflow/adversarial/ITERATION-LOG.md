# Three-layer adversarial iteration (Langflow teaching figures)

Process follows `.claude/skills/figtree-process/SKILL.md` §4 (adversarial improve) and the
`figtree-adversary` / `figtree-refine` workflow contract in `docs/workflows/README.md`.

| Layer | Team role | Action | Output |
|-------|-----------|--------|--------|
| **1 — Attack** | Adversary scorers | `figtree score --source` on each production SVG; log issues as probe briefs | `layer1-attack.json`, `probes/langflow-teaching/*.json` |
| **2 — Repair** | Refine workers | `figtree refine --rounds 3 --no-render` per figure | `*.layer2.svg`, `*.layer2.trajectory.json` |
| **3 — Verify** | Orchestrator | Re-score, promote winners into parent `*.svg`, global `figtree eval` | `three-layer-summary.json`, updated gallery |

## Score delta (overall, teaching rubric)

| Unit | Layer 1 | Layer 3 (promoted) |
|------|---------|---------------------|
| research-workflow | 9.09 | 9.23 |
| source--langflow-flow-topology | 9.71 | 9.86 |
| source--single-agent-tool-loop | 9.86 | 10.00 |
| source--agent-memory-and-session-scope | 9.71 | 9.86 |
| source--mcp-client-pattern | 9.71 | 9.86 |
| source--mcp-server-pattern-flows-as-tools | 9.71 | 9.86 |
| source--multi-tool-agent-coordination | 9.86 | 10.00 |
| source--api-and-programmatic-execution | 9.71 | 9.86 |

## Open items (judge / content)

- `research-workflow`: `flow.crossings` still flagged after layer 2 (content routing decision; see trajectory requests).
- Global teaching probe suite: recall/precision remain 1.0 / 1.0 (`teaching-eval-layer3.json`).

## Re-run

```bash
python3 examples/figtree/langflow/adversarial/run_three_layer_eval.py
```

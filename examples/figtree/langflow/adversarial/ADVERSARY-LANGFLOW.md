# Adversary report: Langflow production figures (teaching rubric)

**Scope:** SVGs under `examples/figtree/langflow/` grounded in Langflow documentation sources.

**Method:** Layer 1 treated each shipped figure as an adversary target (not synthetic probes).
Issues were recorded as regression briefs in `probes/langflow-teaching/` for future fold if the
critic misses them on similar layouts.

## Layer 1 findings (attack)

| unit | overall | dominant checks | cold-eye note |
|------|---------|-----------------|---------------|
| research-workflow | 9.09 | `compactness.blank_margin`, `flow.crossings` | Meta pipeline readable; two arrow crossings remain |
| source--single-agent-tool-loop | 9.86 | `compactness.blank_margin` | Dense tool fan-in; fixed in layer 2 |
| source--mcp-client-pattern | 9.71 | `compactness.blank_margin` | MCP chain clear after canvas tighten |
| others | 9.71–9.86 | mostly blank margin | Auto `set_canvas` edits applied in layer 2 |

No new **gaming** holes were found on Langflow figures (scores were not falsely inflated to 10.0
with visible defects). Remaining gaps are **compactness** (mechanical) and **crossings** on the
research meta-diagram (needs layout decision).

## Layer 2–3 (repair + verify)

Refine workers ran up to **3 rounds**; most units converged in **1 round** via `set_canvas`.
Two tool-loop figures reached **10.0** measured overall.

## Eval (global teaching probes)

```
Layer 0: 53 probes, recall 1.0, precision 1.0  (teaching-eval-layer0.json)
Layer 3: 53 probes, recall 1.0, precision 1.0  (teaching-eval-layer3.json)
```

Langflow-specific JSON briefs do not add SVG probes yet; they document production regressions
until a fold worker adds SVG counterparts.

# Module 1 ASCII topology evaluation

Secondary check: arrow chains in diagram briefs vs blocks in SVG (`data-component`).

| Figure | ASCII intent (summary) | Completeness | Notes |
|--------|------------------------|--------------|-------|
| m1a | Two rows: script chain + agent chain | All brief components present | Simpler than gold panel art; no member quote bubbles |
| m1b | Chat → Prompt → Model → Output; KB → Prompt | **5/5** | Regenerated linear layout; gold had inline example text |
| m1c | Browser → Portal → Langflow → Provider | **4/4** | Key badges omitted vs gold; topology intact |
| m1d | Four beats left-to-right | **5/5** | Numbered beats in gold collapsed to named steps |
| m1e | Three quality checks | **6/6** | Labels match brief (not gold card titles) |
| m1-capstone | FAQ chain + KB side feed | **5/5** | Topology matches reading order; less vertical KB branch art |

**Root cause of “cut off” SVGs:** `compact_trim` had shrunk the canvas while content used negative `translate`, and `refine` sometimes **deleted** terminal blocks (Chat Input/Output) chasing margin score. Pipeline now: **generate → optional guarded refine → safe trim that expands canvas to fit bbox**.

Run audit: `python3 examples/course/agentic-ai-langflow/scripts/figure_ascii_audit.py`

**ASCII secondary check (2025-10):** all six figures pass component set + canvas bbox (no clip, teaching margin). Example capstone:

```
Primary chain(s):
  [Chat Input]  ->  [Prompt Template]  ->  [Chat Model]  ->  [Chat Output]
Side feeds:
  [Knowledge Base] --> [Prompt Template]
```

**Scoring fix:** `topology.empty_container` no longer treats terminal `path` blocks as empty groups, so refine/trim does not delete Chat Input/Output wrappers.

Gold SVGs remain under `gold/` for visual richness regression; production SVGs prioritize **complete topology** and **no clipping**. Regenerated figures score **10.0** on topology but are still **compact** (~170px tall) versus gold **panel** art (~470px with inline example text).

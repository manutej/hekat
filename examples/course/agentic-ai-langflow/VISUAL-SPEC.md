# Course visual artifact profile

Figures for **Agentic AI with Langflow** use FigTree addressable SVG programs embedded in `.sheet` wrappers on the course page.

**Quality bar:** Pursuit course figures (`examples/figtree/langflow/pursuit/module-01/figures/`). See [PURSUIT-VISUAL-BAR.md](../../../docs/course/agentic-ai-langflow/PURSUIT-VISUAL-BAR.md). Lab SVGs from `build_figures.py` are topology/score harnesses—not the learner-facing target.

## Typography and shell

- In-figure font: **IBM Plex Sans** (matches `data-figtree` output).
- Page chrome: Fraunces + Source Sans 3 (HTML shell only; do not bake into FigTree briefs).

## Semantic fills (from gold Module 1)

| Role | Fill | Use |
|------|------|-----|
| Terminal / chat | `#E6E8EC` | Chat Input, Chat Output, member/student |
| Process | `#C9DCF0` | Langflow steps, model, portal |
| Decision | `#F3C9A4` | Reads, decides |
| Store | `#F6EFD2` | Knowledge Base |
| Panel | `#F8F9FB` | Nested containers |

## Accessibility

Each figure must include:

- `role="img"` on root SVG (injected at HTML assembly if missing)
- `<title>` and `<desc>` with stable ids referenced by `aria-labelledby`
- Figcaption text duplicated in [`module-01/manifest.json`](module-01/manifest.json)

## Acceptance gates

1. **Measured:** `figtree score --rubric teaching --source <diagram.md>` → overall **≥ 9.86**, target **10.0**.
2. **Adversarial:** `run_module_adversarial.py` layer 3 → **0 issues** per figure.
3. **Structural gold:** `compare_gold.py` → `data-component` set from PORT comments matches gold SVG (Jaccard **1.0** for capstone and hub figures; narrative panels may omit strict match for `m1a`/`m1e` if brief is checklist-only — see manifest `kind`).

## Adversarial loop

```bash
python3 examples/course/agentic-ai-langflow/module-01/build_figures.py
python3 examples/figtree/langflow/adversarial/run_module_adversarial.py \
  examples/course/agentic-ai-langflow/module-01 \
  docs/course/agentic-ai-langflow/module-01/diagrams \
  --gold examples/course/agentic-ai-langflow/module-01/gold
```

Layer 2 order: `figtree refine` (3 rounds) → `compact_trim` if `compactness.blank_margin` remains.

When refine plateaus on multi-panel layout, use `figtree refine ... --request "<figcaption + fix_instruction>"` (layer 2b).

## Regenerate from brief (optional)

Gold SVGs are the quality bar. To attempt regeneration from markdown:

```bash
python3 -m figtree generate docs/course/.../diagrams/m1-capstone.md \
  -o examples/course/.../module-01/m1-capstone.svg \
  --style teaching --icons --shapes --no-render
```

Prefer gold-backed production when regeneration loses pedagogical detail.

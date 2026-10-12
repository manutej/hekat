# Pursuit visual bar (Module 1)

The **Pursuit** figures under [`examples/figtree/langflow/pursuit/module-01/figures/`](../../../examples/figtree/langflow/pursuit/module-01/figures/) are the **canonical quality bar** for this course: multi-panel layouts, inline member quotes, section titles, and iconography—not compact “workflow block” diagrams.

## Three tiers (do not conflate them)

| Tier | Location | Role |
|------|----------|------|
| **Pursuit** | `examples/figtree/langflow/pursuit/module-01/figures/0*.svg` | Target **course art**; what learners should see in the companion. |
| **Gold** | `examples/course/.../module-01/gold/` | HTML-extracted reference (usually matches Pursuit once synced). |
| **Production (lab)** | `examples/course/.../module-01/m*.svg` | FigTree **`generate --style teaching`** output: topology-complete, score-friendly, **~12 labels max** per rubric—good for pipelines, **not** the visual end state. |

Module 1 work on PR #6 prioritized **topology correctness** (ASCII audit, trim/refine guards) on the **production/lab** tier. It did **not** yet promote Pursuit figures into preview by default or extend FigTree scoring for narrative richness.

## File mapping (your local paths → repo)

| Pursuit file | Course figure |
|--------------|---------------|
| `01-six-module-journey.svg` | Course hero (six modules) |
| `02-script-or-agent.svg` | `m1a` |
| `03-four-parts-real-contents.svg` | `m1b` |
| `04-where-the-key-lives.svg` | `m1c` |
| `05-one-question-four-beats.svg` | `m1d` |
| `06-what-a-good-answer-looks-like.svg` | `m1e` |
| `07-capstone-member-benefits-faq.svg` | `m1-capstone` |

Seed from current gold + hero (until you copy newer Pursuit exports from your machine):

```bash
python3 examples/course/agentic-ai-langflow/scripts/seed_pursuit_figures.py
```

Replace files under `pursuit/module-01/figures/` with your courseware copies when they diverge.

## FigTree vision beyond “scientific / Mermaid” diagrams

Default **`teaching`** rubric (`figtree/rubrics.py`) optimizes **one idea, strong reading order, ≤~12 labelled elements, 8-word labels**—which naturally produces Langflow-style block flows (what you called scientific/Mermaid-like).

Pursuit art needs a different profile, for example **`course-narrative`** (proposed):

- Multiple nested panels and `data-kind="annot"` example text grounded in the brief
- Higher element budget and taller canvas (400–500px class)
- Score **semantic coverage** and **annotation fidelity** against Pursuit/gold, not just arrow topology
- Adversarial loop: **refine toward Pursuit diff** (text nodes, panel count, fill roles) while keeping editability

**ASCII topology audit** remains the hard gate for *missing components*; **Pursuit compare** becomes the gate for *visual comprehensiveness*.

## Preview

```bash
python3 examples/course/agentic-ai-langflow/scripts/seed_pursuit_figures.py
python3 examples/course/agentic-ai-langflow/module-01/build_module_html.py --tier pursuit
```

Lab regeneration (compact SVGs) is unchanged:

```bash
python3 examples/course/agentic-ai-langflow/module-01/build_figures.py
```

## Strategy and orchestration

End-to-end course pipeline: [COURSE-NARRATIVE-STRATEGY.md](./COURSE-NARRATIVE-STRATEGY.md).

```bash
python3 examples/course/agentic-ai-langflow/module-01/build_course_narrative.py
python3 examples/course/agentic-ai-langflow/scripts/run_course_narrative_gate.py
```

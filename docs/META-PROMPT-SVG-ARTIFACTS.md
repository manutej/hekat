# Meta-prompt: iterative construction of editable SVG artifacts

Assumption stated up front: the category is wider than methodology figures. It covers every
artifact that is a *program whose rendering a reader judges*: static diagrams, data figures,
slides, dashboard tiles, icons, and animated explainers. What varies per instance is the
source, the medium and the motion grammar; what stays fixed is the loop: ground → construct
recursively → render → critique in two spaces → edit locally → score → repeat until stable.

## 1. Category

**Editable-SVG artifact synthesis under a rubric.** Instances differ in `Source` (a paper, a
skill, a dataset, a concept, an icon brief), `Medium` (paper figure, teaching diagram, slide,
chart, tile, icon, explainer) and `Motion` (none, reveal, draw, pulse, morph, motion path).
Invariant: the output is an addressable program (every element has an id), the critic sees
both the code and the rendering, every change is a local edit script, and quality is a
per-dimension 1-10 score with anchors.

## 2. Typed slots

```
Source:            str | file                   # what the artifact must be faithful to
Medium:            enum{paper, teaching, slide, data-figure, dashboard, icon, explainer}
Rubric:            Rubric(Medium)                # thresholds + the 8 dimensions
Vocabulary:        set[ElementKind]             # block, store, document, decision, terminal, actor, icon, axis, mark
IconFamily:        {grid: 24, stroke: 2, caps: round, max_strokes: 12, safe_margin: 2}
MotionGrammar:     list[enum{reveal, draw, pulse, morph, motion_path}]  # each tied to a meaning
ContentPlan:       {claim, components[name, evidence_span], flows[from, to, type, evidence_span], inputs, outputs, notation}
LayoutTree:        Node(L_v, C_v, Π_v, D_v, S) with 2-4 children per split, depth ≤ 8, nodes ≤ 32
Program:           SVG with ids, PORT comments, data-role / data-flow / data-bbox attributes
Render:            PNG (or "no-vision")
CriticReport:      list[Issue{dimension, severity, visual_description, code_anchor, fix_instruction, auto_edit?}]
EditScript:        list[Op{set_attr | set_text | translate | recolor | delete | insert | scale_font | set_canvas | center_content}]
Trajectory:        list[Round{round, overall, scores, issues, edits_applied, diff_elements}]
Convergence:       {no_edits_left | plateau(k=2) | budget} and requests_remaining for a human
```

## 3. Procedure

1. **Ground.** Extract `ContentPlan` from `Source` admitting only evidenced elements; every
   component and flow carries a verbatim `evidence_span`; contradictions and unknown endpoints
   are omitted and logged, never invented. An icon brief grounds to a metaphor and a family.
2. **Choose vocabulary and motion.** Map each component to an `ElementKind` and an icon by its
   role; choose each `MotionGrammar` entry only when it carries meaning (a token travelling a
   flow shows what moves; a draw-on shows construction order; a morph shows a transition the
   reader can name). Decoration is refused.
3. **Construct recursively.** Draw atomic nodes; decompose the rest into 2-4 semantic children,
   one level at a time; merge children with parent-owned connections through exported ports;
   keep every marker-ended arrow's final segment ≥ 20 px by moving targets, not endpoints;
   fold wide layouts into rows to respect the medium's aspect.
4. **Critique in two spaces.** Render; check the code against the rubric (grid, strokes,
   fonts, contrast, palette, overflow, overlap, crossings, detours, margins, coverage) and the
   image when available; anchor every issue to an element id with a fix instruction.
5. **Edit locally.** Apply mechanical fixes as an `EditScript`; hand content decisions back as
   requests; measure the element diff of each round so editability stays verifiable.
6. **Score and loop.** Score 1-10 per dimension (a critical defect caps a dimension at 5);
   repeat 4-5 until `Convergence`; keep the `Trajectory` as the record.
7. **Promote.** Accepted icons join `IconFamily`; accepted rules join the verification memory
   `(condition, repair)`; an accepted figure becomes the input of the next medium (figure →
   animated explainer → slide).

## 4. Binding rules

- `ContentPlan` is immutable downstream; layout, motion and edits never add a component.
- `Program` ids are stable across rounds; an `EditScript` addresses only existing ids or
  inserts under an existing parent.
- `MotionGrammar` entries bind to flow types: data → pulse, control → slower dimmer pulse,
  construction order → reveal/draw. Reduced-motion users get the final state.
- A dimension without evidence (no source, no plan) is reported as not assessed, not as 10.
- Output contract: `{program: svg, report: CriticReport, trajectory: Trajectory, requests: list[Issue]}`
  plus `{editability: {passed, diff_element_count}}` on any local edit.

## 5. Rendered meta-prompt

```xml
<system>
  You construct editable SVG artifacts for a stated medium under a rubric. You never invent
  content beyond the source; you draw mechanism, not names; you animate only meaning. You work
  as a loop: ground, construct recursively, render, critique in code and image, edit locally,
  score, repeat until stable. Every element you emit has an id; every issue you raise has an
  anchor and a fix; every change you make is an edit script.
</system>
<syntax>
  <source>…</source> <medium>…</medium> <motion>…</motion>
  <content_plan>components[name, evidence_span] flows[from, to, type, evidence_span] inputs outputs notation</content_plan>
  <program>svg with ids, ports, data-role, data-flow</program>
  <report>issues[dimension, severity, visual_description, code_anchor, fix_instruction, auto_edit?] scores[8×1-10]</report>
  <edit_script>ops[…]</edit_script>
  <trajectory>rounds[…]</trajectory>
  <requests>issues needing a decision</requests>
</syntax>
```

## 6. Recursive refinement log (three passes)

- **Pass 1 critique:** the draft covered figures only; icons and animated explainers had no
  slots. *Edit script:* add `IconFamily`, `MotionGrammar`, step 2 and the promotion rule.
- **Pass 2 critique:** "animate" was unbound (decoration risk); unassessed dimensions inflated
  scores. *Edit script:* bind motion entries to flow types; add the not-assessed rule.
- **Pass 3 critique:** fixed-canvas media (slides, tiles, icons) were shrunk by the compactness
  rule. *Edit script:* `center_content` for fixed canvases; `set_canvas` only for free canvases.
  Pass 4 returned an empty edit script.

## 7. Where it is implemented

`figtree/` realises each slot: `grounder.py` (1), `elements.py` + `icons.py` + `animate.py`
(2), `generator.py` + `worker.py` (3), `critic.py` + `quality.py` + `rubrics.py` (4),
`edits.py` (5), `refine.py` (6), `iconsmith.py` + `memory.py` (7). The Claude-backed agents
(`figtree/agents/`) run on this session's OAuth through the `claude` CLI or on an API key.

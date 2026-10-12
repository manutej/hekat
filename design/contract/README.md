# The FigureProgram contract (generative UI)

A FigTree figure is a *program whose rendering a reader judges*. The contract separates the
program from the design so the design can be swapped without touching the pipeline:

```
source ──ground──▶ ContentPlan ──construct──▶ FigureProgram ──design──▶ SVG / React / anything
                                               ▲                          │
                                               └── edit script ◀── critic ─┘ (issues anchored to ids)
```

`figure-program.schema.json` is the single source of truth. It has three mirrors that must stay
in step (a test fails when the Python side drifts; regenerate the TypeScript types by hand from
the schema when it changes):

| Side | File | What it gives you |
|---|---|---|
| Schema | `design/contract/figure-program.schema.json` | JSON Schema 2020-12: `canvas`, `containers[]`, `nodes[]`, `flows[]`, `ports[]`, `caption`, `residuals[]`, `meta` |
| Python | `figtree/contract.py` | `program_from_svg(svg)` lifts any FigTree SVG into a program; `validate_program(p)` (schema + referential checks); `render_program(p, renderer)` with the `Renderer` protocol and the reference `HouseRenderer(preset)`; CLI `python -m figtree contract export|validate|render` |
| TypeScript | `design/figtree-ds/src/contract.ts`, `renderProgram.tsx` | the same types (`FigureProgram`, `ProgramNode`, …), `validateProgram`, the `DesignAdapter` interface, the `houseAdapter` built from the six components, `renderProgram(program, adapter)` and `<ProgramView>` |

## What a program contains

- **Design-free geometry.** Every node and container has an `id` and a `bbox` in canvas
  coordinates; every flow is a right-angle polyline whose last segment is the arrow shaft. The
  worker already solved layout (grid, 20 px shafts, row wrapping); a design does not re-layout.
- **Meaning, not looks.** Nodes carry `kind` (block, store, document, decision, terminal, actor,
  process), `tone` (attention, processing, residual, input) and an `icon` *name*; flows carry
  `type` (data, control, conditional, feedback). A design decides what a tone or a type looks
  like. The motion grammar binds to `type` too (data pulses, control pulses slower and dimmer).
- **Stable ids.** The critic anchors issues to ids (`n6.label`, `n4.arrow0`) and edit scripts
  address ids. A design must emit the program's ids on the elements it draws (`<id>`,
  `<id>.block`, `<id>.label`, `<id>.icon`) so the loop keeps working after the swap.
- **Provenance.** `evidence_span` per node and flow (from the content plan), `residuals` the
  critic left for a human, `meta` for scores and trajectories.

## Swapping the design

Python: subclass or re-implement `Renderer` (`begin`, `container`, `node`, `flow`, `end`) and
pass it to `render_program`. The test `tests/test_figtree_contract.py::test_design_swap_changes_only_rendering`
shows a two-method swap.

React: implement `DesignAdapter` (`figure`, `container`, `node`, `flow`, optional `caption`) or
spread `houseAdapter` and override one method, then `<ProgramView program={p} adapter={mine} />`.
The design-system preview `ProgramView` (`.design-sync/previews/ProgramView.tsx`) shows the house
design, the paper preset and a swapped adapter rendering the same program.

The critic does not care which design drew the SVG: `python -m figtree score out.svg --rubric
teaching` scores a swapped design against the same rubric, so a design change is itself a
candidate to run through the refine loop.

## Example

`examples/figtree-loop.program.json` was exported from the figure the `figtree-refine` workflow
drove from 9.19 to 10.0 (`examples/figtree/design/workflow-refine/`):

```bash
python -m figtree contract export examples/figtree/design/workflow-refine/figtree-spec.teaching.refined.svg -o loop.program.json --title "FigTree loop"
python -m figtree contract validate loop.program.json
python -m figtree contract render loop.program.json -o loop.paper.svg --preset paper
python -m figtree score loop.paper.svg --rubric methodology
```

## Versioning

`version` is `1`. Add optional fields freely (designs ignore what they do not know); a required
field or a renamed enum bumps the version, and both `validate_program` and `validateProgram`
must reject the other version explicitly.

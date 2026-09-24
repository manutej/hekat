# JEV × HEKAT — Orchestration Classification Mapping

> How the JEV double-operadic type system plugs into HEKAT to turn a static
> orchestration *planner* into a runtime orchestration *classifier + gate*:
> classify elements into the HEKAT domain language, gate compositions
> fail-closed, run a tree of JEV workers on a durable tape, and use the verdict
> to evaluate agent outputs and direct triage.

Status legend: ✅ built in this repo · 🟡 designed, needs a private repo / API · 🔒 blocked on access

---

## 1. The JEV ecosystem (what was loaded)

Discovered under `manutej` via GitHub search. Access from this session:

| Repo | Lang | Role | Access |
|---|---|---|---|
| **`jev`** | TS + Rust | Double operadic type system (Libkind–Myers, arXiv:2505.18329). Colored operads, `γ` composition, fail-closed gate | ✅ public, cloned |
| **`jev-tape`** | TS | Durable execution — "TypeSafe qualifies, Temporal records" | 🔒 private |
| **`JEV-works`** | TS | Evaluation lab — pre-registered holdouts, blind corpora, operadic claim gates | 🔒 private |
| **`jev-domain`** | Rust | Typed work runtime — closed Item/Command/Clarification ADT | 🔒 private |
| **`jev-playground`** | JS | "Jev secretary" — Jev triages; code gates; LLM only when asked | 🔒 private |
| **`volumetric-intelligence`** | HTML | Jev-as-typed-gate + Temporal-as-durable-tape reference mesh | ✅ public, cloned |
| **`jev-tape-wiki` / `-review`** | HTML | jev-tape docs (30-page wiki; only README committed) | ✅ public (stub) |

The four private repos (`jev-tape`, `JEV-works`, `jev-domain`, `jev-playground`) are
**blocked**: the Claude GitHub App is not installed for them. To unblock, install it at
`github.com/apps/claude/installations/select_target` for those repos. Their *public
mirrors* (`volumetric-intelligence`, the wiki) plus the `jev` core were enough to
recover the full contract, so the bridge below is built against verified source.

---

## 2. JEV kernel primer (verified against `manutej/jev@356c112`)

**Five interface colors** (`src/lib/jev/colors.ts:3`) — the "domain language" elements
get classified into. Order is load-bearing (`entity=0 … action=4`, crosses the WASM boundary):

| Color | short | meaning |
|---|---|---|
| `entity` | E | Named things: places, tables, people, tokens |
| `concept` | C | Interfaces, doctrines, types, modules |
| `idea` | I | Hypotheses, claims, theories |
| `evidence` | V | Queries, counts, extents, OCR, catalogs |
| `action` | A | Publish, compose, drop, grant, schedule |

**Three primitives** (`typesafe/contract.ts:18`): `noul` (a `[0,1]` truth value),
`choice` (categorical + probabilities + confidence), `score` (2–10 ordered levels).

**`γ` composition** (`operad.ts:102`, `checkPort:56`): a child plugs into a parent
port **only when the child's output color equals the port's expected input color** —
"composition γ is defined only when colors match — that is type safety." Mismatch →
`{kind:"color-mismatch"}`.

**Fail-closed shipping gate** (`score.ts:43`, `scoreFill`): a color distribution +
an `allowed` set + a `forbidden` set → a verdict, with thresholds
**τ_green=0.72, τ_toxin=0.12, τ_red=0.4**:
- `toxinMass > τ_t` → **RED** (fail closed)
- `allowedMass < τ_r` → **RED**
- `allowedMass ≥ τ_g` and `toxinMass ≤ τ_t` → **GREEN**
- else → **AMBER** ("needs more evidence")
- non-GREEN ⇒ "Fail closed — composition does not ship."

**16 typed seats** (`seats.ts`) classify one element per JEV call (colorist,
primitive-picker, adversary, fail-closed-gate, judge, temporal-steward, …).
**Triage vocabulary** (`eval/depth4.ts`, judge seat): `compose | escalate | refuse`.

**Durable tape** (`temporal.ts`): event-sourced, replayable run
(`WorkflowStarted → SlotSelected → CompositionAttempted → VerdictRecorded → WorkflowCompleted`).
The kernel is **pure/effect-free**; the real durable runtime is `jev-tape` (Temporal).

---

## 3. Entry-point map: where JEV plugs into the HEKAT pipeline

HEKAT's pipeline is `Lexer → Parser → TypeChecker → DAGBuilder → Compiler → (runtime)`.
Each stage gets a JEV entry point:

| HEKAT stage | JEV entry point | What it does | Status |
|---|---|---|---|
| **Lexer** (`hekat_lexer.py`) | `~` TILDE token | Introduces the color-port modifier | ✅ |
| **Parser** (`hekat_parser.py`) | `~color` on `SimpleNode`/`SkilledNode` (`port` field) | Attaches an explicit JEV color to an element | ✅ |
| **TypeChecker** (`hekat_type_checker.py`) | `JEV_COLORS` validation | Rejects non-JEV colors; agents/skills unchanged | ✅ |
| **DAGBuilder** (`hekat_dag_builder.py`) | node = operad slot; edge = `γ` candidate | DAG is already the operadic forest | ✅ (reused) |
| **Compiler / classify** (`hekat_jev.py`) | `classify_orchestration` | Colors nodes, `γ`-gates edges, `scoreFill` verdict, triage, tape | ✅ |
| **Runtime** | tree of `jev-tape` Temporal workers | Each phase = worker; gate qualifies; Temporal records | 🟡 |
| **Eval** | `JEV-works` claim gates | Score agent outputs against blind corpora | 🟡 |

---

## 4. The `~color` classification modifier ✅

New, additive DSL operator (constitutionally the sanctioned extension path —
"extensions only via new operators"). Fully backward compatible: `port` defaults to
`None`, all 59 existing tests pass.

```hekat
# classify each element into the JEV domain language, inline:
deep-researcher~evidence -> api-architect~concept -> practical-programmer~action : "ship API"

# skilled agents can carry a port too:
api-architect + fastapi + postgresql ~ concept : "design user service"
```

Precedence for a node's color (`hekat_jev.classify_expr_color`):
`~color` modifier  >  `AGENT_COLOR_LEXICON`  >  node-kind default  >  `concept`.
There is also a free-text `classify_local(prompt)` bag-of-words classifier ported from
`jev/lexicon.ts` for prompts with no explicit color.

---

## 5. Classify + gate a whole orchestration ✅

`hekat_jev.classify_orchestration(query, dag, allowed, forbidden, τ)` →
per-node colors, `γ` edge gates, a fail-closed `JevScore`, a triage branch, and a
durable tape. Run `python3 jev_classify_demo.py`. Representative results:

```
deep-researcher -> api-architect -> practical-programmer -> test-engineer : "ship a REST API"
  classified : deep-researcher[V] api-architect[C] practical-programmer[A] test-engineer[V]
  γ ✗ deep-researcher(evidence) → api-architect(concept): color-mismatch — insert a bridge agent
  VERDICT: AMBER → ESCALATE      (a color-mismatch seam blocks GREEN)

mercurio-orchestrator -> project-orchestrator : "brainstorm a strategy"
  classified : [I] [I]   → all idea, nothing grounded
  VERDICT: RED → REFUSE          (allowed mass 0.00 < τ_r; fail closed)

deep-researcher -> debug-detective -> deployment-orchestrator : "audit only, no changes"
  policy: forbid {action}
  VERDICT: RED → REFUSE          (deployment is an action; toxin 0.33 > τ_t; fail closed)
```

Two useful, distinct signals fall out:
1. **Edge seams** — `γ` finds where a producer's color does not plug into the
   consumer (e.g. `evidence → concept`), i.e. where an orchestration needs an adapter
   step. A seam downgrades GREEN → AMBER.
2. **Policy gating** — mark a color `forbidden` to assert a constraint that
   **fails closed** (e.g. "this pipeline must not act" → any `action` node ⇒ RED).

The `ACCEPTS` matrix and `allowed`/`forbidden` sets are tunable policy, not canon.

---

## 6. Tree of JEV workers on a durable tape 🟡

`jev-tape` ("TypeSafe qualifies, Temporal records") is the durable runtime; it's
private, so `hekat_jev.Tape` models the event log **in-process** (a faithful port of
`temporal.ts`) and proves the contract. The mapping to the real runtime:

```
HEKAT DAG                         jev-tape (Temporal)
─────────                         ───────────────────
parallel_phases[k]        ─▶      one worker cohort per phase (fan-out, ≤ concurrency cap)
DAG node (agent)          ─▶      one Activity = one agent run + one 16-seat JEV fill
edge (dep → node)         ─▶      γ check gates the hand-off before the child Activity
scoreFill verdict         ─▶      VerdictRecorded event; GREEN qualifies the composition
triage (compose/…/refuse) ─▶      Workflow decision: proceed / signal human / take `?` branch
event log                 ─▶      Temporal event history (replayable, durable)
```

So a HEKAT query compiles to a **tree of gated Temporal workers**: each agent output
is qualified by a JEV fill, only GREEN hand-offs proceed, and the whole run is a
replayable tape. Wiring needs `jev-tape` + a `TYPESAFE_API_KEY` (Vercel env only,
never client-side — see `volumetric-intelligence/README`).

---

## 7. Runtime usefulness: evaluating outputs & directing triage 🟡→✅

This is the "make HEKAT functionally useful at scale at runtime" piece. The loop:

1. An agent (DAG node) produces output.
2. JEV classifies it — locally (`classify_local`) now ✅, or via the 16-seat
   TypeSafe fill for a calibrated `noul/choice/score` 🟡.
3. `scoreFill` returns GREEN / AMBER / RED. **Triage:**
   - **GREEN → `compose`**: accept the output, proceed to the next phase.
   - **AMBER → `escalate`**: mid-band / a seam — request clarification or a human
     verdict (`volumetric-intelligence /api/signal`), do not ship.
   - **RED → `refuse`**: fail closed — reject and **re-route via HEKAT's `?`
     fallback operator** (the existing `FallbackNode` is the natural retry path).

The three-way verdict is exactly HEKAT's existing control structure: `→` is the
GREEN happy path, `?` is the RED re-route, and AMBER is the human-in-the-loop seam.
JEV supplies the *decision*; HEKAT supplies the *plan*.

---

## 8. What's built vs. blocked

**Built (this repo, tested):**
- `~color` modifier: lexer `TILDE`, parser `port` field, type-checker validation
- `hekat_jev.py`: colors, `scoreFill`/τ, `γ` edge gate, agent lexicon + `classify_local`,
  `classify_orchestration`, triage, in-process Temporal tape
- `jev_classify_demo.py`, `test_hekat_jev.py` (20 tests, all pass; 59 existing pass)

**Blocked on access (🔒):** live durable execution (`jev-tape`), calibrated fills and
eval (`JEV-works`, TypeSafe API key), the typed work ADT (`jev-domain`). Install the
Claude GitHub App for those repos to proceed.

## 9. Next steps
1. Grant repo access → clone `jev-tape` + `JEV-works`; replace `hekat_jev.Tape` with a
   real Temporal worker tree and `classify_local` with the 16-seat TypeSafe fill.
2. Tune the `ACCEPTS` matrix and per-domain `allowed`/`forbidden` policies against
   `JEV-works` blind corpora (measure with `brier`, already ported).
3. Emit a `jev-tape` workflow script directly from a HEKAT DAG (codegen target),
   closing the loop from DSL → gated durable run.

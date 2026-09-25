# HANDOFF — HEKAT × JEV integration

> Read this first to resume cold in a new session. The container is ephemeral;
> this branch is the memory. Everything below reflects the repo as pushed.

- **Repo:** `manutej/hekat`  ·  **Default branch:** `master`
- **Work branch:** `claude/hekat-jev-integration` (new; the previous
  `claude/hekat-agentic-orchestration-mapping-3euDo` was merged as PR #2)
- **Review dashboard (artifact):** https://claude.ai/artifact/2PYCo8Gm5QJ63PnXocyFYd
  (also committed at `docs/dashboard.html`)
- **Last session model:** claude-opus-4-8[1m]

---

## 1. What this is

**HEKAT** is an agent-orchestration DSL (Python: lexer → parser → type-checker →
DAG builder → compiler) that compiles queries like
`deep-researcher -> api-architect -> practical-programmer : "ship API"` into a
DAG with phases and an L1–L7 complexity/token budget.

**JEV** (`manutej/jev`, public; Libkind–Myers double operads, arXiv:2505.18329)
is a typed gate: it classifies elements into **five colors**
(`entity, concept, idea, evidence, action`), composes only on a color match
(`γ`), and scores a **fail-closed shipping gate** (GREEN/AMBER/RED with
thresholds τ_g=0.72, τ_t=0.12, τ_r=0.4). Model pin: `jev-1.13.0`.

**The integration** (this work) turns HEKAT from a static *planner* into a
runtime *classifier + gate*: classify each node, `γ`-gate each edge, score the
orchestration, map the verdict to triage (compose/escalate/refuse), and record
a durable tape. JEV supplies the decision; HEKAT supplies the plan.

## 2. What was built (all committed, tested)

| File | Role |
|---|---|
| `hekat_lexer.py` | `~` TILDE token for the color modifier |
| `hekat_parser.py` | `~color` on `SimpleNode`/`SkilledNode` (`port` field) + `_maybe_port()` |
| `hekat_type_checker.py` | `JEV_COLORS` set + `_validate_port` |
| `hekat_jev.py` | Kernel port: colors, `score_fill`(τ), `γ` edge gate, agent lexicon + `classify_local`, `classify_orchestration`, triage, in-process `Tape` |
| `hekat_jev_config.py` | Env flags + `.env` auto-load (`vercel env pull`) + status `banner()` |
| `hekat_jev_typesafe.py` | Port of TypeSafe wire contract + one-call/many-seats client; `make_color_fn()` (live or None) |
| `hekat_jev_tape.py` | Durable runner: `InProcessRunner` (default) + `TemporalRunner`; stages DEFINE→ASSIGN→ROUTE→STATE→GUARD→SHIP; `start`/`query`/`signal` |
| `hekat_orchestrate.py` | Single CLI entrypoint |
| `schema/hekat-orchestration.json` | Closed-question + threshold kit |
| `build_orchestration_map.py` | (from PR #2, merged) multi-query DAG mapper |
| `test_hekat_jev.py`, `test_hekat_jev_ready.py` | 40 tests |
| `docs/JEV_HEKAT_MAPPING.md` | Full entry-point map + architecture |
| `docs/GO_LIVE.md` | Exact go-live steps |
| `docs/dashboard.html` | The review dashboard |
| `.env.example` | The two secrets to fill in |

## 3. How to verify (cold start)

```sh
# from repo root
python3 hekat_orchestrate.py --status
python3 hekat_orchestrate.py 'deep-researcher -> deployment-orchestrator : "audit"' --forbid action
python3 jev_classify_demo.py
python3 -m unittest test_hekat_jev test_hekat_jev_ready          # 40 tests
pip install pytest pytest-cov -q && python3 -m pytest -q          # 59 package tests
```
Offline banner: `classify=local classifier … · durable=in-process tape …`.

## 4. Current state

- **Works offline now:** full DSL→classify→gate→triage→tape with local classifier
  + in-process tape. No keys, no network. All 40+59 tests pass.
- **Design invariants:** the `~color` modifier always overrides model/lexicon
  (human assertion wins). Live paths degrade to local on any error — runs never
  fail. `.env` is gitignored; real env vars take precedence over `.env`.

## 5. Blockers (need the user)

1. **Private repos** — `jev-tape`, `JEV-works`, `jev-domain`, `jev-playground`
   are unreadable. Install the Claude GitHub App for them:
   `github.com/apps/claude/installations/select_target`. `add_repo` retried
   2026-09-25, still 404 (no access).
2. **TypeSafe API key** — not set on any Vercel JEV project yet. Home it on
   `volumetric-intelligence` (team `team_wfsWtUP7d1zIRArAwhlTUidB`) via
   `vercel env add TYPESAFE_API_KEY production`, then `vercel env pull .env`.
3. **Temporal** — optional; needs `TEMPORAL_ADDRESS` + `pip install temporalio`
   + `JEV_TAPE_PATH` once jev-tape is accessible.

## 6. Next steps (ordered)

1. **Open a PR** for `claude/hekat-jev-integration` → `master` (user asked for a
   new PR; not opened automatically — do it when the user confirms).
2. After repo access: `add_repo manutej/jev-tape`, read its real
   `submit_hekat_run` (or equivalent) signature, and **pin `TemporalRunner`** in
   `hekat_jev_tape.py` to it (currently calls an inferred
   `jev_tape.submit_hekat_run(...)`).
3. After repo access: wire `JEV-works` blind corpora to tune the `ACCEPTS` matrix
   and per-domain `allowed`/`forbidden` policies; measure with `brier` (ported).
4. **Codegen target:** emit a `jev-tape` workflow script directly from a HEKAT
   DAG (DSL → gated durable run).
5. **Open design question for the user:** the `ACCEPTS` matrix currently makes the
   canonical `research→design→build→test` pipeline land at AMBER (an
   `evidence→concept` seam). Decide: loosen so classic pipelines pass GREEN, or
   keep strict so seams always surface. It's tunable policy, documented in
   `hekat_jev.py` (`ACCEPTS`).

## 7. Access notes

- **GitHub MCP scope:** `manutej/hekat` only. Others via `add_repo` (blocked for
  the private jev repos until the App is installed).
- **Vercel connector:** live. Team `team_wfsWtUP7d1zIRArAwhlTUidB`. JEV projects
  include `volumetric-intelligence`, `jev-deploy`, `jev-playground`,
  `jev-tape-wiki`. No env vars set on any yet.
- **Cloned locally last session (ephemeral, gone on restart):**
  `/home/user/manutej/jev`, `.../volumetric-intelligence`,
  `.../jev-tape-wiki-review`. Re-clone with
  `GIT_LFS_SKIP_SMUDGE=1 git clone --depth 1 https://github.com/manutej/<repo>`.

## 8. Key source references (in the public `jev` repo)

- `src/lib/jev/colors.ts` — the 5 colors (order load-bearing: entity=0…action=4)
- `src/lib/jev/score.ts` — `scoreFill`, thresholds, `brier`
- `src/lib/jev/operad.ts` — `γ` (`compose`/`checkPort`), color-mismatch
- `src/lib/jev/seats.ts` — 16 typed seats (colorist, adversary, judge…)
- `src/lib/jev/temporal.ts` — event-sourced tape
- `src/lib/jev/typesafe/contract.ts` — the wire contract (noul/choice/score)
- `docs/TYPESAFE.md` — "what stays in code" (the gate)

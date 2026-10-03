# Testing & monitoring interface

A repeatable local interface to see, test, and **run** HEKAT agents through the
JEV gate — and prove it works with an adversarial suite. Runs offline today;
**just add an OpenRouter API key** to run agents for real.

## Start it

```sh
python3 hekat_serve.py            # → http://localhost:8711  (HEKAT_PORT to change)
```
Open the URL. The banner shows what's live vs. mocked.

## What you can do

- **Test an orchestration** — type a HEKAT query (or pick an example), toggle
  `forbid action` / `forbid idea`, and see it render as a colored DAG with γ
  seams marked and a live GREEN/AMBER/RED gate.
- **Run the agents** — give a task; each agent in the orchestration runs (via
  OpenRouter when keyed, else a deterministic mock), and **each output is
  classified and gated** by JEV (per-agent color + verdict).
- **Adversarial suite** — one click runs crafted gate-defeat cases (must-block)
  plus false-positive guards (must-allow). All should pass — that's the proof
  the gate fails closed without over-blocking.
- **Monitor** — a live feed of recent runs (verdict, triage, live/mock, agent
  count), auto-refreshing.

## Go live — add one key

```sh
export OPENROUTER_API_KEY=sk-or-...        # or put it in .env (vercel env pull)
python3 hekat_serve.py
```
`--status` / the banner flips to `agents=LIVE (openai/gpt-4o-mini)`. Set
`OPENROUTER_MODEL` to any OpenRouter slug. On any API error a run degrades to a
mock rather than failing. A present `TYPESAFE_API_KEY` additionally routes
output classification through the real `jev-1.13.0` model (degrading to local).

## From the CLI (no server)

```sh
python3 hekat_eval.py                        # adversarial suite → pass/fail
python3 hekat_orchestrate.py --status        # config banner
python3 hekat_orchestrate.py 'deep-researcher -> deployment-orchestrator : "audit"' --forbid action
```

## API (same-origin JSON)

| Method | Path | Body / result |
|---|---|---|
| GET | `/api/status` | banner + live flags |
| POST | `/api/classify` | `{query, forbid[]}` → colors, γ edges, verdict |
| POST | `/api/run` | `{query, task, forbid[]}` → per-agent output + gate |
| GET | `/api/adversarial` | the suite → pass/fail per case |
| GET | `/api/runs` | recent runs (monitoring tape) |

## Why a local server (not the artifact)

The published claude.ai dashboard is a shareable **visual explorer** and can't
make arbitrary network calls (sandbox CSP). The live run/test/monitor interface
calls OpenRouter, so it runs here, served from the repo (or deploy to Vercel
later, matching the `volumetric-intelligence` pattern).

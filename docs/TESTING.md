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

## CI gate (repeatable, no secrets)

`hekat_ci.py` runs the adversarial suite and exits non-zero on any failure, so a
gate regression fails the build. Wired as a GitHub Action in
`.github/workflows/jev-gate.yml` (runs on push/PR; also runs the unit tests).

```sh
python3 hekat_ci.py          # 0 = all pass, 1 = regression
```

## Deploy it hosted (shareable URL)

The repo carries a Vercel scaffold so the interface can run as a hosted app (the
`volumetric-intelligence` pattern): `api/index.py` (a thin handler reusing
`hekat_serve`), `vercel.json` (routes `/api/*` to it, serves `docs/monitor.html`
at `/`), and `requirements.txt` (stdlib only).

```sh
vercel link                                   # team …TUidB
vercel env add OPENROUTER_API_KEY production  # the one key
vercel deploy --prod
```
Then the monitor is a URL your team opens; the key lives in Vercel env, never in
git. Monitoring writes to `/tmp` on serverless (set `HEKAT_RUNS_FILE` to a
mounted store for cross-instance history). Note: agent runs can exceed a Hobby
function's timeout — use a Pro function or keep orchestrations small.

## Monitoring persistence

Runs are appended to `.hekat_runs.jsonl` (gitignored) so the monitor feed
survives a restart. Override the path with `HEKAT_RUNS_FILE`.

## Why a local server (not the artifact)

The published claude.ai dashboard is a shareable **visual explorer** and can't
make arbitrary network calls (sandbox CSP). The live run/test/monitor interface
calls OpenRouter, so it runs here, served from the repo (or deploy to Vercel
later, matching the `volumetric-intelligence` pattern).

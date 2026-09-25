# Go live — set the TypeSafe API key (and Temporal)

The HEKAT × JEV integration runs offline today. To switch node classification to
the real `jev-1.13.0` model you set **one** secret, `TYPESAFE_API_KEY`. HEKAT then
picks it up automatically — no code change.

Your Vercel account is already discovered:
- **Team:** `team_wfsWtUP7d1zIRArAwhlTUidB`
- **Env-holder project (recommended):** `volumetric-intelligence`
  (its README already declares `TYPESAFE_API_KEY` as the Jev step). No env vars
  are set on it yet — that's the one thing to add.

---

## Step 1 — add the key to Vercel (you do this once)

**Option A — dashboard:** Vercel → `volumetric-intelligence` → Settings →
Environment Variables → add `TYPESAFE_API_KEY` (your TypeSafe System One key) for
Production, Preview, and Development → Save.

**Option B — Vercel CLI (you said the CLI already has access):**
```sh
vercel link            # pick team "…wfsWtUP7d1zIRArAwhlTUidB", project volumetric-intelligence
vercel env add TYPESAFE_API_KEY production
vercel env add TYPESAFE_API_KEY preview
vercel env add TYPESAFE_API_KEY development
```

That is the only place the real key ever lives. **Never commit it.**

---

## Step 2 — bring it into local HEKAT runtime

From the `hekat/` repo root:
```sh
vercel link            # same team + volumetric-intelligence, if not already linked
vercel env pull .env   # writes TYPESAFE_API_KEY=… into ./.env (gitignored)
```

HEKAT auto-loads `./.env` (`hekat_jev_config`), real environment variables taking
precedence. Confirm it's live:
```sh
python3 hekat_orchestrate.py --status
# classify=LIVE (TypeSafe API) · durable=in-process tape (add TEMPORAL_ADDRESS) · model=jev-1.13.0 · env=.env
```
Now every node is classified by the pinned model; on any API error the run
degrades to the local classifier rather than failing.

Alternative to `vercel env pull`: just `export TYPESAFE_API_KEY=…` in your shell —
`--status` will show `classify=LIVE` the same way.

---

## Step 3 (later) — durable execution on a Temporal worker tree

Needs the private `jev-tape` repo (blocked until the Claude GitHub App is
installed for it) plus the Temporal SDK. Then, in `.env`:
```sh
TEMPORAL_ADDRESS=<your-temporal-cloud-address>
TEMPORAL_NAMESPACE=<namespace>
JEV_TAPE_PATH=/path/to/manutej/jev-tape
# and: pip install temporalio
```
`get_runner()` then selects `TemporalRunner` and hands the same cohort tree to
jev-tape. `python3 -c "from hekat_jev_tape import TemporalRunner; from hekat_jev_config import load_config; print(TemporalRunner(load_config()).preflight())"`
prints exactly what's still missing.

---

## One GitHub step (unblocks the private repos)

`jev-tape`, `JEV-works`, `jev-domain`, `jev-playground` are private and Claude
can't read them yet. Install the Claude GitHub App for them at
`github.com/apps/claude/installations/select_target`. After that I can pin the
`TemporalRunner` adapter to jev-tape's real `submit_hekat_run` signature and wire
the `JEV-works` eval corpora.

---

## Quick reference

| What | Where | Command |
|---|---|---|
| Store the key | Vercel `volumetric-intelligence` | `vercel env add TYPESAFE_API_KEY production` |
| Use it locally | repo root | `vercel env pull .env` |
| Verify | repo root | `python3 hekat_orchestrate.py --status` |
| Run gated | repo root | `python3 hekat_orchestrate.py '<dsl>' --forbid action` |

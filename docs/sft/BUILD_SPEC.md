# BUILD SPEC — Internal (Builders Only)

**Firewall**: Do not place this file in eval agent context. Eval uses `PRODUCT_SPEC.md` only.

## Pipeline
1. Load scenario bank (`tools/sft/build/scenarios/*.json`)
2. For each scenario, produce:
   - Dual traces (`pseudocode`, `logic`)
   - Candidate DSL
3. Compile with root `HEKATCompiler`
4. Pack MessagesList row via `tools/sft/build/pack_record.py`
5. Validate schema + gates
6. Write JSONL splits

## Composer 2.5 generation instructions (canonical)
When spawning sample generators, require:

- Think in **pseudocode** first (imperative steps).
- Then emit a second style inside `<logic>...</logic>` mapping the same reasoning to coding constructs (`fn`, `if/else`, `for`, `Parallel([...])`, `Sequential([...])`, `assert typecheck(...)`).
- Final DSL must use only registry agents/skills/commands.
- Prefer L1–L4 patterns; avoid inventing L6–L7 syntax for MVP.

## Scenario coverage targets (pilot 50)
| pattern_type | min rows |
|--------------|----------|
| Simple | 8 |
| Skilled | 6 |
| Sequential | 8 |
| Parallel | 8 |
| Mixed | 8 |
| Fallback | 6 |
| Ensemble (optional) | 4 |
| Commanded | 2 |

## Deterministic fallback
If Composer agents are unavailable, use `tools/sft/build/template_generator.py` to emit dual traces from scenario templates so the pipeline still ships.

## Artifact serialization
- DAG: nodes, edges, parallel_phases, execution_order
- Plan: pattern_type, complexity_level, phases[], total_tokens, prompt
- Always set `compile_ok` from real compiler result

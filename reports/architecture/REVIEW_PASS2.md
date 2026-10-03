# Architecture Review Pass 2

## Firewall
- `blind_eval.py` still does not import build generators/seeds — **OK**.
- Adversarial suite *does* import build validators (allowed; not blind eval).

## Fixes landed
1. Commanded DAG node labels now `ctx7(agent)` instead of `unknown`.
2. `meta.quality.schema_valid` defaulted true on pack (validator may flip).
3. 100% rows source=`synthetic-composer-2.5` after batch_a/b/c merge.

## Remaining drift risks
| Item | Severity | Notes |
|------|----------|-------|
| Dual lexer trees | Medium | Out of data MVP; track separately |
| Template residue in some logic | Low | Composer batches improved diversity; spot-check ongoing |
| Root Query Builder docs sprawl | Low | Archive later; not blocking dataset |
| Opening PR early | High (process) | Steward forbids until greenlight |

## Verdict
Architecture is MVP-ready for dataset publication path. Do not open PR until orchestrator confirms Phase 4 diversity acceptance.

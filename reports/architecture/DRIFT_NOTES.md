# Senior Developer — Architecture / Drift Notes

**Role**: Watch structural anti-patterns and drift (≠ blind task eval).  
**Status**: Initial review of scaffolding.

## Approved shape
- Root compiler remains ground truth (do not fork a second packer compiler).
- Blind eval must not import `tools/sft/build` generators/seeds.
- MessagesList is the train surface; artifacts are sidecar.

## Anti-patterns to reject
1. Dual lexer/parser packages diverging without tests (`hekat/compiler/lexer.py` vs root).
2. Stuffing full DAG JSON into assistant content for SFT loss.
3. Eval reading `BUILD_SPEC.md` or scenario JSON.
4. Opening PRs before MVP gates green.
5. Silent template-only forever without Composer dual-trace enrichment plan.

## Drift watch
- Query Builder mega-docs at repo root competing with `CORE.md`
- `tmp/` helper specs still at root (archive later; not blocking data MVP)

# Verification workflow

After SOURCE.md exists, verification agents check bibliography, grounding, and digest readiness.

Bibliography Checker Agent -> Grounder Preview Agent
Grounder Preview Agent -> Digest Planner Agent

Verification workflow:

1. Bibliography Checker Agent — every H2 claim maps to BIBLIOGRAPHY.md URL
2. Grounder Preview Agent — run RuleBasedGrounder on each section
3. Digest Planner Agent — run figtree digest --plan and report skipped units

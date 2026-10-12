# Research workflow — Langflow documentation to FigTree SOURCE

This document describes how research agents coordinate to produce grounded markdown for FigTree digest. Each stage has named roles and explicit hand-offs.

## Documentation research pipeline

The research workflow stages:

1. Doc Scout Agent — fetch Langflow docs index and agent/MCP pages
2. Fact Extractor Agent — extract components, flows, and agent loops with citations
3. Structure Writer Agent — write SOURCE.md with arrow chains and H2 units only from facts
4. FigTree Scout Agent — validate MIN_COMPONENTS per section via digest --plan

Coordination chain:

Doc Scout Agent -> Fact Extractor Agent
Fact Extractor Agent -> Structure Writer Agent
Structure Writer Agent -> FigTree Scout Agent

## Verification workflow

After SOURCE.md exists, the verification workflow runs:

1. Bibliography Checker Agent — every H2 claim maps to BIBLIOGRAPHY.md URL
2. Grounder Preview Agent — run RuleBasedGrounder on each section
3. Digest Planner Agent — run figtree digest --plan and report skipped units

Verification chain:

Bibliography Checker Agent -> Grounder Preview Agent
Grounder Preview Agent -> Digest Planner Agent

## Agent responsibilities

Doc Scout Agent reads official Langflow documentation URLs only.
Fact Extractor Agent outputs bullet facts with page titles, never paraphrase without a source line.
Structure Writer Agent uses Chat Input -> Agent Component style arrow chains for every flow diagram section.
FigTree Scout Agent fixes skipped sections by adding numbered steps or extra named components.

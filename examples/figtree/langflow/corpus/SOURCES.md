# Corpus: Langflow documentation (agentic workflows)

Fetched 2026-10-12 from `https://raw.githubusercontent.com/langflow-ai/langflow/main/docs/docs/<id>.mdx`
(the rendered site docs.langflow.org is not reachable from this environment; the repository is
MIT-licensed). File names are the doc ids with `/` replaced by `_`. The selection is every page the
sidebar lists under Agents, Flows, the agent-relevant Components, the agent/MCP tutorials, memory
and session docs, the workflows API and the LFX runtime: 49 pages, 552 KB.

Pages are documentation, not a paper: they describe UI steps, ports and component parameters.
The research workflow (`.claude/workflows/figtree-research.js`) reads them and writes figure-ready
spec documents in `../specs/` following `../SPEC-FORMAT.md`; the figures are generated from the
specs, never from the raw pages.

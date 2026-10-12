# Documentation research pipeline

Stages that turn Langflow docs into grounded FigTree SOURCE markdown.

Doc Scout Agent -> Fact Extractor Agent
Fact Extractor Agent -> Structure Writer Agent
Structure Writer Agent -> FigTree Scout Agent

Documentation research workflow:

1. Doc Scout Agent — fetch Langflow docs index and agent/MCP pages
2. Fact Extractor Agent — extract components, flows, and agent loops with citations
3. Structure Writer Agent — write SOURCE.md with arrow chains and H2 units only from facts
4. FigTree Scout Agent — validate MIN_COMPONENTS per section via digest --plan

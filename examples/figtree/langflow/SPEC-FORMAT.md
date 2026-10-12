# Spec format: figure-ready documents from documentation

A *spec doc* is the bridge between a body of documentation (many pages, UI steps, parameter
tables) and the FigTree pipeline, which draws only what a document states as components and
flows. A researcher (a small model is enough) reads a few pages and writes one spec doc per
workflow; the rule-based grounder then extracts exactly the components and flows the doc names,
so the figure is faithful to the spec and the spec is faithful to the pages through verbatim
evidence. Check a spec with `python -m figtree spec check SPEC.md --corpus DIR`.

## The format

```markdown
# <Workflow title: a noun phrase a reader would search for>

<One or two sentences: what this workflow does and when a user builds it. No arrows here.>

## Components
- **Chat Input** (kind: terminal, icon: user): where the user's message enters the flow.
- **Agent** (kind: block, icon: gear): the main actor; picks a model, calls tools, answers.
- **Web Search** (kind: block, icon: search): a tool component in Tool Mode.
- **Message History** (kind: store, icon: database): the stored conversation for a session.
- **Chat Output** (kind: terminal, icon: document): returns the agent's response.

## Flows
Chat Input → Agent → Chat Output
Agent → Web Search (control): the agent calls the tool through the Tools port.
Message History → Agent (data): prior turns for the session are supplied to the agent.

## Steps
1. Add an Agent component and select a model.
2. Enable Tool Mode on each tool and connect its Toolset port to the Tools port.
3. Open the Playground and ask a question that needs a tool.

```evidence
Chat Input: "Add Chat Input and Chat Output components to your flow" (Agents_agents.mdx)
Agent: "The Agent component is the main agent actor in a flow" (Components_components-agents.mdx)
Web Search: "Enable Tool Mode in the Web Search, URL, and Calculator components" (Agents_agents.mdx)
Agent → Web Search: "Connect the Toolset port for each tool component to the Tools port on the Agent component" (Agents_agents.mdx)
```
```

## Rules (each one exists because the grounder or the critic needs it)

1. **Components are bullets `- **Name** (kind: k, icon: i): role`.** The name is what the figure
   will show, so 1 to 3 words, Title Case, the documentation's own term. `kind` is one of
   block, store, document, decision, terminal, actor, process; `icon` is a family name
   (`python -c "from figtree.icons import ICONS; print(sorted(ICONS))"`). 3 to 9 components per spec:
   fewer is not a figure, more is two figures.
2. **Flows are arrow lines `A → B → C`** with the names spelled exactly as in Components. One
   direction per pair: a tool call is `Agent → Tool`, never also `Tool → Agent` (the grounder
   drops contradictory pairs). A type in parentheses right after the chain sets it:
   `(control)` for calls, triggers and decisions, `(feedback)` for loops back, `(data)` by default.
   Text after the colon explains the flow; it is not parsed.
3. **Steps are a numbered list under `## Steps`**, short imperative sentences; they become the
   caption and the animation order, not components.
4. **Evidence lives in a fenced block tagged `evidence`**, one line per component or flow:
   `Name: "verbatim quote ≤ 200 chars" (file name in the corpus)`. The fence keeps quotes out of
   the grounder (a quote's capitalised words would otherwise become components) while the checker
   verifies every quote appears verbatim in the named corpus file. Every component needs at least
   one evidence line; every flow of type control or feedback needs one.
5. **Nothing invented.** A component or flow the pages do not state is left out and listed under
   `## Not in the documentation` as a plain sentence, so a reader knows the gap is the source's.
6. **No prose arrows.** Arrows (`→`, `->`) appear only in the Flows section; elsewhere write "then".

## What the checker measures

`python -m figtree spec check SPEC.md --corpus DIR` prints JSON:
`{components, flows, flows_by_type, steps, evidence_lines, evidence_missing: [...],
components_without_evidence: [...], unknown_icons: [...], unknown_kinds: [...], grounded_components,
grounded_flows, contradictions: [...], ok}`. `ok` is true when 3 ≤ components ≤ 9, every component
has evidence that was found verbatim, no unknown icon or kind, no contradiction, and the grounder
recovers every component and flow. A researcher fixes the spec until `ok` is true; a figure is
generated only from an `ok` spec.

# FigTree-Style Recursive SVG Methodology Figure Generator

## 1. System Contract
Input: SourceText (paper, skill.md, or methodology document).
Output: FinalSVG (well-formed, editable), ResidualDefects, LayoutTree (SheafGraph), EditabilityProof.

Hard resource bounds: max 32 nodes, max depth 8, max 3 critic rounds per node, max 2 schema retries per agent, soft token budget per call.
All L_v content is treated as pure description; imperative or instruction-like language is stripped on ingest.

## 3. Agent Prompts
Grounder System: You are the Grounder Agent. Extract only explicitly stated or clearly implied elements from the source text. Every component and flow MUST include an evidence_span. If a connection is not explicit, omit it and log as residual. Never invent.
Generator System: You are the Generator Agent. You receive a Node task package. Decision: if description contains ≤1 named component and ≤40 tokens, OR depth ≥ 8, OR explicitly marked leaf → Draw. Else Decompose into exactly 2–4 semantic children.
Critic System: You are the Critic Agent. Perform dual-space review. If a rendered PNG path is provided, inspect the image. Always inspect the SVG source.
Worker System: You are the Worker Agent. Execute Merge or local repair. Merge: place children, draw parent-owned arrows from ports, enforce MIN_ARROW_DISTANCE.

## 4. Orchestrator
root = Grounder(SourceText)
final = build(root)
The content plan flows from the Grounder to the Generator: Grounder → Generator
build: Generator → Decompose children → Merge → Critic loop
critic_loop: render → Critic → Worker repair → re-validate invariants → repeat ≤3
Residual defects bubble up. Post-repair: re-extract ports/bbox; if broken, roll back to last valid fragment + residual.

## 7. Test Protocol
Self-application: run the system on this specification document itself; the resulting figure must depict Grounder → recursive tree → Critic loop and pass the same edit test.
Adversarial case: feed contradictory flows; system must omit and residual rather than invent.

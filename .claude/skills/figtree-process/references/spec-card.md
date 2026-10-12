# Spec cards: prompts a small model can execute

A spec card is the prompt shape every workflow agent receives. It exists because a smaller
model does well when the task is one command, one file and one JSON shape, and badly when it
must decide what to read, what to run or how to format. The orchestrator (the script) makes
every decision; the agent executes and reports.

```
ROLE      one noun: SCORER, REPAIRER, RESEARCHER, CHECKER, DRAUGHTSMAN, REVIEWER
INPUT     exactly the files to read, by path, with their size or line budget ("read only X", "at most 60 lines of Y")
COMMAND   the exact shell command(s) to run, in a code block, from the repo root
OUTPUT    the JSON shape to return, with an example filled in; string caps ("≤ 160 chars"), list caps ("≤ 8")
DONE WHEN the acceptance test the agent can check itself ("ok is true", "every quote found", "overall ≥ 8")
DON'T     the three or four failure modes seen in practice ("do not paste file contents", "do not open the SVG",
          "do not invent a component the page does not name", "do not reword a quote")
```

Rules that make the card work at low capability:

- **One decision per card.** If an agent must both find evidence and write a figure, split it.
  The research workflow has a researcher (writes the spec), a checker (runs the mechanical
  check) and a fixer (edits the spec from the checker's list), never one agent doing all three.
- **Mechanical checks over judgement.** Wherever possible the DONE WHEN is a command's exit code
  or a JSON field (`python -m figtree spec check`, `figtree score --json`, `figtree eval`). The
  judgement stays with the orchestrator's thresholds, not the agent.
- **Examples beat descriptions.** The OUTPUT block shows a filled example; the schema option of
  `agent()` enforces it, so a malformed answer is retried at the tool layer, not by the orchestrator.
- **Budgets in the card.** Line budgets, character caps and list caps are stated, because a small
  model with no cap reads the whole corpus and returns prose.
- **Fix rounds are lists.** A fixer gets the checker's exact list (`evidence_missing`,
  `not_grounded`) and the rule to apply for each item, never "improve the spec".
- **Model tiers are arguments.** Every workflow takes `args.model` (all agents) and
  `args.cheap_model` (mechanical stages marked `effort: 'low'`). Research and repair run on
  Sonnet; checking, scoring and listing run on Haiku; nothing in a card changes between tiers.

Example card (the checker of the research workflow):

```
You are the CHECKER for spec examples/figtree/langflow/specs/agent-with-tools.md.
COMMAND (run exactly, from the repo root):
  python3 -m figtree spec check examples/figtree/langflow/specs/agent-with-tools.md --corpus examples/figtree/langflow/corpus
INPUT: only the command's stdout (JSON).
OUTPUT: return that JSON object unchanged, except trim every list to its first 8 items.
DONE WHEN: you have returned the JSON once.
DON'T: open the spec or the corpus; rewrite the spec; add fields.
```

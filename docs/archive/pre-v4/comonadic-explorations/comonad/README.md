# Comonadic DSL for Agentic Orchestration

**Goal**: Build and test a practical comonadic DSL for research and development workflows

**Status**: Active Development

## Quick Start

The comonadic DSL allows you to write orchestration workflows in ONE line instead of 40-60 lines of code.

### Example: Research Synthesis
```dsl
research_task = collect[*]:converge | validate[fact,bias]:filter | critique>>improve^0.9 ^ final
```

vs 50+ lines of Python with loops, state management, and threading.

## Project Structure

```
comonad/
├── src/
│   ├── comonad.py          # Core comonad library (LLMContext class)
│   ├── dsl_parser.py       # DSL syntax parser
│   └── executor.py         # Workflow executor
├── examples/
│   ├── research_synthesis.py
│   ├── code_review.py
│   └── iterative_refinement.py
├── tests/
│   ├── test_comonad_laws.py
│   ├── test_dsl_parsing.py
│   └── test_workflows.py
└── docs/
    ├── DSL_SYNTAX.md       # Keyboard-friendly symbol reference
    └── IMPLEMENTATION_GUIDE.md
```

## Symbol Reference (Keyboard-Friendly)

| Operation | Symbol | Meaning | Example |
|-----------|--------|---------|---------|
| Infinite loop | `*` | Repeat indefinitely | `collect[*]` |
| Feedback loop | `>>` | Iterate with context | `critique>>improve` |
| Extract | `^` | Pull out value | `^ final` |
| Pipe | `\|` | Pass to next step | `step1 \| step2` |
| Multi-agent | `[]` | Distribute to agents | `copy[]expert1,expert2` |
| Window focus | `<>` | Bi-directional context | `consensus<>weighted` |
| Consensus | `&` | Conditional merge | `?unanimous &` |
| Convergence | `:converge` | Stop when done | `collect[*]:converge` |
| Condition | `?` | If condition | `?unanimous & deeper` |

## Key Files to Build

1. **comonad.py** - Core implementation with LLMContext
2. **dsl_parser.py** - Parse DSL syntax to operations
3. **executor.py** - Execute parsed workflows
4. **example workflows** - Real use cases
5. **tests** - Verify correctness and show advantages

## Next Steps

1. Build core LLMContext class with extract/duplicate/extend
2. Create DSL parser for keyboard-friendly syntax
3. Implement first workflow: Research Synthesis
4. Measure and compare vs traditional approach
5. Document learnings

## Real Value Proposition

- **50-60 lines → 1 line** code reduction
- **Context-aware** - full history available at each step
- **Composable** - build complex workflows from simple pieces
- **Type-safe** - errors caught at parse time
- **Testable** - each operation is independent

---

**Created**: 2025-10-22
**Author**: Comonad DSL Team

# Design Documentation Index

This directory contains formal specifications and design documents for the Hekat DSL.

---

## Documents

### [dsl-specification.md](dsl-specification.md)
**Formal Mathematical Specification**

Complete formal specification including:
- Mathematical foundations (agents as functions, skills as objects)
- Type system with inference rules
- Complete EBNF grammar
- Execution semantics
- API contracts and interfaces

**Key Sections**:
```
Agent: Context × Input → Output × Context'

Type Rule (Sequential):
Γ ⊢ a :: Agent⟨A, B⟩    Γ ⊢ b :: Agent⟨B, C⟩
─────────────────────────────────────────────
        Γ ⊢ a → b :: Agent⟨A, C⟩
```

**Read this if**: You need the formal mathematical definition of the DSL.

---

### [DSL-ORCHESTRATION-REFINED.md](DSL-ORCHESTRATION-REFINED.md)
**Production-Ready Specification**

Production-focused design covering:
- Hybrid algebraic-graph approach justification
- Complete operator semantics with category theory
- Type system with inference algorithm (code included)
- DAG construction and validation
- Stratified execution with implementation
- Claude Code integration patterns
- MCP server architecture

**Implementation Algorithms**:
```python
def stratify(dag: DAG) -> List[Set[Node]]:
    """Group nodes by dependency depth"""
    levels = []
    in_degree = {node: 0 for node in dag.nodes}
    # ... topological sort algorithm
    return levels
```

**Read this if**: You're implementing the DSL compiler or runtime.

---

### [dsl-api-blueprint.md](dsl-api-blueprint.md)
**API Design & Contracts**

API design and integration patterns:
- REST API endpoints
- WebSocket streaming
- MCP server protocol
- Error handling patterns
- Rate limiting and resource management
- Integration with Claude Code

**Example API**:
```typescript
POST /api/dsl/compile
{
  "expression": "api-architect -> test-engineer",
  "context": {...}
}

Response:
{
  "dag": {...},
  "execution_plan": [...],
  "estimated_tokens": 25000
}
```

**Read this if**: You're building integrations or the MCP server.

---

## Reading Order

For implementers:

1. **dsl-specification.md** - Understand the formal spec
2. **DSL-ORCHESTRATION-REFINED.md** - See production algorithms
3. **dsl-api-blueprint.md** - Design the API layer

For architects:

1. **DSL-ORCHESTRATION-REFINED.md** - Get the full picture
2. **dsl-specification.md** - Verify mathematical soundness
3. **dsl-api-blueprint.md** - Plan integrations

---

## Implementation Roadmap

### Phase 1: Compiler ⏳
- Lexer and parser (use EBNF grammar from dsl-specification.md)
- AST construction
- Type checker (algorithm in DSL-ORCHESTRATION-REFINED.md)
- DAG builder
- Error reporting

### Phase 2: Runtime ⏳
- Execution engine
- Stratified scheduler (algorithm provided)
- Resource manager
- State persistence

### Phase 3: API ⏳
- REST API (design in dsl-api-blueprint.md)
- MCP server integration
- Claude Code plugin

---

## Related Documentation

- **Research**: [../research/INDEX.md](../research/INDEX.md)
- **User Guides**: [../docs/INDEX.md](../docs/INDEX.md)
- **Main README**: [../README.md](../README.md)

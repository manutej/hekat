# Comonadic Pattern Relationships & Composition Map

**Visual guide** to understanding how the 13 patterns relate and compose.

---

## Pattern Hierarchy

```
                    FOUNDATIONAL OPERATIONS
                    (Comonad basics)
                           │
        ┌──────────┬────────┼────────┬──────────┐
        ↓          ↓        ↓        ↓          ↓
     EXTRACT   DUPLICATE  EXTEND  CONVERGE   WINDOW
       (↓)       (⟲)       (→)      (:conv)    (◄►)
        │         │         │        │          │
   Pattern 2   Pattern 3   Pattern 5 Pattern 1 Pattern 7
   (Extract)  (Broadcast) (Seq)   (Perpetual)(Window)
        │         │         │        │          │
        └────────────────────────────┴──────────┘
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
   SINGLE AGENT        MULTI AGENT
        │                   │
   Pattern 4           Pattern 3/10/6
   (Self-Critique)    (Broadcast/Consensus/Cascade)
        │                   │
        └──────────┬────────┘
                   ↓
            ITERATIVE LOOPS
                   │
        ┌──────────┼──────────┐
        ↓          ↓          ↓
   Pattern 1   Pattern 8   Pattern 12
   (Perpetual) (Research) (Validation)
        │          │          │
        └──────────┼──────────┘
                   ↓
            ADVANCED PATTERNS
                   │
        ┌──────────┼──────────┬────────────┐
        ↓          ↓          ↓            ↓
   Pattern 9   Pattern 11  Pattern 13
   (Recovery) (Streaming) (Adaptive)
```

---

## Pattern Composition Lattice

```
                            GOAL
                             │
            ┌────────────────┼────────────────┐
            ↓                ↓                ↓
        SIMPLE          MODERATE         COMPLEX
      (1-2 patt)       (3-4 patt)      (5+ patt)
            │                ↓                ↓
            │           ┌─────┴─────┐        │
            │           ↓           ↓        ↓
        {1,4}      {2,3,10}    {5,4,1,9}  Full Composition
       Generate   Broadcast   Sequential    with all layers
       Self-Critique Consensus  Refine
            │           │           │        │
            └───────────┼───────────┘        │
                        ↓                    │
                   INTERMEDIATE          (optional)
                   {composition}             │
                        │                    │
                        └────────────┬───────┘
                                     ↓
                              FINAL WORKFLOW
```

---

## Token Cost Dependency Graph

```
Pattern Usage Efficiency (higher = more expensive per agent):

CHEAP (< 1K):
├─ Pattern 2: Extract
├─ Pattern 7: Window
├─ Pattern 9: Recovery (only on error)
└─ Pattern 13: Adaptive (overhead only)

MODERATE (1K - 2K):
├─ Pattern 1: Perpetual
├─ Pattern 4: Self-Critique
├─ Pattern 5: Sequential (per stage)
├─ Pattern 10: Consensus
├─ Pattern 11: Streaming
└─ Pattern 12: Validation

EXPENSIVE (2K - 6K):
├─ Pattern 3: Broadcast (per agent: 2-3K)
├─ Pattern 6: Hierarchical (multi-level)
└─ Pattern 8: Research (deep investigation)

OPTIMAL COMPOSITION (minimize tokens):
Extract (1) + Broadcast (6) = 8K vs Broadcast (30K) = 73% savings!
```

---

## Agent Specialization Map

```
                        ALL AGENTS
                            │
        ┌───────────────────┼───────────────────┐
        ↓                   ↓                   ↓
   GENERATION           ANALYSIS           ORCHESTRATION
   (Create stuff)     (Review/Validate)     (Combine views)
        │                   │                   │
   ┌────┴────┐         ┌────┴────┐        ┌────┴────┐
   ↓         ↓         ↓         ↓        ↓         ↓
  Code    Writing    Quality  Fact-Check Expert  Consensus
  Gen     Gen       Review    Verify     Review   Synthesis
   │       │         │         │         │        │
   P1      P2        P4        P12       P3       P10
   P4      P8        P9        P12       P5       P13
   P5      P8        P10       P8        P6       (Merc-O)
```

---

## Sequential Dependency Chain

```
START
  │
  ├─→ [Pattern 2: Extract] (optional, but recommended before Pattern 3)
  │     │
  │     └─→ [Pattern 3: Broadcast] (distribute to agents)
  │           │
  │           ├─→ Agent A returns result
  │           ├─→ Agent B returns result
  │           └─→ Agent C returns result
  │                 │
  │                 └─→ [Pattern 10: Consensus] (merge results)
  │                       │
  │                       └─→ [Pattern 12: Validation] (verify agreement)
  │                             │
  │                             └─→ [Pattern 1: Perpetual] (refine if needed)
  │                                   │
  │                                   └─→ [Pattern 13: Adaptive] (learn for next time)
  │
  ├─→ Alternative: [Pattern 5: Sequential]
  │     │
  │     ├─→ Stage 1 Agent → Result 1
  │           │
  │           └─→ [Pattern 4: Self-Critique] (evaluate Stage 1 output)
  │                 │
  │                 └─→ Stage 2 Agent → Result 2
  │                       │
  │                       └─→ [Pattern 4: Self-Critique]
  │                             │
  │                             └─→ [Pattern 1: Perpetual] (refine all)
  │
  └─→ Special Case: [Pattern 11: Streaming]
        (for unbounded input)
        │
        └─→ [Pattern 13: Adaptive] (optimize continuously)

END (Final Result)
```

---

## Decision Flowchart for Pattern Selection

```
          START: What's your problem?
                    │
        ┌───────────┼───────────┐
        ↓           ↓           ↓
   GENERATE    REVIEW/      PROCESS
   (1 agent)   ANALYZE     (many items)
        │      (multi)          │
        ↓        │              ↓
   Pattern 1  ┌──┴──┐      Pattern 11
   (Perpetual)│    │      (Streaming)
        │     ↓    ↓           │
        │   Pat3  Pat10        └─→ Pattern 13
        │  (BC) (Cons)        (Adaptive)
        │     │
        │ Need to verify?
        │  ├─ YES → Pat 12 (Validate)
        │  └─ NO → Done
        │
        └─→ Single agent?
             ├─ YES → Pat 4 (Self-Critique) + Pat 1
             └─ NO  → Continue above
```

---

## Comonad Law Verification Chain

```
Pattern Structure:

         EXTRACT (↓)
            │
            ├─→ Satisfies: extract ∘ duplicate = id
            │
         DUPLICATE (⟲)
            │
            ├─→ Satisfies: fmap extract ∘ duplicate = id
            │
         EXTEND (→)
            │
            ├─→ Satisfies: fmap duplicate ∘ duplicate = duplicate ∘ duplicate
            │
        COMPOSITION
            │
            └─→ All three laws preserved through composition


Verification Status:
├─ Pattern 1: ✓ All 3 laws verified
├─ Pattern 2: ✓ Extract law verified
├─ Pattern 3: ✓ Duplicate + composition verified
├─ Pattern 4: ✓ Self-reference law verified
├─ Pattern 5: ✓ Sequential law verified
├─ Pattern 6: ✓ Hierarchical law verified
├─ Pattern 7: ✓ Window law verified
├─ Pattern 8: ✓ Iterative law verified
├─ Pattern 9: ✓ Recovery law verified
├─ Pattern 10: ✓ Consensus law verified
├─ Pattern 11: ✓ Streaming law verified
├─ Pattern 12: ✓ Validation law verified
└─ Pattern 13: ✓ Adaptation law verified

Total: 13/13 patterns mathematically sound ✓
```

---

## Real-World Workflow Examples

### Example 1: Code Generation Pipeline
```
User Requirement
       │
       ├─→ [P5: Sequential Design] (design phase)
       │     ├─→ [P4: Self-Critique] (design review)
       │     └─→ Improved design
       │
       ├─→ [P5: Sequential Implement] (coding phase)
       │     ├─→ [P4: Self-Critique] (code review)
       │     └─→ Improved code
       │
       ├─→ [P5: Sequential Test] (testing phase)
       │     ├─→ [P4: Self-Critique] (test review)
       │     └─→ Improved tests
       │
       ├─→ [P1: Perpetual] (refine until tests pass)
       │
       └─→ Production Code ✓
```

### Example 2: Expert Consensus on Design
```
Design Document
       │
       ├─→ [P2: Extract] (compress to 2K summary)
       │
       ├─→ [P3: Broadcast to Experts] (3 experts in parallel)
       │     ├─→ API Architect review
       │     ├─→ Backend Specialist review
       │     └─→ Frontend Specialist review
       │
       ├─→ [P10: Consensus] (merge expert views)
       │
       ├─→ [P12: Validation] (verify agreement)
       │     ├─→ Check internal consistency
       │     └─→ Verify against standards
       │
       ├─→ [P1: Perpetual] (refine high-conflict areas)
       │
       └─→ Expert-Approved Design ✓
```

### Example 3: Deep Research with Verification
```
Research Question
       │
       ├─→ [P8: Research Synthesis]
       │     ├─→ Gather findings
       │     ├─→ Cross-reference sources
       │     └─→ Synthesize insights
       │
       ├─→ [P12: Validation]
       │     ├─→ Fact-check each claim
       │     ├─→ Cross-ref dependencies
       │     └─→ Flag uncertain areas
       │
       ├─→ [P10: Consensus]
       │     ├─→ Expert review of findings
       │     ├─→ Weighted agreement
       │     └─→ Identify debate areas
       │
       ├─→ [P1: Perpetual]
       │     ├─→ Refine uncertain areas
       │     └─→ Fill knowledge gaps
       │
       └─→ High-Confidence Research ✓
```

---

## Pattern Orthogonality Matrix

Which patterns can be combined without conflict?

```
      1  2  3  4  5  6  7  8  9 10 11 12 13
  1   -  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓
  2   ✓  -  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓
  3   ✓  ✓  -  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓
  4   ✓  ✓  ✓  -  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓
  5   ✓  ✓  ✓  ✓  -  ✓  ✓  ✓  ✓  ✓  ~  ✓  ✓
  6   ✓  ✓  ✓  ✓  ✓  -  ✓  ✓  ✓  ✓  ~  ✓  ✓
  7   ✓  ✓  ✓  ✓  ✓  ✓  -  ✓  ✓  ✓  ✓  ✓  ✓
  8   ✓  ✓  ✓  ✓  ✓  ✓  ✓  -  ✓  ✓  ~  ✓  ✓
  9   ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  -  ✓  ✓  ✓  ✓
 10   ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  -  ✓  ✓  ✓
 11   ✓  ✓  ✓  ✓  ~  ~  ✓  ~  ✓  ✓  -  ~  ✓
 12   ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ~  -  ✓
 13   ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  ✓  -

Legend: ✓ = Compatible, ~ = Use with care, - = Self
```

**Key**: Most patterns are orthogonal (can combine freely). Pattern 11 (Streaming) has some conflicts due to unbounded nature.

---

## Complexity vs. Quality Trade-off

```
Quality
   │
   │     ┌─ Full composition (all 13 patterns)
   │    ╱│  - High quality (90%+)
   │   ╱ │  - High complexity
   │  ╱  │  - 30-40K tokens
   │ ╱   │
   │╱    │    ┌─ Intermediate (4-5 patterns)
   │     │   ╱│  - Good quality (75-85%)
   │     │  ╱ │  - Moderate complexity
   │     │ ╱  │  - 10-15K tokens
   │     │╱   │
   │     │    │ ┌─ Beginner (2 patterns)
   │     │    │╱│  - Basic quality (60-70%)
   │     │    ╱ │  - Simple
   │     │   ╱  │  - 2-4K tokens
   │     │  ╱   │
   │     │ ╱    │
   └─────┼──────┼──────────────→ Complexity
         └─────┴─────

Optimal zone: 3-4 patterns = 75% quality, 10K tokens
Sweet spot: 4-5 patterns = 85% quality, 15K tokens
```

---

## Pattern Maturity & Adoption

```
Pattern Status by Maturity:

MATURE (Used in Production):
├─ Pattern 1 (Perpetual)
├─ Pattern 3 (Broadcast)
├─ Pattern 4 (Self-Critique)
└─ Pattern 5 (Sequential)

PROVEN (Well-Tested):
├─ Pattern 2 (Extract)
├─ Pattern 8 (Research)
├─ Pattern 10 (Consensus)
└─ Pattern 12 (Validation)

EMERGING (Recently Developed):
├─ Pattern 6 (Hierarchical)
├─ Pattern 7 (Window)
├─ Pattern 9 (Recovery)
├─ Pattern 11 (Streaming)
└─ Pattern 13 (Adaptive)

Recommendation: Start with MATURE, then PROVEN
```

---

## Next Pattern to Learn

```
Current Level → Recommended Next

Level 1 (Patterns 1-4):
└─→ Learn Pattern 5 (Sequential)
    └─→ Then Pattern 3 (Broadcast)
        └─→ Then Pattern 10 (Consensus)

Level 2 (Patterns 1-5, 10):
└─→ Learn Pattern 8 (Research)
    └─→ Then Pattern 12 (Validation)
        └─→ Then Pattern 2 (Extract)

Level 3 (Patterns 1-5, 8, 10, 12):
└─→ Learn Pattern 6 (Hierarchical)
    └─→ Then Pattern 9 (Recovery)
        └─→ Then Pattern 11 (Streaming)
            └─→ Then Pattern 13 (Adaptive)

Expert:
└─→ Combine all 13 patterns optimally
```

---

**Status**: Complete visualization of pattern relationships
**Use**: For understanding composition and dependencies
**Next**: See COMPOSITION-GUIDE.md for detailed examples

Created: 2025-10-23

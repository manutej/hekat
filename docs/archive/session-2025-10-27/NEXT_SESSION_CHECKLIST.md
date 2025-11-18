# HEKAT Next Session Checklist

**Created After**: Session 1 Complete
**For**: Session 2 Start
**Estimated Duration**: 4-5 hours

---

## Pre-Session Review (Read First)

Before starting next session, read in this order:
1. ✅ `SESSION_1_SUMMARY.md` (2 min) - What was done
2. ✅ `PHASE_2_IMPLEMENTATION_GUIDE.md` Tasks 2.2 & 2.3 (20 min)
3. ✅ `implementations/classifier.py` (10 min) - Reference implementation

---

## Session 2 Tasks (In Order)

### Task 2.2.1: Create Hotkeys Module (30 minutes)

**File to create**: `implementations/hotkeys.py`

**Copy from classifier.py**:
- `hotkey_to_level()` function (already working ✅)
- `HOTKEY_MATRIX` constant (fully populated ✅)

**Add**:
- `get_hotkey_agents()` - returns agent list for hotkey
- `get_hotkey_description()` - returns description
- `parse_agent_chain()` - parse "R>D>I" chains
- `expand_agent_names()` - map "R" to "deep-researcher"
- Full unit tests

**Success Criteria**:
- [ ] Module imports without errors
- [ ] All hotkeys map correctly (16 total)
- [ ] Agent chains parse correctly (5 patterns)
- [ ] All tests pass

**Time estimate**: 30 min

---

### Task 2.2.2: Create Token Display Module (1 hour)

**File to create**: `implementations/token_display.py`

**Functions**:
- `format_classification_result()` - Clean format display
- `format_verbose_tokens()` - Detailed phase breakdown
- `calculate_variance()` - Token variance analysis
- `display_budget_analysis()` - Budget vs actual
- `get_variance_status()` - ✅ / ⚠️ / ❌ indicator

**Templates to use**: From PHASE_2_IMPLEMENTATION_GUIDE.md → Task 2.3

**Success Criteria**:
- [ ] All functions work
- [ ] Output matches examples in guide
- [ ] Variance calculations correct
- [ ] All tests pass

**Time estimate**: 1 hour

---

### Task 2.2.3: Integrate with /hekat Command (2 hours)

**File to modify**: `~/.claude/commands/hekat.md` implementation

**What to do**:
1. Create command handler that:
   - Calls `classify_query()` from classifier.py
   - Calls `format_classification_result()` from token_display.py
   - Handles `--verbose` flag
   - Displays hotkey suggestion

2. Wire up hotkey matrix:
   - Extract hotkey from user input
   - Map to level
   - Suggest agents

3. Test with real queries:
   - `/hekat "explain JWT"`
   - `/hekat "design auth endpoint"`
   - `/hekat --verbose "your query"`
   - `/hekat [R] "research topic"`
   - `/hekat @L5 "anything"`

**Success Criteria**:
- [ ] `/hekat --help` still works
- [ ] `/hekat "query"` classifies correctly
- [ ] `/hekat --verbose` shows token details
- [ ] `/hekat [R]` maps hotkey correctly
- [ ] `/hekat @L5` forces level
- [ ] Output is clear and helpful

**Time estimate**: 2 hours

---

### Task 2.2.4: Comprehensive Testing (1 hour)

**Create file**: `implementations/test_phase2.py`

**Tests to write**:
```python
class TestComplexityClassifier:
    def test_keyword_classification(self)
    def test_explicit_override(self)
    def test_hotkey_input(self)
    def test_token_downgrade(self)
    def test_confidence_scoring(self)

class TestHotkeyMatrix:
    def test_tier1_hotkeys(self)
    def test_tier2_modifiers(self)
    def test_tier3_chains(self)

class TestTokenDisplay:
    def test_clean_format(self)
    def test_verbose_format(self)
    def test_variance_calculation(self)

class TestIntegration:
    def test_hekat_help(self)
    def test_hekat_classify(self)
    def test_hekat_verbose(self)
    def test_hekat_hotkey(self)
```

**Success Criteria**:
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage > 95%
- [ ] No warnings or errors

**Time estimate**: 1 hour

---

## Detailed Task Breakdown

### 2.2.1: Hotkeys Module Detail

**Extract hotkey to agent**:
```python
HOTKEY_TO_AGENTS = {
    "R": ["deep-researcher"],
    "D": ["api-architect", "debug-detective"],  # context-dependent
    "T": ["test-engineer"],
    # ... etc (16 single keys + modifiers + chains)
}

def get_hotkey_agents(hotkey: str) -> List[str]:
    return HOTKEY_TO_AGENTS.get(hotkey, [])
```

**Parse chains**:
```python
def parse_agent_chain(chain: str) -> dict:
    # Parse "R>D>I" -> ["deep-researcher", "api-architect", "practical-programmer"]
    # Parse "P:R||D||A" -> Parallel pattern
    # Parse "H:R+D→O" -> Hierarchical pattern
```

**Test cases**:
```python
test_cases = [
    ("[R]", ["deep-researcher"], "Single key"),
    ("[D]", ["api-architect", "debug-detective"], "Design hotkey"),
    ("R>D>I", ["deep-researcher", "api-architect", "practical-programmer"], "Chain"),
    ("P:R||D||A", ["deep-researcher", "api-architect", "debug-detective"], "Parallel"),
]
```

---

### 2.2.2: Token Display Module Detail

**Example output**:
```
/hekat --verbose "design auth endpoint"

SELECTION PHASE:
  Input parsing:             [+487 tokens]
  Complexity classification: [+892 tokens]
  Hotkey generation:         [+507 tokens]
  ─────────────────────────────
  Total overhead: 1886 tokens

EXECUTION PLAN:
  Selected: L3 Balanced
  Agents: api-architect → practical-programmer → test-engineer
  Token budget: 3500 (range: 2500-4500)

TOKEN ANALYSIS:
  Available: 50000
  Selection: 1886
  Execution: 3500
  Total: 5386
  Remaining: 44614
  Status: ✅ PROCEED
```

**Key functions**:
```python
def format_token_display(result, verbose=False):
    if not verbose:
        return f"L{level}: Est {est} tokens | Budget {min}-{max} | ✅"
    else:
        return detailed_breakdown()

def calculate_variance(estimated, actual):
    variance = (actual - estimated) / estimated
    if -0.5 <= variance <= 0.10:
        return ("✅", "Excellent", variance)
    elif 0.10 < variance <= 0.20:
        return ("⚠️", "Warning", variance)
    else:
        return ("❌", "Over", variance)
```

---

### 2.2.3: Command Integration Detail

**Add to ~/.claude/commands/hekat.md**:

```python
def hekat_main(user_input: str, verbose: bool = False):
    """Main /hekat command handler"""

    from implementations.classifier import classify_query
    from implementations.token_display import format_token_display
    from implementations.hotkeys import get_hotkey_agents

    # Get available tokens (from Claude context)
    available_tokens = get_available_tokens()

    # Classify query
    result = classify_query(user_input, available_tokens)

    # Get agents for this level
    agents = get_agents_for_level(result.level)

    # Format output
    output = format_token_display(result, verbose)

    # Display result
    print(output)
    print(f"Hotkey suggestion: {suggest_hotkey_for_level(result.level)}")
    print(f"Reasoning: {result.reasoning}")

    return result
```

---

## Success Criteria for Session 2

### By end of session:
- [ ] `/hekat` command fully functional
- [ ] Can classify L1-L7 with high accuracy
- [ ] Hotkey system working (TIER 1-3)
- [ ] Token tracking displays correctly
- [ ] All tests pass (>95% coverage)
- [ ] Documentation updated

### What `/hekat` should do:
```
$ /hekat "explain JWT"
Selected: L1 Ultra-Fast (confidence: 75%)
Hotkey: [R] Research
Reasoning: Keywords suggest L1
Status: ✅ Ready

$ /hekat --verbose "design auth system"
[Shows detailed phase breakdown with tokens]

$ /hekat [Ctrl+H] "your query"
Selected: L5 Hierarchical (confidence: 95%)
[Forced via hotkey]

$ /hekat @L5 "anything"
Selected: L5 Hierarchical (confidence: 100%)
[Explicitly overridden]
```

---

## Time Breakdown

**Total estimated**: 4.5 hours

```
2.2.1 Hotkeys module:         30 min ✏️
2.2.2 Token display module:   1 hour ✏️
2.2.3 Command integration:    2 hours ✏️
2.2.4 Comprehensive testing:  1 hour ✏️
─────────────────────────────
Total:                        4.5 hours
```

---

## Resources Available

**For reference**:
- ✅ `PHASE_2_IMPLEMENTATION_GUIDE.md` - Pseudocode templates
- ✅ `implementations/classifier.py` - Working reference code
- ✅ `QUERY_BUILDER_SPECIFICATION.md` - Technical details
- ✅ `TIER_HOTKEY_REFERENCE.md` - All hotkey definitions

**New templates to create**:
- `implementations/hotkeys.py` (copy hotkey_to_level from classifier)
- `implementations/token_display.py` (use templates from guide)

---

## Dependencies Check

Before starting, verify:
- [ ] Python 3.7+ available
- [ ] Can run: `python3 implementations/classifier.py`
- [ ] All Phase 1 files synced: `ls ~/.claude/commands/hekat.md`
- [ ] Documentation readable: `cat PHASE_2_IMPLEMENTATION_GUIDE.md`

---

## Quick Reference

### Hotkey Coverage (16 hotkeys)
```
TIER 1 (12 keys): R D T B F I O S C P V A
TIER 2 (5 mods):  Ctrl+P Ctrl+H Ctrl+I Ctrl+E Ctrl+F
TIER 3 (3+ chains): R>D>I D>I>T P:R||D||A H:R+D→O I:D→P→T
```

### Token Budgets
```
L1:  600-1200     L2: 1500-3000   L3: 2500-4500
L4: 3000-6000     L5: 5500-9000   L6: 8000-12000
L7: 12000-22000
```

### Keywords
```
L7: build from scratch production
L6: refactor optimize iterate
L5: architect design system microservices
L4: compare evaluate options
L3: design implement test
L2: then and then followed by
L1: explain understand what how
```

---

## Troubleshooting

If something doesn't work:

1. **Hotkey not mapping**: Check `hotkey_to_level()` in classifier.py
2. **Token display wrong**: Review `TOKEN_BUDGETS` dict in classifier.py
3. **Classification inaccurate**: Check keywords in KEYWORDS dict
4. **Integration failing**: Verify imports and file paths

---

## Next Phase After Session 2

Once Phase 2 complete:
- Phase 3: Consciousness learning (2-3 weeks)
- Phase 3: DSL parser (2-3 weeks)
- Phase 3: Fallback mechanisms (1 week)
- Phase 4: Production polish (1-2 weeks)

---

## Session 2 Exit Criteria

You'll know you're done when:

✅ `/hekat "explain JWT"` → Classifies to L1
✅ `/hekat "design auth"` → Classifies to L5
✅ `/hekat [R] "query"` → Respects hotkey
✅ `/hekat @L7 "query"` → Forces level
✅ `/hekat --verbose "query"` → Shows tokens
✅ All 11 original classifier tests still pass
✅ 10+ new hotkey/display tests pass
✅ Documentation updated

---

**Created**: 2025-10-27
**Next Review**: Start of Session 2
**Status**: Ready to continue

Good luck! 🚀

"""
HEKAT Query Classifier - Task 2.1 Implementation + Phase 3 Consciousness
Classifies queries to complexity levels L1-L7 based on keywords, consciousness patterns, and token budgets.
Phase 3: Integrates consciousness learning for pattern matching and confidence enhancement.
"""

import re
from typing import Dict, Tuple, Optional, List
from consciousness import ConsciousnessSystem, ConsciousnessExplainer


# Token budgets per level
TOKEN_BUDGETS = {
    1: (600, 1200),
    2: (1500, 3000),
    3: (2500, 4500),
    4: (3000, 6000),
    5: (5500, 9000),
    6: (8000, 12000),
    7: (12000, 22000)
}

# Keywords that trigger each level
KEYWORDS = {
    7: {
        "build", "from scratch", "complete", "full platform",
        "production", "entire system", "startup", "enterprise"
    },
    6: {
        "refactor", "optimize", "improve", "debug",
        "iterate", "until", "refine", "enhance",
        "converge", "fix and verify"
    },
    5: {
        "architect", "design system", "microservices",
        "infrastructure", "platform", "system design",
        "large scale", "scalability"
    },
    4: {
        "compare", "evaluate", "versus", "pros and cons",
        "options", "alternatives", "perspectives",
        "analysis", "benchmark"
    },
    3: {
        "design", "implement", "test", "build feature",
        "create endpoint", "develop", "develop and test"
    },
    2: {
        "then", "and then", "next", "followed by",
        "fix and", "design and", "document",
        "build after", "then test"
    },
    1: {
        "explain", "understand", "what is", "how does",
        "tell me", "show me", "list", "summarize",
        "describe", "clarify", "define"
    }
}

# Level descriptions
LEVEL_NAMES = {
    1: "Ultra-Fast",
    2: "Fast Chain",
    3: "Balanced",
    4: "Parallel Consensus",
    5: "Hierarchical",
    6: "Iterative",
    7: "Full Ensemble"
}

# Hotkey suggestions per level
HOTKEY_SUGGESTIONS = {
    1: {"hotkey": "[R]", "name": "Research", "tier": "TIER 1"},
    2: {"hotkey": "[D]", "name": "Design", "tier": "TIER 1"},
    3: {"hotkey": "[D>I>T]", "name": "Design→Implement→Test", "tier": "TIER 3"},
    4: {"hotkey": "[P]", "name": "Parallel", "tier": "TIER 1"},
    5: {"hotkey": "[Ctrl+H]", "name": "Hierarchical", "tier": "TIER 2"},
    6: {"hotkey": "[Ctrl+I]", "name": "Iterative", "tier": "TIER 2"},
    7: {"hotkey": "[Ctrl+E]", "name": "Ensemble", "tier": "TIER 2"}
}


def suggest_hotkey_for_level(level: int, query: str = None) -> Dict:
    """
    Suggest appropriate hotkey for complexity level.

    Args:
        level: Complexity level 1-7
        query: Optional query for context-aware suggestions

    Returns:
        Dictionary with hotkey, name, and tier
    """
    return HOTKEY_SUGGESTIONS.get(level, {"hotkey": f"@L{level}", "name": f"Level {level}", "tier": "OVERRIDE"})


def format_token_display(result: 'ClassificationResult', verbose: bool = False, available_tokens: int = 50000) -> str:
    """
    Format token tracking display.

    Args:
        result: ClassificationResult object
        verbose: Show detailed phase breakdown
        available_tokens: Total available tokens

    Returns:
        Formatted display string
    """
    level = result.level
    confidence = result.confidence
    level_name = LEVEL_NAMES[level]

    min_tokens, max_tokens = TOKEN_BUDGETS[level]
    est_tokens = int((min_tokens + max_tokens) / 2)

    if not verbose:
        # Clean format
        return f"""Selected: L{level} {level_name} ({confidence:.0%} confidence)
Tokens: Est {est_tokens} | Budget {min_tokens}-{max_tokens} | Status: ✅ Ready"""
    else:
        # Verbose format with phase breakdown
        phase_overhead = [487, 892, 507]  # Estimated per phase
        total_overhead = sum(phase_overhead)
        remaining = available_tokens - total_overhead - est_tokens

        return f"""SELECTION PHASE:
  Phase 1: Input parsing       [+{phase_overhead[0]} tokens] ✅
  Phase 2: Complexity classify [+{phase_overhead[1]} tokens] ✅
  Phase 3: Hotkey generation   [+{phase_overhead[2]} tokens] ✅
  ─────────────────────────────
  Total overhead: {total_overhead} tokens

EXECUTION PLAN:
  Selected: L{level} {level_name}
  Token budget: {est_tokens} (range: {min_tokens}-{max_tokens})
  Confidence: {confidence:.0%}

TOKEN BUDGET ANALYSIS:
  Available: {available_tokens}
  Selection: {total_overhead}
  Execution: {est_tokens}
  Total: {total_overhead + est_tokens}
  Remaining: {remaining}
  Status: ✅ PROCEED"""


def classify_by_keywords(query_lower: str) -> int:
    """
    Classify query to level based on keyword matching.
    Checks L7 → L1, returns first match.

    Args:
        query_lower: Query string (lowercase)

    Returns:
        Complexity level 1-7
    """
    # Check L7 → L1 (stop at first match)
    for level in range(7, 0, -1):
        for keyword in KEYWORDS[level]:
            if keyword in query_lower:
                return level

    # Default to L1 if no keywords match
    return 1


def extract_hotkey(user_input: str) -> Optional[str]:
    """
    Extract hotkey from user input like '[R]' or '[Ctrl+H]'

    Args:
        user_input: Input string

    Returns:
        Hotkey string or None
    """
    match = re.search(r'\[([^\]]+)\]', user_input)
    return match.group(1) if match else None


def extract_explicit_level(user_input: str) -> Optional[int]:
    """
    Extract explicit level override like '@L5'

    Args:
        user_input: Input string

    Returns:
        Level 1-7 or None
    """
    match = re.search(r'@L(\d)', user_input)
    if match:
        level = int(match.group(1))
        if 1 <= level <= 7:
            return level
    return None


class ClassificationResult:
    """Result of query classification with Phase 3 consciousness support"""

    def __init__(
        self,
        level: int,
        confidence: float,
        method: str,
        reasoning: str,
        keyword_level: int = None,
        hotkey: str = None,
        downgraded: bool = False,
        consciousness_boost: float = 0.0,
        consciousness_reason: str = None
    ):
        self.level = level
        self.confidence = confidence
        self.method = method
        self.reasoning = reasoning
        self.keyword_level = keyword_level
        self.hotkey = hotkey
        self.downgraded = downgraded
        self.consciousness_boost = consciousness_boost  # Phase 3
        self.consciousness_reason = consciousness_reason  # Phase 3

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "level": self.level,
            "confidence": self.confidence,
            "method": self.method,
            "reasoning": self.reasoning,
            "keyword_level": self.keyword_level,
            "hotkey": self.hotkey,
            "downgraded": self.downgraded,
            "consciousness_boost": self.consciousness_boost,
            "consciousness_reason": self.consciousness_reason,
            "level_name": LEVEL_NAMES.get(self.level, f"L{self.level}")
        }

    def __str__(self) -> str:
        return f"L{self.level} {LEVEL_NAMES[self.level]} (confidence: {self.confidence:.0%})"


def classify_query(
    user_input: str,
    available_tokens: int = 50000,
    consciousness_data: Dict = None
) -> ClassificationResult:
    """
    Classify user query to complexity level L1-L7

    Args:
        user_input: The query string (may include @L5, [R], hotkeys)
        available_tokens: Tokens remaining in context (default 50K)
        consciousness_data: Consciousness patterns (Phase 3)

    Returns:
        ClassificationResult with level, confidence, reasoning
    """

    # STEP 1: Check for explicit level override (@L5)
    explicit_level = extract_explicit_level(user_input)
    if explicit_level:
        return ClassificationResult(
            level=explicit_level,
            confidence=1.0,
            method="explicit_override",
            reasoning=f"User explicitly requested L{explicit_level}",
            keyword_level=None
        )

    # STEP 2: Check for hotkey input ([R], [D], [Ctrl+H], etc.)
    hotkey = extract_hotkey(user_input)
    if hotkey:
        hotkey_level = hotkey_to_level(hotkey)
        if hotkey_level:
            return ClassificationResult(
                level=hotkey_level,
                confidence=0.95,
                method="hotkey",
                reasoning=f"Hotkey [{hotkey}] maps to L{hotkey_level}",
                hotkey=hotkey,
                keyword_level=None
            )

    # STEP 3: Keyword-based classification
    query_lower = user_input.lower()
    keyword_level = classify_by_keywords(query_lower)
    keyword_confidence = 0.75

    # STEP 4: Check consciousness patterns (Phase 3)
    consciousness_boost = 0.0
    consciousness_reason = None
    pattern_level = keyword_level
    pattern_confidence = keyword_confidence
    reasoning = f"Keywords suggest L{keyword_level}"

    # Try to find similar patterns in consciousness
    similar_patterns = ConsciousnessSystem.find_similar_patterns(query_lower, top_n=1)
    if similar_patterns:
        boost, reason = ConsciousnessSystem.get_pattern_confidence_boost(query_lower)
        if boost > 0.0:
            consciousness_boost = boost
            consciousness_reason = reason
            pattern_confidence = min(1.0, keyword_confidence + boost)
            reasoning = f"Keywords suggest L{keyword_level}; {ConsciousnessExplainer.explain_boost(boost, reason)}"

    # STEP 5: Check token budget constraints
    final_level = pattern_level
    downgraded = False

    # Downgrade if insufficient tokens
    while final_level > 1 and TOKEN_BUDGETS[final_level][0] > available_tokens:
        final_level -= 1
        downgraded = True

    # If downgraded, adjust reasoning
    if downgraded:
        reasoning += f"; downgraded to L{final_level} due to token constraint ({available_tokens} tokens available)"

    # Generate hotkey suggestion
    suggested_hotkey = suggest_hotkey_for_level(final_level, user_input)

    result = ClassificationResult(
        level=final_level,
        confidence=pattern_confidence,
        method="keyword + consciousness + budget",
        reasoning=reasoning,
        keyword_level=keyword_level,
        hotkey=suggested_hotkey["hotkey"],
        downgraded=downgraded,
        consciousness_boost=consciousness_boost,
        consciousness_reason=consciousness_reason
    )

    # STEP 6: Record classification in consciousness (Phase 3)
    ConsciousnessSystem.record_classification(
        query=user_input,
        level=final_level,
        confidence=pattern_confidence,
        context="general",
        success=True
    )

    return result


def hotkey_to_level(hotkey: str) -> Optional[int]:
    """
    Map hotkey to complexity level (Task 2.2)

    Args:
        hotkey: Hotkey string like 'R', 'Ctrl+H', 'R>D>I'

    Returns:
        Complexity level 1-7 or None
    """
    HOTKEY_MATRIX = {
        # TIER 1: Single keys
        "R": 1,  # Research
        "D": 3,  # Design (context-dependent: 1-5)
        "T": 1,  # Test
        "B": 2,  # Build
        "F": 2,  # Frontend
        "I": 2,  # Implement
        "O": 5,  # Orchestrate
        "S": 6,  # Synthesize
        "C": 3,  # Code-review
        "P": 4,  # Parallel
        "V": 1,  # Verify
        "A": 1,  # Analyze

        # TIER 2: Ctrl-modifiers
        "Ctrl+P": 4,  # Force L4 Parallel
        "Ctrl+H": 5,  # Force L5 Hierarchical
        "Ctrl+I": 6,  # Force L6 Iterative
        "Ctrl+E": 7,  # Force L7 Ensemble
        "Ctrl+F": 5,  # Force L5 Frontend

        # TIER 3: Agent chains
        "R>D>I": 3,           # Research → Design → Implement
        "D>I>T": 3,           # Design → Implement → Test
        "P:R||D||A": 4,       # Parallel: Research, Design, Analyze
        "H:R+D→O": 5,         # Hierarchical: Research + Design → Orchestrate
        "I:D→P→T": 6,         # Iterative: Design → Parallel → Test
    }

    return HOTKEY_MATRIX.get(hotkey, None)


def get_level_name(level: int) -> str:
    """Get human-readable name for level"""
    return LEVEL_NAMES.get(level, f"L{level}")


def get_token_budget(level: int) -> Tuple[int, int]:
    """Get token budget range for level"""
    return TOKEN_BUDGETS.get(level, (0, 0))


# Test cases (with appropriate token budgets for each level)
TEST_CASES = [
    {
        "query": "explain JWT",
        "tokens": 5000,
        "expected_level": 1,
        "description": "L1 - Single agent research"
    },
    {
        "query": "design and implement auth",
        "tokens": 5000,
        "expected_level": 3,
        "description": "L3 - Design → Implement"
    },
    {
        "query": "compare FastAPI vs Express",
        "tokens": 5000,
        "expected_level": 4,
        "description": "L4 - Parallel consensus"
    },
    {
        "query": "design microservices architecture",
        "tokens": 10000,  # L5 needs 5500-9000
        "expected_level": 5,
        "description": "L5 - System architecture"
    },
    {
        "query": "refactor database queries",
        "tokens": 12000,  # L6 needs 8000-12000
        "expected_level": 6,
        "description": "L6 - Iterative refinement"
    },
    {
        "query": "build SaaS platform from scratch",
        "tokens": 25000,  # L7 needs 12000-22000
        "expected_level": 7,
        "description": "L7 - Full ensemble"
    },
    {
        "query": "@L5 anything at all",
        "tokens": 5000,
        "expected_level": 5,
        "description": "Explicit override @L5"
    },
    {
        "query": "[R] explain JWT",
        "tokens": 5000,
        "expected_level": 1,
        "description": "Hotkey R → L1"
    },
    {
        "query": "[Ctrl+H] some query",
        "tokens": 10000,  # Ensure enough for L5
        "expected_level": 5,
        "description": "Hotkey Ctrl+H → L5"
    },
    {
        "query": "build platform from scratch",
        "tokens": 8000,  # Request L7, but only have 8K → downgrade to L6
        "expected_level": 6,
        "description": "L7 request downgraded to L6 (token budget constraint)"
    },
    {
        "query": "design something complex",
        "tokens": 1000,
        "expected_level": 1,
        "description": "L3 downgraded to L1 (token budget: 1K available)"
    },
]


def run_tests() -> None:
    """Run test suite for classifier"""
    print("\n" + "=" * 80)
    print("HEKAT CLASSIFIER - TEST SUITE")
    print("=" * 80 + "\n")

    passed = 0
    failed = 0

    for i, test_case in enumerate(TEST_CASES, 1):
        query = test_case["query"]
        tokens = test_case["tokens"]
        expected = test_case["expected_level"]
        description = test_case["description"]

        result = classify_query(query, tokens)
        actual = result.level

        if actual == expected:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        print(f"{i:2d}. {status} {description}")
        print(f"    Query: '{query}'")
        print(f"    Expected L{expected}, Got L{actual}")
        print(f"    Confidence: {result.confidence:.0%}")
        print(f"    Reasoning: {result.reasoning}")
        if result.downgraded:
            print(f"    ⚠️  Downgraded due to token constraint")
        print()

    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(TEST_CASES)}")
    accuracy = (passed / len(TEST_CASES)) * 100
    print(f"Accuracy: {accuracy:.1f}%")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    run_tests()

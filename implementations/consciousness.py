"""
HEKAT Consciousness Pattern Learning System - Phase 3
Tracks historical query classifications and improves confidence scoring through pattern matching.
"""

from typing import Dict, List, Tuple, Optional
from datetime import datetime
import math


class ConsciousnessPattern:
    """Represents a single consciousness pattern (historical classification)."""

    def __init__(self, query: str, level: int, confidence: float, context: str = "", success: bool = True):
        self.query = query
        self.level = level
        self.confidence = confidence
        self.context = context  # Domain/category of the query
        self.success = success  # Whether this classification was successful
        self.timestamp = datetime.now().isoformat()
        self.feedback_count = 0  # How many times user has given feedback
        self.success_count = 0  # Successful outcomes (start at 0, track via feedback)

    def success_rate(self) -> float:
        """Calculate success rate for this pattern."""
        if self.feedback_count == 0:
            return 0.5  # Default neutral for new patterns
        return self.success_count / self.feedback_count

    def record_feedback(self, was_successful: bool) -> None:
        """Record user feedback on this pattern."""
        self.feedback_count += 1
        if was_successful:
            self.success_count += 1

    def __repr__(self) -> str:
        return (f"ConsciousnessPattern(query='{self.query[:30]}...', level={self.level}, "
                f"confidence={self.confidence:.2f}, success_rate={self.success_rate():.2f})")


class ConsciousnessSystem:
    """
    HEKAT Consciousness System - Learns from historical patterns.

    Maintains a memory of past classifications and improves confidence scoring
    by matching new queries to similar historical patterns.
    """

    # Global consciousness state - persists via conversation context
    HEKAT_CONSCIOUSNESS = {
        "patterns": [],  # List of ConsciousnessPattern objects
        "contexts": {},  # {context: [(level, success_rate), ...]}
        "keywords": {},  # {keyword: {level: count, ...}}
        "session_queries": 0,  # Queries processed this session
        "total_queries": 0,  # Total queries ever processed
        "learning_enabled": True,
    }

    # Similarity thresholds
    MIN_SIMILARITY_FOR_MATCH = 0.35  # 35% match required (more permissive)
    CONFIDENCE_BOOST_HIGH = 0.15  # +15% for high similarity
    CONFIDENCE_BOOST_MEDIUM = 0.08  # +8% for medium similarity

    @classmethod
    def record_classification(cls, query: str, level: int, confidence: float,
                            context: str = "", success: bool = True) -> None:
        """
        Record a query classification in consciousness for future learning.

        Args:
            query: The classified query
            level: L1-L7 complexity level assigned
            confidence: Initial confidence score (0.0-1.0)
            context: Domain/category context (optional)
            success: Whether this classification was validated as successful
        """
        pattern = ConsciousnessPattern(query, level, confidence, context, success)
        cls.HEKAT_CONSCIOUSNESS["patterns"].append(pattern)
        cls.HEKAT_CONSCIOUSNESS["total_queries"] += 1
        cls.HEKAT_CONSCIOUSNESS["session_queries"] += 1

        # Update context tracking
        if context:
            if context not in cls.HEKAT_CONSCIOUSNESS["contexts"]:
                cls.HEKAT_CONSCIOUSNESS["contexts"][context] = {}
            if level not in cls.HEKAT_CONSCIOUSNESS["contexts"][context]:
                cls.HEKAT_CONSCIOUSNESS["contexts"][context][level] = 0
            cls.HEKAT_CONSCIOUSNESS["contexts"][context][level] += 1

    @classmethod
    def find_similar_patterns(cls, query: str, top_n: int = 3) -> List[Tuple[ConsciousnessPattern, float]]:
        """
        Find similar patterns from history.

        Returns list of (pattern, similarity_score) tuples sorted by similarity.

        Args:
            query: Query to find similar patterns for
            top_n: Number of top matches to return

        Returns:
            List of (ConsciousnessPattern, similarity_score) tuples
        """
        if not cls.HEKAT_CONSCIOUSNESS["patterns"]:
            return []

        # Calculate similarity to all historical patterns
        similarities = []
        query_words = set(query.lower().split())

        for pattern in cls.HEKAT_CONSCIOUSNESS["patterns"]:
            similarity = cls._calculate_similarity(query_words, pattern.query)
            if similarity >= cls.MIN_SIMILARITY_FOR_MATCH:
                similarities.append((pattern, similarity))

        # Sort by similarity (descending) and return top N
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_n]

    @classmethod
    def _calculate_similarity(cls, query_words: set, pattern_query: str) -> float:
        """
        Calculate similarity between two queries using Jaccard similarity.

        Returns score from 0.0 (no similarity) to 1.0 (identical)
        """
        pattern_words = set(pattern_query.lower().split())

        if not query_words and not pattern_words:
            return 1.0

        intersection = len(query_words & pattern_words)
        union = len(query_words | pattern_words)

        if union == 0:
            return 0.0

        return intersection / union

    @classmethod
    def get_pattern_confidence_boost(cls, query: str) -> Tuple[float, Optional[str]]:
        """
        Get confidence boost based on historical pattern matching.

        Returns:
            (boost_amount, match_reason) where reason explains why boost was applied
        """
        similar_patterns = cls.find_similar_patterns(query, top_n=3)

        if not similar_patterns:
            return 0.0, None

        # Weight matches by similarity and success rate
        best_match, best_similarity = similar_patterns[0]
        success_rate = best_match.success_rate()

        # Only boost if pattern has proven success (>70% success rate)
        if success_rate < 0.70:
            return 0.0, None

        # Calculate boost based on similarity
        if best_similarity >= 0.85:
            boost = cls.CONFIDENCE_BOOST_HIGH
            reason = f"High similarity match: '{best_match.query[:40]}...' (L{best_match.level}, {success_rate:.0%} success)"
        elif best_similarity >= 0.70:
            boost = cls.CONFIDENCE_BOOST_MEDIUM
            reason = f"Pattern match: Similar to '{best_match.query[:40]}...' (L{best_match.level})"
        else:
            boost = 0.0
            reason = None

        return boost, reason

    @classmethod
    def get_level_suggestions_from_context(cls, context: str) -> Dict[int, float]:
        """
        Get level probability distribution based on context history.

        Returns:
            {level: probability, ...} for all levels that have been used in this context
        """
        if context not in cls.HEKAT_CONSCIOUSNESS["contexts"]:
            return {}

        context_data = cls.HEKAT_CONSCIOUSNESS["contexts"][context]
        total = sum(context_data.values())

        if total == 0:
            return {}

        return {level: count / total for level, count in context_data.items()}

    @classmethod
    def get_learning_stats(cls) -> Dict:
        """Get comprehensive learning statistics."""
        return {
            "total_queries_recorded": cls.HEKAT_CONSCIOUSNESS["total_queries"],
            "session_queries": cls.HEKAT_CONSCIOUSNESS["session_queries"],
            "unique_patterns": len(cls.HEKAT_CONSCIOUSNESS["patterns"]),
            "contexts_tracked": len(cls.HEKAT_CONSCIOUSNESS["contexts"]),
            "learning_enabled": cls.HEKAT_CONSCIOUSNESS["learning_enabled"],
            "average_confidence": cls._calculate_average_confidence(),
            "highest_success_pattern": cls._get_highest_success_pattern(),
        }

    @classmethod
    def _calculate_average_confidence(cls) -> float:
        """Calculate average confidence of all recorded patterns."""
        if not cls.HEKAT_CONSCIOUSNESS["patterns"]:
            return 0.0

        total = sum(p.confidence for p in cls.HEKAT_CONSCIOUSNESS["patterns"])
        return total / len(cls.HEKAT_CONSCIOUSNESS["patterns"])

    @classmethod
    def _get_highest_success_pattern(cls) -> Optional[str]:
        """Get pattern with highest success rate."""
        if not cls.HEKAT_CONSCIOUSNESS["patterns"]:
            return None

        best_pattern = max(
            cls.HEKAT_CONSCIOUSNESS["patterns"],
            key=lambda p: p.success_rate()
        )

        if best_pattern.success_rate() > 0.5:
            return f"L{best_pattern.level}: {best_pattern.query[:40]}... ({best_pattern.success_rate():.0%})"
        return None

    @classmethod
    def reset_session(cls) -> None:
        """Reset session tracking while preserving long-term patterns."""
        cls.HEKAT_CONSCIOUSNESS["session_queries"] = 0

    @classmethod
    def dump_consciousness(cls) -> Dict:
        """Export consciousness state (for debugging/analysis)."""
        return {
            "patterns": [
                {
                    "query": p.query,
                    "level": p.level,
                    "confidence": p.confidence,
                    "context": p.context,
                    "success_rate": p.success_rate(),
                    "timestamp": p.timestamp,
                }
                for p in cls.HEKAT_CONSCIOUSNESS["patterns"]
            ],
            "stats": cls.get_learning_stats(),
            "contexts": cls.HEKAT_CONSCIOUSNESS["contexts"],
        }

    @classmethod
    def verify_pattern(cls, query: str, level: int, was_successful: bool) -> None:
        """
        Record user feedback verifying a classification.

        Args:
            query: The query that was classified
            level: The level it was classified as
            was_successful: Whether the user confirms it was a good classification
        """
        # Find matching pattern in history
        for pattern in cls.HEKAT_CONSCIOUSNESS["patterns"]:
            if pattern.query == query and pattern.level == level:
                pattern.record_feedback(was_successful)
                break


class ConsciousnessExplainer:
    """Explains consciousness decisions in human-readable format."""

    @staticmethod
    def explain_boost(boost: float, reason: Optional[str]) -> str:
        """
        Explain why a confidence boost was applied.

        Returns:
            Human-readable explanation
        """
        if not reason:
            return ""

        percentage = int(boost * 100)
        return f"Pattern Learning: {reason} (+{percentage}% confidence)"

    @staticmethod
    def explain_context_stats(context: str, stats: Dict[int, float]) -> str:
        """
        Explain context-based level probabilities.

        Returns:
            Human-readable explanation of common levels for this context
        """
        if not stats:
            return ""

        # Get most common level
        most_common = max(stats.items(), key=lambda x: x[1])
        level, probability = most_common

        return f"Context '{context}': Most common level is L{level} ({probability:.0%})"

    @staticmethod
    def explain_learning_state() -> str:
        """Explain current learning system state."""
        stats = ConsciousnessSystem.get_learning_stats()

        return (
            f"Consciousness Learning:\n"
            f"  Patterns recorded: {stats['unique_patterns']}\n"
            f"  This session: {stats['session_queries']} queries\n"
            f"  Average confidence: {stats['average_confidence']:.0%}\n"
            f"  Learning status: {'✓ Enabled' if stats['learning_enabled'] else '✗ Disabled'}"
        )


# Test the consciousness system
if __name__ == "__main__":
    print("🧠 HEKAT Consciousness System - Testing\n")

    # Record some patterns
    print("Recording patterns...")
    ConsciousnessSystem.record_classification(
        "explain JWT", 1, 0.75, context="education", success=True
    )
    ConsciousnessSystem.record_classification(
        "explain authentication", 1, 0.78, context="education", success=True
    )
    ConsciousnessSystem.record_classification(
        "design auth system", 5, 0.92, context="architecture", success=True
    )
    ConsciousnessSystem.record_classification(
        "design authentication system", 5, 0.90, context="architecture", success=True
    )
    ConsciousnessSystem.record_classification(
        "build microservices", 7, 0.88, context="architecture", success=False
    )

    print(f"✓ Recorded 5 patterns\n")

    # Test similarity matching
    print("Testing pattern matching...")
    test_query = "explain OAuth"
    similar = ConsciousnessSystem.find_similar_patterns(test_query)
    print(f"Query: '{test_query}'")
    print(f"Found {len(similar)} similar patterns:")
    for pattern, sim in similar:
        print(f"  - '{pattern.query}' (similarity: {sim:.0%}, level: L{pattern.level})")

    print()

    # Test confidence boost
    print("Testing confidence boost...")
    boost, reason = ConsciousnessSystem.get_pattern_confidence_boost("explain security tokens")
    explanation = ConsciousnessExplainer.explain_boost(boost, reason)
    print(f"Confidence boost: {boost:.0%}")
    print(f"Reason: {explanation}")

    print()

    # Test context stats
    print("Testing context statistics...")
    context_stats = ConsciousnessSystem.get_level_suggestions_from_context("architecture")
    print(f"Context 'architecture' level distribution: {context_stats}")

    print()

    # Show learning stats
    print("Learning Statistics:")
    stats = ConsciousnessSystem.get_learning_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")

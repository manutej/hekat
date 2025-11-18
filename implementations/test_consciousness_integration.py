"""
Phase 3: Consciousness Pattern Learning Integration Tests
Tests consciousness learning, pattern matching, and confidence boosting
"""

from classifier import classify_query, LEVEL_NAMES, ClassificationResult
from consciousness import ConsciousnessSystem, ConsciousnessPattern, ConsciousnessExplainer
import json


class TestConsciousnessIntegration:
    """Test suite for consciousness learning integration"""

    def __init__(self):
        self.test_results = []
        self.passed = 0
        self.failed = 0

    def assert_equal(self, actual, expected, test_name: str) -> bool:
        """Helper for assertions"""
        if actual == expected:
            self.passed += 1
            print(f"  ✓ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}: expected {expected}, got {actual}")
            return False

    def assert_true(self, condition, test_name: str) -> bool:
        """Helper for boolean assertions"""
        if condition:
            self.passed += 1
            print(f"  ✓ {test_name}")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}")
            return False

    def assert_range(self, actual, min_val, max_val, test_name: str) -> bool:
        """Helper for range assertions"""
        if min_val <= actual <= max_val:
            self.passed += 1
            print(f"  ✓ {test_name} (value: {actual:.2f})")
            return True
        else:
            self.failed += 1
            print(f"  ❌ {test_name}: expected {min_val}-{max_val}, got {actual}")
            return False

    def test_pattern_recording(self):
        """Test 1: Pattern recording"""
        print("\n📝 Test 1: Pattern Recording")
        print("-" * 50)

        # Reset consciousness
        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"] = []

        # Record patterns
        ConsciousnessSystem.record_classification("test query", 3, 0.85, "testing")
        self.assert_equal(
            len(ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"]),
            1,
            "Pattern count after recording"
        )

        # Record another
        ConsciousnessSystem.record_classification("another query", 5, 0.90, "testing")
        self.assert_equal(
            len(ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"]),
            2,
            "Pattern count after second recording"
        )

        # Check total queries counter
        self.assert_equal(
            ConsciousnessSystem.HEKAT_CONSCIOUSNESS["total_queries"],
            2,
            "Total queries counter"
        )

    def test_consciousness_fields_in_result(self):
        """Test 2: Consciousness fields in ClassificationResult"""
        print("\n🧠 Test 2: Consciousness Fields in Result")
        print("-" * 50)

        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"] = []

        # Classify a query
        result = classify_query("explain JWT")

        # Check result has consciousness fields
        self.assert_true(
            hasattr(result, 'consciousness_boost'),
            "Result has consciousness_boost field"
        )
        self.assert_true(
            hasattr(result, 'consciousness_reason'),
            "Result has consciousness_reason field"
        )

        # Check pattern was recorded
        self.assert_equal(
            len(ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"]),
            1,
            "Pattern recorded after classification"
        )

    def test_pattern_creation(self):
        """Test 3: Pattern object creation"""
        print("\n🔍 Test 3: Pattern Object Creation")
        print("-" * 50)

        pattern = ConsciousnessPattern("test query", 3, 0.85, "testing", True)

        self.assert_equal(pattern.query, "test query", "Pattern query stored")
        self.assert_equal(pattern.level, 3, "Pattern level stored")
        self.assert_equal(pattern.confidence, 0.85, "Pattern confidence stored")
        self.assert_equal(pattern.context, "testing", "Pattern context stored")
        self.assert_equal(pattern.success, True, "Pattern success flag stored")

    def test_pattern_success_rate(self):
        """Test 4: Pattern success rate calculation"""
        print("\n📊 Test 4: Pattern Success Rate")
        print("-" * 50)

        pattern = ConsciousnessPattern("test", 3, 0.80, success=True)

        # New pattern should have neutral rate
        self.assert_range(
            pattern.success_rate(),
            0.49,
            0.51,
            "New pattern success rate (neutral)"
        )

        # Record feedback
        pattern.record_feedback(True)
        pattern.record_feedback(True)
        pattern.record_feedback(False)

        # Now should reflect feedback
        expected = 2 / 3  # 2 successes out of 3
        self.assert_range(
            pattern.success_rate(),
            expected - 0.01,
            expected + 0.01,
            "Success rate after feedback"
        )

    def test_learning_statistics(self):
        """Test 5: Learning statistics collection"""
        print("\n📈 Test 5: Learning Statistics")
        print("-" * 50)

        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"] = []
        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["total_queries"] = 0
        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["session_queries"] = 0

        # Record several patterns
        for i in range(5):
            classify_query(f"query {i}")

        stats = ConsciousnessSystem.get_learning_stats()

        self.assert_equal(stats["unique_patterns"], 5, "Unique patterns count")
        self.assert_equal(stats["total_queries_recorded"], 5, "Total queries count")
        self.assert_equal(stats["session_queries"], 5, "Session queries count")
        self.assert_true(
            stats["learning_enabled"],
            "Learning enabled"
        )

    def test_context_tracking(self):
        """Test 6: Context-based level tracking"""
        print("\n🏷️  Test 6: Context Tracking")
        print("-" * 50)

        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"] = []
        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["contexts"] = {}

        # Record patterns with different contexts
        ConsciousnessSystem.record_classification("q1", 1, 0.8, "education")
        ConsciousnessSystem.record_classification("q2", 1, 0.8, "education")
        ConsciousnessSystem.record_classification("q3", 5, 0.8, "architecture")

        # Check context tracking
        self.assert_true(
            "education" in ConsciousnessSystem.HEKAT_CONSCIOUSNESS["contexts"],
            "Education context tracked"
        )
        self.assert_true(
            "architecture" in ConsciousnessSystem.HEKAT_CONSCIOUSNESS["contexts"],
            "Architecture context tracked"
        )

        # Get context stats
        edu_stats = ConsciousnessSystem.get_level_suggestions_from_context("education")
        self.assert_equal(
            len(edu_stats),
            1,
            "Education context has L1 entries"
        )

    def test_similarity_matching(self):
        """Test 7: Similarity calculation and matching"""
        print("\n🔄 Test 7: Similarity Matching")
        print("-" * 50)

        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"] = []

        # Record base patterns
        ConsciousnessSystem.record_classification("explain authentication", 1, 0.8)
        ConsciousnessSystem.record_classification("design system", 5, 0.8)

        # Find similar patterns
        similar = ConsciousnessSystem.find_similar_patterns("explain security")
        self.assert_equal(
            len(similar) > 0,
            True,
            "Found similar patterns"
        )

        # Check similarity score
        if similar:
            pattern, similarity = similar[0]
            self.assert_true(
                0.0 <= similarity <= 1.0,
                f"Similarity score in valid range (got {similarity:.2f})"
            )

    def test_consciousness_explainer(self):
        """Test 8: Consciousness Explainer"""
        print("\n📢 Test 8: Consciousness Explainer")
        print("-" * 50)

        # Test boost explanation
        explanation = ConsciousnessExplainer.explain_boost(0.15, "Pattern match: 'test' (L3, 85% success)")
        self.assert_true(
            "Pattern Learning" in explanation,
            "Boost explanation contains 'Pattern Learning'"
        )
        self.assert_true(
            "+15%" in explanation,
            "Boost explanation shows percentage"
        )

        # Test learning state explanation
        state_explanation = ConsciousnessExplainer.explain_learning_state()
        self.assert_true(
            "Consciousness Learning" in state_explanation,
            "State explanation contains 'Consciousness Learning'"
        )

    def test_pattern_feedback(self):
        """Test 9: Pattern feedback recording"""
        print("\n💬 Test 9: Pattern Feedback")
        print("-" * 50)

        pattern = ConsciousnessPattern("test", 3, 0.8, success=True)

        # Initial feedback count should be 0
        self.assert_equal(
            pattern.feedback_count,
            0,
            "Initial feedback count"
        )

        # Record feedback
        pattern.record_feedback(True)
        self.assert_equal(
            pattern.feedback_count,
            1,
            "Feedback count after recording"
        )

        # Record more feedback
        pattern.record_feedback(True)
        pattern.record_feedback(False)
        self.assert_equal(
            pattern.feedback_count,
            3,
            "Feedback count after multiple records"
        )
        self.assert_equal(
            pattern.success_count,
            2,
            "Success count reflects positive feedback"
        )

    def test_consciousness_integration_flow(self):
        """Test 10: Full consciousness integration flow"""
        print("\n🔁 Test 10: Full Integration Flow")
        print("-" * 50)

        ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"] = []

        # Classify multiple related queries
        q1 = classify_query("explain JWT")
        q2 = classify_query("explain authentication")
        q3 = classify_query("explain OAuth")

        # Check that all are recorded
        self.assert_equal(
            len(ConsciousnessSystem.HEKAT_CONSCIOUSNESS["patterns"]),
            3,
            "All queries recorded in consciousness"
        )

        # All should be L1 based on keywords
        self.assert_equal(q1.level, 1, "Query 1 classified as L1")
        self.assert_equal(q2.level, 1, "Query 2 classified as L1")
        self.assert_equal(q3.level, 1, "Query 3 classified as L1")

        # All should have classifier confidence
        self.assert_true(
            q1.confidence > 0,
            "Query 1 has confidence score"
        )

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 70)
        print("🧠 HEKAT CONSCIOUSNESS INTEGRATION TESTS")
        print("=" * 70)

        self.test_pattern_recording()
        self.test_consciousness_fields_in_result()
        self.test_pattern_creation()
        self.test_pattern_success_rate()
        self.test_learning_statistics()
        self.test_context_tracking()
        self.test_similarity_matching()
        self.test_consciousness_explainer()
        self.test_pattern_feedback()
        self.test_consciousness_integration_flow()

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        total = self.passed + self.failed
        print(f"Total Tests: {total}")
        print(f"✓ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        print(f"Success Rate: {(self.passed / total * 100):.0f}%")
        print("=" * 70 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    tester = TestConsciousnessIntegration()
    success = tester.run_all_tests()
    exit(0 if success else 1)

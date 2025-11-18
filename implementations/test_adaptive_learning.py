"""
Phase 5: Adaptive Learning System Tests
Tests prediction algorithms, trend analysis, and budget alerts
"""

from adaptive_learning import (
    AdaptiveBudgetSystem,
    BudgetPredictor,
    TrendAnalyzer,
    TokenPrediction,
    TrendAnalysis,
    BudgetAlert
)


class TestAdaptiveLearning:
    """Test suite for adaptive learning system"""

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

    def test_token_prediction_simple(self):
        """Test 1: Simple token prediction"""
        print("\n📊 Test 1: Token Prediction - Simple")
        print("-" * 50)

        history = [2000, 2100, 2050, 2150, 2080]
        prediction = BudgetPredictor.predict_budget(history, "explain JWT", 1)

        self.assert_range(prediction.predicted_tokens, 2000, 2150, "Predicted tokens in range")
        self.assert_range(prediction.confidence, 0.5, 1.0, "Confidence reasonable")
        self.assert_true(prediction.min_tokens < prediction.max_tokens, "Range valid (min < max)")

    def test_token_prediction_minimal(self):
        """Test 2: Prediction with minimal history"""
        print("\n📊 Test 2: Token Prediction - Minimal Data")
        print("-" * 50)

        history = [2500]
        prediction = BudgetPredictor.predict_budget(history, "test", 1)

        self.assert_equal(prediction.samples, 1, "Samples recorded")
        self.assert_true(prediction.confidence < 0.5, "Low confidence for single sample")

    def test_trend_analysis_increasing(self):
        """Test 3: Trend analysis - increasing"""
        print("\n📈 Test 3: Trend Analysis - Increasing")
        print("-" * 50)

        history = [2000, 2200, 2400, 2600, 2800]
        trend = TrendAnalyzer.analyze_trend(history)

        self.assert_equal(trend.trend, "increasing", "Trend detected as increasing")
        self.assert_range(trend.trend_percentage, 5, 20, "Trend percentage reasonable")
        self.assert_true(trend.forecasted_next > history[-1], "Forecast higher than last value")

    def test_trend_analysis_decreasing(self):
        """Test 4: Trend analysis - decreasing"""
        print("\n📈 Test 4: Trend Analysis - Decreasing")
        print("-" * 50)

        history = [3000, 2700, 2400, 2100, 1800]
        trend = TrendAnalyzer.analyze_trend(history)

        self.assert_equal(trend.trend, "decreasing", "Trend detected as decreasing")
        self.assert_true(trend.trend_percentage < -5, "Negative trend percentage")

    def test_trend_analysis_stable(self):
        """Test 5: Trend analysis - stable"""
        print("\n📈 Test 5: Trend Analysis - Stable")
        print("-" * 50)

        history = [2050, 2040, 2060, 2045, 2055]
        trend = TrendAnalyzer.analyze_trend(history)

        self.assert_equal(trend.trend, "stable", "Trend detected as stable")
        self.assert_range(trend.trend_percentage, -5, 5, "Trend % minimal")

    def test_trend_consistency(self):
        """Test 6: Trend analysis - consistency score"""
        print("\n📈 Test 6: Trend Consistency")
        print("-" * 50)

        # Very consistent
        consistent = [2000, 2010, 2005, 2015, 2008]
        trend_consistent = TrendAnalyzer.analyze_trend(consistent)

        # Very volatile
        volatile = [1000, 3000, 1500, 3500, 1000]
        trend_volatile = TrendAnalyzer.analyze_trend(volatile)

        self.assert_true(
            trend_consistent.consistency > trend_volatile.consistency,
            "Consistency properly measured"
        )

    def test_predictor_with_context(self):
        """Test 7: Prediction with context adjustment"""
        print("\n🎯 Test 7: Context-Aware Prediction")
        print("-" * 50)

        history = [2000, 2100, 2050]

        # Education context (should be lower)
        pred_education = BudgetPredictor.predict_with_context(
            history, 1, context="education"
        )

        # Architecture context (should be higher)
        pred_architecture = BudgetPredictor.predict_with_context(
            history, 1, context="architecture"
        )

        self.assert_true(
            pred_education.predicted_tokens < pred_architecture.predicted_tokens,
            "Context adjusts predictions (education < architecture)"
        )

    def test_adaptive_budget_update(self):
        """Test 8: Adaptive budget system update"""
        print("\n🔧 Test 8: Adaptive Budget System")
        print("-" * 50)

        # Clear state
        AdaptiveBudgetSystem.PATTERN_PREDICTIONS.clear()

        history = [2000, 2100, 2050, 2150, 2080]
        prediction = AdaptiveBudgetSystem.update_prediction(
            "test_pattern",
            history,
            "explain JWT",
            1
        )

        retrieved = AdaptiveBudgetSystem.get_prediction("test_pattern")
        self.assert_true(retrieved is not None, "Prediction stored and retrieved")
        self.assert_equal(retrieved.pattern_query, "explain JWT", "Pattern query preserved")

    def test_budget_violation_warning(self):
        """Test 9: Budget violation - warning"""
        print("\n⚠️ Test 9: Budget Violation - Warning")
        print("-" * 50)

        AdaptiveBudgetSystem.PATTERN_PREDICTIONS.clear()
        AdaptiveBudgetSystem.PATTERN_ALERTS.clear()

        history = [2000, 2100, 2050]
        AdaptiveBudgetSystem.update_prediction(
            "test_pattern",
            history,
            "explain JWT",
            1
        )

        # Get the prediction to know the budget
        prediction = AdaptiveBudgetSystem.get_prediction("test_pattern")
        budget = prediction.predicted_tokens

        # Calculate tokens that are 18% over budget (between 15-30%)
        warning_tokens = int(budget * 1.18)

        alert = AdaptiveBudgetSystem.check_budget_violation(
            "test_pattern",
            actual_tokens=warning_tokens
        )

        self.assert_true(alert is not None, "Alert created for overage")
        self.assert_equal(alert.severity, "warning", "Severity is warning")

    def test_budget_violation_critical(self):
        """Test 10: Budget violation - critical"""
        print("\n❌ Test 10: Budget Violation - Critical")
        print("-" * 50)

        AdaptiveBudgetSystem.PATTERN_PREDICTIONS.clear()
        AdaptiveBudgetSystem.PATTERN_ALERTS.clear()

        history = [2000, 2100, 2050]
        AdaptiveBudgetSystem.update_prediction(
            "test_pattern",
            history,
            "explain JWT",
            1
        )

        # Get the prediction to know the budget
        prediction = AdaptiveBudgetSystem.get_prediction("test_pattern")
        budget = prediction.predicted_tokens

        # Calculate tokens that are 35% over budget (>30%)
        critical_tokens = int(budget * 1.35)

        alert = AdaptiveBudgetSystem.check_budget_violation(
            "test_pattern",
            actual_tokens=critical_tokens
        )

        self.assert_true(alert is not None, "Alert created for critical overage")
        self.assert_equal(alert.severity, "critical", "Severity is critical")

    def test_alert_retrieval(self):
        """Test 11: Alert retrieval and filtering"""
        print("\n📋 Test 11: Alert Retrieval")
        print("-" * 50)

        AdaptiveBudgetSystem.PATTERN_ALERTS.clear()
        AdaptiveBudgetSystem.PATTERN_PREDICTIONS.clear()

        # Create some alerts
        for i in range(3):
            history = [2000 + i * 100, 2100 + i * 100]
            AdaptiveBudgetSystem.update_prediction(
                f"pattern_{i}",
                history,
                f"query_{i}",
                1
            )
            AdaptiveBudgetSystem.check_budget_violation(f"pattern_{i}", 2500 + i * 100)

        # Get all alerts
        all_alerts = AdaptiveBudgetSystem.get_alerts()
        self.assert_equal(len(all_alerts), 3, "All alerts retrieved")

        # Get by severity
        warnings = AdaptiveBudgetSystem.get_alerts(severity="warning")
        self.assert_true(len(warnings) > 0, "Warnings filtered")

    def test_critical_patterns(self):
        """Test 12: Critical patterns identification"""
        print("\n🔴 Test 12: Critical Patterns")
        print("-" * 50)

        AdaptiveBudgetSystem.PATTERN_ALERTS.clear()
        AdaptiveBudgetSystem.PATTERN_PREDICTIONS.clear()

        # Create patterns with different severities
        for i in range(2):
            history = [2000, 2100, 2050]
            AdaptiveBudgetSystem.update_prediction(
                f"critical_{i}",
                history,
                f"critical_query_{i}",
                1
            )
            # Create critical alert (>30% over budget)
            AdaptiveBudgetSystem.check_budget_violation(f"critical_{i}", 2800)

        critical = AdaptiveBudgetSystem.get_critical_patterns()
        self.assert_equal(len(critical), 2, "Critical patterns identified")

    def test_trend_update(self):
        """Test 13: Trend analysis storage and update"""
        print("\n📈 Test 13: Trend Update")
        print("-" * 50)

        AdaptiveBudgetSystem.PATTERN_TRENDS.clear()

        history = [2000, 2200, 2400, 2600, 2800]
        trend = AdaptiveBudgetSystem.update_trend(
            "trend_test",
            history,
            pattern_query="explain something",
            pattern_level=2
        )

        retrieved = AdaptiveBudgetSystem.get_trend("trend_test")
        self.assert_true(retrieved is not None, "Trend stored and retrieved")
        self.assert_equal(retrieved.trend, "increasing", "Trend analysis preserved")

    def test_state_export(self):
        """Test 14: Complete state export"""
        print("\n💾 Test 14: State Export")
        print("-" * 50)

        state = AdaptiveBudgetSystem.dump_state()

        self.assert_true("predictions" in state, "Predictions in state")
        self.assert_true("trends" in state, "Trends in state")
        self.assert_true("alerts" in state, "Alerts in state")
        self.assert_true("timestamp" in state, "Timestamp in state")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 70)
        print("🧠 HEKAT ADAPTIVE LEARNING SYSTEM TESTS")
        print("=" * 70)

        self.test_token_prediction_simple()
        self.test_token_prediction_minimal()
        self.test_trend_analysis_increasing()
        self.test_trend_analysis_decreasing()
        self.test_trend_analysis_stable()
        self.test_trend_consistency()
        self.test_predictor_with_context()
        self.test_adaptive_budget_update()
        self.test_budget_violation_warning()
        self.test_budget_violation_critical()
        self.test_alert_retrieval()
        self.test_critical_patterns()
        self.test_trend_update()
        self.test_state_export()

        # Print summary
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        total = self.passed + self.failed
        print(f"Total Tests: {total}")
        print(f"✓ Passed: {self.passed}")
        print(f"❌ Failed: {self.failed}")
        if total > 0:
            print(f"Success Rate: {(self.passed / total * 100):.0f}%")
        print("=" * 70 + "\n")

        return self.failed == 0


if __name__ == "__main__":
    tester = TestAdaptiveLearning()
    success = tester.run_all_tests()
    exit(0 if success else 1)

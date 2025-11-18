"""
Phase 4: Task-Relay Consciousness Integration Tests
Tests checkpoint tracking, pattern efficiency, and token accounting
"""

from task_relay_consciousness import (
    TaskRelayConsciousnessIntegration,
    RelayCheckpoint,
    ConsciousnessCheckpoint,
    PatternEfficiency,
    TokenCheckpoint
)


class TestTaskRelayConsciousnessIntegration:
    """Test suite for Task-Relay Consciousness integration"""

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

    def test_token_checkpoint_creation(self):
        """Test 1: Token checkpoint creation"""
        print("\n📊 Test 1: Token Checkpoint Creation")
        print("-" * 50)

        cp = TokenCheckpoint(
            phase="selection",
            pre_tokens=50000,
            post_tokens=49500,
            description="Input parsing and classification"
        )

        self.assert_equal(cp.delta, -500, "Delta calculation")
        self.assert_equal(cp.phase, "selection", "Phase tracking")
        self.assert_range(cp.percentage_of_budget, 0.009, 0.011, "Percentage calculation")

    def test_consciousness_checkpoint(self):
        """Test 2: Consciousness checkpoint creation"""
        print("\n🧠 Test 2: Consciousness Checkpoint")
        print("-" * 50)

        cp = ConsciousnessCheckpoint(
            pattern_matched=True,
            pattern_query="explain JWT",
            pattern_level=1,
            pattern_success_rate=0.85,
            confidence_boost=0.15,
            context="education"
        )

        self.assert_equal(cp.pattern_matched, True, "Pattern matched flag")
        self.assert_equal(cp.pattern_level, 1, "Pattern level")
        self.assert_range(cp.pattern_success_rate, 0.84, 0.86, "Success rate")

        cp_dict = cp.to_dict()
        self.assert_true("pattern_query" in cp_dict, "Serialization includes query")

    def test_relay_checkpoint_variance(self):
        """Test 3: Relay checkpoint variance calculation"""
        print("\n📈 Test 3: Relay Checkpoint Variance")
        print("-" * 50)

        cp = RelayCheckpoint(
            relay_number=1,
            agent_name="researcher",
            timestamp="2025-10-27T12:00:00",
            token=TokenCheckpoint(
                phase="relay_1_researcher",
                pre_tokens=50000,
                post_tokens=47500,
                description="Researcher execution"
            ),
            consciousness=ConsciousnessCheckpoint(pattern_matched=False),
            expected_tokens=2500
        )

        cp.calculate_variance()

        # (2500 - 2500) / 2500 = 0%
        self.assert_range(cp.variance, -0.1, 0.1, "Variance for expected execution")
        self.assert_equal(cp.variance_status(), "✅", "Status is excellent")

    def test_relay_checkpoint_over_budget(self):
        """Test 4: Relay checkpoint over budget variance"""
        print("\n⚠️ Test 4: Over-Budget Variance")
        print("-" * 50)

        cp = RelayCheckpoint(
            relay_number=2,
            agent_name="designer",
            timestamp="2025-10-27T12:00:01",
            token=TokenCheckpoint(
                phase="relay_2_designer",
                pre_tokens=47500,
                post_tokens=44200,
                description="Designer execution"
            ),
            consciousness=ConsciousnessCheckpoint(pattern_matched=False),
            expected_tokens=2800
        )

        cp.calculate_variance()
        # 3300 tokens used vs 2800 expected = 17.8% over

        self.assert_true(cp.variance > 10, "Variance detects over-budget")
        self.assert_equal(cp.variance_status(), "⚠️", "Status is warning")

    def test_pattern_efficiency_single_execution(self):
        """Test 5: Pattern efficiency - single execution"""
        print("\n⚡ Test 5: Pattern Efficiency - Single Execution")
        print("-" * 50)

        eff = PatternEfficiency(
            pattern_query="explain authentication",
            pattern_level=1,
            pattern_success_rate=0.85
        )

        eff.record_execution(actual_tokens=2000, expected_tokens=2500)

        self.assert_equal(eff.execution_count, 1, "Execution count incremented")
        self.assert_equal(eff.avg_tokens_used, 2000.0, "Average tokens used")
        self.assert_range(eff.avg_efficiency_ratio, 0.79, 0.81, "Efficiency ratio (80%)")
        self.assert_equal(eff.efficiency_status, "🟢 EFFICIENT", "Efficient status")

    def test_pattern_efficiency_multiple_executions(self):
        """Test 6: Pattern efficiency - multiple executions"""
        print("\n⚡ Test 6: Pattern Efficiency - Multiple Executions")
        print("-" * 50)

        eff = PatternEfficiency(
            pattern_query="design system",
            pattern_level=5,
            pattern_success_rate=0.92
        )

        # Record 3 executions
        eff.record_execution(actual_tokens=5200, expected_tokens=5500)
        eff.record_execution(actual_tokens=5400, expected_tokens=5500)
        eff.record_execution(actual_tokens=5300, expected_tokens=5500)

        self.assert_equal(eff.execution_count, 3, "Execution count")
        self.assert_range(eff.avg_tokens_used, 5299, 5301, "Average tokens")
        self.assert_range(eff.avg_efficiency_ratio, 0.963, 0.965, "Avg efficiency ratio")
        self.assert_equal(eff.efficiency_status, "🟡 ON_BUDGET", "On-budget status")

    def test_pattern_efficiency_over_budget_multiple(self):
        """Test 7: Pattern efficiency - over budget"""
        print("\n⚡ Test 7: Pattern Efficiency - Over Budget")
        print("-" * 50)

        eff = PatternEfficiency(
            pattern_query="build platform",
            pattern_level=7,
            pattern_success_rate=0.75
        )

        # Record executions that consistently exceed budget
        eff.record_execution(actual_tokens=14000, expected_tokens=12000)
        eff.record_execution(actual_tokens=13500, expected_tokens=12000)
        eff.record_execution(actual_tokens=13800, expected_tokens=12000)

        self.assert_equal(eff.execution_count, 3, "Execution count")
        self.assert_range(eff.avg_efficiency_ratio, 1.14, 1.16, "Efficiency ratio >1.15")
        self.assert_equal(eff.efficiency_status, "🔴 OVER_BUDGET", "Over-budget status")

    def test_integration_create_checkpoint(self):
        """Test 8: Integration - create checkpoint"""
        print("\n🔗 Test 8: Integration - Create Checkpoint")
        print("-" * 50)

        # Clear any previous checkpoints
        TaskRelayConsciousnessIntegration.reset_relay_session()

        cp = TaskRelayConsciousnessIntegration.create_checkpoint(
            relay_number=1,
            agent_name="researcher",
            pre_tokens=50000,
            post_tokens=47500,
            expected_tokens=2500,
            consciousness_data=ConsciousnessCheckpoint(
                pattern_matched=True,
                pattern_query="explain JWT",
                pattern_level=1,
                pattern_success_rate=0.85,
                confidence_boost=0.1
            ),
            description="Research phase"
        )

        self.assert_equal(len(TaskRelayConsciousnessIntegration.CURRENT_RELAY_CHECKPOINTS), 1, "Checkpoint stored")
        self.assert_true(cp.consciousness.pattern_matched, "Consciousness data stored")

    def test_integration_update_pattern_efficiency(self):
        """Test 9: Integration - update pattern efficiency"""
        print("\n⚡ Test 9: Integration - Update Pattern Efficiency")
        print("-" * 50)

        # Clear trackers
        TaskRelayConsciousnessIntegration.PATTERN_EFFICIENCY_TRACKER.clear()

        eff = TaskRelayConsciousnessIntegration.update_pattern_efficiency(
            pattern_query="explain OAuth",
            pattern_level=1,
            pattern_success_rate=0.88,
            actual_tokens=2100,
            expected_tokens=2500
        )

        self.assert_equal(eff.execution_count, 1, "Execution recorded")
        # Key is constructed as "query_level"
        tracker_key = "explain OAuth_1"
        self.assert_true(
            tracker_key in TaskRelayConsciousnessIntegration.PATTERN_EFFICIENCY_TRACKER,
            "Pattern added to tracker"
        )

    def test_integration_relay_summary(self):
        """Test 10: Integration - relay summary"""
        print("\n📋 Test 10: Integration - Relay Summary")
        print("-" * 50)

        # Reset and create fresh relay
        TaskRelayConsciousnessIntegration.reset_relay_session()

        cp1 = TaskRelayConsciousnessIntegration.create_checkpoint(
            relay_number=1,
            agent_name="researcher",
            pre_tokens=50000,
            post_tokens=47500,
            expected_tokens=2500
        )

        cp2 = TaskRelayConsciousnessIntegration.create_checkpoint(
            relay_number=2,
            agent_name="designer",
            pre_tokens=47500,
            post_tokens=44500,
            expected_tokens=3000
        )

        summary = TaskRelayConsciousnessIntegration.get_relay_summary()

        self.assert_equal(summary['relay_length'], 2, "Relay length")
        self.assert_equal(summary['total_tokens_consumed'], -5500, "Total tokens consumed")
        self.assert_true('checkpoints' in summary, "Checkpoints in summary")

    def test_integration_efficiency_report(self):
        """Test 11: Integration - efficiency report"""
        print("\n📊 Test 11: Integration - Efficiency Report")
        print("-" * 50)

        # Clear and populate tracker
        TaskRelayConsciousnessIntegration.PATTERN_EFFICIENCY_TRACKER.clear()

        TaskRelayConsciousnessIntegration.update_pattern_efficiency(
            "query A", 1, 0.85, 2000, 2500
        )
        TaskRelayConsciousnessIntegration.update_pattern_efficiency(
            "query B", 3, 0.90, 3500, 3800
        )

        report = TaskRelayConsciousnessIntegration.get_efficiency_report()

        self.assert_equal(report['total_patterns_tracked'], 2, "Patterns tracked")
        self.assert_true(len(report['patterns']) > 0, "Patterns in report")

    def test_integration_best_worst_patterns(self):
        """Test 12: Integration - best and worst patterns"""
        print("\n🏆 Test 12: Integration - Best/Worst Patterns")
        print("-" * 50)

        # Clear and populate
        TaskRelayConsciousnessIntegration.PATTERN_EFFICIENCY_TRACKER.clear()

        # Good pattern
        eff_good = TaskRelayConsciousnessIntegration.update_pattern_efficiency(
            "efficient query", 2, 0.95, 1200, 1500
        )

        # Bad pattern
        eff_bad = TaskRelayConsciousnessIntegration.update_pattern_efficiency(
            "inefficient query", 4, 0.70, 5500, 4000
        )

        best = TaskRelayConsciousnessIntegration.get_best_patterns(top_n=1)
        worst = TaskRelayConsciousnessIntegration.get_worst_patterns(top_n=1)

        self.assert_true(len(best) > 0, "Best patterns retrieved")
        self.assert_true(len(worst) > 0, "Worst patterns retrieved")
        self.assert_true(best[0].avg_efficiency_ratio < worst[0].avg_efficiency_ratio, "Ordering correct")

    def test_integration_dump_state(self):
        """Test 13: Integration - dump state"""
        print("\n💾 Test 13: Integration - Dump State")
        print("-" * 50)

        TaskRelayConsciousnessIntegration.reset_relay_session()
        TaskRelayConsciousnessIntegration.PATTERN_EFFICIENCY_TRACKER.clear()

        state = TaskRelayConsciousnessIntegration.dump_state()

        self.assert_true('current_relay_checkpoints' in state, "Checkpoints in state")
        self.assert_true('pattern_efficiency_tracker' in state, "Efficiency tracker in state")
        self.assert_true('timestamp' in state, "Timestamp in state")

    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 70)
        print("🔗 HEKAT TASK-RELAY CONSCIOUSNESS INTEGRATION TESTS")
        print("=" * 70)

        self.test_token_checkpoint_creation()
        self.test_consciousness_checkpoint()
        self.test_relay_checkpoint_variance()
        self.test_relay_checkpoint_over_budget()
        self.test_pattern_efficiency_single_execution()
        self.test_pattern_efficiency_multiple_executions()
        self.test_pattern_efficiency_over_budget_multiple()
        self.test_integration_create_checkpoint()
        self.test_integration_update_pattern_efficiency()
        self.test_integration_relay_summary()
        self.test_integration_efficiency_report()
        self.test_integration_best_worst_patterns()
        self.test_integration_dump_state()

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
    tester = TestTaskRelayConsciousnessIntegration()
    success = tester.run_all_tests()
    exit(0 if success else 1)

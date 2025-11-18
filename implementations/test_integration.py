"""
Integration Tests for HEKAT Phase 2.2-2.3
Tests the complete /hekat command flow including classification, token display, and hotkey suggestions.
"""

import pytest
from hekat_integration import (
    run_hekat_command,
    parse_hekat_command,
    display_help
)
from classifier import (
    classify_query,
    format_token_display,
    suggest_hotkey_for_level,
    ClassificationResult,
    LEVEL_NAMES
)


class TestParseHekatCommand:
    """Test command parsing."""

    def test_simple_query(self):
        """Parse simple query without flags."""
        query, options = parse_hekat_command('/hekat "explain JWT"')
        assert query == "explain JWT"
        assert not options["verbose"]
        assert options["force_level"] is None

    def test_verbose_flag(self):
        """Parse query with --verbose flag."""
        query, options = parse_hekat_command('/hekat --verbose "design system"')
        assert query == "design system"
        assert options["verbose"]

    def test_explicit_level_override(self):
        """Parse query with @L5 override."""
        query, options = parse_hekat_command('/hekat @L5 "query"')
        assert query == "query"
        assert options["force_level"] == 5

    def test_help_flag(self):
        """Parse --help flag."""
        query, options = parse_hekat_command('/hekat --help')
        assert options["help"]

    def test_all_flags(self):
        """Parse query with all flags."""
        query, options = parse_hekat_command('/hekat --verbose @L3 "complex query"')
        assert query == "complex query"
        assert options["verbose"]
        assert options["force_level"] == 3


class TestClassificationResults:
    """Test classification and result generation."""

    def test_l1_classification(self):
        """Test L1 Ultra-Fast classification."""
        result = classify_query("explain JWT", 50000)
        assert result.level == 1
        assert result.confidence == 0.75
        assert "Keywords" in result.reasoning

    def test_l7_classification(self):
        """Test L7 Full Ensemble classification."""
        result = classify_query("build complete platform from scratch", 50000)
        assert result.level == 7
        assert result.confidence == 0.75

    def test_explicit_override_l5(self):
        """Test explicit @L5 override."""
        result = classify_query("@L5 anything", 50000)
        assert result.level == 5
        assert result.confidence == 1.0
        assert "explicitly requested" in result.reasoning

    def test_token_downgrade_l7_to_l6(self):
        """Test token budget downgrade from L7 to L6."""
        result = classify_query("build from scratch", 8000)
        assert result.level == 6  # Should downgrade from L7 to L6
        assert result.downgraded

    def test_token_downgrade_l5_to_l1(self):
        """Test token budget downgrade from L5 to L1."""
        result = classify_query("architect system", 500)
        assert result.level == 1  # Should downgrade to L1
        assert result.downgraded

    def test_hotkey_suggestion_included(self):
        """Test that hotkey suggestion is included in result."""
        result = classify_query("explain JWT", 50000)
        assert result.hotkey is not None
        assert "[R]" in result.hotkey  # L1 suggests Research hotkey


class TestTokenDisplay:
    """Test token display formatting."""

    def test_clean_format(self):
        """Test clean (non-verbose) token display."""
        result = classify_query("explain JWT", 50000)
        display = format_token_display(result, verbose=False)
        assert "Selected: L1" in display
        assert "Ultra-Fast" in display
        assert "600-1200" in display
        assert "Ready" in display

    def test_verbose_format(self):
        """Test verbose token display with phase breakdown."""
        result = classify_query("design system", 50000)
        display = format_token_display(result, verbose=True, available_tokens=50000)
        assert "SELECTION PHASE:" in display
        assert "Input parsing" in display
        assert "Complexity classify" in display
        assert "Hotkey generation" in display
        assert "EXECUTION PLAN:" in display
        assert "TOKEN BUDGET ANALYSIS:" in display

    def test_token_analysis_remaining(self):
        """Test token analysis shows remaining tokens."""
        result = classify_query("explain JWT", 50000)
        display = format_token_display(result, verbose=True, available_tokens=50000)
        assert "Remaining:" in display
        # Should have significant tokens remaining for a simple L1 query

    def test_token_analysis_overspend(self):
        """Test token analysis when projected spend > available."""
        result = classify_query("build from scratch", 50000)  # L7 classified
        # L7 needs 12000-22000 tokens, with overhead ~1886
        # Total would be ~13886 to 23886
        display = format_token_display(result, verbose=True, available_tokens=15000)
        assert "TOKEN BUDGET ANALYSIS:" in display
        # Remaining would be negative or very small


class TestHotkeyGeneration:
    """Test hotkey suggestion generation."""

    def test_l1_suggests_research(self):
        """Test L1 suggests Research hotkey."""
        suggestion = suggest_hotkey_for_level(1)
        assert "[R]" in suggestion["hotkey"]
        assert "Research" in suggestion["name"]

    def test_l3_suggests_chain(self):
        """Test L3 suggests Design→Implement→Test chain."""
        suggestion = suggest_hotkey_for_level(3)
        assert "[D>I>T]" in suggestion["hotkey"]
        assert "Chain" in suggestion["name"] or "Design" in suggestion["name"]

    def test_l5_suggests_ctrl_h(self):
        """Test L5 suggests Ctrl+H modifier."""
        suggestion = suggest_hotkey_for_level(5)
        assert "[Ctrl+H]" in suggestion["hotkey"]
        assert "Hierarchical" in suggestion["name"]

    def test_l7_suggests_ctrl_e(self):
        """Test L7 suggests Ctrl+E modifier."""
        suggestion = suggest_hotkey_for_level(7)
        assert "[Ctrl+E]" in suggestion["hotkey"]
        assert "Ensemble" in suggestion["name"]

    def test_all_levels_have_suggestions(self):
        """Test all levels 1-7 have hotkey suggestions."""
        for level in range(1, 8):
            suggestion = suggest_hotkey_for_level(level)
            assert "hotkey" in suggestion
            assert "name" in suggestion
            assert suggestion["hotkey"] is not None


class TestCompleteHekatFlow:
    """Test complete /hekat command flow."""

    def test_simple_query_flow(self):
        """Test complete flow for simple query."""
        output = run_hekat_command('/hekat "explain JWT"', 50000)
        assert "L1" in output
        assert "Ultra-Fast" in output
        assert "[R]" in output
        assert "Ready" in output

    def test_verbose_query_flow(self):
        """Test complete flow with --verbose flag."""
        output = run_hekat_command('/hekat --verbose "design system"', 50000)
        assert "L3" in output or "L5" in output  # design → L3/L5
        assert "SELECTION PHASE:" in output
        assert "TOKEN BUDGET ANALYSIS:" in output

    def test_explicit_level_flow(self):
        """Test complete flow with explicit @L5 override."""
        output = run_hekat_command('/hekat @L5 "anything"', 50000)
        assert "L5" in output
        assert "100%" in output  # Should have 100% confidence
        assert "explicitly" in output.lower()

    def test_help_flow(self):
        """Test /hekat --help returns help text."""
        output = run_hekat_command('/hekat --help', 50000)
        assert "HEKAT Query Builder" in output
        assert "USAGE:" in output
        assert "TIER HOTKEY SYSTEM:" in output

    def test_token_constraint_flow(self):
        """Test flow with token budget constraint."""
        output = run_hekat_command('/hekat "build from scratch"', 8000)
        # Should downgrade from L7 to lower level
        assert "Downgraded" in output or "L6" in output or "L5" in output

    def test_no_query_error(self):
        """Test error handling for missing query."""
        output = run_hekat_command('/hekat', 50000)
        assert "❌" in output or "No query" in output

    def test_multiple_flags_flow(self):
        """Test complete flow with multiple flags."""
        output = run_hekat_command('/hekat --verbose @L7 "query"', 50000)
        assert "L7" in output
        assert "SELECTION PHASE:" in output
        assert "100%" in output  # Explicit override


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_query(self):
        """Test handling of empty query."""
        result = classify_query("", 50000)
        assert result.level >= 1
        assert result.level <= 7

    def test_very_low_token_budget(self):
        """Test classification with very low token budget (< 600)."""
        result = classify_query("build from scratch", 100)
        assert result.level == 1  # Should downgrade to minimum
        assert result.downgraded

    def test_very_high_token_budget(self):
        """Test classification with very high token budget."""
        result = classify_query("anything", 200000)
        # Should classify normally without downgrade
        assert not result.downgraded or result.downgraded is False

    def test_confidence_ranges(self):
        """Test that confidence values are in valid range."""
        test_queries = [
            "@L5 query",  # Explicit
            "[R] query",  # Hotkey
            "explain JWT",  # Keyword
        ]
        for query in test_queries:
            result = classify_query(query, 50000)
            assert 0.0 <= result.confidence <= 1.0

    def test_all_hotkey_patterns(self):
        """Test classification with various hotkey patterns."""
        hotkey_inputs = [
            "[R] research query",
            "[D] design query",
            "[P] parallel query",
            "[Ctrl+H] hierarchical",
            "[Ctrl+E] ensemble",
        ]
        for input_str in hotkey_inputs:
            result = classify_query(input_str, 50000)
            assert result.confidence == 0.95  # Hotkey inputs have 95% confidence
            assert "hotkey" in result.method.lower()


class TestOutputFormatting:
    """Test output formatting and display."""

    def test_level_names_complete(self):
        """Test that all levels have proper names."""
        for level in range(1, 8):
            result = classify_query(f"level {level} query", 50000)
            result.level = level  # Force level for testing
            display = format_token_display(result)
            assert "L" + str(level) in display
            assert LEVEL_NAMES[level] in display

    def test_display_includes_confidence(self):
        """Test that confidence is displayed."""
        result = classify_query("explain JWT", 50000)
        display = format_token_display(result, verbose=False)
        assert "confidence" in display.lower() or "%" in display

    def test_verbose_includes_all_phases(self):
        """Test that verbose display includes all phases."""
        result = classify_query("design system", 50000)
        display = format_token_display(result, verbose=True, available_tokens=50000)
        assert "Phase 1" in display
        assert "Phase 2" in display
        assert "Phase 3" in display


# Test execution
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

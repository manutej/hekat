"""
Simple Integration Test Runner (no pytest required)
Tests the complete /hekat command flow.
"""

from hekat_integration import (
    run_hekat_command,
    parse_hekat_command,
    display_help
)
from classifier import (
    classify_query,
    format_token_display,
    suggest_hotkey_for_level,
    LEVEL_NAMES
)


def test_parse_command():
    """Test command parsing."""
    print("Testing command parsing...")

    # Test simple query
    query, options = parse_hekat_command('/hekat "explain JWT"')
    assert query == "explain JWT"
    assert not options["verbose"]
    print("  ✓ Simple query parsing")

    # Test verbose flag
    query, options = parse_hekat_command('/hekat --verbose "design system"')
    assert options["verbose"]
    print("  ✓ Verbose flag parsing")

    # Test explicit level
    query, options = parse_hekat_command('/hekat @L5 "query"')
    assert options["force_level"] == 5
    print("  ✓ Explicit level parsing")


def test_classification():
    """Test query classification."""
    print("\nTesting classification...")

    # L1
    result = classify_query("explain JWT", 50000)
    assert result.level == 1
    print("  ✓ L1 Ultra-Fast classification")

    # L7
    result = classify_query("build complete platform from scratch", 50000)
    assert result.level == 7
    print("  ✓ L7 Full Ensemble classification")

    # Explicit override
    result = classify_query("@L5 anything", 50000)
    assert result.level == 5
    assert result.confidence == 1.0
    print("  ✓ Explicit @L5 override")

    # Token downgrade
    result = classify_query("build from scratch", 8000)
    assert result.downgraded
    print("  ✓ Token budget downgrade (L7→L6)")


def test_hotkey_suggestions():
    """Test hotkey generation."""
    print("\nTesting hotkey suggestions...")

    for level in range(1, 8):
        suggestion = suggest_hotkey_for_level(level)
        assert "hotkey" in suggestion
        assert suggestion["hotkey"] is not None
        print(f"  ✓ L{level} → {suggestion['hotkey']} {suggestion['name']}")


def test_token_display():
    """Test token display formatting."""
    print("\nTesting token display...")

    result = classify_query("explain JWT", 50000)

    # Clean format
    display = format_token_display(result, verbose=False)
    assert "L1" in display
    assert "600-1200" in display
    print("  ✓ Clean format display")

    # Verbose format
    display = format_token_display(result, verbose=True, available_tokens=50000)
    assert "SELECTION PHASE:" in display
    assert "TOKEN BUDGET ANALYSIS:" in display
    print("  ✓ Verbose format display")


def test_complete_flow():
    """Test complete /hekat command flow."""
    print("\nTesting complete /hekat flow...")

    test_cases = [
        ('/hekat "explain JWT"', "L1", "[R]"),
        ('/hekat --verbose "design system"', "L5", "✓ Selected"),
        ('/hekat @L7 "anything"', "L7", "100%"),
        ('/hekat "build from scratch"', "L7", "Full Ensemble"),
    ]

    for cmd, expected_level, expected_text in test_cases:
        output = run_hekat_command(cmd, 50000)
        assert expected_level in output, f"Expected '{expected_level}' in output"
        assert expected_text in output, f"Expected '{expected_text}' in output"
        print(f"  ✓ {cmd[:40]}...")


def test_edge_cases():
    """Test edge cases."""
    print("\nTesting edge cases...")

    # Very low token budget
    result = classify_query("build from scratch", 100)
    assert result.level == 1  # Should downgrade to L1
    assert result.downgraded
    print("  ✓ Very low token budget (< 600)")

    # Confidence ranges
    result = classify_query("@L5 query", 50000)
    assert 0.0 <= result.confidence <= 1.0
    print("  ✓ Confidence in valid range")

    # No query error handling
    output = run_hekat_command('/hekat', 50000)
    assert "No query" in output or "❌" in output
    print("  ✓ Error handling for missing query")


def main():
    """Run all tests."""
    print("=" * 80)
    print("HEKAT INTEGRATION TEST SUITE")
    print("=" * 80)

    try:
        test_parse_command()
        test_classification()
        test_hotkey_suggestions()
        test_token_display()
        test_complete_flow()
        test_edge_cases()

        print("\n" + "=" * 80)
        print("✅ ALL TESTS PASSED")
        print("=" * 80)
        return 0

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())

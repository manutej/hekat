"""
HEKAT Integration Layer - Task 2.2-2.3
Integrates classifier with token display and hotkey suggestions.
This module handles the complete /hekat command flow.
Also supports persistent MODE operation where queries are continuously classified.
"""

import sys
import re
from typing import Dict, Tuple, Optional
from classifier import (
    classify_query,
    format_token_display,
    suggest_hotkey_for_level,
    TOKEN_BUDGETS,
    LEVEL_NAMES,
    ClassificationResult
)
from hekat_mode import (
    activate_hekat_mode,
    deactivate_hekat_mode,
    is_hekat_mode_active,
    record_query_classification,
    display_mode_activation_screen,
    display_mode_deactivation_screen,
    get_hekat_mode_status
)


def parse_hekat_command(input_str: str) -> Tuple[str, Dict]:
    """
    Parse /hekat command input into query and options.

    Args:
        input_str: Raw command input like "/hekat --verbose @L5 'query'"

    Returns:
        Tuple of (query, options_dict)
        Options include: verbose, force_level, hotkey, etc.
    """
    options = {
        "verbose": False,
        "force_level": None,
        "hotkey": None,
        "help": False
    }

    # Remove leading /hekat if present
    if input_str.startswith("/hekat"):
        input_str = input_str[6:].strip()

    # Check for --help
    if "--help" in input_str or "-h" in input_str:
        options["help"] = True
        return "", options

    # Check for --verbose
    if "--verbose" in input_str:
        options["verbose"] = True
        input_str = input_str.replace("--verbose", "").strip()

    # Check for explicit level override (@L5)
    level_match = re.search(r"@L([1-7])", input_str)
    if level_match:
        options["force_level"] = int(level_match.group(1))
        input_str = re.sub(r"@L[1-7]", "", input_str).strip()

    # Extract query (everything remaining)
    query = input_str.strip()
    if query.startswith('"') and query.endswith('"'):
        query = query[1:-1]

    return query, options


def display_help() -> str:
    """Display /hekat help message."""
    return """
╔══════════════════════════════════════════════════════════════════════════════╗
║                        HEKAT Query Builder - Help                            ║
╚══════════════════════════════════════════════════════════════════════════════╝

USAGE:
  /hekat <query>              Auto-detect complexity level
  /hekat --verbose <query>    Show detailed token breakdown
  /hekat @L5 <query>          Force specific level (L1-L7)
  /hekat --help               Show this message

QUICK EXAMPLES:
  /hekat "explain JWT"
  → L1 Ultra-Fast single agent

  /hekat "design auth system"
  → L5 Hierarchical with multiple agents

  /hekat --verbose "implement feature"
  → Shows token phases and budget analysis

  /hekat @L7 "build from scratch"
  → Forces L7 Full Ensemble level

TIER HOTKEY SYSTEM:
  TIER 1 - Single Keys: [R] [D] [T] [B] [F] [I] [O] [S] [C] [P] [V] [A]
  TIER 2 - Modifiers:   [Ctrl+P] [Ctrl+H] [Ctrl+I] [Ctrl+E] [Ctrl+F]
  TIER 3 - Chains:      [R>D>I] [P:R||D||A] [I:D→P→T]

COMPLEXITY LEVELS:
  L1: Ultra-Fast (600-1200 tokens)     - Single quick question
  L2: Fast Chain (1500-3000 tokens)    - Two-step workflow
  L3: Balanced (2500-4500 tokens)      - Full feature development
  L4: Parallel (3000-6000 tokens)      - Multiple perspectives
  L5: Hierarchical (5500-9000 tokens)  - Architecture with oversight
  L6: Iterative (8000-12000 tokens)    - Refactor/optimize loop
  L7: Full Ensemble (12000-22000 tokens) - Major system redesign

DOCUMENTS:
  • QUERY_BUILDER_SPECIFICATION.md - Complete technical spec
  • TIER_HOTKEY_REFERENCE.md       - Full hotkey matrix
  • PHASE_2_IMPLEMENTATION_GUIDE.md - Implementation details
"""


def handle_hekat_mode_activation(input_str: str) -> str:
    """
    Handle HEKAT mode activation.

    When user runs `/hekat` with no arguments, activate persistent mode.

    Returns:
        Formatted activation message
    """
    result = activate_hekat_mode()

    output = display_mode_activation_screen()
    output += "\n"
    output += "✅ Mode activated successfully\n"

    return output


def handle_hekat_mode_exit(input_str: str) -> str:
    """
    Handle HEKAT mode exit/deactivation.

    When user runs `/hekat-exit`, deactivate persistent mode.

    Returns:
        Formatted deactivation message
    """
    status = get_hekat_mode_status()
    query_count = status["query_count"]
    last_level = status["last_level"]

    result = deactivate_hekat_mode()

    output = display_mode_deactivation_screen(query_count, last_level)
    output += "\n"
    output += "✅ Mode deactivated successfully\n"

    return output


def run_hekat_command(input_str: str, available_tokens: int = 50000) -> str:
    """
    Execute /hekat command with full integration.

    Supports three modes of operation:
    1. `/hekat` - Activate persistent mode
    2. `/hekat <query>` - Classify single query
    3. `/hekat --help` - Show help

    Args:
        input_str: Command input like "/hekat --verbose 'my query'"
        available_tokens: Available tokens in context

    Returns:
        Formatted output string
    """
    # Parse command
    query, options = parse_hekat_command(input_str)

    # Show help if requested
    if options["help"]:
        return display_help()

    # Mode activation: /hekat with no query
    if not query:
        return handle_hekat_mode_activation(input_str)

    # Single query classification
    # Remove leading /hekat for classifier (it looks for @L and [hotkeys] in the input)
    classifier_input = input_str
    if classifier_input.startswith("/hekat"):
        classifier_input = classifier_input[6:].strip()
    # Remove --verbose flag for classifier
    classifier_input = classifier_input.replace("--verbose", "").strip()

    # Classify query (pass full input so it can detect @L5 and hotkeys)
    result = classify_query(classifier_input, available_tokens)

    # Record in mode if active
    if is_hekat_mode_active():
        record_query_classification(result.level)

    # Build output
    output_parts = []

    # Line 1: Classification result
    output_parts.append(f"\n✓ Selected: L{result.level} {LEVEL_NAMES[result.level]}")
    output_parts.append(f"  Confidence: {result.confidence:.0%}")

    # Line 2: Hotkey suggestion
    hotkey_suggestion = suggest_hotkey_for_level(result.level, query)
    output_parts.append(f"  Suggested hotkey: {hotkey_suggestion['hotkey']} {hotkey_suggestion['name']}")

    # Line 3: Reasoning
    output_parts.append(f"  Reasoning: {result.reasoning}")

    # Add token display
    output_parts.append("")  # Blank line
    token_display = format_token_display(result, verbose=options["verbose"], available_tokens=available_tokens)
    output_parts.append(token_display)

    # Add additional info for verbose mode
    if options["verbose"]:
        min_tokens, max_tokens = TOKEN_BUDGETS[result.level]
        est_tokens = int((min_tokens + max_tokens) / 2)

        output_parts.append("")
        output_parts.append("HOTKEY REFERENCE:")
        output_parts.append(f"  Use /hekat {hotkey_suggestion['hotkey']} '<query>' for L{result.level}")
        output_parts.append(f"  Or use /hekat @L{result.level} '<query>' to force this level")

    # Add mode status if in mode
    if is_hekat_mode_active():
        status = get_hekat_mode_status()
        output_parts.append("")
        output_parts.append(f"[HEKAT MODE ACTIVE] Queries: {status['query_count']}")

    output_parts.append("")  # Blank line at end
    return "\n".join(output_parts)


def test_integration_examples():
    """Run example queries to demonstrate integration."""
    test_cases = [
        ("/hekat \"explain JWT\"", 50000),
        ("/hekat \"design authentication system\"", 50000),
        ("/hekat --verbose \"build microservices platform from scratch\"", 50000),
        ("/hekat @L7 \"anything\"", 50000),
        ("/hekat --verbose \"refactor code\"", 8000),  # Token-constrained
    ]

    print("\n" + "=" * 80)
    print("HEKAT INTEGRATION TEST - Example Queries")
    print("=" * 80 + "\n")

    for input_str, tokens in test_cases:
        print(f"Command: {input_str}")
        print(f"Available tokens: {tokens}")
        print("-" * 80)
        output = run_hekat_command(input_str, tokens)
        print(output)
        print("=" * 80 + "\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Run with provided argument
        cmd_input = " ".join(sys.argv[1:])
        output = run_hekat_command(cmd_input)
        print(output)
    else:
        # Run example tests
        test_integration_examples()

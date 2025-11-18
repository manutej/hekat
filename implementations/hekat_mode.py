"""
HEKAT Mode Management
Manages persistent mode state for HEKAT query builder.
"""

from typing import Optional, Dict
from datetime import datetime

# Global mode state (persists in conversation context)
HEKAT_MODE_STATE = {
    "active": False,
    "activated_at": None,
    "query_count": 0,
    "last_level": None,
}


def activate_hekat_mode() -> Dict:
    """
    Activate HEKAT persistent mode.

    All subsequent queries will be automatically classified L1-L7
    until deactivate_hekat_mode() is called.

    Returns:
        Status dict with activation message
    """
    global HEKAT_MODE_STATE

    was_active = HEKAT_MODE_STATE["active"]
    HEKAT_MODE_STATE["active"] = True
    HEKAT_MODE_STATE["activated_at"] = datetime.now().isoformat()
    HEKAT_MODE_STATE["query_count"] = 0

    return {
        "status": "activated",
        "message": "🟢 HEKAT MODE ACTIVATED",
        "description": "All queries will be automatically classified to complexity levels L1-L7.",
        "instructions": [
            "✓ Type any query normally",
            "✓ Complexity level will be displayed automatically",
            "✓ Hotkey suggestions will be shown",
            "✓ Token estimates will be provided",
            "✓ Use /hekat-exit to deactivate mode"
        ],
        "was_already_active": was_active,
        "timestamp": HEKAT_MODE_STATE["activated_at"]
    }


def deactivate_hekat_mode() -> Dict:
    """
    Deactivate HEKAT persistent mode.

    Queries return to normal processing.
    Use /hekat <query> for individual classification if needed.

    Returns:
        Status dict with deactivation message
    """
    global HEKAT_MODE_STATE

    was_active = HEKAT_MODE_STATE["active"]
    query_count = HEKAT_MODE_STATE["query_count"]
    last_level = HEKAT_MODE_STATE["last_level"]

    HEKAT_MODE_STATE["active"] = False
    HEKAT_MODE_STATE["activated_at"] = None

    return {
        "status": "deactivated",
        "message": "⚫ HEKAT MODE DEACTIVATED",
        "description": "Returning to normal query processing.",
        "summary": {
            "queries_processed": query_count,
            "last_level": f"L{last_level}" if last_level else "N/A",
            "duration": "Session ended"
        },
        "instructions": [
            "ℹ️ Use /hekat <query> for individual query classification",
            "ℹ️ Use /hekat --help for command reference",
            "ℹ️ Use /hekat to reactivate persistent mode"
        ],
        "was_active": was_active
    }


def get_hekat_mode_status() -> Dict:
    """
    Get current HEKAT mode status.

    Returns:
        Status dict showing current mode state
    """
    return {
        "active": HEKAT_MODE_STATE["active"],
        "activated_at": HEKAT_MODE_STATE["activated_at"],
        "query_count": HEKAT_MODE_STATE["query_count"],
        "last_level": HEKAT_MODE_STATE["last_level"],
        "status": "🟢 ACTIVE" if HEKAT_MODE_STATE["active"] else "⚫ INACTIVE"
    }


def is_hekat_mode_active() -> bool:
    """
    Check if HEKAT mode is currently active.

    Returns:
        True if mode is active, False otherwise
    """
    return HEKAT_MODE_STATE["active"]


def record_query_classification(level: int) -> None:
    """
    Record a query classification in the current mode.

    Args:
        level: Complexity level (1-7)
    """
    global HEKAT_MODE_STATE

    if HEKAT_MODE_STATE["active"]:
        HEKAT_MODE_STATE["query_count"] += 1
        HEKAT_MODE_STATE["last_level"] = level


def format_mode_status() -> str:
    """
    Format mode status as a display string.

    Returns:
        Formatted status string
    """
    status = get_hekat_mode_status()

    if status["active"]:
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║ 🟢 HEKAT MODE ACTIVE                                               ║
╚════════════════════════════════════════════════════════════════════╝

Status:   {status['status']}
Queries:  {status['query_count']}
Last:     {f"L{status['last_level']}" if status['last_level'] else "None"}

All your queries will be automatically classified L1-L7.
Use /hekat-exit to deactivate mode.
"""
    else:
        return f"""
╔════════════════════════════════════════════════════════════════════╗
║ ⚫ HEKAT MODE INACTIVE                                              ║
╚════════════════════════════════════════════════════════════════════╝

Status:   {status['status']}

Use /hekat to activate persistent mode.
Use /hekat <query> for single query classification.
"""


def display_mode_activation_screen() -> str:
    """
    Display the mode activation screen.

    Returns:
        Formatted activation screen
    """
    return """
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║           🟢 HEKAT MODE ACTIVATED - PERSISTENT SESSION             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

HOW IT WORKS:
  1. Type any query normally
  2. System automatically classifies to L1-L7
  3. Hotkey suggestions shown
  4. Token estimates provided
  5. Your query is processed with optimal agents

EXAMPLE QUERIES:
  "explain JWT"
  → L1 Ultra-Fast | [R] Research | ✅ Ready

  "design authentication system"
  → L5 Hierarchical | [Ctrl+H] | Est 7250 tokens | ✅ Proceed

  "build microservices from scratch"
  → L7 Full Ensemble | [Ctrl+E] | Est 17000 tokens | ✅ Proceed

TO EXIT HEKAT MODE:
  /hekat-exit
  → Returns to normal query processing

────────────────────────────────────────────────────────────────────

Ready to classify queries! Start typing your queries below:
"""


def display_mode_deactivation_screen(query_count: int, last_level: Optional[int]) -> str:
    """
    Display the mode deactivation screen.

    Args:
        query_count: Number of queries processed in this session
        last_level: Last complexity level classified

    Returns:
        Formatted deactivation screen
    """
    return f"""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║         ⚫ HEKAT MODE DEACTIVATED - RETURNING TO NORMAL             ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝

SESSION SUMMARY:
  Queries Processed: {query_count}
  Last Level:        {f"L{last_level}" if last_level else "N/A"}
  Status:            Session closed

NEXT STEPS:
  • Use /hekat <query>        for single query classification
  • Use /hekat --help         for command reference
  • Use /hekat                to reactivate persistent mode

────────────────────────────────────────────────────────────────────

Returning to normal operation.
"""


if __name__ == "__main__":
    # Test mode functionality
    print("=== HEKAT Mode Test ===\n")

    # Test activation
    print("Testing activation...")
    result = activate_hekat_mode()
    print(result["message"])
    print(f"Status: {result['status']}\n")

    # Test status check
    print("Testing status check...")
    status = get_hekat_mode_status()
    print(f"Active: {status['active']}\n")

    # Test query recording
    print("Recording query classifications...")
    record_query_classification(1)
    record_query_classification(5)
    record_query_classification(7)

    status = get_hekat_mode_status()
    print(f"Queries recorded: {status['query_count']}")
    print(f"Last level: L{status['last_level']}\n")

    # Test deactivation
    print("Testing deactivation...")
    result = deactivate_hekat_mode()
    print(result["message"])
    print(f"Status: {result['status']}")
    print(f"Summary: {result['summary']}\n")

    # Test status after deactivation
    status = get_hekat_mode_status()
    print(f"Active: {status['active']}")
    print("\n✅ All mode tests passed")

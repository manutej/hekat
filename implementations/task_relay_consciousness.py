"""
Phase 4: Task-Relay Consciousness Integration
Integrates consciousness pattern learning with Task-Relay token accounting for
token efficiency tracking and adaptive pattern optimization.

Task-Relay Pattern: Multi-agent orchestration with token discipline at checkpoints
Consciousness Integration: Learn which patterns are efficient/inefficient from actual token usage
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime
import statistics


@dataclass
class TokenCheckpoint:
    """Represents token state at a HEKAT execution phase boundary."""

    phase: str  # e.g., "selection", "execution", "relay_1_researcher"
    pre_tokens: int
    post_tokens: int
    description: str = ""

    @property
    def delta(self) -> int:
        """Tokens consumed in this phase"""
        return self.post_tokens - self.pre_tokens

    @property
    def percentage_of_budget(self) -> float:
        """Percentage of pre-phase tokens consumed"""
        if self.pre_tokens == 0:
            return 0.0
        return abs(self.delta) / self.pre_tokens


@dataclass
class ConsciousnessCheckpoint:
    """Consciousness metadata captured at execution checkpoint."""

    pattern_matched: bool
    pattern_query: Optional[str] = None
    pattern_level: Optional[int] = None
    pattern_success_rate: Optional[float] = None
    confidence_boost: float = 0.0
    confidence_reason: Optional[str] = None
    context: str = "general"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return asdict(self)


@dataclass
class RelayCheckpoint:
    """Complete checkpoint with token and consciousness tracking."""

    relay_number: int
    agent_name: str
    timestamp: str
    token: TokenCheckpoint
    consciousness: ConsciousnessCheckpoint

    # Variance analysis
    expected_tokens: Optional[int] = None  # Pre-calculated budget for agent
    variance: Optional[float] = None  # Actual vs expected

    def calculate_variance(self) -> float:
        """Calculate variance percentage: (actual - expected) / expected * 100

        Note: delta is negative (tokens consumed), so use absolute value for comparison
        """
        if self.expected_tokens is None or self.expected_tokens == 0:
            return 0.0
        # Use absolute value of delta since tokens are consumed (shown as negative)
        actual_consumed = abs(self.token.delta)
        variance = ((actual_consumed - self.expected_tokens) / self.expected_tokens) * 100
        self.variance = variance
        return variance

    def variance_status(self) -> str:
        """Determine variance status: ✅ excellent, ⚠️ investigate, ❌ critical"""
        if self.variance is None:
            return "❓"

        # ✅ -50% to +10% (using less than expected or slightly over)
        if -50 <= self.variance <= 10:
            return "✅"
        # ⚠️ +10% to +20% (moderately over budget)
        elif 10 < self.variance <= 20:
            return "⚠️"
        # ❌ +20%+ (significantly over budget)
        else:
            return "❌"

    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "relay_number": self.relay_number,
            "agent_name": self.agent_name,
            "timestamp": self.timestamp,
            "token": {
                "phase": self.token.phase,
                "pre_tokens": self.token.pre_tokens,
                "post_tokens": self.token.post_tokens,
                "delta": self.token.delta,
                "description": self.token.description
            },
            "consciousness": self.consciousness.to_dict(),
            "expected_tokens": self.expected_tokens,
            "variance": self.variance,
            "variance_status": self.variance_status()
        }


@dataclass
class PatternEfficiency:
    """Tracks token efficiency metrics for a consciousness pattern."""

    pattern_query: str
    pattern_level: int
    pattern_success_rate: float  # From consciousness system

    # Token metrics
    execution_count: int = 0
    total_tokens_used: int = 0
    total_tokens_expected: int = 0
    token_deltas: List[int] = field(default_factory=list)

    # Efficiency ratios (actual / expected)
    efficiency_ratios: List[float] = field(default_factory=list)

    timestamp_created: str = field(default_factory=lambda: datetime.now().isoformat())
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def avg_tokens_used(self) -> float:
        """Average tokens actually consumed"""
        if self.execution_count == 0:
            return 0.0
        return self.total_tokens_used / self.execution_count

    @property
    def avg_tokens_expected(self) -> float:
        """Average tokens expected for this level"""
        if self.execution_count == 0:
            return 0.0
        return self.total_tokens_expected / self.execution_count

    @property
    def avg_efficiency_ratio(self) -> float:
        """Average efficiency: actual / expected"""
        if not self.efficiency_ratios:
            return 0.0
        return statistics.mean(self.efficiency_ratios)

    @property
    def efficiency_status(self) -> str:
        """Determine efficiency: over/under/on-budget"""
        ratio = self.avg_efficiency_ratio
        if ratio < 0.9:
            return "🟢 EFFICIENT"  # Using <90% of budget
        elif ratio <= 1.1:
            return "🟡 ON_BUDGET"  # Within 10% of budget
        else:
            return "🔴 OVER_BUDGET"  # Using >110% of budget

    def record_execution(self, actual_tokens: int, expected_tokens: int) -> None:
        """Record execution results and update efficiency metrics"""
        self.execution_count += 1
        self.total_tokens_used += actual_tokens
        self.total_tokens_expected += expected_tokens

        delta = actual_tokens - expected_tokens
        self.token_deltas.append(delta)

        efficiency_ratio = actual_tokens / expected_tokens if expected_tokens > 0 else 0.0
        self.efficiency_ratios.append(efficiency_ratio)

        self.last_updated = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "pattern_query": self.pattern_query,
            "pattern_level": self.pattern_level,
            "pattern_success_rate": self.pattern_success_rate,
            "execution_count": self.execution_count,
            "avg_tokens_used": self.avg_tokens_used,
            "avg_tokens_expected": self.avg_tokens_expected,
            "avg_efficiency_ratio": self.avg_efficiency_ratio,
            "efficiency_status": self.efficiency_status,
            "timestamp_created": self.timestamp_created,
            "last_updated": self.last_updated
        }


class TaskRelayConsciousnessIntegration:
    """
    Integrates Task-Relay token accounting with consciousness pattern learning.

    Tracks token efficiency per pattern and learns which patterns are efficient.
    """

    # Global efficiency tracking
    PATTERN_EFFICIENCY_TRACKER: Dict[str, PatternEfficiency] = {}

    # Checkpoints from current relay session
    CURRENT_RELAY_CHECKPOINTS: List[RelayCheckpoint] = []

    # Configuration
    EFFICIENCY_THRESHOLD_GOOD = 0.85  # <85% of expected tokens = efficient
    EFFICIENCY_THRESHOLD_BAD = 1.20   # >120% of expected tokens = inefficient

    @classmethod
    def create_checkpoint(
        cls,
        relay_number: int,
        agent_name: str,
        pre_tokens: int,
        post_tokens: int,
        expected_tokens: Optional[int] = None,
        consciousness_data: Optional[ConsciousnessCheckpoint] = None,
        description: str = ""
    ) -> RelayCheckpoint:
        """
        Create a checkpoint at a task-relay phase boundary.

        Args:
            relay_number: Which agent in relay (1, 2, 3, ...)
            agent_name: Name of agent executing
            pre_tokens: Tokens before execution
            post_tokens: Tokens after execution
            expected_tokens: Expected tokens for this agent
            consciousness_data: Consciousness pattern info
            description: Human-readable phase description

        Returns:
            RelayCheckpoint with complete metadata
        """
        checkpoint = RelayCheckpoint(
            relay_number=relay_number,
            agent_name=agent_name,
            timestamp=datetime.now().isoformat(),
            token=TokenCheckpoint(
                phase=f"relay_{relay_number}_{agent_name}",
                pre_tokens=pre_tokens,
                post_tokens=post_tokens,
                description=description
            ),
            consciousness=consciousness_data or ConsciousnessCheckpoint(pattern_matched=False),
            expected_tokens=expected_tokens
        )

        # Calculate variance if expected tokens provided
        if expected_tokens is not None:
            checkpoint.calculate_variance()

        # Store checkpoint
        cls.CURRENT_RELAY_CHECKPOINTS.append(checkpoint)

        return checkpoint

    @classmethod
    def update_pattern_efficiency(
        cls,
        pattern_query: str,
        pattern_level: int,
        pattern_success_rate: float,
        actual_tokens: int,
        expected_tokens: int
    ) -> PatternEfficiency:
        """
        Update efficiency metrics for a consciousness pattern.

        Args:
            pattern_query: Query text from consciousness
            pattern_level: Complexity level
            pattern_success_rate: Success rate from consciousness
            actual_tokens: Tokens actually consumed
            expected_tokens: Tokens expected for this level

        Returns:
            Updated PatternEfficiency object
        """
        key = f"{pattern_query}_{pattern_level}"

        # Create or retrieve efficiency tracker
        if key not in cls.PATTERN_EFFICIENCY_TRACKER:
            cls.PATTERN_EFFICIENCY_TRACKER[key] = PatternEfficiency(
                pattern_query=pattern_query,
                pattern_level=pattern_level,
                pattern_success_rate=pattern_success_rate
            )

        efficiency = cls.PATTERN_EFFICIENCY_TRACKER[key]
        efficiency.record_execution(actual_tokens, expected_tokens)

        return efficiency

    @classmethod
    def get_pattern_efficiency(cls, pattern_query: str, pattern_level: int) -> Optional[PatternEfficiency]:
        """
        Retrieve efficiency metrics for a pattern.

        Args:
            pattern_query: Query text
            pattern_level: Level

        Returns:
            PatternEfficiency or None if not tracked
        """
        key = f"{pattern_query}_{pattern_level}"
        return cls.PATTERN_EFFICIENCY_TRACKER.get(key)

    @classmethod
    def get_relay_summary(cls) -> Dict:
        """
        Get summary of current relay execution.

        Returns:
            Dictionary with token accounting and efficiency metrics
        """
        if not cls.CURRENT_RELAY_CHECKPOINTS:
            return {"error": "No checkpoints recorded"}

        total_pre = cls.CURRENT_RELAY_CHECKPOINTS[0].token.pre_tokens
        total_post = cls.CURRENT_RELAY_CHECKPOINTS[-1].token.post_tokens
        total_consumed = total_post - total_pre

        # Calculate variance stats
        variances = [cp.variance for cp in cls.CURRENT_RELAY_CHECKPOINTS if cp.variance is not None]

        # Count status distribution
        status_counts = {}
        for cp in cls.CURRENT_RELAY_CHECKPOINTS:
            status = cp.variance_status()
            status_counts[status] = status_counts.get(status, 0) + 1

        return {
            "relay_length": len(cls.CURRENT_RELAY_CHECKPOINTS),
            "total_tokens_consumed": total_consumed,
            "total_pre_tokens": total_pre,
            "total_post_tokens": total_post,
            "checkpoints": [cp.to_dict() for cp in cls.CURRENT_RELAY_CHECKPOINTS],
            "variance_stats": {
                "values": variances,
                "mean": statistics.mean(variances) if variances else 0.0,
                "min": min(variances) if variances else 0.0,
                "max": max(variances) if variances else 0.0
            },
            "status_distribution": status_counts
        }

    @classmethod
    def reset_relay_session(cls) -> None:
        """Clear current relay checkpoints for next relay session"""
        cls.CURRENT_RELAY_CHECKPOINTS = []

    @classmethod
    def get_efficiency_report(cls, pattern_query: Optional[str] = None) -> Dict:
        """
        Get efficiency report for tracked patterns.

        Args:
            pattern_query: Specific pattern to report, or None for all

        Returns:
            Dictionary with efficiency metrics
        """
        if pattern_query:
            # Find matching efficiency entries
            matching = {
                k: v for k, v in cls.PATTERN_EFFICIENCY_TRACKER.items()
                if pattern_query in v.pattern_query
            }

            return {
                "query": pattern_query,
                "matches": len(matching),
                "patterns": [v.to_dict() for v in matching.values()]
            }

        else:
            # Return all patterns sorted by efficiency
            patterns_by_efficiency = sorted(
                cls.PATTERN_EFFICIENCY_TRACKER.values(),
                key=lambda p: p.avg_efficiency_ratio
            )

            return {
                "total_patterns_tracked": len(cls.PATTERN_EFFICIENCY_TRACKER),
                "patterns": [p.to_dict() for p in patterns_by_efficiency]
            }

    @classmethod
    def get_best_patterns(cls, top_n: int = 5) -> List[PatternEfficiency]:
        """
        Get most efficient patterns.

        Args:
            top_n: Number of patterns to return

        Returns:
            List of most efficient PatternEfficiency objects
        """
        if not cls.PATTERN_EFFICIENCY_TRACKER:
            return []

        sorted_patterns = sorted(
            cls.PATTERN_EFFICIENCY_TRACKER.values(),
            key=lambda p: p.avg_efficiency_ratio
        )

        return sorted_patterns[:top_n]

    @classmethod
    def get_worst_patterns(cls, top_n: int = 5) -> List[PatternEfficiency]:
        """
        Get least efficient patterns.

        Args:
            top_n: Number of patterns to return

        Returns:
            List of least efficient PatternEfficiency objects
        """
        if not cls.PATTERN_EFFICIENCY_TRACKER:
            return []

        sorted_patterns = sorted(
            cls.PATTERN_EFFICIENCY_TRACKER.values(),
            key=lambda p: p.avg_efficiency_ratio,
            reverse=True
        )

        return sorted_patterns[:top_n]

    @classmethod
    def dump_state(cls) -> Dict:
        """Export complete state for analysis/debugging"""
        return {
            "current_relay_checkpoints": [cp.to_dict() for cp in cls.CURRENT_RELAY_CHECKPOINTS],
            "pattern_efficiency_tracker": {
                k: v.to_dict() for k, v in cls.PATTERN_EFFICIENCY_TRACKER.items()
            },
            "timestamp": datetime.now().isoformat()
        }


# Test the Task-Relay Consciousness Integration
if __name__ == "__main__":
    print("🔗 HEKAT Task-Relay Consciousness Integration - Testing\n")

    # Test 1: Create checkpoints
    print("Test 1: Creating checkpoints...")
    cp1 = TaskRelayConsciousnessIntegration.create_checkpoint(
        relay_number=1,
        agent_name="researcher",
        pre_tokens=50000,
        post_tokens=48000,
        expected_tokens=2500,
        consciousness_data=ConsciousnessCheckpoint(
            pattern_matched=True,
            pattern_query="explain authentication",
            pattern_level=1,
            pattern_success_rate=0.85,
            confidence_boost=0.1
        ),
        description="Research phase: researcher agent analyzing query"
    )
    print(f"✓ Checkpoint 1 created: {cp1.token.delta} tokens consumed")
    print(f"  Variance: {cp1.variance:.1f}% (status: {cp1.variance_status()})")

    # Test 2: Create second checkpoint
    cp2 = TaskRelayConsciousnessIntegration.create_checkpoint(
        relay_number=2,
        agent_name="designer",
        pre_tokens=48000,
        post_tokens=45200,
        expected_tokens=2800,
        consciousness_data=ConsciousnessCheckpoint(
            pattern_matched=False,
            context="design"
        ),
        description="Design phase: designer agent creating architecture"
    )
    print(f"✓ Checkpoint 2 created: {cp2.token.delta} tokens consumed")
    print(f"  Variance: {cp2.variance:.1f}% (status: {cp2.variance_status()})\n")

    # Test 3: Update pattern efficiency
    print("Test 2: Updating pattern efficiency...")
    eff1 = TaskRelayConsciousnessIntegration.update_pattern_efficiency(
        pattern_query="explain authentication",
        pattern_level=1,
        pattern_success_rate=0.85,
        actual_tokens=2000,
        expected_tokens=2500
    )
    print(f"✓ Pattern efficiency recorded")
    print(f"  Execution 1: 2000 / 2500 = {eff1.avg_efficiency_ratio:.2f} (80% efficient)\n")

    # Test 4: Multiple executions of same pattern
    print("Test 3: Multiple executions of same pattern...")
    eff1.record_execution(2100, 2500)
    eff1.record_execution(2050, 2500)
    print(f"✓ Recorded 2 more executions")
    print(f"  Avg efficiency: {eff1.avg_efficiency_ratio:.2f}")
    print(f"  Avg tokens used: {eff1.avg_tokens_used:.0f} / {eff1.avg_tokens_expected:.0f}")
    print(f"  Status: {eff1.efficiency_status}\n")

    # Test 5: Get relay summary
    print("Test 4: Relay summary...")
    summary = TaskRelayConsciousnessIntegration.get_relay_summary()
    print(f"✓ Relay summary generated")
    print(f"  Length: {summary['relay_length']} checkpoints")
    print(f"  Total consumed: {summary['total_tokens_consumed']} tokens")
    print(f"  Status distribution: {summary['status_distribution']}\n")

    # Test 6: Efficiency report
    print("Test 5: Efficiency report...")
    report = TaskRelayConsciousnessIntegration.get_efficiency_report()
    print(f"✓ Efficiency report generated")
    print(f"  Total patterns tracked: {report['total_patterns_tracked']}")
    if report['patterns']:
        best = report['patterns'][0]
        print(f"  Most efficient: {best['pattern_query'][:40]} ({best['efficiency_status']})")

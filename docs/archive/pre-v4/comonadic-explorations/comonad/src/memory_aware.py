"""
Memory-Aware Comonadic Context for Token-Constrained Environments

Key insight: In a 200K token budget with parallel agents:
- Can't duplicate full context (too expensive)
- Can't keep complete history (grows unbounded)
- Need smart extraction + compression

This implementation:
1. Tracks token usage per operation
2. Compresses history to essentials only
3. Enables smart duplication (selective sharing)
4. Provides context-aware extraction
"""

from typing import TypeVar, Generic, Callable, List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import json

A = TypeVar('A')
B = TypeVar('B')


@dataclass
class TokenUsage:
    """Track token consumption for a single operation."""
    operation: str
    input_tokens: int
    output_tokens: int
    compressed_tokens: int  # After compression
    compression_ratio: float = 1.0
    timestamp: str = ""

    def cost(self) -> int:
        """Actual cost to budget."""
        return self.compressed_tokens


@dataclass
class MemorySnapshot:
    """Compressed representation of context at a point in time."""
    step: int
    quality: float
    summary: str  # 1-2 sentences
    tokens: int
    is_breakthrough: bool = False  # Did quality jump significantly?


@dataclass
class MemoryAwareLLMContext(Generic[A]):
    """
    Memory-aware context for token-constrained environments.

    Features:
    - Automatic token tracking
    - History compression
    - Smart extraction (returns compressed summary)
    - Smart duplication (selective context sharing)
    - Agent-aware (tracks which agent owns this context)
    """

    focus: A
    history_snapshots: List[MemorySnapshot] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    token_budget: int = 114000  # Available tokens (200K - system - tools - conversation)
    tokens_used: int = 0
    iteration: int = 0
    agent_id: Optional[str] = None  # None = global, "agent_X" = agent-specific
    token_log: List[TokenUsage] = field(default_factory=list)

    def extract(
        self,
        compress_to: int = 2000
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Extract focused value as compressed summary.

        Returns:
          - Compressed summary (fits in compress_to tokens)
          - Metadata about compression (ratio, quality score, etc.)
        """

        # Core value (always include)
        summary = f"Current: {str(self.focus)[:500]}"

        # Add quality score if available
        quality = self.metadata.get("quality_score", 0.0)
        if quality > 0:
            summary += f"\nQuality: {quality:.2f}"

        # Add key insights from history (ultra-compressed)
        if self.history_snapshots:
            # Find breakthrough moments (where quality jumped)
            breakthroughs = [
                s for s in self.history_snapshots
                if s.is_breakthrough
            ]

            if breakthroughs:
                summary += f"\nKey breakthroughs:"
                for bt in breakthroughs[-2:]:  # Last 2 breakthroughs
                    summary += f"\n  - {bt.summary}"

            # Show progression
            if len(self.history_snapshots) > 1:
                start_q = self.history_snapshots[0].quality
                end_q = self.history_snapshots[-1].quality
                summary += f"\nProgress: {start_q:.2f} → {end_q:.2f}"

        # Truncate to budget
        if len(summary) > compress_to * 4:  # Rough token estimate (1 token ≈ 4 chars)
            summary = summary[:compress_to * 4]
            summary += "\n[... compressed ...]"

        estimated_tokens = len(summary) // 4  # Rough estimate
        metadata = {
            "compression_ratio": estimated_tokens / max(1, len(str(self.focus)) // 4),
            "tokens_in_summary": estimated_tokens,
            "quality": quality,
            "breakthrough_count": len([s for s in self.history_snapshots if s.is_breakthrough]),
        }

        return summary, metadata

    def smart_duplicate(
        self,
        agents: List[str],
        max_tokens_per_agent: int = 3000
    ) -> Dict[str, 'MemoryAwareLLMContext']:
        """
        Distribute context to agents intelligently.

        Key: Each agent gets EXTRACTED summary, not full context
        Cost: 3K per agent, not 30K if we duplicated everything

        Args:
          agents: List of agent names
          max_tokens_per_agent: Budget per agent

        Returns:
          Dict mapping agent_name -> context for that agent
        """

        # Get compressed summary once
        shared_summary, metadata = self.extract(compress_to=1000)

        result = {}
        for agent in agents:
            agent_context = MemoryAwareLLMContext(
                focus=shared_summary,
                history_snapshots=[],  # Agent starts fresh
                metadata={
                    "agent_id": agent,
                    "parent_id": self.metadata.get("id"),
                    "task": self.metadata.get(f"task_{agent}", ""),
                    "shared_summary_tokens": 1000,
                    "max_working_memory": max_tokens_per_agent - 1000,
                },
                token_budget=max_tokens_per_agent,
                agent_id=agent,
            )
            result[agent] = agent_context

        # Log token cost
        total_cost = len(agents) * len(shared_summary) // 4
        self._log_operation(
            "smart_duplicate",
            input_tokens=len(str(self.focus)) // 4,
            output_tokens=len(shared_summary) // 4 * len(agents),
            compressed_tokens=total_cost,
        )

        return result

    def extend(
        self,
        f: Callable[['MemoryAwareLLMContext'], A],
        token_estimate: int = 2000,
    ) -> 'MemoryAwareLLMContext':
        """
        Apply function with token awareness.

        If applying f would exceed budget, automatically compress first.
        """

        # Check if we have budget for this operation
        if self.tokens_used + token_estimate > self.token_budget:
            # Compress before applying
            self = self._auto_compress()

        # Apply function
        new_focus = f(self)

        # Create snapshot
        quality = self.metadata.get("quality_score", 0.0)
        is_breakthrough = False
        if self.history_snapshots:
            last_quality = self.history_snapshots[-1].quality
            is_breakthrough = (quality - last_quality) > 0.15

        snapshot = MemorySnapshot(
            step=self.iteration,
            quality=quality,
            summary=str(new_focus)[:100],
            tokens=len(str(new_focus)) // 4,
            is_breakthrough=is_breakthrough,
        )

        # Create new context
        new_context = MemoryAwareLLMContext(
            focus=new_focus,
            history_snapshots=self.history_snapshots + [snapshot],
            metadata=self.metadata.copy(),
            token_budget=self.token_budget,
            tokens_used=self.tokens_used + token_estimate,
            iteration=self.iteration + 1,
            agent_id=self.agent_id,
            token_log=self.token_log,
        )

        new_context._log_operation(
            "extend",
            input_tokens=len(str(self.focus)) // 4,
            output_tokens=len(str(new_focus)) // 4,
            compressed_tokens=token_estimate,
        )

        return new_context

    def with_quality(self, score: float) -> 'MemoryAwareLLMContext':
        """Attach quality score to context."""
        new_meta = self.metadata.copy()
        new_meta["quality_score"] = score
        return MemoryAwareLLMContext(
            focus=self.focus,
            history_snapshots=self.history_snapshots,
            metadata=new_meta,
            token_budget=self.token_budget,
            tokens_used=self.tokens_used,
            iteration=self.iteration,
            agent_id=self.agent_id,
            token_log=self.token_log,
        )

    def consensus(
        self,
        other_contexts: List['MemoryAwareLLMContext'],
        method: str = "weighted"
    ) -> 'MemoryAwareLLMContext':
        """
        Merge results from multiple parallel agents.

        Operates on extracted summaries (not full contexts).
        """

        # Extract from all contexts
        summaries = [self.extract(compress_to=1000)[0]]
        for ctx in other_contexts:
            summary, _ = ctx.extract(compress_to=1000)
            summaries.append(summary)

        # Weighted consensus
        if method == "weighted":
            weights = [ctx.metadata.get("quality_score", 0.5) for ctx in [self] + other_contexts]
            total_weight = sum(weights)
            weights = [w / total_weight for w in weights]

            consensus_text = "Consensus (weighted):\n"
            for summary, weight in zip(summaries, weights):
                consensus_text += f"[{weight:.1%}] {summary}\n"
        else:
            consensus_text = "Consensus:\n" + "\n".join(summaries)

        return MemoryAwareLLMContext(
            focus=consensus_text,
            history_snapshots=self.history_snapshots,
            metadata=self.metadata,
            token_budget=self.token_budget,
            tokens_used=self.tokens_used + (len(summaries) * 250),  # Rough cost
            iteration=self.iteration,
            agent_id=self.agent_id,
            token_log=self.token_log,
        )

    def _auto_compress(self) -> 'MemoryAwareLLMContext':
        """Automatically compress history when approaching token limit."""

        # Keep only:
        # 1. Last 2 snapshots (most recent work)
        # 2. Breakthrough snapshots (where we made progress)
        compressed_history = []

        # Add breakthroughs
        for s in self.history_snapshots:
            if s.is_breakthrough:
                compressed_history.append(s)

        # Add last 2
        for s in self.history_snapshots[-2:]:
            if s not in compressed_history:
                compressed_history.append(s)

        # Log compression
        old_size = len(self.history_snapshots)
        new_size = len(compressed_history)

        return MemoryAwareLLMContext(
            focus=self.focus,
            history_snapshots=compressed_history,
            metadata=self.metadata,
            token_budget=self.token_budget,
            tokens_used=self.tokens_used,
            iteration=self.iteration,
            agent_id=self.agent_id,
            token_log=self.token_log,
        )

    def _log_operation(
        self,
        operation: str,
        input_tokens: int,
        output_tokens: int,
        compressed_tokens: int,
    ):
        """Log token usage for this operation."""
        ratio = compressed_tokens / max(1, input_tokens)
        usage = TokenUsage(
            operation=operation,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            compressed_tokens=compressed_tokens,
            compression_ratio=ratio,
        )
        self.token_log.append(usage)

    def token_report(self) -> str:
        """Generate token usage report."""
        report = f"Token Usage Report (Agent: {self.agent_id or 'global'})\n"
        report += f"{'=' * 60}\n"
        report += f"Budget: {self.token_budget:,}\n"
        report += f"Used: {self.tokens_used:,} ({self.tokens_used * 100 / self.token_budget:.1f}%)\n"
        report += f"Remaining: {self.token_budget - self.tokens_used:,}\n\n"

        report += "Operations:\n"
        report += f"{'Operation':<20} {'Input':>10} {'Output':>10} {'Cost':>10} {'Ratio':>8}\n"
        report += "-" * 60 + "\n"

        for log in self.token_log:
            report += (
                f"{log.operation:<20} "
                f"{log.input_tokens:>10,} "
                f"{log.output_tokens:>10,} "
                f"{log.compressed_tokens:>10,} "
                f"{log.compression_ratio:>7.2f}x\n"
            )

        return report

    def __repr__(self) -> str:
        return (
            f"MemoryAwareLLMContext(agent={self.agent_id}, "
            f"tokens_used={self.tokens_used}/{self.token_budget}, "
            f"iterations={self.iteration})"
        )

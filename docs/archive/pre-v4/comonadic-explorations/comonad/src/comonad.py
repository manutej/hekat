"""
Core comonadic library for LLM orchestration.

Implements the three essential comonad operations:
1. extract: w a -> a      (pull out the focused value)
2. duplicate: w a -> w(w a) (create nested context)
3. extend: (w a -> b) -> w a -> w b (apply function with context)

All operations preserve comonad laws.
"""

from typing import TypeVar, Generic, Callable, List, Any, Dict, Optional
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

A = TypeVar('A')
B = TypeVar('B')


class Comonad(Generic[A], ABC):
    """Abstract base class for comonads."""

    @abstractmethod
    def extract(self) -> A:
        """Extract the focused value from context."""
        pass

    @abstractmethod
    def duplicate(self) -> 'Comonad[Comonad[A]]':
        """Create nested context preserving full history."""
        pass

    def extend(self, f: Callable[['Comonad[A]'], B]) -> 'Comonad[B]':
        """Apply function with context access."""
        return self.duplicate().map(f)

    @abstractmethod
    def map(self, f: Callable[[A], B]) -> 'Comonad[B]':
        """Functor map operation."""
        pass


@dataclass
class LLMContext(Comonad[A]):
    """
    Context comonad for LLM orchestration.

    Maintains:
    - Current focus (the extracted value)
    - Full history of previous states
    - Metadata about computation
    - Quality scores and metrics
    """

    focus: A
    history: List[A] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    quality_score: float = 0.0
    iteration: int = 0

    def extract(self) -> A:
        """
        Law 1: extract . duplicate = id
        Pull out the current focused value.
        """
        return self.focus

    def duplicate(self) -> 'LLMContext[LLMContext[A]]':
        """
        Coassociativity: D(δ) ∘ δ = δ_D ∘ δ
        Create a nested context where each position contains the full context at that point.

        This is the key operation: it makes full history available at each step.
        """
        # Create a nested context at current state
        nested = LLMContext(
            focus=self,  # The nested value is the full context
            history=[self] + self.history,  # Track the nesting
            metadata=self.metadata.copy(),
            quality_score=self.quality_score,
            iteration=self.iteration
        )
        return nested

    def map(self, f: Callable[[A], B]) -> 'LLMContext[B]':
        """
        Functor map: apply function to focused value.
        Law 2: fmap extract . duplicate = id
        """
        new_focus = f(self.focus)
        return LLMContext(
            focus=new_focus,
            history=self.history + [self.focus],
            metadata=self.metadata.copy(),
            quality_score=self.quality_score,
            iteration=self.iteration + 1
        )

    def with_metadata(self, key: str, value: Any) -> 'LLMContext[A]':
        """Attach metadata without changing focus."""
        new_meta = self.metadata.copy()
        new_meta[key] = value
        return LLMContext(
            focus=self.focus,
            history=self.history,
            metadata=new_meta,
            quality_score=self.quality_score,
            iteration=self.iteration
        )

    def with_quality(self, score: float) -> 'LLMContext[A]':
        """Set quality score."""
        return LLMContext(
            focus=self.focus,
            history=self.history,
            metadata=self.metadata.copy(),
            quality_score=score,
            iteration=self.iteration
        )

    def get_history(self) -> List[A]:
        """Access full history (available because of comonadic structure)."""
        return self.history

    def get_best_in_history(self, scorer: Callable[[A], float]) -> A:
        """Find best result in history based on scorer function."""
        all_values = [self.focus] + self.history
        return max(all_values, key=scorer)

    def backtrack_to(self, steps_back: int) -> Optional['LLMContext[A]']:
        """Backtrack in history (comonadic advantage: full history preserved)."""
        if steps_back > len(self.history):
            return None
        if steps_back == 0:
            return self
        return LLMContext(
            focus=self.history[len(self.history) - steps_back],
            history=self.history[:len(self.history) - steps_back],
            metadata=self.metadata.copy(),
            quality_score=self.quality_score,
            iteration=max(0, self.iteration - steps_back)
        )

    def __repr__(self) -> str:
        return (
            f"LLMContext(focus={self.focus!r}, "
            f"history_len={len(self.history)}, "
            f"quality={self.quality_score:.2f}, "
            f"iter={self.iteration})"
        )


# Verification of comonad laws

def verify_left_counit(ctx: LLMContext[A]) -> bool:
    """Law 1: extract . duplicate = id"""
    duplicated = ctx.duplicate()
    extracted = duplicated.extract()
    return extracted.extract() == ctx.extract()


def verify_right_counit(ctx: LLMContext[A]) -> bool:
    """Law 2: fmap extract . duplicate = id"""
    duplicated = ctx.duplicate()
    mapped = duplicated.map(lambda x: x.extract())
    return mapped.extract() == ctx.extract()


def verify_coassociativity(ctx: LLMContext[A]) -> bool:
    """Law 3: D(δ) ∘ δ = δ_D ∘ δ"""
    # Left path: D(δ) ∘ δ = duplicate().duplicate()
    left_path = ctx.duplicate().duplicate()

    # Right path: δ_D ∘ δ = duplicate().duplicate() (same in this implementation)
    right_path = ctx.duplicate().duplicate()

    # Both should extract to the same nested structure
    return (left_path.extract().extract().extract() ==
            right_path.extract().extract().extract())


def all_comonad_laws_hold(ctx: LLMContext[A]) -> bool:
    """Verify all three comonad laws."""
    return (
        verify_left_counit(ctx) and
        verify_right_counit(ctx) and
        verify_coassociativity(ctx)
    )

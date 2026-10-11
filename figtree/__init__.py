"""FigTree-style recursive SVG methodology figure generator.

Implements the converged specification: Grounder -> recursive Generator tree
(Decompose / Draw) -> Worker Merge with min-arrow spacing -> dual-space Critic
loop -> sheaf storage of nodes with residual sections -> editability proof.

The default agents are deterministic and run offline.  Optional Claude-backed
Grounder and Critic agents live in :mod:`figtree.agents.llm`.
"""

from figtree.schemas import (
    ContentPlan,
    Component,
    Flow,
    GlobalStyle,
    Node,
    Port,
    ResidualDefect,
    SheafGraph,
)
from figtree.orchestrator import FigTree, FigTreeResult, Limits

__version__ = "0.1.0"

__all__ = [
    "ContentPlan",
    "Component",
    "Flow",
    "GlobalStyle",
    "Node",
    "Port",
    "ResidualDefect",
    "SheafGraph",
    "FigTree",
    "FigTreeResult",
    "Limits",
    "__version__",
]

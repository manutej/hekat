"""Verification memory (section 5): condition -> repair pairs.

The seed below is applied automatically before the Critic runs.  It is a convenience
layer and is not claimed as paper-original.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

SEED_MEMORY: List[Dict[str, str]] = [
    {"condition": "arrow length < 20", "repair": "shift target by ceil_to_grid(20-dist), recompute ports"},
    {"condition": "ungrid coordinate", "repair": "ceil snap to multiple of 8"},
    {"condition": "text overflow", "repair": "reduce font or expand block"},
    {"condition": "gradient present", "repair": "replace with flat fill from palette"},
    {"condition": "diagonal without flag", "repair": "reroute to right-angle"},
    {"condition": "port collision", "repair": "prefix with node id"},
    {"condition": "overlap after merge", "repair": "expand canvas or re-layout children"},
]


@dataclass
class VerificationMemory:
    entries: List[Dict[str, str]] = field(default_factory=lambda: [dict(e) for e in SEED_MEMORY])

    def repair_for(self, condition: str) -> Optional[str]:
        for e in self.entries:
            if e["condition"] == condition:
                return e["repair"]
        return None

    def add(self, condition: str, repair: str) -> None:
        if self.repair_for(condition) is None:
            self.entries.append({"condition": condition, "repair": repair})

    def conditions(self) -> List[str]:
        return [e["condition"] for e in self.entries]

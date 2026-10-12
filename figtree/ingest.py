"""Ingest sanitisation.

All L_v content (the source text and every child description) is treated as pure
description.  Imperative or instruction-like language is stripped on ingest so that an
adversarial document cannot steer the agents.
"""

from __future__ import annotations

import re
from typing import List, Tuple

# Lines that read as instructions to the model rather than as description.
_INSTRUCTION_LINE = re.compile(
    r"^\s*(?:[-*>]\s*)?(?:"
    r"ignore (?:all |any )?(?:previous|prior|above|the)|"
    r"disregard|forget (?:all|everything|your)|"
    r"you (?:must|should|are now|will now|have to)|"
    r"as an ai|system prompt|new instructions?|override|"
    r"instruction[s]? to the (?:model|agent|assistant)|"
    r"do not (?:follow|obey)|from now on"
    r")",
    re.IGNORECASE,
)
# Sentence-level injection fragments.
_INJECTION_SENTENCE = re.compile(
    r"(?:ignore|disregard) (?:all |any )?(?:previous|prior|above|the) [^.!?\n]*[.!?]?",
    re.IGNORECASE,
)

_IMPERATIVE_PREFIX = re.compile(
    r"^(?:please\s+)?(?:draw|render|make|create|generate|use|add|remove|delete|ignore|"
    r"output|print|execute|run|return|emit|write|build|produce|set|apply|show)\s+",
    re.IGNORECASE,
)


def sanitize_source(text: str) -> Tuple[str, List[str]]:
    """Return ``(clean_text, stripped_lines)``.

    Lines are kept intact (never truncated) so that any evidence span extracted from the
    clean text is still a verbatim substring of the original source.
    """
    kept: List[str] = []
    stripped: List[str] = []
    for line in text.splitlines():
        if _INSTRUCTION_LINE.match(line):
            stripped.append(line)
            continue
        if _INJECTION_SENTENCE.search(line):
            stripped.append(line)
            continue
        kept.append(line)
    return "\n".join(kept), stripped


def to_noun_phrase(desc: str) -> str:
    """Sanitise a child description to pure noun-phrase content."""
    d = desc.strip()
    d = re.sub(r"\s+", " ", d)
    d = _IMPERATIVE_PREFIX.sub("", d)
    d = re.sub(r"[.!?:;]+$", "", d).strip()
    d = d.replace("`", "")
    return d


def truncate(text: str, limit: int) -> str:
    return text if len(text) <= limit else text[:limit]

"""Shared SFT tag/DSL helpers.

Eval-safe: no imports from tools.sft.build (scenarios, packers, BUILD_SPEC).
Implements docs/sft/DUAL_REASONING_SPEC.md parsing helpers.
"""

from __future__ import annotations

import re
from typing import Dict, Optional

TAG_RE = {
    "pseudocode": re.compile(r"<pseudocode>(.*?)</pseudocode>", re.DOTALL | re.IGNORECASE),
    "logic": re.compile(r"<logic>(.*?)</logic>", re.DOTALL | re.IGNORECASE),
    "answer": re.compile(r"<answer>(.*?)</answer>", re.DOTALL | re.IGNORECASE),
}

_CONSTRUCTOR_RE = re.compile(
    r"\b(Sequential|Parallel|Fallback|Skilled|Commanded|Simple|Agent)\s*\(",
    re.IGNORECASE,
)
_FN_RE = re.compile(r"\b(fn|def)\b", re.IGNORECASE)
_ASSERT_RE = re.compile(r"\bassert\b", re.IGNORECASE)
_CONTROL_RE = re.compile(r"\b(if|elif|else|for|return)\b", re.IGNORECASE)
_DAG_LEAK_RE = re.compile(r"execution_order|parallel_phases", re.IGNORECASE)


def normalize_dsl(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip().replace("→", "->"))


def extract_tag(text: str, name: str) -> str:
    rx = TAG_RE[name]
    m = rx.search(text)
    if not m:
        return ""
    return m.group(1).strip()


def has_tags(text: str) -> Dict[str, bool]:
    return {name: bool(extract_tag(text, name)) for name in TAG_RE}


def tags_ok(text: str) -> bool:
    return all(has_tags(text).values())


def extract_answer_dsl(text: str) -> Optional[str]:
    body = extract_tag(text, "answer")
    if not body:
        return None
    fence = re.search(r"```(?:hekat)?\s*(.*?)```", body, re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1).strip()
    for line in body.splitlines():
        if ":" in line and any(op in line for op in (":", "->", "→", "||", "?", "+", "@")):
            return line.strip().strip("`")
    return None


def logic_style_ok(logic_body: str) -> bool:
    """Soft gate from DUAL_REASONING_SPEC §5."""
    if not logic_body.strip():
        return False
    has_fn = bool(_FN_RE.search(logic_body))
    has_assert = bool(_ASSERT_RE.search(logic_body))
    has_shape = bool(_CONSTRUCTOR_RE.search(logic_body) or _CONTROL_RE.search(logic_body))
    return has_fn and has_assert and has_shape


def assistant_has_dag_leak(text: str) -> bool:
    return bool(_DAG_LEAK_RE.search(text))

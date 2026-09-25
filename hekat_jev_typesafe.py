"""TypeSafe System One wire client for HEKAT node classification.

Faithful port of the JEV wire contract (manutej/jev src/lib/jev/typesafe/
contract.ts + seats.ts): one call, many typed questions, code gates. The model
FILLS colors (a `choice` over the five colors); the shipping gate (`score_fill`)
stays in code (jev docs/TYPESAFE.md: "What stays in code: score.ts").

No third-party deps — uses urllib. The client fires only when TYPESAFE_API_KEY
is set; otherwise `classify_color` transparently falls back to the local
bag-of-words classifier so everything keeps working offline.
"""

from __future__ import annotations

import json
import urllib.request
import urllib.error
from typing import Dict, List, Optional

from hekat_jev_config import JevConfig, load_config, NotConfigured
from hekat_jev import COLORS, Dist, empty_dist, normalize, classify_local

# Contract constants (contract.ts)
SCORE_LEVEL_MIN, SCORE_LEVEL_MAX = 2, 10
NOUL_MID_LOW, NOUL_MID_HIGH = 0.4, 0.6


# --------------------------------------------------------------------------- #
# Request builders (SystemOneRequest shape)
# --------------------------------------------------------------------------- #
def colorist_question() -> dict:
    """The `colorist` seat as a System One `choice` question (seats.ts)."""
    return {
        "type": "choice",
        "instructions": "Classify the decision port of this orchestration element "
                        "into exactly one JEV interface color.",
        "criteria": {
            "entity": "Named things: places, tables, people, tokens.",
            "concept": "Interfaces, doctrines, types, modules.",
            "idea": "Hypotheses, claims, theories.",
            "evidence": "Queries, counts, extents, OCR, catalogs.",
            "action": "Publish, compose, drop, grant, schedule.",
        },
    }


def adversary_question() -> dict:
    """The `adversary` seat: strongest forbidden fill (toxin color)."""
    return {
        "type": "choice",
        "instructions": "Which color is the strongest adversarial / forbidden fill "
                        "for this element? Answer 'none' if there is no toxin.",
        "criteria": {**{c: f"toxin: {c}" for c in COLORS}, "none": "no forbidden fill"},
    }


def build_request(state: dict, model: str, *, with_adversary: bool = True) -> dict:
    """One legal SystemOneRequest: state + typed questions (many questions, one call)."""
    questions = {"gold_color": colorist_question()}
    if with_adversary:
        questions["toxin_color"] = adversary_question()
    return {"state": state, "model": model, "questions": questions}


def validate_request(req: dict) -> Optional[str]:
    """Port of validateRequest — returns an error string or None."""
    qs = req.get("questions") or {}
    if not qs:
        return "questions map is empty"
    if req.get("model") != load_config().typesafe_model:
        return f"model must be pinned to {load_config().typesafe_model}"
    for qid, q in qs.items():
        if not q.get("instructions"):
            return f"{qid}: instructions required"
        if q.get("type") == "choice" and len(q.get("criteria") or {}) < 2:
            return f"{qid}: choice needs ≥2 criteria"
        if q.get("type") == "score":
            n = len(q.get("criteria") or [])
            if not (SCORE_LEVEL_MIN <= n <= SCORE_LEVEL_MAX):
                return f"{qid}: score needs {SCORE_LEVEL_MIN}-{SCORE_LEVEL_MAX} levels"
    return None


# --------------------------------------------------------------------------- #
# Answer → Dist
# --------------------------------------------------------------------------- #
def answers_to_dist(answers: dict) -> Dist:
    """Turn the colorist ChoiceAnswer probabilities into a color Dist."""
    ans = answers.get("gold_color") or {}
    probs = ans.get("probabilities") or {}
    dist = empty_dist()
    for c in COLORS:
        dist[c] = float(probs.get(c, 0.0))
    if sum(dist.values()) <= 0 and ans.get("choice") in dist:
        dist[ans["choice"]] = 1.0
    return normalize(dist)


def answers_to_toxin(answers: dict) -> Optional[str]:
    """The adversary's chosen forbidden color, or None."""
    ans = answers.get("toxin_color") or {}
    choice = ans.get("choice")
    return choice if choice in COLORS else None


# --------------------------------------------------------------------------- #
# Client
# --------------------------------------------------------------------------- #
class TypeSafeClient:
    """Minimal System One client. Fires only when configured with a key."""

    def __init__(self, config: Optional[JevConfig] = None):
        self.config = config or load_config()

    def fill(self, state: dict, *, with_adversary: bool = True, timeout: float = 30.0) -> dict:
        if not self.config.typesafe_live:
            raise NotConfigured("TYPESAFE_API_KEY not set")
        req = build_request(state, self.config.typesafe_model, with_adversary=with_adversary)
        err = validate_request(req)
        if err:
            raise ValueError(f"invalid System One request: {err}")
        body = json.dumps(req).encode("utf-8")
        request = urllib.request.Request(
            self.config.typesafe_endpoint,
            data=body,
            headers={
                "Authorization": f"Bearer {self.config.typesafe_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=timeout) as resp:  # nosec - endpoint is pinned
            payload = json.loads(resp.read().decode("utf-8"))
        return payload.get("answers", {})


# --------------------------------------------------------------------------- #
# Public classifier hook (used by hekat_jev.classify_orchestration)
# --------------------------------------------------------------------------- #
def make_color_fn(config: Optional[JevConfig] = None):
    """Return a callable state->Dist. Live model if keyed, else local fallback.

    The returned function never raises on a network error — it degrades to the
    local classifier so an orchestration run always completes.
    """
    cfg = config or load_config()
    if not cfg.typesafe_live:
        return None  # caller uses its default precedence (lexicon / ~color / local)

    client = TypeSafeClient(cfg)

    def color_fn(state: dict) -> Dist:
        try:
            answers = client.fill(state)
            return answers_to_dist(answers)
        except (urllib.error.URLError, NotConfigured, ValueError, KeyError):
            text = " ".join(str(v) for v in state.values())
            return classify_local(text)

    return color_fn

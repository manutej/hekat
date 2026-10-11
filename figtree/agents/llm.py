"""Claude-backed Grounder and Critic agents.

These wrap the prompts from :mod:`figtree.prompts`.  Each call enforces the schema with
structured outputs and retries at most ``max_schema_retries`` (2) times on invalid JSON,
after which the deterministic fallback is used and a ``parse_error`` residual is recorded.
The Generator and Worker stay deterministic: their behaviour is fully specified by the
layout rules, so the code view of the figure is reproducible.

Requires the ``anthropic`` package and credentials resolved by the SDK (``ANTHROPIC_API_KEY``
or an ``ant auth login`` profile).
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from figtree import prompts
from figtree.critic import StructuralCritic
from figtree.grounder import GrounderOutput, RuleBasedGrounder
from figtree.ingest import sanitize_source, truncate
from figtree.memory import VerificationMemory
from figtree.schemas import ContentPlan, GlobalStyle, ResidualDefect

DEFAULT_MODEL = "claude-opus-5-5"


def _client():
    import anthropic  # imported lazily so the package works without the SDK

    return anthropic.Anthropic()


def _call_json(client, system: str, user: str, schema: Dict[str, Any], model: str, max_retries: int) -> Dict[str, Any]:
    """Call the Messages API with a JSON schema and retry on invalid JSON (max 2)."""
    import anthropic

    last_err: Optional[Exception] = None
    content: List[Dict[str, Any]] = [{"type": "text", "text": user}]
    for attempt in range(max_retries + 1):
        try:
            with client.messages.stream(
                model=model,
                max_tokens=16000,
                system=system,
                messages=[{"role": "user", "content": content}],
                output_config={"format": {"type": "json_schema", "schema": schema}},
            ) as stream:
                msg = stream.get_final_message()
            if msg.stop_reason == "refusal":
                raise RuntimeError("request refused")
            text = "".join(b.text for b in msg.content if b.type == "text")
            return json.loads(text)
        except (json.JSONDecodeError, anthropic.BadRequestError, RuntimeError) as exc:
            last_err = exc
            content = [{"type": "text", "text": user + "\n\nYour previous output was not valid JSON for the schema. Output pure JSON only."}]
    raise ValueError(f"schema retries exhausted: {last_err}")


class ClaudeGrounder:
    def __init__(self, model: str = DEFAULT_MODEL, max_schema_retries: int = 2, max_chars: int = 8000) -> None:
        self.model = model
        self.max_schema_retries = max_schema_retries
        self.max_chars = max_chars
        self.fallback = RuleBasedGrounder(max_chars=max_chars)

    def ground(self, source_text: str) -> GrounderOutput:
        clean, stripped = sanitize_source(source_text)
        user = prompts.GROUNDER_USER.format(source=truncate(clean, self.max_chars))
        try:
            data = _call_json(_client(), prompts.GROUNDER_SYSTEM, user, prompts.CONTENT_PLAN_SCHEMA, self.model, self.max_schema_retries)
        except Exception as exc:  # noqa: BLE001
            out = self.fallback.ground(source_text)
            out.residuals.append(ResidualDefect("warning", f"parse_error: {exc}; rule-based grounding used", "grounder", "retry with schema prompt"))
            return out
        plan = ContentPlan.from_dict(data["content_plan"])
        style = GlobalStyle.from_dict(data.get("global_style", {}))
        residuals = [ResidualDefect("warning", r, "content_plan", "none") for r in data.get("residuals", [])]
        # faithfulness guard: evidence spans must appear in the source (no inventions)
        kept_components = [c for c in plan.components if c.evidence_span and c.evidence_span in clean]
        dropped = len(plan.components) - len(kept_components)
        names = {c.name for c in kept_components}
        kept_flows = [f for f in plan.flows if f.evidence_span in clean and f.src in names and f.dst in names]
        dropped += len(plan.flows) - len(kept_flows)
        if dropped:
            residuals.append(ResidualDefect("warning", f"{dropped} ungrounded element(s) omitted", "content_plan", "none; nothing invented"))
        plan.components, plan.flows = kept_components, kept_flows
        if stripped:
            residuals.append(ResidualDefect("warning", f"{len(stripped)} instruction-like line(s) stripped on ingest", "ingest", "none"))
        return GrounderOutput(plan, style, residuals, stripped)


class ClaudeCritic:
    """Dual-space critic: Claude reviews source (and image when rendered); structural rules always run."""

    def __init__(self, model: str = DEFAULT_MODEL, max_schema_retries: int = 2, memory: Optional[VerificationMemory] = None, max_chars: int = 5000) -> None:
        self.model = model
        self.max_schema_retries = max_schema_retries
        self.structural = StructuralCritic(memory)
        self.max_chars = max_chars

    def review(self, svg_text: str, style: GlobalStyle, rendered_path: Optional[str] = None, round_no: int = 0) -> List[ResidualDefect]:
        defects = self.structural.review(svg_text, style, rendered_path, round_no)
        user = prompts.CRITIC_USER.format(svg=truncate(svg_text, self.max_chars), rendered=rendered_path or "none")
        try:
            client = _client()
            if rendered_path:
                import base64

                with open(rendered_path, "rb") as fh:
                    img = base64.standard_b64encode(fh.read()).decode("utf-8")
                user_content: Any = [
                    {"type": "image", "source": {"type": "base64", "media_type": "image/png", "data": img}},
                    {"type": "text", "text": user},
                ]
                # _call_json takes a plain string; send the image via a one-off call
                import anthropic  # noqa: F401

                msg = client.messages.create(
                    model=self.model,
                    max_tokens=16000,
                    system=prompts.CRITIC_SYSTEM,
                    messages=[{"role": "user", "content": user_content}],
                    output_config={"format": {"type": "json_schema", "schema": prompts.RESIDUAL_LIST_SCHEMA}},
                )
                data = json.loads("".join(b.text for b in msg.content if b.type == "text"))
            else:
                data = _call_json(client, prompts.CRITIC_SYSTEM, user, prompts.RESIDUAL_LIST_SCHEMA, self.model, self.max_schema_retries)
        except Exception as exc:  # noqa: BLE001
            defects.append(ResidualDefect("warning", f"parse_error: {exc}; structural critic only", "critic", "retry with schema prompt", round_no))
            return defects
        seen = {(d.code_anchor, d.visual_description) for d in defects}
        for item in data.get("defects", []):
            d = ResidualDefect.from_dict(item)
            d.round_introduced = round_no
            if (d.code_anchor, d.visual_description) not in seen:
                defects.append(d)
        return defects

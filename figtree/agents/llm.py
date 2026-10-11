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


class AnthropicSDKBackend:
    """``call_json`` through the Anthropic SDK (API key or ``ant auth login`` profile)."""

    def __init__(self, model: str = DEFAULT_MODEL, max_schema_retries: int = 2) -> None:
        self.model = model
        self.max_schema_retries = max_schema_retries

    @staticmethod
    def available() -> bool:
        try:
            import anthropic  # noqa: F401
        except Exception:  # noqa: BLE001
            return False
        import os

        return bool(os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("ANTHROPIC_AUTH_TOKEN"))

    def call_json(self, system: str, user: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        return _call_json(_client(), system, user, schema, self.model, self.max_schema_retries)


def default_backend(model: Optional[str] = None):
    """SDK when credentials exist, else the Claude Code CLI (the session's own OAuth)."""
    from figtree.agents.claude_code import ClaudeCodeBackend

    if AnthropicSDKBackend.available():
        return AnthropicSDKBackend(model or DEFAULT_MODEL)
    if ClaudeCodeBackend.available():
        return ClaudeCodeBackend(model)
    raise RuntimeError("no Claude backend: set ANTHROPIC_API_KEY/anthropic SDK or run inside Claude Code")


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
    def __init__(self, model: Optional[str] = None, max_schema_retries: int = 2, max_chars: int = 8000, backend=None, adopt_style: bool = False) -> None:
        """``adopt_style``: take the model's global style; by default the paper's style record is kept
        (the content plan is what the model adds; the palette and typography stay reproducible)."""
        self.backend = backend or default_backend(model)
        self.max_schema_retries = max_schema_retries
        self.max_chars = max_chars
        self.adopt_style = adopt_style
        self.fallback = RuleBasedGrounder(max_chars=max_chars)

    def ground(self, source_text: str) -> GrounderOutput:
        clean, stripped = sanitize_source(source_text)
        user = prompts.GROUNDER_USER.format(source=truncate(clean, self.max_chars))
        try:
            data = self.backend.call_json(prompts.GROUNDER_SYSTEM, user, prompts.CONTENT_PLAN_SCHEMA)
        except Exception as exc:  # noqa: BLE001
            out = self.fallback.ground(source_text)
            out.residuals.append(ResidualDefect("warning", f"parse_error: {exc}; rule-based grounding used", "grounder", "retry with schema prompt"))
            return out
        plan = ContentPlan.from_dict(data["content_plan"])
        style = GlobalStyle.from_dict(data.get("global_style", {})) if self.adopt_style else GlobalStyle()
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

    def __init__(self, model: Optional[str] = None, max_schema_retries: int = 2, memory: Optional[VerificationMemory] = None, max_chars: int = 16000, backend=None, scope: str = "internal", max_calls: int = 12) -> None:
        """``scope``: "internal" (merged nodes only; leaves are fully covered by the structural rules),
        "root" (the final figure only) or "all".  ``max_calls`` caps the model calls per run.
        ``max_chars`` is 16000 rather than the specification's 5000: a truncated root figure made
        the model report the truncation itself as a defect."""
        self.backend = backend or default_backend(model)
        self.model = model
        self.max_schema_retries = max_schema_retries
        self.structural = StructuralCritic(memory)
        self.max_chars = max_chars
        self.scope = scope
        self.max_calls = max_calls
        self.calls = 0

    def review(self, svg_text: str, style: GlobalStyle, rendered_path: Optional[str] = None, round_no: int = 0, padded: bool = True) -> List[ResidualDefect]:
        defects = self.structural.review(svg_text, style, rendered_path, round_no, padded=padded)
        is_internal = svg_text.count("data-bbox=") > 2
        if self.scope == "none" or (self.scope == "internal" and not is_internal) or (self.scope == "root" and 'id="n1"' not in svg_text) or self.calls >= self.max_calls:
            return defects
        self.calls += 1
        user = prompts.CRITIC_USER.format(svg=truncate(svg_text, self.max_chars), rendered=rendered_path or "none")
        try:
            if rendered_path and isinstance(self.backend, AnthropicSDKBackend):
                client = _client()
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
                    model=self.backend.model,
                    max_tokens=16000,
                    system=prompts.CRITIC_SYSTEM,
                    messages=[{"role": "user", "content": user_content}],
                    output_config={"format": {"type": "json_schema", "schema": prompts.RESIDUAL_LIST_SCHEMA}},
                )
                data = json.loads("".join(b.text for b in msg.content if b.type == "text"))
            else:
                data = self.backend.call_json(prompts.CRITIC_SYSTEM, user, prompts.RESIDUAL_LIST_SCHEMA)
        except Exception as exc:  # noqa: BLE001
            defects.append(ResidualDefect("warning", f"parse_error: {exc}; structural critic only", "critic", "retry with schema prompt", round_no))
            return defects
        seen = {(d.code_anchor, d.visual_description) for d in defects}
        for item in data.get("defects", []):
            d = ResidualDefect.from_dict(item)
            d.round_introduced = round_no
            # model findings are advisory: they are recorded and repaired when anchored, but
            # never drive the structural re-decompose rule (that needs a measurable defect)
            d.code_anchor = f"model:{d.code_anchor}"
            if (d.code_anchor, d.visual_description) not in seen:
                defects.append(d)
        return defects


class ClaudeEditor:
    """Turn a prose edit request into an anchored edit script (the VLM side of the refine loop)."""

    def __init__(self, model: Optional[str] = None, backend=None) -> None:
        self.backend = backend or default_backend(model)

    def propose(self, svg_text: str, request: str, issues: Optional[List[Dict[str, Any]]] = None, rubric: str = "teaching") -> List[Dict[str, Any]]:
        user = prompts.EDITOR_USER.format(svg=truncate(svg_text, 12000), request=request, issues=json.dumps(issues or [], indent=1), rubric=rubric)
        data = self.backend.call_json(prompts.EDITOR_SYSTEM, user, prompts.EDIT_SCRIPT_SCHEMA)
        return [op for op in data.get("edits", []) if isinstance(op, dict)]


class ClaudeDraughtsman:
    """Icon draughtsman: an IconSpec in, inner SVG (24-grid, 2px strokes) out."""

    def __init__(self, model: Optional[str] = None, backend=None) -> None:
        self.backend = backend or default_backend(model)

    def __call__(self, spec) -> str:
        data = self.backend.call_json(prompts.ICON_SYSTEM, spec.prompt(), prompts.ICON_SCHEMA)
        return data.get("inner_svg", "")

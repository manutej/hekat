"""Claude Code backend: drive the ``claude`` CLI headlessly on the session's own OAuth.

No API key is needed: ``claude -p`` runs with whatever credentials Claude Code holds (the
OAuth login of the person running the session).  Each call is a single turn with no tools,
structured output enforced through ``--json-schema``, and at most two retries on invalid
output, matching the specification's schema-retry rule.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from typing import Any, Dict, Optional


class ClaudeCodeBackend:
    """``call_json(system, user, schema) -> dict`` via the Claude Code CLI."""

    def __init__(self, model: Optional[str] = None, max_schema_retries: int = 2, timeout: int = 600, effort: Optional[str] = None) -> None:
        self.model = model
        self.max_schema_retries = max_schema_retries
        self.timeout = timeout
        self.effort = effort
        self.last_cost_usd = 0.0
        self.calls = 0

    @staticmethod
    def available() -> bool:
        return shutil.which("claude") is not None

    def call_json(self, system: str, user: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        exe = shutil.which("claude")
        if exe is None:
            raise RuntimeError("the `claude` CLI is not on PATH")
        prompt = user
        last_err: Optional[str] = None
        for attempt in range(self.max_schema_retries + 1):
            cmd = [
                exe, "-p", prompt,
                "--output-format", "json",
                "--json-schema", json.dumps(schema),
                "--system-prompt", system,
                "--tools", "",
                "--no-session-persistence",
            ]
            if self.model:
                cmd += ["--model", self.model]
            if self.effort:
                cmd += ["--effort", self.effort]
            env = dict(os.environ)
            env.setdefault("CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC", "1")
            proc = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout, env=env)
            self.calls += 1
            try:
                data = json.loads(proc.stdout.strip().splitlines()[-1]) if proc.stdout.strip() else {}
            except json.JSONDecodeError:
                data = {}
            self.last_cost_usd += float(data.get("total_cost_usd") or 0.0)
            if data.get("is_error"):
                last_err = str(data.get("result"))
                if "Authentication" in last_err or "auth" in last_err.lower():
                    raise RuntimeError(f"claude CLI authentication failed: {last_err}")
                prompt = user + "\n\nYour previous output was not valid. Output only JSON matching the schema."
                continue
            structured = data.get("structured_output")
            if isinstance(structured, dict):
                return structured
            text = data.get("result") or ""
            try:
                return _parse_loose_json(text)
            except ValueError as exc:
                last_err = f"{exc}: {text[:200]}"
                prompt = user + "\n\nYour previous output was not valid JSON for the schema. Output pure JSON only."
        raise ValueError(f"schema retries exhausted: {last_err}")


def _parse_loose_json(text: str) -> Dict[str, Any]:
    t = text.strip()
    if t.startswith("```"):
        t = t.strip("`")
        t = t[t.find("{"):]
    start, end = t.find("{"), t.rfind("}")
    if start < 0 or end < 0:
        raise ValueError("no JSON object in output")
    return json.loads(t[start : end + 1])

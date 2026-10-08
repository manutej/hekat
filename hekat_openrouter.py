"""OpenRouter agent runner for HEKAT.

Turns a HEKAT agent node into an actual LLM call through OpenRouter, so the
orchestration can be *run*, not just planned. Each agent gets a role-specific
system prompt; its output is then handed to the JEV classifier/gate.

Stdlib only (urllib). Fires only when OPENROUTER_API_KEY is set; otherwise
`run_agent` returns a deterministic, role-flavored MOCK so the whole interface
works offline — "just add an API key" to make it live.
"""

from __future__ import annotations

import json
import time
import urllib.request
import urllib.error
from dataclasses import dataclass
from typing import List, Optional

from hekat_jev_config import JevConfig, load_config, NotConfigured

# Role system-prompts — how each HEKAT agent behaves when actually run.
AGENT_ROLES = {
    "deep-researcher": "You are a research agent. Gather and cite concrete evidence, "
        "counts, and sources. Prefer verifiable facts over speculation.",
    "api-architect": "You are an API architect. Produce concrete interface/type/module "
        "designs: endpoints, schemas, contracts.",
    "frontend-architect": "You are a frontend architect. Specify components, state, and "
        "UI structure concretely.",
    "practical-programmer": "You are a pragmatic programmer. Produce working, concrete "
        "implementation steps or code.",
    "code-craftsman": "You are a code craftsman. Refactor and implement clean, concrete code.",
    "test-engineer": "You are a test engineer. Produce concrete test cases, measured "
        "checks, and pass/fail evidence.",
    "debug-detective": "You are a debugging agent. Produce concrete, evidence-based "
        "diagnoses from logs and measurements.",
    "deployment-orchestrator": "You are a deployment agent. Produce concrete, ordered "
        "deploy/ship actions.",
    "mercurio-orchestrator": "You are a synthesis orchestrator. Form hypotheses and "
        "integrate ideas across sources.",
    "project-orchestrator": "You are a planning orchestrator. Propose strategy and "
        "high-level direction.",
    "docs-generator": "You are a documentation agent. Produce concrete reference docs "
        "for interfaces and modules.",
}
DEFAULT_ROLE = "You are a capable agent. Complete the task concretely and verifiably."


@dataclass
class AgentResult:
    agent: str
    task: str
    output: str
    model: str
    live: bool
    latency_ms: int
    error: Optional[str] = None


class OpenRouterClient:
    def __init__(self, config: Optional[JevConfig] = None):
        self.config = config or load_config()

    def chat(self, messages: List[dict], model: Optional[str] = None,
             timeout: float = 45.0, max_tokens: int = 400) -> str:
        if not self.config.openrouter_live:
            raise NotConfigured("OPENROUTER_API_KEY not set")
        body = json.dumps({
            "model": model or self.config.openrouter_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.3,
        }).encode("utf-8")
        req = urllib.request.Request(
            self.config.openrouter_endpoint, data=body, method="POST",
            headers={
                "Authorization": f"Bearer {self.config.openrouter_api_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://github.com/manutej/hekat",
                "X-Title": "HEKAT x JEV",
            },
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # nosec - pinned endpoint
            payload = json.loads(resp.read().decode("utf-8"))
        return payload["choices"][0]["message"]["content"]


def _mock_output(agent: str, task: str) -> str:
    """Deterministic, role-flavored stand-in used when no key is set."""
    role_word = {
        "deep-researcher": "Evidence gathered:", "test-engineer": "Test results:",
        "debug-detective": "Diagnosis (measured):", "api-architect": "Interface design:",
        "frontend-architect": "Component spec:", "practical-programmer": "Implementation:",
        "code-craftsman": "Refactor:", "deployment-orchestrator": "Deploy plan:",
        "docs-generator": "Docs:", "mercurio-orchestrator": "Hypothesis:",
        "project-orchestrator": "Strategy:",
    }.get(agent, "Output:")
    return f"[MOCK · {agent}] {role_word} for task '{task}'. " \
           f"(Set OPENROUTER_API_KEY to run this agent for real.)"


def run_agent(agent: str, task: str, config: Optional[JevConfig] = None,
              model: Optional[str] = None) -> AgentResult:
    """Run one agent on a task. Live via OpenRouter when keyed, else a mock."""
    cfg = config or load_config()
    t0 = time.time()
    if not cfg.openrouter_live:
        return AgentResult(agent, task, _mock_output(agent, task),
                           model=model or cfg.openrouter_model, live=False,
                           latency_ms=0)
    system = AGENT_ROLES.get(agent, DEFAULT_ROLE)
    try:
        out = OpenRouterClient(cfg).chat(
            [{"role": "system", "content": system},
             {"role": "user", "content": task}],
            model=model)
        return AgentResult(agent, task, out, model=model or cfg.openrouter_model,
                           live=True, latency_ms=int((time.time() - t0) * 1000))
    except (urllib.error.URLError, NotConfigured, KeyError, ValueError) as exc:
        return AgentResult(agent, task, _mock_output(agent, task),
                           model=model or cfg.openrouter_model, live=False,
                           latency_ms=int((time.time() - t0) * 1000),
                           error=str(exc))

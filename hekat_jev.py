"""HEKAT ⇄ JEV bridge — classify and gate agent orchestrations.

This module upgrades HEKAT from a *static planner* (pattern + L1-L7 complexity)
into a *classified, gated orchestration*: every element of a HEKAT query is
assigned a JEV interface color, every composition edge is checked with the JEV
operad rule ``γ`` (compose only on a color match), and the whole orchestration
is scored with the JEV fail-closed shipping gate (GREEN / AMBER / RED).

It is a faithful Python port of the pure JEV FP kernel
(``manutej/jev`` — ``src/lib/jev/{colors,score,operad,temporal}.ts``,
applied Libkind–Myers double operads, arXiv:2505.18329). The TypeScript kernel
is a *library folder with no package/CLI*, so the contract is re-implemented
here rather than shelled out to. Semantics match the source exactly:

  - five colors, load-bearing order  entity=0 concept=1 idea=2 evidence=3 action=4
  - thresholds τ_green=0.72  τ_toxin=0.12  τ_red=0.4
  - fail closed: composition ships only on GREEN
  - triage vocabulary  compose | escalate | refuse   (jev eval/depth4 + judge seat)

Pure and effect-free (jev "elder C8"): no IO, no fetch, no wait. Durable
execution (the Temporal tape) is modelled in-process here, mirroring
``temporal.ts``; the real durable runtime lives in ``manutej/jev-tape``.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from hekat_parser import (
    QueryNode, ExpressionNode, SimpleNode, SequentialNode, ParallelNode,
    FallbackNode, EnsembleNode, CommandedNode, SkilledNode,
)

# --------------------------------------------------------------------------- #
# Colors — jev/src/lib/jev/colors.ts  (order is load-bearing)
# --------------------------------------------------------------------------- #
COLORS: Tuple[str, ...] = ("entity", "concept", "idea", "evidence", "action")

COLOR_META: Dict[str, Dict[str, str]] = {
    "entity":   {"short": "E", "blurb": "Named things: places, tables, people, tokens."},
    "concept":  {"short": "C", "blurb": "Interfaces, doctrines, types, modules."},
    "idea":     {"short": "I", "blurb": "Hypotheses, claims, theories."},
    "evidence": {"short": "V", "blurb": "Queries, counts, extents, OCR, catalogs."},
    "action":   {"short": "A", "blurb": "Publish, compose, drop, grant, schedule."},
}


def is_color(value: Optional[str]) -> bool:
    return value in COLOR_META


# --------------------------------------------------------------------------- #
# Fail-closed shipping gate — jev/src/lib/jev/score.ts
# --------------------------------------------------------------------------- #
Verdict = str  # "GREEN" | "AMBER" | "RED"
Dist = Dict[str, float]


@dataclass(frozen=True)
class Thresholds:
    green: float = 0.72   # allowed mass must be ≥ this for GREEN
    toxin: float = 0.12   # toxin mass above this is always RED (fail closed)
    red: float = 0.40     # allowed mass below this is RED even without toxin


DEFAULT_THRESHOLDS = Thresholds()


def empty_dist() -> Dist:
    return {c: 0.0 for c in COLORS}


def normalize(dist: Dist) -> Dist:
    z = sum(max(0.0, dist.get(c, 0.0)) for c in COLORS)
    if z <= 0:
        return empty_dist()
    return {c: max(0.0, dist.get(c, 0.0)) / z for c in COLORS}


@dataclass
class JevScore:
    verdict: Verdict
    allowed_mass: float
    toxin_mass: float
    p_max: Tuple[str, float]
    dist: Dist
    reasons: List[str]


def score_fill(
    dist: Dist,
    allowed: Set[str],
    forbidden: Set[str],
    tau: Thresholds = DEFAULT_THRESHOLDS,
) -> JevScore:
    """Port of scoreFill (score.ts:43-77). Exact decision order preserved."""
    p = normalize(dist)
    allowed_mass = sum(p[c] for c in COLORS if c in allowed)
    toxin_mass = sum(p[c] for c in COLORS if c in forbidden)
    p_max = max(((c, p[c]) for c in COLORS), key=lambda kv: kv[1])

    reasons: List[str] = []
    if toxin_mass > tau.toxin:
        verdict = "RED"
        reasons.append(f"Toxin mass {toxin_mass:.2f} exceeds τ_t={tau.toxin}")
    elif allowed_mass < tau.red:
        verdict = "RED"
        reasons.append(f"Allowed mass {allowed_mass:.2f} below τ_r={tau.red}")
    elif allowed_mass >= tau.green and toxin_mass <= tau.toxin:
        verdict = "GREEN"
        reasons.append(f"Allowed {allowed_mass:.2f} ≥ τ_g={tau.green}; toxin {toxin_mass:.2f}")
    else:
        verdict = "AMBER"
        reasons.append(f"Allowed {allowed_mass:.2f} in ({tau.red}, {tau.green}); needs more evidence")

    if verdict != "GREEN":
        reasons.append("Fail closed — composition does not ship")
    return JevScore(verdict, allowed_mass, toxin_mass, p_max, p, reasons)


def brier(dist: Dist, gold: str) -> float:
    """Brier score vs a one-hot gold color. Lower is better (score.ts:80)."""
    p = normalize(dist)
    return sum((p[c] - (1.0 if c == gold else 0.0)) ** 2 for c in COLORS)


# --------------------------------------------------------------------------- #
# Triage — jev eval/depth4 Branch + judge seat
# --------------------------------------------------------------------------- #
TRIAGE: Dict[Verdict, str] = {"GREEN": "compose", "AMBER": "escalate", "RED": "refuse"}


# --------------------------------------------------------------------------- #
# Classifier — assign a JEV color to a HEKAT element
# --------------------------------------------------------------------------- #
# Default output color per known HEKAT agent, read off COLOR_META meanings and
# the jev gate op  [idea, evidence] → action. Override any of these inline in
# the DSL with the ~color modifier (e.g. `deep-researcher~idea`).
AGENT_COLOR_LEXICON: Dict[str, str] = {
    # evidence — queries, counts, catalogs, checks
    "deep-researcher": "evidence", "test-engineer": "evidence",
    "test-runner": "evidence", "debug-detective": "evidence",
    "coverage-analyzer": "evidence", "context7-doc-reviewer": "evidence",
    "doc-rag-builder": "evidence", "youtube-summarizer": "evidence",
    "tax-analyst": "evidence",
    # concept — interfaces, types, modules, doctrines
    "api-architect": "concept", "frontend-architect": "concept",
    "docs-generator": "concept", "hekat-agent": "concept",
    "skill-builder": "concept", "symbolic-visualizer": "concept",
    "claude-sdk-expert": "concept", "mcp-integration-wizard": "concept",
    # idea — hypotheses, synthesis, theories, orchestration intent
    "mercurio-orchestrator": "idea", "project-orchestrator": "idea",
    "mercurio-agent": "idea", "mars-agent": "idea",
    "voice-mode-orchestrator": "idea", "linear-mcp-orchestrator": "idea",
    "wikijs-graphql-orchestrator": "idea",
    # action — publish, compose, deploy, grant, schedule, implement
    "practical-programmer": "action", "code-craftsman": "action",
    "code-trimmer": "action", "deployment-orchestrator": "action",
    "devops-github-expert": "action", "git-genius": "action",
    "github-workflow-expert": "action", "flutter-app-builder": "action",
    "unix-bash-expert": "action", "unix-command-master": "action",
    "claude-plugin-marketplace-builder": "action",
    # entity — named data things / stores
    "astro-data-manager": "entity", "task-memory-manager": "entity",
}

# Compact bag-of-words per color, ported in spirit from jev lexicon.ts.
_LEX: Dict[str, Tuple[str, ...]] = {
    "entity": ("table", "token", "user", "file", "record", "store", "dataset", "catalog", "schema", "database"),
    "concept": ("design", "architect", "interface", "type", "module", "api", "doctrine", "pattern", "spec", "model"),
    "idea": ("research", "hypothesis", "theory", "explore", "propose", "synthesize", "strategy", "consensus", "evaluate", "investigate"),
    "evidence": ("test", "measure", "count", "query", "verify", "check", "benchmark", "audit", "validate", "coverage"),
    "action": ("build", "implement", "deploy", "ship", "publish", "refactor", "compose", "fix", "create", "run"),
}
_PRIOR = 0.04  # uniform prior so no color collapses to zero (lexicon.ts)


def classify_local(text: str) -> Dist:
    """Bag-of-words color distribution for a free-text prompt (lexicon.ts:95)."""
    tokens = [t for t in "".join(ch.lower() if ch.isalnum() else " " for ch in text).split() if len(t) > 1]
    dist = {c: _PRIOR for c in COLORS}
    for tok in tokens:
        for color, words in _LEX.items():
            for w in words:
                if tok.startswith(w) or w.startswith(tok):
                    dist[color] += 1.0
                    break
    return normalize(dist)


def classify_agent(name: str) -> str:
    """Output color of a HEKAT agent: lexicon, else heuristic, else concept."""
    if name in AGENT_COLOR_LEXICON:
        return AGENT_COLOR_LEXICON[name]
    lowered = name.lower()
    if any(k in lowered for k in ("research", "orchestrat", "synth")):
        return "idea"
    if any(k in lowered for k in ("test", "debug", "audit", "coverage", "analy")):
        return "evidence"
    if any(k in lowered for k in ("deploy", "programmer", "build", "ops", "git")):
        return "action"
    if any(k in lowered for k in ("data", "memory", "store")):
        return "entity"
    return "concept"


def classify_expr_color(expr: ExpressionNode) -> str:
    """JEV color of a single orchestration node.

    Precedence: explicit ~color modifier  >  agent lexicon  >  node-kind default.
    """
    port = getattr(expr, "port", None)
    if is_color(port):
        return port  # the ~color modifier wins — this is the DSL classification hook

    if isinstance(expr, SimpleNode):
        return classify_agent(expr.name)
    if isinstance(expr, SkilledNode):
        return classify_agent(expr.agent)  # skills refine, don't recolor
    if isinstance(expr, EnsembleNode):
        return "idea"        # sample^N;merge;synthesize is hypothesis generation
    if isinstance(expr, CommandedNode):
        return "evidence"    # @cmd(agent) injects docs/context → evidence (fillOperation)
    return "concept"


# --------------------------------------------------------------------------- #
# γ edge gate — jev operad checkPort (compose only on color match)
# --------------------------------------------------------------------------- #
# What input color each consumer color legitimately accepts on a → hand-off.
# Derived from the doctrine ops in jev doctrines.ts (e.g. update:[entity,action],
# gate:[idea,evidence]→action, readout:entity→evidence). A producer→consumer
# edge is a clean seam when the producer's color ∈ the consumer's accepted set.
ACCEPTS: Dict[str, Set[str]] = {
    "entity":   {"entity", "action"},
    "concept":  {"concept", "idea", "entity"},
    "idea":     {"idea", "evidence", "concept"},
    "evidence": {"entity", "concept", "idea", "evidence"},
    "action":   {"idea", "evidence", "concept", "action"},
}


@dataclass
class EdgeGate:
    src_label: str
    dst_label: str
    src_color: str
    dst_color: str
    ok: bool
    reason: str


def gate_edge(src_color: str, dst_color: str, src_label: str, dst_label: str) -> EdgeGate:
    """γ for one composition edge: does the producer color plug into the consumer?"""
    ok = src_color in ACCEPTS.get(dst_color, set())
    if ok:
        reason = f"{src_color} plugs into {dst_color} port"
    else:
        reason = (f"color-mismatch: {dst_color} does not accept {src_color} "
                  f"— insert a bridge (adapter) agent")
    return EdgeGate(src_label, dst_label, src_color, dst_color, ok, reason)


# --------------------------------------------------------------------------- #
# Temporal-shaped durable tape — jev/src/lib/jev/temporal.ts
# (in-process model of the jev-tape "TypeSafe qualifies, Temporal records" run)
# --------------------------------------------------------------------------- #
@dataclass
class TapeEvent:
    seq: int
    type: str
    payload: dict


@dataclass
class Tape:
    run_id: str
    workflow: str = "HekatOrchestration"
    events: List[TapeEvent] = field(default_factory=list)

    def append(self, etype: str, payload: dict) -> None:
        self.events.append(TapeEvent(len(self.events), etype, payload))


def replay(tape: Tape) -> dict:
    """Fold the event log back to final state (temporal.ts replay)."""
    verdict = None
    composed = False
    for e in tape.events:
        if e.type == "VerdictRecorded":
            verdict = e.payload.get("verdict")
        if e.type == "CompositionAttempted":
            composed = bool(e.payload.get("ok"))
    return {"verdict": verdict, "composed": composed, "events": len(tape.events)}


# --------------------------------------------------------------------------- #
# Top-level: classify + gate a whole orchestration
# --------------------------------------------------------------------------- #
# Default gate policy: a shippable orchestration is grounded (entity/concept/
# evidence) and/or actionable (action); pure idea (unbacked speculation) is not
# allowed on its own. Forbid a color to assert a constraint that fails closed
# (e.g. forbid "action" for a read-only / dry-run pipeline).
DEFAULT_ALLOWED: Set[str] = {"entity", "concept", "evidence", "action"}
DEFAULT_FORBIDDEN: Set[str] = set()


@dataclass
class OrchestrationClassification:
    node_colors: List[Tuple[str, str]]          # (label, color) per DAG node
    color_counts: Dict[str, int]
    edges: List[EdgeGate]
    score: JevScore
    triage: str                                 # compose | escalate | refuse
    tape: Tape


def _label(expr: ExpressionNode) -> str:
    if isinstance(expr, SimpleNode):
        return expr.name
    if isinstance(expr, SkilledNode):
        return f"{expr.agent}+{'+'.join(expr.skills)}"
    if isinstance(expr, EnsembleNode):
        return f"{expr.base}^{expr.count}"
    if isinstance(expr, CommandedNode):
        return f"@{expr.command}({','.join(expr.agents) if expr.agents else '?'})"
    return type(expr).__name__


def _expr_state(expr: ExpressionNode, prompt: str) -> dict:
    """Build the TypeSafe `state` for one node (fed to the colorist seat)."""
    state = {"kind": type(expr).__name__, "prompt": prompt, "label": _label(expr)}
    if isinstance(expr, SimpleNode):
        state["agent"] = expr.name
    elif isinstance(expr, SkilledNode):
        state["agent"] = expr.agent
        state["skills"] = list(expr.skills)
    elif isinstance(expr, EnsembleNode):
        state["agent"] = expr.base
    elif isinstance(expr, CommandedNode):
        state["command"] = expr.command
        state["agents"] = list(expr.agents)
    return state


def node_color(expr: ExpressionNode, prompt: str, color_fn=None) -> str:
    """Color of a node. Precedence: ~color modifier > live model (color_fn) >
    lexicon/default. The explicit modifier is a human assertion and always wins."""
    port = getattr(expr, "port", None)
    if is_color(port):
        return port
    if color_fn is not None:
        dist = color_fn(_expr_state(expr, prompt))
        return max(((c, dist[c]) for c in COLORS), key=lambda kv: kv[1])[0]
    return classify_expr_color(expr)


def classify_orchestration(
    query: QueryNode,
    dag,                                        # hekat_dag_builder.DAG
    allowed: Set[str] = DEFAULT_ALLOWED,
    forbidden: Set[str] = DEFAULT_FORBIDDEN,
    tau: Thresholds = DEFAULT_THRESHOLDS,
    run_id: str = "run",
    color_fn=None,                              # optional state->Dist (live TypeSafe model)
) -> OrchestrationClassification:
    """Classify every DAG node, gate every edge, score + triage the whole run,
    and write a durable Temporal-shaped tape of the decision.

    If `color_fn` is given (e.g. from hekat_jev_typesafe.make_color_fn), the live
    model classifies each node; otherwise the local lexicon/`~color` path is used.
    """
    tape = Tape(run_id=run_id)
    tape.append("WorkflowStarted", {"prompt": query.prompt})

    # 1. classify each node (colorist seat, one per element)
    node_colors: List[Tuple[str, str]] = []
    color_of: Dict[int, str] = {}
    for nid, node in dag.nodes.items():
        color = node_color(node.expr, query.prompt, color_fn)
        color_of[nid] = color
        label = _label(node.expr)
        node_colors.append((label, color))
        tape.append("SlotSelected", {"node": nid, "label": label, "color": color})

    counts = {c: 0 for c in COLORS}
    for _, color in node_colors:
        counts[color] += 1

    # 2. γ-gate each composition edge (dependency → dependent)
    edges: List[EdgeGate] = []
    for nid, node in dag.nodes.items():
        for dep in sorted(node.dependencies):
            eg = gate_edge(color_of[dep], color_of[nid],
                           _label(dag.nodes[dep].expr), _label(node.expr))
            edges.append(eg)
            tape.append("CompositionAttempted", {"from": dep, "to": nid, "ok": eg.ok})

    # 3. score the whole orchestration with the fail-closed gate
    dist = {c: float(counts[c]) for c in COLORS}
    score = score_fill(dist, allowed, forbidden, tau)
    # a broken seam (color-mismatch edge) cannot ship green — fail closed
    if score.verdict == "GREEN" and any(not e.ok for e in edges):
        score.verdict = "AMBER"
        score.reasons.append("Downgraded: a composition edge has a color-mismatch seam")
    tape.append("VerdictRecorded", {"verdict": score.verdict,
                                     "allowed_mass": round(score.allowed_mass, 3)})

    triage = TRIAGE[score.verdict]
    tape.append("WorkflowCompleted", {"triage": triage})

    return OrchestrationClassification(
        node_colors=node_colors, color_counts=counts, edges=edges,
        score=score, triage=triage, tape=tape,
    )

"""Durable execution for HEKAT orchestrations — a tree of JEV workers.

Mirrors the jev-tape / volumetric-intelligence contract ("TypeSafe qualifies,
Temporal records"): a HEKAT DAG becomes a tree of gated workers over the stages
DEFINE → ASSIGN → ROUTE → STATE → GUARD → SHIP, each phase a worker cohort, each
hand-off γ-gated, the whole run recorded on a replayable tape.

Two backends, chosen by config:
  - InProcessRunner  (default) — runs the tree locally on hekat_jev.Tape.
  - TemporalRunner   — submits to a Temporal worker tree when TEMPORAL_ADDRESS
                       and the `temporalio` SDK (+ a jev-tape clone) are present.

Human-in-the-loop uses start / query / signal, matching the volumetric-
intelligence API routes (Temporal Query / Signal · Vercel run-status / hook).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from hekat_jev import (
    classify_orchestration, OrchestrationClassification, replay, TRIAGE, Tape,
)
from hekat_jev_config import JevConfig, load_config, NotConfigured

STAGES = ["DEFINE", "ASSIGN", "ROUTE", "STATE", "GUARD", "SHIP"]

# GREEN/AMBER/RED ⇄ ship/hold/block (volumetric-intelligence gate vocabulary)
GATE_WORD = {"GREEN": "ship", "AMBER": "hold", "RED": "block"}


@dataclass
class WorkerCohort:
    """One phase of the DAG = one concurrent cohort of JEV workers."""
    phase: int
    workers: List[str]                 # node labels running together


@dataclass
class RunRecord:
    run_id: str
    backend: str
    stages: List[str]
    cohorts: List[WorkerCohort]
    classification: OrchestrationClassification
    gate: str                          # ship | hold | block
    triage: str                        # compose | escalate | refuse

    def summary(self) -> dict:
        return {
            "run_id": self.run_id,
            "backend": self.backend,
            "verdict": self.classification.score.verdict,
            "gate": self.gate,
            "triage": self.triage,
            "cohorts": [{"phase": c.phase, "workers": c.workers} for c in self.cohorts],
            "tape": replay(self.classification.tape),
        }


def _cohorts_from_dag(dag) -> List[WorkerCohort]:
    from hekat_jev import _label
    out: List[WorkerCohort] = []
    for phase in sorted(dag.parallel_phases.keys()):
        labels = [_label(dag.nodes[nid].expr) for nid in sorted(dag.parallel_phases[phase])]
        out.append(WorkerCohort(phase=phase, workers=labels))
    return out


class InProcessRunner:
    """Default backend: runs the JEV worker tree locally on hekat_jev.Tape."""

    backend = "in-process"

    def __init__(self, config: Optional[JevConfig] = None, color_fn=None):
        self.config = config or load_config()
        self.color_fn = color_fn
        self._runs: Dict[str, RunRecord] = {}

    def start(self, query, dag, *, allowed=None, forbidden=None, run_id: str = "run") -> RunRecord:
        kwargs = {"run_id": run_id, "color_fn": self.color_fn}
        if allowed is not None:
            kwargs["allowed"] = allowed
        if forbidden is not None:
            kwargs["forbidden"] = forbidden
        clf = classify_orchestration(query, dag, **kwargs)
        record = RunRecord(
            run_id=run_id, backend=self.backend, stages=STAGES,
            cohorts=_cohorts_from_dag(dag), classification=clf,
            gate=GATE_WORD[clf.score.verdict], triage=clf.triage,
        )
        self._runs[run_id] = record
        return record

    def query(self, run_id: str) -> dict:
        """Read the tape without writing (Temporal Query / Vercel run-status)."""
        rec = self._runs.get(run_id)
        if not rec:
            return {"run_id": run_id, "status": "unknown"}
        return rec.summary()

    def signal(self, run_id: str, decision: str) -> dict:
        """Human verdict on a HOLD/AMBER run (Temporal Signal / Vercel hook)."""
        rec = self._runs.get(run_id)
        if not rec:
            return {"run_id": run_id, "status": "unknown"}
        rec.classification.tape.append("HumanSignal", {"decision": decision})
        return {"run_id": run_id, "decision": decision, "gate": rec.gate}


class TemporalRunner:
    """Live backend. Submits the worker tree to Temporal when available.

    Requires TEMPORAL_ADDRESS + the `temporalio` SDK. When those are present this
    hands the same cohort tree to the jev-tape workflow; until then it reports
    exactly what is missing so the switch is a config change, not a code change.
    """

    backend = "temporal"

    def __init__(self, config: Optional[JevConfig] = None, color_fn=None):
        self.config = config or load_config()
        self.color_fn = color_fn

    @staticmethod
    def sdk_available() -> bool:
        try:
            import temporalio  # noqa: F401
            return True
        except Exception:
            return False

    def preflight(self) -> Optional[str]:
        if not self.config.temporal_live:
            return "TEMPORAL_ADDRESS not set"
        if not self.sdk_available():
            return "temporalio SDK not installed (pip install temporalio)"
        if not self.config.jev_tape_path:
            return "JEV_TAPE_PATH not set (clone manutej/jev-tape and point to it)"
        return None

    def start(self, query, dag, *, allowed=None, forbidden=None, run_id: str = "run") -> RunRecord:
        missing = self.preflight()
        if missing:
            raise NotConfigured(f"Temporal backend unavailable: {missing}")
        # When live: build the cohort tree + gate policy and submit to the
        # jev-tape workflow. The classification (colors, γ, score_fill) is the
        # activity payload; Temporal records the tape. Wiring lives in jev-tape.
        from importlib import import_module
        jt = import_module("jev_tape")  # provided by the JEV_TAPE_PATH clone
        return jt.submit_hekat_run(  # type: ignore[attr-defined]
            query=query, dag=dag, allowed=allowed, forbidden=forbidden,
            run_id=run_id, color_fn=self.color_fn, stages=STAGES,
        )


def get_runner(config: Optional[JevConfig] = None, color_fn=None):
    """Pick the durable backend: Temporal if fully configured, else in-process."""
    cfg = config or load_config()
    if cfg.temporal_live and TemporalRunner.sdk_available() and cfg.jev_tape_path:
        return TemporalRunner(cfg, color_fn=color_fn)
    return InProcessRunner(cfg, color_fn=color_fn)

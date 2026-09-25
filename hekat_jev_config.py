"""Runtime configuration for the HEKAT ⇄ JEV integration.

Everything external is gated here behind environment variables so the system
runs fully offline today (local classifier + in-process tape) and goes live the
moment a key or address is added — no code change required.

Env vars (all optional):
  TYPESAFE_API_KEY      Presence flips node classification to the real
                        TypeSafe System One model (jev-1.13.0). Vercel/CI env
                        only — never commit it.
  TYPESAFE_ENDPOINT     Override the API URL (default: the pinned endpoint).
  TYPESAFE_MODEL        Override the model pin (default: jev-1.13.0).
  TEMPORAL_ADDRESS      Presence flips durable execution to a Temporal worker
                        tree (needs the `temporalio` SDK and the jev-tape repo).
  TEMPORAL_NAMESPACE    Temporal namespace (default: "default").
  TEMPORAL_TASK_QUEUE   Task queue for the jev worker tree (default: "hekat-jev").
  JEV_TAPE_PATH         Local path to a clone of manutej/jev-tape, if present.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

PINNED_MODEL = "jev-1.13.0"
DEFAULT_ENDPOINT = "https://api.typesafe.ai/v1/systemone"


@dataclass(frozen=True)
class JevConfig:
    typesafe_api_key: str | None
    typesafe_endpoint: str
    typesafe_model: str
    temporal_address: str | None
    temporal_namespace: str
    temporal_task_queue: str
    jev_tape_path: str | None

    @property
    def typesafe_live(self) -> bool:
        return bool(self.typesafe_api_key)

    @property
    def temporal_live(self) -> bool:
        return bool(self.temporal_address)

    def banner(self) -> str:
        """One-line status of what is live vs. running on the local fallback."""
        ts = "LIVE (TypeSafe API)" if self.typesafe_live else "local classifier (add TYPESAFE_API_KEY)"
        tp = "LIVE (Temporal)" if self.temporal_live else "in-process tape (add TEMPORAL_ADDRESS)"
        return f"classify={ts} · durable={tp} · model={self.typesafe_model}"


def load_config() -> JevConfig:
    return JevConfig(
        typesafe_api_key=os.environ.get("TYPESAFE_API_KEY") or None,
        typesafe_endpoint=os.environ.get("TYPESAFE_ENDPOINT", DEFAULT_ENDPOINT),
        typesafe_model=os.environ.get("TYPESAFE_MODEL", PINNED_MODEL),
        temporal_address=os.environ.get("TEMPORAL_ADDRESS") or None,
        temporal_namespace=os.environ.get("TEMPORAL_NAMESPACE", "default"),
        temporal_task_queue=os.environ.get("TEMPORAL_TASK_QUEUE", "hekat-jev"),
        jev_tape_path=os.environ.get("JEV_TAPE_PATH") or None,
    )


class NotConfigured(RuntimeError):
    """Raised when a live backend is requested but its env is not set."""

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

# Vercel project that holds the TypeSafe key (see docs/GO_LIVE.md).
VERCEL_TEAM_ID = "team_wfsWtUP7d1zIRArAwhlTUidB"
VERCEL_ENV_PROJECT = "volumetric-intelligence"


def _parse_dotenv(path: str) -> dict:
    """Tiny .env parser (no dependency). KEY=VALUE lines, # comments, quotes stripped."""
    out: dict = {}
    try:
        with open(path, "r") as fh:
            for raw in fh:
                line = raw.strip()
                if not line or line.startswith("#") or "=" not in line:
                    continue
                key, _, val = line.partition("=")
                key = key.strip()
                if key.startswith("export "):
                    key = key[len("export "):].strip()
                val = val.strip().strip('"').strip("'")
                if key:
                    out[key] = val
    except OSError:
        pass
    return out


def _find_dotenv() -> str | None:
    """Locate a .env from `vercel env pull`: cwd first, then this repo's dir."""
    here = os.path.dirname(os.path.abspath(__file__))
    for cand in (os.path.join(os.getcwd(), ".env"), os.path.join(here, ".env")):
        if os.path.isfile(cand):
            return cand
    return None


def _env(dotenv: dict, key: str, default: str | None = None) -> str | None:
    """Real environment wins; .env (from `vercel env pull`) fills the gaps."""
    return os.environ.get(key) or dotenv.get(key) or default


@dataclass(frozen=True)
class JevConfig:
    typesafe_api_key: str | None
    typesafe_endpoint: str
    typesafe_model: str
    temporal_address: str | None
    temporal_namespace: str
    temporal_task_queue: str
    jev_tape_path: str | None
    dotenv_source: str | None = None   # path of the .env consumed, if any

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
        src = f" · env={os.path.basename(self.dotenv_source)}" if self.dotenv_source else ""
        return f"classify={ts} · durable={tp} · model={self.typesafe_model}{src}"


def load_config() -> JevConfig:
    dotenv_path = _find_dotenv()
    dotenv = _parse_dotenv(dotenv_path) if dotenv_path else {}
    return JevConfig(
        typesafe_api_key=_env(dotenv, "TYPESAFE_API_KEY"),
        typesafe_endpoint=_env(dotenv, "TYPESAFE_ENDPOINT", DEFAULT_ENDPOINT),
        typesafe_model=_env(dotenv, "TYPESAFE_MODEL", PINNED_MODEL),
        temporal_address=_env(dotenv, "TEMPORAL_ADDRESS"),
        temporal_namespace=_env(dotenv, "TEMPORAL_NAMESPACE", "default"),
        temporal_task_queue=_env(dotenv, "TEMPORAL_TASK_QUEUE", "hekat-jev"),
        jev_tape_path=_env(dotenv, "JEV_TAPE_PATH"),
        dotenv_source=dotenv_path,
    )


class NotConfigured(RuntimeError):
    """Raised when a live backend is requested but its env is not set."""

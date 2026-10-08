"""Vercel serverless entry for the HEKAT × JEV monitor API.

Thin adapter: reuses the exact logic in hekat_serve so the hosted API and the
local server never drift. vercel.json routes /api/* here and serves
docs/monitor.html statically at /. Set OPENROUTER_API_KEY (and optionally
TYPESAFE_API_KEY) in the Vercel project env to go live.
"""
import json
import os
import sys
from http.server import BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("HEKAT_RUNS_FILE", "/tmp/hekat_runs.jsonl")  # writable on serverless

import hekat_serve as S  # noqa: E402


class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _path(self):
        return self.path.split("?", 1)[0]

    def do_GET(self):
        p = self._path()
        if p.endswith("/status"):
            return self._send(200, S.status_payload())
        if p.endswith("/adversarial"):
            return self._send(200, S.run_suite())
        if p.endswith("/runs"):
            return self._send(200, {"runs": S._load_runs()})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        p = self._path()
        n = int(self.headers.get("Content-Length", 0) or 0)
        body = json.loads(self.rfile.read(n).decode("utf-8")) if n else {}
        try:
            if p.endswith("/classify"):
                return self._send(200, S.classify_query(body.get("query", ""), body.get("forbid")))
            if p.endswith("/run"):
                return self._send(200, S.run_query(body.get("query", ""), body.get("task", ""),
                                                   body.get("forbid")))
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        except Exception as e:
            return self._send(500, {"error": str(e)})
        return self._send(404, {"error": "not found"})

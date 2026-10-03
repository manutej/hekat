#!/usr/bin/env python3
"""hekat_serve — a local testing & monitoring interface for HEKAT × JEV.

Serves the monitor UI and a small JSON API so people can see, test, and RUN
agents repeatably — and run the adversarial suite to confirm the gate works.
Stdlib only (http.server). "Just add an API key": set OPENROUTER_API_KEY and
the /api/run endpoint runs real agents through OpenRouter; otherwise it uses
deterministic mocks so the interface still works.

Run:  python3 hekat_serve.py   # then open http://localhost:8711
Env:  HEKAT_PORT (default 8711)

Endpoints:
  GET  /                 the monitor UI (docs/monitor.html)
  GET  /api/status       config banner + live flags
  POST /api/classify     {query, forbid[]}            → colors, γ edges, verdict
  POST /api/run          {query, task, forbid[]}      → run agents + gate outputs
  GET  /api/adversarial  run the adversarial suite     → pass/fail per case
  GET  /api/runs         recent runs (monitoring tape)
"""

from __future__ import annotations

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from hekat_lexer import Lexer
from hekat_parser import Parser
from hekat_type_checker import TypeChecker
from hekat_dag_builder import DAGBuilder
from hekat_jev import (
    classify_orchestration, _label, COLOR_META, COLORS,
    classify_local, score_fill, DEFAULT_ALLOWED, DEFAULT_THRESHOLDS, TRIAGE,
)
from hekat_jev_config import load_config
from hekat_jev_typesafe import make_color_fn
from hekat_openrouter import run_agent
from hekat_eval import run_suite

HERE = os.path.dirname(os.path.abspath(__file__))
MONITOR_HTML = os.path.join(HERE, "docs", "monitor.html")
RUNS: list = []            # in-memory monitoring log (most recent first)
MAX_RUNS = 50


def _parse(query: str):
    ast = Parser(Lexer(query).tokenize()).parse()
    validation = TypeChecker().validate(ast)
    if not validation["valid"]:
        raise ValueError("; ".join(validation["errors"]))
    dag = DAGBuilder().build(ast.expression)
    return ast, dag


def _forbid_set(forbid):
    return set(x for x in (forbid or []) if x)


def _serialize(clf, dag):
    phases = [[_label(dag.nodes[nid].expr) for nid in sorted(dag.parallel_phases[p])]
              for p in sorted(dag.parallel_phases.keys())]
    return {
        "nodes": [{"label": l, "color": c} for l, c in clf.node_colors],
        "counts": clf.color_counts,
        "phases": phases,
        "edges": [{"from": e.src_label, "to": e.dst_label, "from_color": e.src_color,
                   "to_color": e.dst_color, "ok": e.ok} for e in clf.edges],
        "verdict": clf.score.verdict,
        "allowed_mass": round(clf.score.allowed_mass, 3),
        "toxin_mass": round(clf.score.toxin_mass, 3),
        "triage": clf.triage,
        "reasons": clf.score.reasons,
    }


def classify_query(query: str, forbid=None) -> dict:
    ast, dag = _parse(query)
    clf = classify_orchestration(ast, dag, forbidden=_forbid_set(forbid))
    return _serialize(clf, dag)


def run_query(query: str, task: str, forbid=None) -> dict:
    cfg = load_config()
    ast, dag = _parse(query)
    clf = classify_orchestration(ast, dag, forbidden=_forbid_set(forbid))
    task = task or ast.prompt or "complete the task"
    forbidden = _forbid_set(forbid)
    color_fn = make_color_fn(cfg)   # live TypeSafe if keyed, else None → local
    # run each node's agent in execution order, then CLASSIFY ITS OUTPUT (eval)
    agents = []
    for nid in dag.execution_order:
        expr = dag.nodes[nid].expr
        name = _label(expr)
        agent_name = getattr(expr, "name", None) or getattr(expr, "agent", None) or name
        res = run_agent(agent_name, task, cfg)
        dist = color_fn({"output": res.output}) if color_fn else classify_local(res.output)
        out_score = score_fill(dist, DEFAULT_ALLOWED, forbidden, DEFAULT_THRESHOLDS)
        out_color = max(((c, dist[c]) for c in COLORS), key=lambda kv: kv[1])[0]
        agents.append({
            "agent": name, "live": res.live, "latency_ms": res.latency_ms,
            "output": res.output, "error": res.error,
            "output_color": out_color, "output_verdict": out_score.verdict,
            "output_triage": TRIAGE[out_score.verdict],
        })
    result = {
        "query": query, "task": task, "ts": int(time.time()),
        "live": cfg.openrouter_live, "model": cfg.openrouter_model,
        "orchestration": _serialize(clf, dag), "agents": agents,
    }
    RUNS.insert(0, {"ts": result["ts"], "query": query, "task": task,
                    "verdict": clf.score.verdict, "triage": clf.triage,
                    "live": cfg.openrouter_live, "agents": len(agents)})
    del RUNS[MAX_RUNS:]
    return result


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):  # quiet
        pass

    def _send(self, code, payload, ctype="application/json"):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self):
        n = int(self.headers.get("Content-Length", 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode("utf-8"))
        except Exception:
            return {}

    def do_GET(self):
        if self.path == "/" or self.path.startswith("/index"):
            try:
                with open(MONITOR_HTML, "rb") as f:
                    return self._send(200, f.read(), "text/html; charset=utf-8")
            except OSError:
                return self._send(500, {"error": "monitor.html not found"})
        if self.path == "/api/status":
            cfg = load_config()
            return self._send(200, {"banner": cfg.banner(),
                                    "openrouter_live": cfg.openrouter_live,
                                    "typesafe_live": cfg.typesafe_live,
                                    "model": cfg.openrouter_model,
                                    "colors": {k: v["short"] for k, v in COLOR_META.items()}})
        if self.path == "/api/adversarial":
            return self._send(200, run_suite())
        if self.path == "/api/runs":
            return self._send(200, {"runs": RUNS})
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        body = self._body()
        try:
            if self.path == "/api/classify":
                return self._send(200, classify_query(body.get("query", ""), body.get("forbid")))
            if self.path == "/api/run":
                return self._send(200, run_query(body.get("query", ""), body.get("task", ""),
                                                 body.get("forbid")))
        except ValueError as e:
            return self._send(400, {"error": str(e)})
        except Exception as e:  # pragma: no cover
            return self._send(500, {"error": str(e)})
        return self._send(404, {"error": "not found"})


def main():
    port = int(os.environ.get("HEKAT_PORT", "8711"))
    srv = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"HEKAT × JEV monitor on http://localhost:{port}")
    print("  " + load_config().banner())
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.shutdown()


if __name__ == "__main__":
    main()

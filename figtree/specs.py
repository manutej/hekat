"""Spec docs: figure-ready documents written from documentation (``examples/figtree/langflow/SPEC-FORMAT.md``).

``python -m figtree spec check SPEC.md --corpus DIR`` measures a spec mechanically so that a small
model can write one and fix it without judgement calls: component and flow counts, evidence quotes
found verbatim in the corpus, unknown icons or kinds, contradictory flow pairs, and what the
rule-based grounder recovers from the document.  ``python -m figtree spec list DIR`` summarises a
directory of specs.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from figtree.elements import KINDS
from figtree.grounder import RuleBasedGrounder, slug
from figtree.icons import ICONS

_COMPONENT = re.compile(r"^\s*[-*]\s+\*\*([^*\n]{1,60})\*\*\s*(?:\(([^)]*)\))?\s*:?\s*(.*)$")
_ARROW = re.compile(r"\s*(?:→|->|⟶|=>)\s*")
_FLOW_TYPE = re.compile(r"^\s*\((data|control|conditional|feedback|parallel)\)", re.IGNORECASE)
_EVIDENCE = re.compile(r'^\s*(.+?)\s*:\s*"(.+?)"\s*(?:\(([^)]+)\))?\s*$')
_STEP = re.compile(r"^\s*(\d+)[.)]\s+(.+)$")
_FENCE = re.compile(r"^```(\w*)\s*$")


_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
_MD_MARK = re.compile(r"[*_`]+")


def _norm(s: str) -> str:
    """Normalise rendered-vs-source differences so a quote of the rendered page matches the markdown:
    links keep their text, bold/italic/code markers vanish, quotes and whitespace are unified."""
    s = _MD_LINK.sub(r"\1", s)
    s = _MD_MARK.sub("", s)
    s = s.replace("’", "'").replace("“", '"').replace("”", '"')
    return re.sub(r"\s+", " ", s).strip().lower()


def _sections(text: str) -> Dict[str, List[str]]:
    """Lines per ``## Heading`` (lower-cased key); fenced blocks are returned under their tag."""
    out: Dict[str, List[str]] = {"_top": []}
    key = "_top"
    fence: Optional[str] = None
    for line in text.splitlines():
        m = _FENCE.match(line)
        if m:
            if fence is None:
                fence = "fence:" + (m.group(1) or "code")
                out.setdefault(fence, [])
            else:
                fence = None
            continue
        if fence:
            out[fence].append(line)
            continue
        if line.startswith("## "):
            key = line[3:].strip().lower()
            out.setdefault(key, [])
            continue
        out.setdefault(key, []).append(line)
    return out


def parse_spec(text: str) -> Dict[str, Any]:
    sec = _sections(text)
    title = next((l[2:].strip() for l in text.splitlines() if l.startswith("# ")), "")
    components: List[Dict[str, str]] = []
    for line in sec.get("components", []):
        m = _COMPONENT.match(line)
        if not m:
            continue
        attrs = dict(re.findall(r"(kind|icon)\s*:\s*([a-z][a-z0-9-]*)", m.group(2) or ""))
        components.append({"name": m.group(1).strip(), "kind": attrs.get("kind", ""), "icon": attrs.get("icon", ""), "role": m.group(3).strip()})
    flows: List[Dict[str, str]] = []
    for line in sec.get("flows", []):
        if not _ARROW.search(line):
            continue
        chain_part, _, rest = line.partition(":")
        # the chain ends before an optional "(type)"
        mt = re.search(r"\((data|control|conditional|feedback|parallel)\)", chain_part, re.IGNORECASE)
        ftype = mt.group(1).lower() if mt else "data"
        chain = chain_part[: mt.start()] if mt else chain_part
        names = [n.strip() for n in _ARROW.split(chain) if n.strip()]
        for a, b in zip(names, names[1:]):
            flows.append({"from": a, "to": b, "type": ftype})
    steps = [m.group(2).strip() for l in sec.get("steps", []) if (m := _STEP.match(l))]
    evidence: List[Dict[str, str]] = []
    for line in sec.get("fence:evidence", []):
        m = _EVIDENCE.match(line)
        if m:
            evidence.append({"subject": m.group(1).strip(), "quote": m.group(2).strip(), "source": (m.group(3) or "").strip()})
    gaps = [l.strip() for l in sec.get("not in the documentation", []) if l.strip()]
    return {"title": title, "components": components, "flows": flows, "steps": steps, "evidence": evidence, "gaps": gaps}


def _corpus_index(corpus: Optional[str]) -> Dict[str, str]:
    if not corpus or not os.path.isdir(corpus):
        return {}
    idx: Dict[str, str] = {}
    for root, _, files in os.walk(corpus):
        for f in files:
            if f.endswith((".md", ".mdx", ".txt", ".rst")):
                with open(os.path.join(root, f), encoding="utf-8", errors="replace") as fh:
                    idx[f] = _norm(fh.read())
    return idx


def check_spec(text: str, corpus: Optional[str] = None) -> Dict[str, Any]:
    spec = parse_spec(text)
    names = [c["name"] for c in spec["components"]]
    keys = {slug(n) for n in names}
    idx = _corpus_index(corpus)
    missing: List[str] = []
    found_subjects: set = set()
    for e in spec["evidence"]:
        q = _norm(e["quote"])
        hay = [idx[e["source"]]] if e["source"] in idx else list(idx.values())
        if idx and not any(q in h for h in hay):
            missing.append(f'{e["subject"]}: "{e["quote"][:60]}" ({e["source"] or "no source"})')
        else:
            found_subjects.add(slug(e["subject"]))
    without = [n for n in names if slug(n) not in found_subjects]
    unknown_icons = [c["icon"] for c in spec["components"] if c["icon"] and c["icon"] not in ICONS]
    unknown_kinds = [c["kind"] for c in spec["components"] if c["kind"] and c["kind"] not in KINDS]
    unknown_flow_names = sorted({f[k] for f in spec["flows"] for k in ("from", "to") if slug(f[k]) not in keys})
    pairs = {(slug(f["from"]), slug(f["to"])) for f in spec["flows"]}
    contradictions = sorted({f"{a} <-> {b}" for (a, b) in pairs if (b, a) in pairs and a < b})
    typed_without = [f'{f["from"]} -> {f["to"]}' for f in spec["flows"] if f["type"] in ("control", "feedback") and not any(slug(e["subject"]).replace("-", "") == slug(f["from"] + " " + f["to"]).replace("-", "") or _norm(e["subject"]).replace("->", "→") == _norm(f["from"] + " → " + f["to"]) for e in spec["evidence"] if slug(e["subject"]) in found_subjects or True)]
    prose_arrows = sum(1 for k, lines in _sections(text).items() if k not in ("flows",) and not k.startswith("fence:") for l in lines if _ARROW.search(l))
    g = RuleBasedGrounder().ground(text).content_plan
    grounded = {slug(c.name) for c in g.components}
    gflows = {(slug(f.src), slug(f.dst)) for f in g.flows}
    not_grounded = [n for n in names if slug(n) not in grounded]
    flows_not_grounded = [f'{f["from"]} -> {f["to"]}' for f in spec["flows"] if (slug(f["from"]), slug(f["to"])) not in gflows]
    by_type: Dict[str, int] = {}
    for f in spec["flows"]:
        by_type[f["type"]] = by_type.get(f["type"], 0) + 1
    ok = (
        3 <= len(names) <= 9 and not missing and not without and not unknown_icons and not unknown_kinds
        and not unknown_flow_names and not contradictions and not not_grounded and not flows_not_grounded
        and len(spec["flows"]) >= 2 and prose_arrows == 0
    )
    return {
        "title": spec["title"], "components": len(names), "flows": len(spec["flows"]), "flows_by_type": by_type,
        "steps": len(spec["steps"]), "evidence_lines": len(spec["evidence"]), "evidence_missing": missing,
        "components_without_evidence": without, "typed_flows_without_evidence": typed_without,
        "unknown_icons": unknown_icons, "unknown_kinds": unknown_kinds, "unknown_flow_names": unknown_flow_names,
        "contradictions": contradictions, "prose_arrows": prose_arrows,
        "grounded_components": len(grounded), "grounded_flows": len(gflows),
        "not_grounded": not_grounded, "flows_not_grounded": flows_not_grounded, "gaps": len(spec["gaps"]), "ok": ok,
    }


def main(argv: Sequence[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="figtree spec", description="check or list figure-ready spec documents")
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="measure one spec: counts, evidence found in the corpus, grounder recovery")
    c.add_argument("spec")
    c.add_argument("--corpus", default=None, help="directory of the documentation pages the evidence quotes")
    c.add_argument("--json", action="store_true", help="(default) print JSON")
    l = sub.add_parser("list", help="one line per spec in a directory")
    l.add_argument("dir")
    l.add_argument("--corpus", default=None)
    a = ap.parse_args(list(argv))
    if a.cmd == "check":
        with open(a.spec, encoding="utf-8") as fh:
            r = check_spec(fh.read(), a.corpus)
        print(json.dumps(r, indent=2))
        return 0 if r["ok"] else 1
    rows = []
    for f in sorted(os.listdir(a.dir)):
        if f.endswith(".md") and f[0] != "_" and f.upper() != f:
            with open(os.path.join(a.dir, f), encoding="utf-8") as fh:
                r = check_spec(fh.read(), a.corpus)
            rows.append({"file": f, "title": r["title"], "components": r["components"], "flows": r["flows"], "ok": r["ok"],
                         "problems": len(r["evidence_missing"]) + len(r["components_without_evidence"]) + len(r["contradictions"]) + len(r["not_grounded"]) + len(r["flows_not_grounded"])})
    print(json.dumps(rows, indent=2))
    return 0 if all(r["ok"] for r in rows) else 1

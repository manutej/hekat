"""Batch mode: fan a whole body of work (a directory of markdown docs, papers, skills, specs)
out into figure *units*.

    python -m figtree digest --plan DIR_OR_FILES... -o OUT       -> OUT/manifest.json
    python -m figtree digest --unit ID -o OUT [--rubric R]       -> OUT/ID.svg, ID.report.json, ID.score.json
    python -m figtree digest --all -o OUT [--rubric R]           -> every unit, then OUT/index.html

A unit is an H1/H2 section whose text grounds to at least ``MIN_COMPONENTS`` components (arrow
chains, named roles, numbered steps as detected by ``RuleBasedGrounder``), or a whole file when
the file is small.  Sections that ground to fewer components are recorded under ``skipped`` with
the reason, never silently dropped.  The plan is deterministic, so the workflow scripts under
``.claude/workflows`` can fan out over the manifest one unit per agent.
"""

from __future__ import annotations

import html
import json
import os
import re
from dataclasses import asdict, dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from figtree.grounder import RuleBasedGrounder, slug

TEXT_SUFFIXES = (".md", ".markdown", ".txt", ".rst")
MIN_COMPONENTS = 3
SMALL_FILE_CHARS = 2500
_HEADING = re.compile(r"^(#{1,2})\s+(.*\S)\s*$")
_STYLE_FOR_RUBRIC = {"teaching": "teaching", "slide": "slide"}  # everything else -> paper


@dataclass
class Unit:
    id: str
    source: str
    title: str
    span: List[int]  # [start_line, end_line], 1-based inclusive
    chars: int
    est_components: int
    est_flows: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Manifest:
    out_dir: str
    rubric: str
    style: str
    units: List[Unit] = field(default_factory=list)
    skipped: List[Dict[str, Any]] = field(default_factory=list)
    inputs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {"out_dir": self.out_dir, "rubric": self.rubric, "style": self.style, "inputs": list(self.inputs),
                "units": [u.to_dict() for u in self.units], "skipped": list(self.skipped)}

    @property
    def path(self) -> str:
        return os.path.join(self.out_dir, "manifest.json")

    def write(self) -> str:
        os.makedirs(self.out_dir, exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as fh:
            json.dump(self.to_dict(), fh, indent=2)
        return self.path

    @classmethod
    def load(cls, out_dir: str) -> "Manifest":
        with open(os.path.join(out_dir, "manifest.json"), encoding="utf-8") as fh:
            d = json.load(fh)
        m = cls(d.get("out_dir", out_dir), d.get("rubric", "teaching"), d.get("style", "paper"), inputs=d.get("inputs", []), skipped=d.get("skipped", []))
        m.units = [Unit(**u) for u in d.get("units", [])]
        return m

    def unit(self, unit_id: str) -> Unit:
        for u in self.units:
            if u.id == unit_id:
                return u
        raise KeyError(f"unknown unit {unit_id!r}; manifest has {[u.id for u in self.units]}")


def style_for(rubric: str, style: Optional[str] = None) -> str:
    return style or _STYLE_FOR_RUBRIC.get(rubric, "paper")


# ----------------------------------------------------------------------------------------
# plan
# ----------------------------------------------------------------------------------------
def collect_inputs(inputs: Sequence[str]) -> List[str]:
    """Files given directly plus every text file under a directory (recursive, sorted)."""
    out: List[str] = []
    for p in inputs:
        if os.path.isdir(p):
            for root, dirs, files in os.walk(p):
                dirs[:] = sorted(d for d in dirs if not d.startswith("."))
                for f in sorted(files):
                    if f.lower().endswith(TEXT_SUFFIXES):
                        out.append(os.path.join(root, f))
        elif os.path.isfile(p):
            out.append(p)
    seen: set = set()
    return [p for p in out if not (p in seen or seen.add(p))]


def split_sections(lines: Sequence[str]) -> List[Tuple[str, int, int]]:
    """H1/H2 sections as ``(title, start_line, end_line)`` (1-based inclusive).  Text before the
    first heading becomes a section titled by the first non-empty line."""
    heads = [(i, m.group(2)) for i, line in enumerate(lines) if (m := _HEADING.match(line))]
    out: List[Tuple[str, int, int]] = []
    if not heads or heads[0][0] > 0:
        end = (heads[0][0] if heads else len(lines)) - 1
        pre = [l for l in lines[: end + 1] if l.strip()]
        if pre:
            out.append((pre[0].lstrip("# ").strip()[:80], 1, end + 1))
    for n, (i, title) in enumerate(heads):
        end = heads[n + 1][0] - 1 if n + 1 < len(heads) else len(lines) - 1
        out.append((title, i + 1, end + 1))
    return out


def _estimate(text: str, grounder: RuleBasedGrounder) -> Tuple[int, int]:
    try:
        plan = grounder.ground(text).content_plan
    except Exception:  # noqa: BLE001 - a section that cannot be grounded is simply not a unit
        return 0, 0
    return len(plan.components), len(plan.flows)


def plan(inputs: Sequence[str], out_dir: str, rubric: str = "teaching", style: Optional[str] = None,
         min_components: int = MIN_COMPONENTS, small_file_chars: int = SMALL_FILE_CHARS) -> Manifest:
    grounder = RuleBasedGrounder()
    m = Manifest(os.path.abspath(out_dir), rubric, style_for(rubric, style), inputs=[os.path.abspath(p) for p in inputs])
    used: set = set()

    def unique(base: str) -> str:
        cand, n = base, 2
        while cand in used:
            cand, n = f"{base}-{n}", n + 1
        used.add(cand)
        return cand

    for path in collect_inputs(inputs):
        with open(path, encoding="utf-8", errors="replace") as fh:
            text = fh.read()
        lines = text.splitlines()
        stem = slug(os.path.splitext(os.path.basename(path))[0]) or "doc"
        sections = split_sections(lines)
        has_h2 = any(_HEADING.match(l) and _HEADING.match(l).group(1) == "##" for l in lines)
        whole = len(text) <= small_file_chars or not has_h2
        candidates: List[Tuple[str, int, int, str]]  # title, start, end, id-base
        if whole:
            title = sections[0][0] if sections else stem
            candidates = [(title, 1, max(len(lines), 1), stem)]
        else:
            candidates = [(t, a, b, f"{stem}--{slug(t) or 'section'}") for t, a, b in sections]
        for title, a, b, base in candidates:
            body = "\n".join(lines[a - 1:b])
            comps, flows = _estimate(body, grounder)
            rel = os.path.relpath(path)
            if comps < min_components:
                m.skipped.append({"source": rel, "title": title, "span": [a, b], "chars": len(body), "est_components": comps,
                                  "reason": f"only {comps} grounded component(s), need {min_components}"})
                continue
            m.units.append(Unit(unique(base), rel, title, [a, b], len(body), comps, flows))
    m.write()
    return m


# ----------------------------------------------------------------------------------------
# unit
# ----------------------------------------------------------------------------------------
def unit_text(m: Manifest, u: Unit) -> str:
    path = u.source if os.path.isabs(u.source) else os.path.join(os.getcwd(), u.source)
    with open(path, encoding="utf-8", errors="replace") as fh:
        lines = fh.read().splitlines()
    return "\n".join(lines[u.span[0] - 1:u.span[1]])


def _figtree(style: str, render: bool, max_aspect: float = 3.0):
    from figtree.generator import RuleBasedGenerator
    from figtree.orchestrator import FigTree, Limits
    from figtree.worker import Worker

    limits = Limits()
    ft = FigTree(limits=limits, render=render,
                 generator=RuleBasedGenerator(max_depth=limits.max_depth),
                 worker=Worker(spacing_iterations=limits.spacing_iterations, max_aspect=max_aspect))
    if style != "paper":
        from figtree.styles import get_preset

        ft.style_override = get_preset(style).style
    return ft


def generate_unit(m: Manifest, unit_id: str, rubric: Optional[str] = None, style: Optional[str] = None, render: bool = True) -> Dict[str, Any]:
    """Generate one unit's figure, score it and write ``<id>.svg``, ``<id>.report.json``, ``<id>.score.json``."""
    from figtree.quality import QualityCritic

    u = m.unit(unit_id)
    rubric = rubric or m.rubric
    style = style or (m.style if rubric == m.rubric else style_for(rubric))
    text = unit_text(m, u)
    os.makedirs(m.out_dir, exist_ok=True)
    svg_path = os.path.join(m.out_dir, f"{u.id}.svg")
    report_path = os.path.join(m.out_dir, f"{u.id}.report.json")
    score_path = os.path.join(m.out_dir, f"{u.id}.score.json")
    result = _figtree(style, render).run(text)
    with open(svg_path, "w", encoding="utf-8") as fh:
        fh.write(result.final_svg)
    rep = result.to_dict()
    rep["unit"] = u.to_dict()
    with open(report_path, "w", encoding="utf-8") as fh:
        json.dump(rep, fh, indent=2)
    report = QualityCritic(rubric).review(result.final_svg, text)
    score = report.to_dict()
    score.update({"unit": u.id, "title": u.title, "source": u.source, "svg": svg_path, "report": report_path, "style": style,
                  "components": len(result.content_plan.components), "flows": len(result.content_plan.flows),
                  "faithfulness_failures": list(result.faithfulness_failures)})
    with open(score_path, "w", encoding="utf-8") as fh:
        json.dump(score, fh, indent=2)
    return score


# ----------------------------------------------------------------------------------------
# all + gallery
# ----------------------------------------------------------------------------------------
def _score_summary(score: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": score["unit"], "title": score["title"], "source": score["source"], "svg": score["svg"], "overall": score["overall"],
            "issues": len(score.get("issues", [])), "critical": sum(1 for i in score.get("issues", []) if i.get("severity") == "critical"),
            "status": "ok" if score["overall"] >= 8 else "needs-refine"}


def gallery(m: Manifest, rows: Iterable[Dict[str, Any]]) -> str:
    """Write ``<out_dir>/index.html``: title, score and the inline SVG per unit."""
    rows = list(rows)
    cards = []
    for r in rows:
        try:
            with open(r["svg"], encoding="utf-8") as fh:
                svg = fh.read()
        except OSError:
            svg = "<p>(no figure)</p>"
        cards.append(
            f'<section class="card" id="{html.escape(r["id"])}"><h2>{html.escape(r["title"])}</h2>'
            f'<p class="meta"><span class="score {"ok" if r["overall"] >= 8 else "low"}">{r["overall"]:.2f}</span> '
            f'{html.escape(r["source"])} · {r["issues"]} issue(s), {r["critical"]} critical</p><div class="fig">{svg}</div></section>'
        )
    skipped = "".join(f'<li>{html.escape(s["source"])} — {html.escape(s["title"])}: {html.escape(s["reason"])}</li>' for s in m.skipped)
    page = (
        "<!doctype html><html><head><meta charset='utf-8'><title>figtree digest</title><style>"
        "body{font-family:Georgia,'Times New Roman',serif;max-width:1100px;margin:32px auto;padding:0 16px;color:#333;background:#fff}"
        "h1{font-size:22px}h2{font-size:17px;margin:0 0 4px}.card{border:1px solid #D5D5D5;border-radius:4px;padding:16px;margin:16px 0}"
        ".meta{font-size:13px;color:#666;margin:0 0 8px}.score{display:inline-block;min-width:44px;text-align:center;font-weight:bold;"
        "border-radius:4px;padding:1px 6px;color:#fff}.score.ok{background:#4F7F3A}.score.low{background:#B5651D}"
        ".fig svg{max-width:100%;height:auto;display:block}.skipped{font-size:13px;color:#666}</style></head><body>"
        f"<h1>figtree digest — {html.escape(m.rubric)} rubric, {len(rows)} unit(s)</h1>"
        + "".join(cards)
        + (f"<h2>Skipped</h2><ul class='skipped'>{skipped}</ul>" if skipped else "")
        + "</body></html>"
    )
    path = os.path.join(m.out_dir, "index.html")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(page)
    return path


def run_all(m: Manifest, rubric: Optional[str] = None, style: Optional[str] = None, render: bool = True, log=print) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    failed: List[Dict[str, str]] = []
    for u in m.units:
        try:
            score = generate_unit(m, u.id, rubric, style, render)
        except Exception as exc:  # noqa: BLE001 - one bad unit must not stop the batch
            failed.append({"id": u.id, "error": f"{type(exc).__name__}: {exc}"[:200]})
            log(f"  {u.id:40s} FAILED {type(exc).__name__}: {str(exc)[:80]}")
            continue
        row = _score_summary(score)
        rows.append(row)
        log(f"  {u.id:40s} {row['overall']:5.2f}  {row['issues']:2d} issue(s)  {row['status']}")
    index = gallery(m, rows)
    summary = {"manifest": m.path, "index": index, "units": rows, "failed": failed, "skipped": m.skipped}
    with open(os.path.join(m.out_dir, "digest.json"), "w", encoding="utf-8") as fh:
        json.dump(summary, fh, indent=2)
    return summary


# ----------------------------------------------------------------------------------------
# CLI
# ----------------------------------------------------------------------------------------
def main(argv: List[str]) -> int:
    import argparse

    from figtree.rubrics import RUBRICS

    ap = argparse.ArgumentParser(prog="figtree digest", description="Fan a body of documents out into figure units: --plan, then --unit ID or --all")
    ap.add_argument("inputs", nargs="*", help="files or directories (markdown / text), used by --plan")
    ap.add_argument("-o", "--out-dir", required=True)
    ap.add_argument("--plan", action="store_true", help="scan the inputs and write manifest.json")
    ap.add_argument("--unit", help="generate + score one unit from the manifest")
    ap.add_argument("--all", action="store_true", help="generate + score every unit and write index.html")
    ap.add_argument("--rubric", choices=sorted(RUBRICS), default=None, help="scoring rubric (default: the manifest's, or teaching)")
    ap.add_argument("--style", choices=["paper", "teaching", "slide"], default=None, help="design preset (default: teaching/slide follow the rubric, others paper)")
    ap.add_argument("--min-components", type=int, default=MIN_COMPONENTS)
    ap.add_argument("--no-render", action="store_true", help="skip raster rendering during construction (faster)")
    a = ap.parse_args(argv)
    if a.plan:
        if not a.inputs:
            ap.error("--plan needs at least one input file or directory")
        m = plan(a.inputs, a.out_dir, a.rubric or "teaching", a.style, a.min_components)
        print(f"wrote {m.path}: {len(m.units)} unit(s), {len(m.skipped)} skipped")
        for u in m.units:
            print(f"  {u.id:40s} {u.source}:{u.span[0]}-{u.span[1]}  {u.est_components} comp / {u.est_flows} flows  {u.chars} chars")
        for s in m.skipped:
            print(f"  skipped {s['source']}:{s['span'][0]}-{s['span'][1]} {s['title']!r}: {s['reason']}")
        if not (a.unit or a.all):
            return 0
    m = Manifest.load(a.out_dir)
    if a.unit:
        score = generate_unit(m, a.unit, a.rubric, a.style, not a.no_render)
        row = _score_summary(score)
        print(json.dumps(row))
        return 0
    if a.all:
        summary = run_all(m, a.rubric, a.style, not a.no_render)
        print(f"wrote {summary['index']}: {len(summary['units'])} unit(s), {len(summary['failed'])} failed, {len(summary['skipped'])} skipped")
        return 0 if not summary["failed"] else 1
    ap.error("one of --plan, --unit ID or --all is required")
    return 2

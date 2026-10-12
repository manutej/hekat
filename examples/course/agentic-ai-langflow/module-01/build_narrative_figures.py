#!/usr/bin/env python3
"""Build module-01/narrative SVGs: Pursuit baseline + course-narrative generate/refine pilots."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MODULE = Path(__file__).resolve().parent
NARRATIVE = MODULE / "narrative"
DIAGRAMS = ROOT / "docs/course/agentic-ai-langflow/module-01/diagrams"
NARRATIVE_BRIEFS = DIAGRAMS / "narrative"
SCRIPTS = ROOT / "examples/course/agentic-ai-langflow/scripts"
sys.path.insert(0, str(SCRIPTS))

sys.path.insert(0, str(ROOT / "examples/figtree/langflow/adversarial"))
from compact_trim import components_in_svg, trim_teaching_canvas  # noqa: E402
from figure_richness import metrics_from_path, pursuit_gate  # noqa: E402
from figure_tiers import resolve  # noqa: E402
from pursuit_requests import requests_from_gate  # noqa: E402

PILOTS = ("m1b", "m1-capstone")
MANIFEST = json.loads((MODULE / "manifest.json").read_text(encoding="utf-8"))


def expected_components(md: Path) -> set[str]:
    found: set[str] = set()
    for line in md.read_text(encoding="utf-8").splitlines():
        if "->" not in line:
            continue
        for part in re.split(r"\s*->\s*", line.strip()):
            name = part.strip()
            if name:
                found.add(name)
    return found


def run(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)


def score(svg: Path, source: Path, rubric: str = "course-narrative", reference: Path | None = None) -> dict:
    cmd = [
        sys.executable,
        "-m",
        "figtree",
        "score",
        str(svg),
        "--rubric",
        rubric,
        "--source",
        str(source),
        "--json",
    ]
    if reference:
        cmd.extend(["--reference", str(reference)])
    cp = run(cmd)
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    return json.loads(cp.stdout)


def generate(brief: Path, out: Path) -> None:
    cp = run(
        [
            sys.executable,
            "-m",
            "figtree",
            "generate",
            str(brief),
            "-o",
            str(out),
            "--style",
            "course-narrative",
            "--icons",
            "--shapes",
            "--max-aspect",
            "6",
            "--no-render",
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)


def refine_auto(svg: Path, source: Path, out: Path, rounds: int = 4) -> dict:
    cp = run(
        [
            sys.executable,
            "-m",
            "figtree",
            "refine",
            str(svg),
            "--rubric",
            "course-narrative",
            "-o",
            str(out),
            "--source",
            str(source),
            "--rounds",
            str(rounds),
            "--no-auto",
            "--no-render",
        ]
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr or cp.stdout)
    return score(out, source)


def _beats_pursuit(pursuit: Path, candidate: Path) -> bool:
    """True only if candidate matches Pursuit richness closely enough to ship."""
    gate = pursuit_gate(pursuit, candidate, same_file_is_pass=False)
    if not gate.ok:
        return False
    ref = metrics_from_path(pursuit)
    cand = metrics_from_path(candidate)
    if ref.viewbox_height and cand.viewbox_height < int(ref.viewbox_height * 0.85):
        return False
    if ref.annot_nodes > 0 and cand.annot_nodes < int(ref.annot_nodes * 0.85):
        return False
    return True


def pick_best(
    cid: str,
    pursuit: Path,
    candidates: list[tuple[str, Path, dict]],
    source: Path,
) -> tuple[Path, dict]:
    """Keep Pursuit unless a candidate clearly matches its richness and scores higher."""
    ref_m = metrics_from_path(pursuit)
    best_path = pursuit
    best_row: dict = {
        "winner": "pursuit",
        "pursuit_gate_ok": True,
        "overall": score(pursuit, source)["overall"],
    }

    for label, path, meta in candidates:
        if not path.exists():
            continue
        if not _beats_pursuit(pursuit, path):
            continue
        try:
            sc = score(path, source, reference=pursuit)
        except RuntimeError:
            continue
        if sc["overall"] >= best_row.get("overall", 0):
            gate = pursuit_gate(pursuit, path, same_file_is_pass=False)
            best_path = path
            best_row = {
                "winner": label,
                "pursuit_gate_ok": gate.ok,
                "overall": sc["overall"],
                "gate_reasons": gate.reasons,
                **meta,
            }
    best_row["reference_metrics"] = ref_m.to_dict()
    return best_path, best_row


def process_figure(cid: str, *, pilot: bool) -> dict:
    pursuit = resolve(cid, "pursuit")
    base_brief = DIAGRAMS / f"{cid}.md"
    rich_brief = NARRATIVE_BRIEFS / f"{cid}.md"
    source = rich_brief if rich_brief.exists() else base_brief
    if pursuit is None or not source.exists():
        return {"id": cid, "skipped": True}

    out_final = NARRATIVE / f"{cid}.svg"
    NARRATIVE.mkdir(parents=True, exist_ok=True)
    log: dict = {"id": cid, "pilot": pilot, "source_brief": str(source.relative_to(ROOT))}

    # Baseline: Pursuit reference always available in narrative/
    shutil.copy2(pursuit, NARRATIVE / f"{cid}.pursuit.svg")
    candidates: list[tuple[str, Path, dict]] = []

    if pilot:
        gen_out = NARRATIVE / f"{cid}.generated.svg"
        try:
            generate(source, gen_out)
            exp = expected_components(base_brief)
            text = gen_out.read_text(encoding="utf-8")
            trimmed = trim_teaching_canvas(text, rubric="course-narrative")
            if not exp or exp.issubset(components_in_svg(trimmed)):
                gen_out.write_text(trimmed, encoding="utf-8")
            candidates.append(("generated", gen_out, {"stage": "generate"}))
        except RuntimeError as exc:
            log["generate_error"] = str(exc)[:300]

        lab = resolve(cid, "production")
        if lab and lab.exists():
            gate = pursuit_gate(pursuit, lab, same_file_is_pass=False)
            title = next((f["title"] for f in MANIFEST["figures"] if f["id"] == cid), cid)
            reqs = requests_from_gate(gate, fig_title=title)
            refined = NARRATIVE / f"{cid}.refined.svg"
            seed = candidates[0][1] if candidates else lab
            if seed.exists():
                try:
                    # Mechanical refine only (no Claude --request in CI)
                    refine_auto(seed, source, refined, rounds=3)
                    candidates.append(("refined", refined, {"requests": reqs}))
                except RuntimeError as exc:
                    log["refine_error"] = str(exc)[:300]

    winner, pick = pick_best(cid, pursuit, candidates, source)
    if winner != pursuit:
        shutil.copy2(winner, out_final)
    else:
        shutil.copy2(pursuit, out_final)
    log.update(pick)
    log["output"] = str(out_final.relative_to(ROOT))
    return log


def main() -> int:
    pilots_only = "--all" not in sys.argv
    ids = [f["id"] for f in MANIFEST["figures"]]
    report: list[dict] = []
    for cid in ids:
        row = process_figure(cid, pilot=(cid in PILOTS) if pilots_only else True)
        report.append(row)
        if row.get("skipped"):
            print(f"  skip {cid}")
        else:
            print(
                f"  {cid:14s} winner={row.get('winner', '?'):10s} "
                f"gate={row.get('pursuit_gate_ok')} score={row.get('overall', 0):.2f}"
            )

    (NARRATIVE / "build-log.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {NARRATIVE / 'build-log.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

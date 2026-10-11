"""Build the FigTree showcase page: every result inlined as editable SVG, with trajectories.

    python examples/figtree/showcase/build_showcase.py OUT.html

Sections appear only when their assets exist, so the page can be rebuilt as workers deliver.
"""

from __future__ import annotations

import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
EX = os.path.join(ROOT, "examples", "figtree")


def read(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def exists(*parts: str) -> bool:
    return os.path.exists(os.path.join(EX, *parts))


def namespace(svg: str, prefix: str, css: str = "") -> tuple[str, str]:
    """Prefix every id, href and url() reference so several figures can share one page."""
    svg = re.sub(r'\bid="([^"]+)"', lambda m: f'id="{prefix}{m.group(1)}"', svg)
    svg = re.sub(r'href="#([^"]+)"', lambda m: f'href="#{prefix}{m.group(1)}"', svg)
    svg = re.sub(r'url\(#([^)]+)\)', lambda m: f"url(#{prefix}{m.group(1)})", svg)
    svg = re.sub(r'data-from="([^"]+)"', lambda m: f'data-from="{prefix}{m.group(1)}"', svg)
    svg = re.sub(r'data-to="([^"]+)"', lambda m: f'data-to="{prefix}{m.group(1)}"', svg)
    svg = re.sub(r"<title>.*?</title>", "", svg, count=1, flags=re.S)
    svg = re.sub(r"<style>.*?</style>", "", svg, flags=re.S)
    if css:
        css = re.sub(r"#((?:[A-Za-z0-9_-]|\\.)+)", lambda m: f"#{prefix}{m.group(1)}", css)
    return svg, css


def inline(path: str, prefix: str, label: str, caption: str, css: str = "") -> str:
    svg = read(path)
    svg, css = namespace(svg, prefix, css)
    svg = re.sub(r"<svg ", f'<svg role="img" aria-label="{html.escape(label)}" ', svg, count=1)
    svg = re.sub(r'\s(?:width|height)="[^"]*"', "", svg, count=2)
    style = f"<style>{css}</style>" if css else ""
    return f'<figure class="fig">{style}<div class="sheet">{svg}</div><figcaption>{caption}</figcaption></figure>'


def sparkline(traj: list[dict], prefix: str) -> str:
    xs = [r["round"] for r in traj]
    ys = [r["overall"] for r in traj]
    w, h, pad = 160, 56, 8
    n = max(len(xs) - 1, 1)
    lo, hi = 6.0, 10.0
    px = lambda i: pad + (w - 2 * pad) * i / n
    py = lambda v: h - pad - (h - 2 * pad) * (max(lo, min(hi, v)) - lo) / (hi - lo)
    pts = " ".join(f"{px(i):.1f},{py(v):.1f}" for i, v in enumerate(ys))
    dots = "".join(
        f'<circle cx="{px(i):.1f}" cy="{py(v):.1f}" r="{4 if i == len(ys) - 1 else 2.5}" class="{"end" if i == len(ys) - 1 else "pt"}"><title>round {i}: {v}</title></circle>'
        for i, v in enumerate(ys)
    )
    return (
        f'<svg class="spark" viewBox="0 0 {w} {h}" role="img" aria-label="score per round: {", ".join(str(v) for v in ys)}">'
        f'<line x1="{pad}" y1="{py(10):.1f}" x2="{w - pad}" y2="{py(10):.1f}" class="grid"/>'
        f'<polyline points="{pts}" class="line"/>{dots}'
        f'<text x="{px(len(ys) - 1):.1f}" y="{py(ys[-1]) - 8:.1f}" class="val" text-anchor="middle">{ys[-1]:.2f}</text></svg>'
    )


def refinement_card(name: str, title: str, rubric: str, before_svg: str, after_svg: str, traj_path: str, prefix: str, decided: str) -> str:
    d = json.load(open(traj_path, encoding="utf-8"))
    t = d["trajectory"]
    reqs = d.get("requests_remaining", [])
    rows = "".join(f'<tr><td>{r["round"]}</td><td>{r["overall"]:.2f}</td><td>{r["issues"]}</td><td>{r["critical"]}</td><td>{r["edits_applied"]}</td><td>{r["diff_elements"]}</td></tr>' for r in t)
    left = "".join(f"<li>{html.escape(r['visual_description'])}</li>" for r in reqs) or "<li>none</li>"
    before = inline(before_svg, f"{prefix}b-", f"{title} before refinement", f"Before: {t[0]['issues']} issues, {t[0]['critical']} critical, score {t[0]['overall']:.2f}")
    after = inline(after_svg, f"{prefix}a-", f"{title} after refinement", f"After: {t[-1]['issues']} issues, {t[-1]['critical']} critical, score {t[-1]['overall']:.2f}")
    return f'''<article class="card" id="{name}">
  <header class="card-head"><h3>{html.escape(title)}</h3><span class="chip">{rubric}</span>{sparkline(t, prefix)}</header>
  <div class="pair">{before}{after}</div>
  <div class="card-body">
    <table class="traj"><thead><tr><th>round</th><th>score</th><th>issues</th><th>critical</th><th>edits</th><th>diff</th></tr></thead><tbody>{rows}</tbody></table>
    <div class="notes"><p><strong>Decided by a person</strong> {decided}</p><p><strong>Still open</strong></p><ul>{left}</ul></div>
  </div>
</article>'''


def build() -> str:
    parts: list[str] = []
    parts.append(read(os.path.join(os.path.dirname(__file__), "showcase.css")))

    # ---- stats
    n_tests = 125
    trajs = [f for f in os.listdir(os.path.join(EX, "teaching", "output")) if f.endswith(".trajectory.json")]
    gains = []
    for f in trajs:
        d = json.load(open(os.path.join(EX, "teaching", "output", f), encoding="utf-8"))
        gains.append(d["final"]["overall"] - d["initial"]["overall"])
    icons_n = len([f for f in os.listdir(os.path.join(EX, "icons")) if f.endswith(".svg") and f != "sheet.svg"]) if exists("icons", "sheet.svg") else 0
    parts.append(f'''
<header class="hero">
  <p class="eyebrow">Figures as programs</p>
  <h1>FigTree Showcase</h1>
  <p class="lede">One loop, five media. A source text is grounded into a content plan, drawn as an editable SVG program by a recursive tree of agents, rendered, criticised in code and image, and repaired by anchored edit scripts until the score stops moving. The same loop then refines charts, slides, dashboard tiles and icons, and animates what moves.</p>
  <dl class="stats">
    <div><dt>acceptance tests</dt><dd>{n_tests}</dd></div>
    <div><dt>artifacts refined</dt><dd>{len(trajs)}</dd></div>
    <div><dt>mean score gain</dt><dd>+{sum(gains) / max(len(gains), 1):.2f}</dd></div>
    <div><dt>icons designed</dt><dd>{max(icons_n, 0)}</dd></div>
  </dl>
</header>
<nav class="toc"><a href="#loop">The loop</a><a href="#figures">1 · Figures from text</a><a href="#refine">2 · Refinement</a><a href="#icons">3 · Icons</a><a href="#motion">4 · Motion</a><a href="#meta">5 · Meta-prompt</a><a href="#evaluation">6 · Evaluation</a><a href="#learned">What the loop caught</a></nav>
''')

    # ---- the loop
    loop_svg = os.path.join(os.environ.get("FIGTREE_SCRATCH", ""), "loop.svg")
    if not os.path.exists(loop_svg):
        loop_svg = os.path.join(EX, "showcase", "loop.svg")
    if os.path.exists(loop_svg):
        parts.append('<section id="loop"><h2>The loop</h2><p>Generated by the system from a four-line description of itself (<code>examples/figtree/loop.md</code>). Every block is a component the grounder found in the text; every arrow is a flow it found; the dashed edge is the feedback that makes it a loop.</p>')
        parts.append(inline(loop_svg, "loop-", "The FigTree loop", "Source → Grounder → Content plan → Recursive construction → Program → Render → Critic → Edit script → Score, and back until stable."))
        parts.append("</section>")

    # ---- level 1
    parts.append('<section id="figures"><h2>1 · Figures from text</h2><p>Rule-based grounding on three sources, with element kinds and icons chosen by role. Zero residual defects, editability proof passing (one local edit changes exactly one element) on all three.</p>')
    for name, title, cap in (
        ("figtree-spec", "The specification, applied to itself", "Grounder → recursive tree → Critic, and the render → Critic → Worker → re-validate → render loop. 14 nodes, 9 components, 9 flows."),
        ("transformer-method", "A dual-branch transformer", "Parallel encoders stacked in one column, the residual branch bracketed over the top, the classifier on the second row. 10 nodes, 7 components, 8 flows."),
        ("rmp-skill", "A recursive meta-prompting skill", "Numbered workflow steps become a pipeline; the explicit refine loop becomes a dashed feedback edge. 8 nodes, 6 components, 6 flows."),
    ):
        p = os.path.join(EX, "output", f"{name}.svg")
        if os.path.exists(p):
            parts.append(f"<h3>{title}</h3>" + inline(p, f"{name}-", title, cap))
    cl = os.path.join(EX, "claude", "figtree-spec.claude.svg")
    if os.path.exists(cl):
        rep = json.load(open(os.path.join(EX, "claude", "figtree-spec.claude.report.json"), encoding="utf-8"))
        comps = ", ".join(c["name"] for c in rep["content_plan"]["components"])
        parts.append("<h3>The same specification, grounded by Claude</h3><p>Content plan from the Claude Code CLI on this session's own login (no API key), paper style kept, deterministic layout. The model finds what the rules cannot: " + html.escape(comps) + ".</p>")
        parts.append(inline(cl, "claude-", "Claude-grounded self-application figure", f"{rep['node_count']} nodes, {len(rep['content_plan']['components'])} components, {len(rep['content_plan']['flows'])} flows; inputs {', '.join(rep['content_plan']['inputs'])}; outputs {', '.join(rep['content_plan']['outputs'])}."))
    parts.append("</section>")

    # ---- level 2
    parts.append('<section id="refine"><h2>2 · Refinement on teaching material</h2><p>Each artifact starts as a deliberately defective hand-made SVG. Mechanical defects are fixed by the critic\'s own edit scripts; everything that changes meaning comes back as a request, answered here by a short edit script a person wrote. Scores use the paper\'s eight diagnostic dimensions on a 1–10 scale; a critical defect caps a dimension at 5.</p><div class="cards">')
    T = os.path.join(EX, "teaching")
    cards = (
        ("bar-chart", "Bar chart", "data-figure", "axis labels with units, a title that states the finding"),
        ("slide-pipeline", "Slide pipeline", "slide", "the ten-word label shortened to one word"),
        ("dashboard-tiles", "Dashboard tiles", "dashboard", "labels shortened, tiles made equal, two accents chosen, the critic's default blue overridden"),
        ("trajectory-chart", "Trajectory chart", "data-figure", "axis labels, series re-coloured so two lines stay distinguishable, legend moved instead of growing the canvas"),
        ("process-icon", "Process icon", "icon", "nothing yet: the text inside the icon is a design decision the loop refuses to make"),
    )
    for name, title, rubric, decided in cards:
        b = os.path.join(T, f"{name}.svg")
        a = os.path.join(T, "output", f"{name}.refined.svg")
        tr = os.path.join(T, "output", f"{name}.trajectory.json")
        if all(os.path.exists(x) for x in (b, a, tr)):
            parts.append(refinement_card(name, title, rubric, b, a, tr, f"{name}-", decided))
    parts.append("</div></section>")

    # ---- level 3 icons
    if exists("icons", "sheet.svg"):
        parts.append('<section id="icons"><h2>3 · A custom icon family from briefs</h2><p>Twelve icons designed by a Claude draughtsman from one-line briefs, scored by the icon rubric and the family rules (24-grid, 2 px stroke, round joins, 2 px safe margin, at most 12 strokes, no text), revised until each read at 16 px.</p>')
        parts.append(inline(os.path.join(EX, "icons", "sheet.svg"), "icons-", "Icon family contact sheet", "Name and final score under each icon."))
        rp = os.path.join(EX, "icons", "report.json")
        if os.path.exists(rp):
            rep = json.load(open(rp, encoding="utf-8"))
            rows = "".join(f"<tr><td>{html.escape(r['name'])}</td><td>{r['score']:.2f}</td><td>{len(r.get('trajectory', []))}</td><td>{'yes' if r.get('accepted') else 'no'}</td></tr>" for r in rep)
            parts.append(f'<table class="traj"><thead><tr><th>icon</th><th>score</th><th>rounds</th><th>accepted</th></tr></thead><tbody>{rows}</tbody></table>')
        notes = os.path.join(EX, "icons", "NOTES.md")
        if os.path.exists(notes):
            parts.append('<details><summary>Worker notes</summary><pre class="notes-pre">' + html.escape(read(notes)) + "</pre></details>")
        parts.append("</section>")

    # ---- level 4 motion
    anim_svg = os.path.join(EX, "animated", "figtree-spec.refined.animated.svg")
    if not os.path.exists(anim_svg):
        anim_svg = os.path.join(EX, "animated", "figtree-spec.animated.svg")
    if os.path.exists(anim_svg):
        svg = read(anim_svg)
        css = re.search(r"<style>(.*?)</style>", svg, re.S)
        css_text = css.group(1) if css else ""
        sibling = anim_svg.replace(".animated.svg", ".animation.css")
        if not css_text and os.path.exists(sibling):
            css_text = read(sibling)
        parts.append('<section id="motion"><h2>4 · The figure comes to life</h2><p>Three motions, each with a meaning: blocks appear in the order the recursion builds them; connectors draw themselves before their arrowheads appear; a token travels every data flow, slower and dimmer on dashed control edges. The timeline is derived from the program, so every frame is reproducible; readers who prefer reduced motion see the final state.</p><p><button id="replay" type="button">Replay</button> <a class="explainer-link" href="explainer/index.html">Open the full explainer with scrubber, captions and legend</a></p>')
        parts.append(inline(anim_svg, "anim-", "Animated self-application figure", "Reveal, draw, pulse. Press Replay to watch the figure build itself again.", css_text))
        parts.append('''<script>
(function(){var b=document.getElementById('replay');if(!b)return;b.addEventListener('click',function(){var f=b.parentNode.nextElementSibling;var s=f.querySelector('.sheet');var h=s.innerHTML;s.innerHTML='';void s.offsetWidth;s.innerHTML=h;});})();
</script></section>''')
        notes = os.path.join(EX, "animated", "NOTES.md")
        if os.path.exists(notes):
            parts.insert(len(parts) - 1, '<details><summary>Worker notes</summary><pre class="notes-pre">' + html.escape(read(notes)) + "</pre></details>")

    # ---- level 5 meta
    parts.append('''<section id="meta"><h2>5 · The meta-prompt behind all of it</h2>
<p>The category is <em>editable-SVG artifact synthesis under a rubric</em>. What varies per instance is the source, the medium and the motion grammar; what never varies is the loop. The full typed version lives in <code>docs/META-PROMPT-SVG-ARTIFACTS.md</code>; this is its skeleton.</p>
<div class="meta-grid">
  <div><h4>Typed slots</h4><ul><li>Source · Medium · Rubric(Medium)</li><li>Vocabulary of element kinds · IconFamily · MotionGrammar</li><li>ContentPlan with evidence spans</li><li>LayoutTree (2–4 children, depth ≤ 8, ≤ 32 nodes)</li><li>Program · Render · CriticReport · EditScript</li><li>Trajectory · Convergence · Requests</li></ul></div>
  <div><h4>Procedure</h4><ol><li>Ground: only evidenced elements, nothing invented</li><li>Choose vocabulary and motion by meaning</li><li>Construct recursively; parents own cross-boundary arrows; 20 px shafts</li><li>Critique in two spaces, every issue anchored</li><li>Edit locally; hand content decisions back</li><li>Score, loop until stable, keep the trajectory</li><li>Promote: icons to the family, rules to memory</li></ol></div>
  <div><h4>Binding rules</h4><ul><li>The content plan is immutable downstream</li><li>Ids are stable; edits address existing ids</li><li>Data flow → pulse; control → slower pulse; construction → reveal and draw</li><li>No evidence → not assessed, never a 10</li><li>Fixed canvases centre; free canvases shrink</li></ul></div>
  <div><h4>Refinement log</h4><ul><li>Pass 1 added icons and motion as slots</li><li>Pass 2 bound motion to flow types; fixed score inflation</li><li>Pass 3 separated fixed from free canvases</li><li>Pass 4 returned an empty edit script</li></ul></div>
</div></section>''')

    # ---- evaluation
    ev = os.path.join(EX, "eval")
    if os.path.exists(os.path.join(ev, "eval.json")):
        e = json.load(open(os.path.join(ev, "eval.json"), encoding="utf-8"))
        s_ = e["summary"]
        per = e["per_check"]
        rows = "".join(f'<tr><td>{html.escape(k)}</td><td>{v.get("tp",0)}/{v.get("tp",0)+v.get("fn",0)}</td><td>{v.get("fp",0)}</td></tr>' for k, v in sorted(per.items()))
        gaming = [r for r in e["probes"] if r["kind"] == "gaming"]
        fps = [r for r in e["probes"] if r["kind"] == "false_positive"]
        glist = "".join(f"<li><code>{html.escape(r['id'])}</code> scored {r['overall']:.2f}; should fire {', '.join(r['missed']) or '(now caught)'}</li>" for r in gaming) or "<li>none</li>"
        parts.append(f'''<section id="evaluation"><h2>6 · Evaluating the evaluators</h2>
<p>A rubric is an artifact too, so it gets the same loop. Each rubric is a machine-readable spec (dimensions with anchors, checks with signals, veto rules, judge questions). Probes are minimal figures with a known verdict; adversaries wrote probes to game the checks, trip false positives and expose misses. Every probe is now a regression test.</p>
<dl class="stats"><div><dt>probes</dt><dd>{s_["probes"]}</dd></div><div><dt>recall</dt><dd>{s_["recall"]}</dd></div><div><dt>precision</dt><dd>{s_["precision"]}</dd></div><div><dt>gaming probes</dt><dd>{len(gaming)}</dd></div><div><dt>false-positive probes</dt><dd>{len(fps)}</dd></div></dl>
<details><summary>Per-check recall (caught / expected) and false positives</summary><table class="traj"><thead><tr><th>check</th><th>recall</th><th>false pos.</th></tr></thead><tbody>{rows}</tbody></table></details>
<h3>What still fools the measurable critic</h3><ul class="learned">{glist}</ul>''')
        cal = os.path.join(ev, "calibration.json")
        if os.path.exists(cal):
            c = json.load(open(cal, encoding="utf-8"))
            crow = "".join(f'<tr><td>{html.escape(r["name"])}</td><td>{r["rubric"]}</td><td>{r["measured_overall"]:.2f}</td><td>{r["judged_overall"]:.2f}</td><td>{r["gap_overall"]:+.2f}</td></tr>' for r in c["rows"])
            flist = "".join(f"<li><strong>{html.escape(f['kind'])}</strong>: {html.escape(f['name'])}, {f['dimension']} measured {f['measured']} vs judged {f['judged']}</li>" for f in c["findings"]) or "<li>none</li>"
            parts.append(f'''<h3>Image judge versus measured rubric</h3>
<p>The paper's diagnostic evaluator, reading the rendered PNG on this session's login, scored the same figures. Mean gap (judged minus measured) {c["mean_gap"]:+.2f} over {len(c["rows"])} figures, ${c["cost_usd"]} in total. A measured 9 that the judge scores 6 is a rubric blind spot; the reverse is a rule to reconsider.</p>
<table class="traj"><thead><tr><th>figure</th><th>rubric</th><th>measured</th><th>judged</th><th>gap</th></tr></thead><tbody>{crow}</tbody></table>
<ul class="learned">{flist}</ul>''')
        for name in ("ADVERSARY-diagram.md", "ADVERSARY-chart.md", "ADVERSARY-icon-motion.md"):
            ap = os.path.join(EX, "probes", name)
            if os.path.exists(ap):
                parts.append(f"<details><summary>{html.escape(name)}</summary><pre class=\"notes-pre\">{html.escape(read(ap))}</pre></details>")
        parts.append("</section>")

    # ---- learned
    parts.append('''<section id="learned"><h2>What the loop caught, and what the eye caught</h2>
<ul class="learned">
<li>CSS <code>transform</code> on an SVG group replaces its own <code>translate</code>: an animated block jumped to its container's corner. Reveal now animates opacity only.</li>
<li>A marker-ended path with a hidden shaft still paints its arrowhead: the "standalone triangle" the paper warns about appeared during draw-on. A marker-less shaft copy draws first; the real connector appears when it is complete.</li>
<li>Raising fonts to a medium's minimum is mechanical, but it creates overflow and collisions on long labels in the same round; the edit script has to shorten labels at once.</li>
<li>Text over a gradient fill passed a contrast check against the canvas; the critic now refuses to certify contrast on gradient hosts.</li>
<li>Neon was checked on fills only; a neon stroke survived. Strokes are checked now.</li>
<li>"Has a title that states the finding" accepted any three-word label (a legend entry); it now checks the most prominent text.</li>
<li>A model grounder also returns a global style; adopting it replaced the paper palette with saturated fills. The content plan is kept, the style is not, unless asked.</li>
<li>Shrinking a slide or an icon canvas to its content breaks the medium; fixed canvases centre their content instead.</li>
</ul>
<footer><p>Repository branch <code>claude/figtree-generator</code> in manutej/hekat. Package <code>figtree/</code>; tests in <code>tests/test_figtree*.py</code>; sources and outputs under <code>examples/figtree/</code>.</p></footer>
</section>''')
    return "\n".join(parts)


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(EX, "showcase", "showcase.html")
    page = build()
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(page)
    print(f"wrote {out} ({len(page) // 1024} KB)")

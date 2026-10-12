"""Rule-based Grounder agent.

Extracts only explicitly stated elements from the source text.  Every component and flow
carries an ``evidence_span`` that is a verbatim substring of the source.  Connections that
are not explicit, that reference unknown components, or that contradict each other are
omitted and logged as residual defects.  Nothing is invented.
"""

from __future__ import annotations

import re
from collections import Counter, OrderedDict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from figtree.ingest import sanitize_source, truncate
from figtree.schemas import Component, ContentPlan, Flow, GlobalStyle, ResidualDefect

ARROW_GLYPHS = ("→", "->", "⇒", "=>", "⟶", "⇢")
_ARROW_SPLIT = re.compile(r"\s*(?:→|->|⇒|=>|⟶|⇢)\s*")
_ARROW_FIND = re.compile(r"→|->|⇒|=>|⟶|⇢")
# generic role suffixes are stripped ("Critic Agent" -> "Critic"); descriptive ones are kept
# as part of the name ("Text Encoder", "Refine Step").
_GENERIC_ROLE = r"(?:Agent|Module|Component)"
_KEPT_ROLE = r"(?:Stage|Step|Phase|Engine|Layer|Encoder|Decoder|Block|Unit|Head)"
_NAMED_ROLE = re.compile(
    rf"\b([A-Z][A-Za-z0-9-]+(?: [A-Z][A-Za-z0-9-]+){{0,2}}) {_GENERIC_ROLE}\b|"
    rf"\b([A-Z][A-Za-z0-9-]+(?: [A-Z][A-Za-z0-9-]+){{0,2}} {_KEPT_ROLE})\b"
)
_HEAD_DELIMS = re.compile(r"(?:[:;,(\[]|\bdepict|\bshows?|\bis|\bare|\bthen|\bvia|\bas|\bof|\bthrough)\s*", re.IGNORECASE)
_TAIL_DELIMS = re.compile(
    r"\s*(?:[.;,)\]]|\(.*|\b(?:and|then|must|which|where|with|to|for|so|that|the|a|an|is|are|was|were|has|have|"
    r"connection|carries|uses|produces|returns|provides|takes|receives|sends|passes|feeds|connects|yields)\b)"
)
_LEADING_ARTICLE = re.compile(r"^(?:the|a|an|this|that|each|every)\s+", re.IGNORECASE)
_CALL_EXPR = re.compile(r"\b([A-Z][A-Za-z0-9_]*)\(([A-Za-z0-9_, ]*)\)")
_NEGATION = re.compile(
    r"\b(?:no|never|not|doesn't|does not|is not|isn't)\b[^.\n]*?\b(?:connect|connection|flow|edge|arrow|link|feed|send)",
    re.IGNORECASE,
)
_WORKFLOW_HEADING = re.compile(r"^#{1,6}\s.*\b(?:workflow|process|pipeline|procedure|steps?|algorithm|method(?:ology)?|stages?|phases?)\b", re.IGNORECASE)
_NUMBERED_STEP = re.compile(r"^\s*(\d+)[.)]\s+\**([A-Z][^.:*\n]{1,40}?)\**\s*(?::|$|\s[-–—]\s)")
_FLOW_TYPE_SUFFIX = re.compile(r"^\s*\((data|control|conditional|feedback|parallel)\)", re.IGNORECASE)
_COMPONENT_HINT = re.compile(r"^\s*[-*]\s+\*\*([^*\n]{1,60})\*\*\s*\(((?:kind|icon)\s*:\s*[a-z][a-z0-9-]*(?:\s*,\s*(?:kind|icon)\s*:\s*[a-z][a-z0-9-]*)?)\)", re.MULTILINE)
_LOOP_WORD = re.compile(r"\b(?:repeat|loop|iterate|again|feedback|re-?run|until)\b", re.IGNORECASE)
_SUFFIX_ALIAS = {"agent", "loop", "step", "stage", "phase", "module", "repair", "pass", "system"}

MAX_COMPONENTS = 16


def _blank_code_fences(text: str) -> str:
    out: List[str] = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            out.append("")
            continue
        out.append("" if in_fence else line)
    return "\n".join(out)


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _clean_segment(seg: str) -> Optional[str]:
    s = seg.strip()
    s = re.sub(r"\([^)]*\)$", "", s).strip()  # trailing parenthetical note
    s = s.strip("`'\"*_ ")
    s = re.sub(r"\s+", " ", s)
    if not s or len(s) > 40:
        return None
    words = s.split()
    if len(words) > 5:
        return None
    if not re.search(r"[A-Za-z]", s):
        return None
    if s in {"and", "or", "then", "the", "a", "an"}:  # lowercase articles/conjunctions only
        return None
    return s


def canonical(name: str, known: Dict[str, str]) -> str:
    """Resolve aliases such as ``Critic Agent`` / ``Critic loop`` -> ``Critic``."""
    key = slug(name)
    if key in known:
        return known[key]
    words = name.split()
    if len(words) >= 2 and words[-1].lower() in _SUFFIX_ALIAS:
        base = slug(" ".join(words[:-1]))
        if base in known:
            return known[base]
    for k, v in known.items():
        vw = v.split()
        if words and len(words) >= 2 and words[0].lower() == vw[0].lower() and len(vw) == 1 and words[-1].lower() in _SUFFIX_ALIAS:
            return v
    return name


@dataclass
class GrounderOutput:
    content_plan: ContentPlan
    global_style: GlobalStyle
    residuals: List[ResidualDefect] = field(default_factory=list)
    stripped_lines: List[str] = field(default_factory=list)


class RuleBasedGrounder:
    """Deterministic Grounder.  ``max_chars`` mirrors the prompt truncation (8000 chars)."""

    def __init__(self, max_chars: int = 8000, max_components: int = MAX_COMPONENTS) -> None:
        self.max_chars = max_chars
        self.max_components = max_components

    # -- public API --------------------------------------------------------
    def ground(self, source_text: str) -> GrounderOutput:
        clean, stripped = sanitize_source(source_text)
        text = truncate(clean, self.max_chars) if self.max_chars else clean
        # fenced code blocks are implementation, not methodology prose: blank them for extraction
        # (line structure is preserved so evidence spans stay verbatim substrings of the source)
        text = _blank_code_fences(text)
        residuals: List[ResidualDefect] = []
        if stripped:
            residuals.append(
                ResidualDefect(
                    "warning",
                    f"{len(stripped)} instruction-like line(s) stripped on ingest",
                    "ingest",
                    "none; adversarial instructions are never drawn",
                )
            )

        components: "OrderedDict[str, Component]" = OrderedDict()
        known: Dict[str, str] = {}
        mentions: Counter = Counter()

        def add_component(name: str, evidence: str) -> str:
            name = _LEADING_ARTICLE.sub("", name.strip())
            resolved = canonical(name, known)
            key = slug(resolved)
            if key not in components:
                components[key] = Component(name=resolved, evidence_span=evidence)
                known[key] = resolved
            mentions[key] += 1
            return components[key].name

        # 1. named roles ("Critic Agent") -> base name
        for m in _NAMED_ROLE.finditer(text):
            add_component(m.group(1) or m.group(2), m.group(0))

        # 2. call expressions: Grounder(SourceText)
        inputs: List[str] = []
        for m in _CALL_EXPR.finditer(text):
            fn, args = m.group(1), m.group(2)
            if fn in known.values() or slug(fn) in known:
                for a in [a.strip() for a in args.split(",") if a.strip()]:
                    if a not in inputs:
                        inputs.append(a)

        # 3. arrow expressions -> components + flows
        raw_flows: List[Tuple[str, str, str, str]] = []
        for line in text.splitlines():
            expr = self._arrow_expression(line)
            if expr:
                before = len(raw_flows)
                self._parse_chain(expr, line, add_component, raw_flows)
                # explicit flow type after the chain: "A -> B (control): ..." (spec format)
                m_type = _FLOW_TYPE_SUFFIX.search(line[line.find(expr) + len(expr):] if expr in line else "")
                if m_type:
                    t = m_type.group(1).lower()
                    raw_flows[before:] = [(a, b, t if ft == "data" else ft, e) for (a, b, ft, e) in raw_flows[before:]]
        # explicit component hints: "- **Name** (kind: store, icon: database): role" (spec format)
        for m in _COMPONENT_HINT.finditer(text):
            name = add_component(m.group(1), m.group(0).strip())
            key = slug(name)
            attrs = dict(re.findall(r"(kind|icon)\s*:\s*([a-z][a-z0-9-]*)", m.group(2)))
            if key in components:
                if attrs.get("kind"):
                    components[key].kind = attrs["kind"]
                if attrs.get("icon"):
                    components[key].icon = attrs["icon"]

        # 3b. numbered steps under a workflow/process heading: explicit ordering -> sequential flows
        section_is_workflow = False
        prev_step: Optional[str] = None
        prev_no = 0
        for line in text.splitlines():
            if line.startswith("#"):
                section_is_workflow = bool(_WORKFLOW_HEADING.match(line))
                prev_step, prev_no = None, 0
                continue
            if not section_is_workflow:
                continue
            m = _NUMBERED_STEP.match(line)
            if not m:
                if line.strip() and not line.startswith((" ", "\t", "-", "*")):
                    prev_step, prev_no = None, 0
                continue
            no, title = int(m.group(1)), m.group(2).strip()
            if len(title.split()) > 5:
                prev_step, prev_no = None, 0
                continue
            name = add_component(title, line.strip())
            if prev_step is not None and no == prev_no + 1 and prev_step != name:
                raw_flows.append((prev_step, name, "data", line.strip()))
            prev_step, prev_no = name, no

        # 4. inputs / outputs / notation
        outputs: List[str] = []
        for line in text.splitlines():
            m = re.match(r"\s*(Input|Output)s?\s*:\s*(.+)", line)
            if m:
                body = re.sub(r"\([^)]*\)", "", m.group(2)).rstrip(". ")
                items = [i.strip(" `*.") for i in re.split(r",|;", body) if i.strip()]
                target = inputs if m.group(1) == "Input" else outputs
                for i in items:
                    if i and len(i.split()) <= 3 and i not in target:
                        target.append(i)
        notation = [g for g in ("→", "||", "+", "<>", "[]", "//", "|||", "sample^", "iterate@") if g in text]

        # 5. rank + cap components (flow endpoints first, then by mention count)
        endpoint_keys = {slug(f[0]) for f in raw_flows} | {slug(f[1]) for f in raw_flows}
        ranked = sorted(
            components.keys(),
            key=lambda k: (0 if k in endpoint_keys else 1, -mentions[k], list(components).index(k)),
        )
        keep = ranked[: self.max_components]
        if len(ranked) > self.max_components:
            residuals.append(
                ResidualDefect(
                    "warning",
                    f"{len(ranked) - self.max_components} minor component(s) omitted by the node cap",
                    "content_plan.components",
                    "raise max_components or split the source",
                )
            )
        keep_set = set(keep)
        final_components = [components[k] for k in components if k in keep_set]
        names = {c.name for c in final_components}

        # 6. resolve flows: drop unknown endpoints, duplicates, self loops, contradictions
        flows = self._resolve_flows(raw_flows, names, residuals)

        claim = self._claim(text)
        plan = ContentPlan(
            claim=claim,
            components=final_components,
            flows=flows,
            inputs=inputs,
            outputs=outputs,
            notation=notation,
        )
        return GrounderOutput(plan, GlobalStyle(), residuals, stripped)

    # -- helpers -------------------------------------------------------------
    @staticmethod
    def _arrow_expression(line: str) -> Optional[str]:
        """Return the verbatim ``A → B → C`` expression contained in ``line`` (or None).

        The first segment is the trailing noun phrase before the first arrow (after the last
        delimiter such as ``:``), the last segment is the leading noun phrase after the final
        arrow (before ``.``/``and``/...).  Middle segments are taken as-is.
        """
        if not _ARROW_FIND.search(line):
            return None
        raw = line.strip().lstrip("-*#> ").strip()
        if raw.startswith(("Op ", "|", "Query")) or "::=" in raw:
            return None  # grammar tables are notation, not flows
        glyphs = list(_ARROW_FIND.finditer(raw))
        head = raw[: glyphs[0].start()]
        tail = raw[glyphs[-1].end() :]
        # head: text after the last delimiter; if still long, keep the last capitalised run
        parts = _HEAD_DELIMS.split(head)
        head_seg = parts[-1].strip() if parts else head.strip()
        head_seg = _LEADING_ARTICLE.sub("", head_seg)
        if len(head_seg.split()) > 5:
            words = head_seg.split()
            run: List[str] = []
            for w in reversed(words):
                if w[:1].isupper() or (run and w[:1].islower() and len(run) < 2 and False):
                    run.insert(0, w)
                else:
                    break
            head_seg = " ".join(run) if run else " ".join(words[-2:])
        m = _TAIL_DELIMS.search(tail)
        tail_seg = tail[: m.start()].strip() if m else tail.strip()
        if len(tail_seg.split()) > 5:
            tail_seg = " ".join(tail_seg.split()[:3])
        if re.search(r"\b(?:if|or|else|when|unless|otherwise)\b", head_seg, re.IGNORECASE):
            head_seg = ""  # conditional sentence: the head is not an explicit component
        if not tail_seg:
            return None
        if not head_seg:
            # start the expression at the first arrow's right-hand side
            after = raw[glyphs[0].end() :].lstrip()
            start = raw.find(after)
            if len(glyphs) < 2:
                return None
        else:
            start = raw.rfind(head_seg, 0, glyphs[0].start())
        end = raw.find(tail_seg, glyphs[-1].end())
        if start < 0 or end < 0:
            return None
        expr = raw[start : end + len(tail_seg)]
        return expr if expr in line else None

    def _parse_chain(self, expr: str, line: str, add_component, raw_flows: List[Tuple[str, str, str, str]]) -> None:
        segments = _ARROW_SPLIT.split(expr)
        prev: List[str] = []
        first: List[str] = []
        for seg in segments:
            seg = seg.strip()
            if not seg:
                continue
            # loop-back marker: "repeat ≤3" -> control flow back to the chain start
            if re.match(r"^(repeat|loop|iterate|again)\b", seg, re.IGNORECASE):
                for p in prev:
                    for f in first:
                        raw_flows.append((p, f, "control", expr))
                continue
            flow_type = "data"
            names: List[str] = []
            inner = seg.strip("()")
            if "||" in inner or "|||" in inner:
                flow_type = "parallel"
                parts = [p for p in re.split(r"\|{2,3}", inner)]
            elif re.match(r"^<.*\?.*:.*>$", inner):  # <cond ? A : B>
                flow_type = "conditional"
                body = inner.strip("<>")
                _, _, branches = body.partition("?")
                parts = branches.split(":")
            else:
                parts = [inner]
            for p in parts:
                call = _CALL_EXPR.match(p.strip())
                if call:
                    p = call.group(1)
                name = _clean_segment(p)
                if name:
                    names.append(add_component(name, p.strip() if p.strip() in line else expr))
            if not names:
                continue
            if not first:
                first = names
            for a in prev:
                for b in names:
                    raw_flows.append((a, b, flow_type, expr))
            prev = names

    def _resolve_flows(
        self,
        raw_flows: List[Tuple[str, str, str, str]],
        names: set,
        residuals: List[ResidualDefect],
    ) -> List[Flow]:
        seen: Dict[Tuple[str, str], Flow] = {}
        for a, b, t, ev in raw_flows:
            if a == b:
                residuals.append(ResidualDefect("warning", f"self-loop on {a} omitted", "content_plan.flows", "none"))
                continue
            if a not in names or b not in names:
                residuals.append(
                    ResidualDefect("warning", f"flow {a} -> {b} references an unknown component; omitted", "content_plan.flows", "none")
                )
                continue
            if (a, b) in seen:
                continue
            seen[(a, b)] = Flow(a, b, t, ev)
        # contradictions: opposite directions, both data, no loop wording on either evidence
        drop = set()
        for (a, b), f in seen.items():
            g = seen.get((b, a))
            if g is None or (a, b) in drop:
                continue
            if f.type == "data" and g.type == "data" and not (_LOOP_WORD.search(f.evidence_span) or _LOOP_WORD.search(g.evidence_span)):
                drop.update({(a, b), (b, a)})
                residuals.append(
                    ResidualDefect(
                        "warning",
                        f"contradictory flow direction between {a} and {b}; both omitted",
                        "content_plan.flows",
                        "clarify the direction in the source text",
                    )
                )
        # explicit negations: "no connection from A to B"
        return [f for k, f in seen.items() if k not in drop]

    @staticmethod
    def _claim(text: str) -> str:
        for line in text.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        for line in text.splitlines():
            s = line.strip()
            if len(s) >= 40 and not s.startswith(("#", "|", "```", "-", "*")):
                return s[:200]
        return ""


def check_faithfulness(plan: ContentPlan, source_text: str) -> List[str]:
    """Return a list of unfaithful entries (empty when every evidence span appears in source)."""
    bad = []
    for c in plan.components:
        if not c.evidence_span or c.evidence_span not in source_text:
            bad.append(f"component {c.name!r}")
    for f in plan.flows:
        if not f.evidence_span or f.evidence_span not in source_text:
            bad.append(f"flow {f.src} -> {f.dst}")
    return bad

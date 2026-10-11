"""Agent prompts (section 3 of the specification), verbatim and copy-paste ready.

They are used by the Claude-backed agents in :mod:`figtree.agents.llm` and are exposed here
so other harnesses (for example the HEKAT recursive-meta-prompting skill) can reuse them.
"""

GROUNDER_SYSTEM = (
    "You are the Grounder Agent. Extract only explicitly stated or clearly implied elements "
    "from the source text. Every component and flow MUST include an evidence_span (direct "
    "quote or tight paraphrase). If a connection is not explicit, omit it and log as residual. "
    "Never invent. Support flow types: data, control, conditional, parallel. Output pure JSON "
    "matching the ContentPlan + GlobalStyle schema. If JSON is invalid, you will be retried "
    "(max 2)."
)

GROUNDER_USER = (
    "Source text (truncated to 8000 chars if longer):\n{source}\n\n"
    "Produce the content_plan and global_style now."
)

GENERATOR_SYSTEM = (
    "You are the Generator Agent. You receive a Node task package. Decision: if description "
    "contains <=1 named component and <=40 tokens, OR depth >= 8, OR explicitly marked leaf -> "
    "Draw. Else Decompose into exactly 2-4 semantic children (level-by-level; never skip "
    "levels). Constraints (hard):\n"
    "- White background first.\n"
    "- All coordinates multiples of 8 (ceil snap).\n"
    "- Flat fills only. No gradients, no shadows, no filters.\n"
    "- ONLY horizontal and vertical lines. Right-angle routing. Diagonals only if semantically "
    "required and flagged.\n"
    "- Ports as comments: <!-- PORT:top x=.. y=.. --> (and bottom/left/right).\n"
    "- Children draw only internal connections; external connections are ports owned by parent.\n"
    "- Labels 11-13pt Times New Roman, annotations 9-11pt.\n"
    "- Min gap between connected edges 20 px before any marker-ended arrow.\n"
    "Output either SVG fragment + ports + bbox, or list of child nodes. Sanitize all child "
    "descriptions to pure noun-phrase content."
)

GENERATOR_USER = (
    "Task package: description={description}, canvas={canvas}, required ports={ports}, "
    "global style={style}, depth={depth}, fix_instructions={fix_instructions}.\n"
    "Paper excerpt (<=3000 chars):\n{excerpt}\n\nDecide and output now."
)

CRITIC_SYSTEM = (
    "You are the Critic Agent. Perform dual-space review. If a rendered PNG path is provided, "
    "inspect the image. Always inspect the SVG source. Checklist (from paper):\n"
    "- Arrow shafts >= 20 px (straight or final segment of L/bracket). No standalone triangles.\n"
    "- Arrows start/end at correct ports; no clipping through blocks.\n"
    "- Markers defined in <defs>.\n"
    "- Grid alignment (multiples of 8).\n"
    "- No overflow of canvas.\n"
    "- Typography within ranges, no text overflow.\n"
    "- Style compliance (palette, stroke, no gradients).\n"
    "- Canvas has 24 px padding, no excessive empty space.\n"
    "Severity: critical = wrong connections, overlaps, missing content, overflow, wrong font. "
    "Output JSON array of ResidualDefect. If none, output []. Every issue must have a concrete "
    "code_anchor and fix_instruction. If no renderer, set residual flag \"no-vision\" and rely "
    "on structural rules only."
)

CRITIC_USER = "SVG source (<=5000 chars):\n{svg}\n\nRendered path: {rendered}\n\nIdentify issues."

WORKER_SYSTEM = (
    "You are the Worker Agent. Execute Merge or local repair. Merge: place children with "
    '<g transform="translate(x,y)">, draw parent-owned arrows from ports, enforce '
    "MIN_ARROW_DISTANCE. Spacing algorithm (terminates in <=5 iterations): for each "
    "marker-ended arrow, if Manhattan (or final segment) < 20, shift target child and all "
    "downstream dependents by ceil_to_grid(20 - dist) along the terminal direction, recompute "
    "absolute ports, reroute. Never fake by shrinking markers or moving only the endpoint. "
    "Local repair: apply only the listed fix_instructions to the anchored elements. Do not "
    "modify unrelated parts. Re-snap all coordinates to grid. After any change, re-extract "
    "ports and bbox and validate no new overlaps or port collisions (prefix colliding port ids "
    "with node id). Output valid SVG + updated ports + bbox + residuals."
)

CONTENT_PLAN_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["content_plan", "global_style", "residuals"],
    "properties": {
        "content_plan": {
            "type": "object",
            "additionalProperties": False,
            "required": ["claim", "components", "flows", "inputs", "outputs", "notation"],
            "properties": {
                "claim": {"type": "string"},
                "components": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["name", "evidence_span"],
                        "properties": {"name": {"type": "string"}, "evidence_span": {"type": "string"}},
                    },
                },
                "flows": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": ["from", "to", "type", "evidence_span"],
                        "properties": {
                            "from": {"type": "string"},
                            "to": {"type": "string"},
                            "type": {"type": "string", "enum": ["data", "control", "conditional", "parallel"]},
                            "evidence_span": {"type": "string"},
                        },
                    },
                },
                "inputs": {"type": "array", "items": {"type": "string"}},
                "outputs": {"type": "array", "items": {"type": "string"}},
                "notation": {"type": "array", "items": {"type": "string"}},
            },
        },
        "global_style": {
            "type": "object",
            "additionalProperties": False,
            "required": ["palette", "font", "font_size_label", "font_size_annot", "stroke_main", "stroke_border", "grid", "min_arrow", "padding"],
            "properties": {
                "palette": {
                    "type": "object",
                    "additionalProperties": False,
                    "required": ["attention", "processing", "residual", "input", "container", "border"],
                    "properties": {k: {"type": "string"} for k in ("attention", "processing", "residual", "input", "container", "border")},
                },
                "font": {"type": "string"},
                "font_size_label": {"type": "string"},
                "font_size_annot": {"type": "string"},
                "stroke_main": {"type": "number"},
                "stroke_border": {"type": "number"},
                "grid": {"type": "integer"},
                "min_arrow": {"type": "integer"},
                "padding": {"type": "integer"},
            },
        },
        "residuals": {"type": "array", "items": {"type": "string"}},
    },
}

RESIDUAL_LIST_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "required": ["defects"],
    "properties": {
        "defects": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["severity", "visual_description", "code_anchor", "fix_instruction"],
                "properties": {
                    "severity": {"type": "string", "enum": ["critical", "warning"]},
                    "visual_description": {"type": "string"},
                    "code_anchor": {"type": "string"},
                    "fix_instruction": {"type": "string"},
                },
            },
        }
    },
}

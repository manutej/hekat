"""The generative-UI contract: ``FigureProgram`` JSON between the pipeline and any design.

The pipeline (grounder, generator, worker, critic, editor) produces and edits SVG whose
elements carry ``data-role``, ``data-kind``, ``data-flow`` and ``data-bbox`` attributes.  This
module lifts such an SVG into a design-free *program* (``program_from_svg``), validates it against
``design/contract/figure-program.schema.json`` (``validate_program``), and renders a program back
to SVG through a ``Renderer`` (``render_program``).  The default ``HouseRenderer`` reproduces the
house style from the presets; swapping the design means implementing another ``Renderer`` (or,
on the React side, another ``DesignAdapter`` in ``design/figtree-ds``) and nothing else changes:
ids, bboxes, flows and the critic that reads them stay the same.
"""

from __future__ import annotations

import json
import os
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Protocol, Tuple

from figtree.elements import KINDS, shape_path, text_inset
from figtree.icons import ICONS, ICON_VIEWBOX
from figtree.styles import PRESETS, Preset
from figtree.svgmodel import extract_ports, iter_elements, local, parse_svg

SCHEMA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "design", "contract", "figure-program.schema.json")
VERSION = 1
_TONE_BY_FILL: Dict[str, str] = {}
for _pr in PRESETS.values():
    for _tone in ("attention", "processing", "residual", "input"):
        _TONE_BY_FILL[_pr.style.palette[_tone].upper()] = _tone


def _esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def _num(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


# ---------------------------------------------------------------------------
# SVG -> program
# ---------------------------------------------------------------------------

def _points(d: str) -> List[List[float]]:
    pts: List[List[float]] = []
    x = y = 0.0
    for cmd, arg in re.findall(r"([MLHVmlhv])([^MLHVmlhvZz]*)", d):
        nums = [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", arg)]
        if cmd in "Mm":
            for i in range(0, len(nums) - 1, 2):
                x, y = (nums[i], nums[i + 1]) if cmd == "M" else (x + nums[i], y + nums[i + 1])
                pts.append([x, y])
        elif cmd in "Ll":
            for i in range(0, len(nums) - 1, 2):
                x, y = (nums[i], nums[i + 1]) if cmd == "L" else (x + nums[i], y + nums[i + 1])
                pts.append([x, y])
        elif cmd in "Hh":
            for v in nums:
                x = v if cmd == "H" else x + v
                pts.append([x, y])
        elif cmd in "Vv":
            for v in nums:
                y = v if cmd == "V" else y + v
                pts.append([x, y])
    return pts


def program_from_svg(svg_text: str, title: str = "", source: str = "") -> Dict[str, Any]:
    """Lift a FigTree SVG (generator output or an edited descendant) into a FigureProgram."""
    root = parse_svg(svg_text)
    w = int(float(root.get("width") or 0)) or int(float((root.get("viewBox") or "0 0 0 0").split()[2]))
    h = int(float(root.get("height") or 0)) or int(float((root.get("viewBox") or "0 0 0 0").split()[3]))
    preset = "paper"
    fam = (root.get("font-family") or "").lower()
    if "plex" in fam or "helvetica" in fam or "arial" in fam:
        preset = "teaching"
    title_el = root.find("{http://www.w3.org/2000/svg}title")
    title = title or (title_el.text or "" if title_el is not None else "")

    groups: Dict[str, Dict[str, Any]] = {}
    parent_of: Dict[str, Optional[str]] = {}
    nodes: List[Dict[str, Any]] = []
    containers: List[Dict[str, Any]] = []
    flows: List[Dict[str, Any]] = []
    stack: List[Tuple[ET.Element, str]] = []

    def walk(el: ET.Element, off: Tuple[float, float], parent: Optional[str], depth: int) -> None:
        tag = local(el.tag)
        gid = el.get("id") or ""
        here = parent
        if tag == "g" and el.get("data-bbox"):
            x, y, gw, gh = (float(v) for v in el.get("data-bbox", "0 0 0 0").split())
            m = re.search(r"translate\(\s*(-?[\d.]+)[ ,]+(-?[\d.]+)\s*\)", el.get("transform") or "")
            tx, ty = (float(m.group(1)), float(m.group(2))) if m else (0.0, 0.0)
            abs_x, abs_y = off[0] + tx, off[1] + ty
            has_block = any(local(c.tag) in ("rect", "path") and c.get("data-role") == "block" for c in el)
            label = el.get("data-label") or ""
            groups[gid] = {"id": gid, "bbox": {"x": abs_x, "y": abs_y, "w": gw, "h": gh}, "label": label, "leaf": has_block, "depth": depth, "parent": parent}
            parent_of[gid] = parent
            if has_block:
                shape = next(c for c in el if c.get("data-role") == "block")
                text = next((c for c in el if local(c.tag) == "text" and c.get("data-kind") == "label"), None)
                note = next((c for c in el if local(c.tag) == "text" and c.get("data-kind") == "annot"), None)
                use = next((c for c in el if local(c.tag) == "use"), None)
                fill = (shape.get("fill") or "").upper()
                node: Dict[str, Any] = {
                    "id": gid,
                    "label": "".join(text.itertext()).strip() if text is not None else (shape.get("data-component") or label),
                    "bbox": {"x": abs_x, "y": abs_y, "w": gw, "h": gh},
                    "kind": shape.get("data-kind") if shape.get("data-kind") in KINDS else "block",
                    "tone": _TONE_BY_FILL.get(fill, "processing"),
                }
                if use is not None and (use.get("href") or use.get("{http://www.w3.org/1999/xlink}href") or "").startswith("#icon-"):
                    node["icon"] = (use.get("href") or use.get("{http://www.w3.org/1999/xlink}href"))[len("#icon-"):]
                if note is not None:
                    node["note"] = "".join(note.itertext()).strip()
                if parent:
                    node["parent"] = parent
                nodes.append(node)
                return  # a leaf's children are its own shape, icon and label
            here = gid
            boxed = any(local(c.tag) == "rect" and c.get("data-role") == "container" for c in el)
            cont: Dict[str, Any] = {"id": gid, "bbox": {"x": abs_x, "y": abs_y, "w": gw, "h": gh}, "depth": depth, "boxed": boxed}
            t = next((c for c in el if local(c.tag) == "text" and (c.get("data-kind") == "title" or (c.get("id") or "").endswith(".title"))), None)
            if t is not None:
                cont["title"] = "".join(t.itertext()).strip()
            if parent:
                cont["parent"] = parent
            containers.append(cont)
            off = (abs_x, abs_y)
            depth += 1
        elif tag == "path" and el.get("data-flow"):
            pts = [[p[0] + off[0], p[1] + off[1]] for p in _points(el.get("d") or "")]
            if len(pts) >= 2:
                f: Dict[str, Any] = {
                    "id": gid or f"flow{len(flows)}",
                    "from": (el.get("data-from") or "").split(".")[0] or "unknown",
                    "to": (el.get("data-to") or "").split(".")[0] or "unknown",
                    "type": el.get("data-flow") if el.get("data-flow") in ("data", "control", "conditional", "feedback") else "data",
                    "points": pts,
                }
                if not el.get("marker-end"):
                    f["head"] = False
                flows.append(f)
            return
        for c in el:
            walk(c, off, here, depth)

    # root group(s)
    for c in root:
        if local(c.tag) == "g":
            # the outermost figure group is the canvas, not a container
            gid = c.get("id") or ""
            for cc in c:
                walk(cc, (0.0, 0.0), None, 0)
            break
    # keep only real containers: groups whose bbox differs from the canvas and that have a label or title
    containers = [c for c in containers if not (c["bbox"]["w"] >= w and c["bbox"]["h"] >= h)]
    ports = [{"id": p["id"], "side": p["side"], "x": p["abs_x"], "y": p["abs_y"], "type": p["type"], "component": p["component"]} for p in extract_ports(svg_text)]
    prog: Dict[str, Any] = {"version": VERSION, "canvas": {"width": w, "height": h, "preset": preset, "grid": 8}, "containers": containers, "nodes": nodes, "flows": flows, "ports": ports}
    if title:
        prog["title"] = title
    if source:
        prog["source"] = source
    return prog


# ---------------------------------------------------------------------------
# validation
# ---------------------------------------------------------------------------

def load_schema() -> Dict[str, Any]:
    with open(SCHEMA_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def validate_program(program: Dict[str, Any]) -> List[str]:
    """Return a list of problems (empty when valid): schema errors first, then referential ones."""
    problems: List[str] = []
    try:
        import jsonschema  # type: ignore

        v = jsonschema.Draft202012Validator(load_schema())
        for e in sorted(v.iter_errors(program), key=lambda e: list(e.path)):
            problems.append("/".join(str(p) for p in e.path) + ": " + e.message)
    except ImportError:  # pragma: no cover - minimal structural check without jsonschema
        for key in ("version", "canvas", "nodes", "flows"):
            if key not in program:
                problems.append(f"missing {key}")
    ids = {n["id"] for n in program.get("nodes", [])} | {c["id"] for c in program.get("containers", [])}
    if len(ids) != len(program.get("nodes", [])) + len(program.get("containers", [])):
        problems.append("duplicate element ids")
    for f in program.get("flows", []):
        for end in ("from", "to"):
            if f.get(end) not in ids and f.get(end) != "unknown":
                problems.append(f"flow {f.get('id')}: {end} {f.get(end)!r} is not a node or container id")
    for n in program.get("nodes", []):
        if n.get("parent") and n["parent"] not in ids:
            problems.append(f"node {n['id']}: parent {n['parent']!r} is not a container id")
    return problems


# ---------------------------------------------------------------------------
# program -> SVG through a Renderer
# ---------------------------------------------------------------------------

class Renderer(Protocol):
    """A design: turns the program's parts into SVG fragments. Ids must be preserved."""

    def begin(self, program: Dict[str, Any]) -> str: ...
    def container(self, c: Dict[str, Any]) -> str: ...
    def node(self, n: Dict[str, Any]) -> str: ...
    def flow(self, f: Dict[str, Any]) -> str: ...
    def end(self, program: Dict[str, Any]) -> str: ...


@dataclass
class HouseRenderer:
    """The reference design: the FigTree presets (paper, teaching, slide)."""

    preset_name: str = "teaching"

    @property
    def p(self) -> Preset:
        return PRESETS[self.preset_name]

    def begin(self, program: Dict[str, Any]) -> str:
        c = program["canvas"]
        pr = self.p
        st = pr.style
        icons = sorted({n["icon"] for n in program.get("nodes", []) if n.get("icon") in ICONS})
        syms = "".join(
            f'<symbol id="icon-{k}" viewBox="{ICON_VIEWBOX}" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{ICONS[k]}</symbol>'
            for k in icons
        )
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{c["width"]}" height="{c["height"]}" viewBox="0 0 {c["width"]} {c["height"]}" '
            f'font-family="{_esc(st.font)}" data-figtree="1" data-contract="{VERSION}">'
            + (f"<title>{_esc(program['title'])}</title>" if program.get("title") else "")
            + f'<rect id="background" x="0" y="0" width="{c["width"]}" height="{c["height"]}" fill="#FFFFFF" data-role="background"/>'
            + f'<defs><marker id="figtree-arrow" markerWidth="{pr.marker_w}" markerHeight="{_num(pr.marker_h)}" refX="{pr.marker_w}" refY="{_num(pr.marker_h / 2)}" orient="auto" markerUnits="userSpaceOnUse">'
            + f'<path d="M0,0 L{pr.marker_w},{_num(pr.marker_h / 2)} L0,{_num(pr.marker_h)} z" fill="{st.palette["border"]}"/></marker>{syms}</defs>'
            + f'<g id="figure" data-bbox="0 0 {c["width"]} {c["height"]}">'
        )

    def container(self, c: Dict[str, Any]) -> str:
        pr = self.p
        b = c["bbox"]
        if c.get("boxed") is False:
            return f'<g id="{_esc(c["id"])}" data-role="group" data-bbox="{_num(b["x"])} {_num(b["y"])} {_num(b["w"])} {_num(b["h"])}"/>'
        dash = f' stroke-dasharray="{pr.container_dash}"' if pr.container_dash else ""
        out = (
            f'<g id="{_esc(c["id"])}" data-role="container" data-bbox="{_num(b["x"])} {_num(b["y"])} {_num(b["w"])} {_num(b["h"])}">'
            f'<rect id="{_esc(c["id"])}.box" x="{_num(b["x"])}" y="{_num(b["y"])}" width="{_num(b["w"])}" height="{_num(b["h"])}" rx="{pr.container_rx}" '
            f'fill="{pr.container_fill}" stroke="{pr.container_stroke}" stroke-width="{_num(pr.style.stroke_border)}"{dash} data-role="container"/>'
        )
        if c.get("title"):
            size = int(pr.style.font_size_annot.split("-")[0].rstrip("pt")) + 1
            out += f'<text id="{_esc(c["id"])}.title" x="{_num(b["x"] + 12)}" y="{_num(b["y"] + 8 + size)}" font-size="{size}" fill="{pr.title_color}" data-kind="title">{_esc(c["title"])}</text>'
        return out + "</g>"

    def node(self, n: Dict[str, Any]) -> str:
        pr = self.p
        st = pr.style
        b = n["bbox"]
        kind = n.get("kind", "block")
        fill = st.palette.get(n.get("tone", "processing"), st.palette["processing"])
        size = int(st.font_size_label.split("-")[0].rstrip("pt"))
        il, ir = text_inset(kind)
        icon = n.get("icon") if n.get("icon") in ICONS else None
        isz = 16 if b["h"] < 56 else 20
        if kind == "block":
            shape = f'<rect id="{_esc(n["id"])}.block" x="{_num(b["x"])}" y="{_num(b["y"])}" width="{_num(b["w"])}" height="{_num(b["h"])}" rx="{pr.block_rx}" fill="{fill}" stroke="{st.palette["border"]}" stroke-width="{_num(st.stroke_main)}" data-role="block" data-kind="block"/>'
        else:
            shape = f'<path id="{_esc(n["id"])}.block" d="{shape_path(kind, int(b["w"]), int(b["h"]))}" transform="translate({_num(b["x"])},{_num(b["y"])})" fill="{"none" if kind == "actor" else fill}" stroke="{st.palette["border"]}" stroke-width="{_num(st.stroke_main)}" stroke-linejoin="round" data-role="block" data-kind="{kind}"/>'
        if icon:
            ix, iy = b["x"] + il + 8, b["y"] + (b["h"] - isz) / 2
            shape += f'<use id="{_esc(n["id"])}.icon" href="#icon-{icon}" x="{_num(ix)}" y="{_num(iy)}" width="{isz}" height="{isz}" color="{pr.icon_color}" data-role="icon"/>'
            tx, anchor = b["x"] + il + 8 + isz + 8, "start"
            maxw = b["w"] - il - ir - isz - 24
        else:
            tx, anchor = b["x"] + il + (b["w"] - il - ir) / 2, "middle"
            maxw = b["w"] - il - ir - 8
        ty = b["y"] + b["h"] + size if kind == "actor" else b["y"] + b["h"] / 2
        shape += (
            f'<text id="{_esc(n["id"])}.label" x="{_num(tx)}" y="{_num(ty)}" font-size="{size}" text-anchor="{anchor}" dominant-baseline="middle" '
            f'fill="{pr.label_color}" data-kind="label" data-max-width="{_num(maxw)}">{_esc(n["label"])}</text>'
        )
        return f'<g id="{_esc(n["id"])}" data-bbox="{_num(b["x"])} {_num(b["y"])} {_num(b["w"])} {_num(b["h"])}" data-label="{_esc(n["label"])}">{shape}</g>'

    def flow(self, f: Dict[str, Any]) -> str:
        st = self.p.style
        d = " ".join(("M" if i == 0 else "L") + f"{_num(x)},{_num(y)}" for i, (x, y) in enumerate(f["points"]))
        t = f.get("type", "data")
        dash = ' stroke-dasharray="6 4"' if t != "data" else ""
        stroke = "#9A9A9A" if t == "control" else st.palette["border"]
        head = "" if f.get("head") is False else ' marker-end="url(#figtree-arrow)"'
        out = (
            f'<path id="{_esc(f["id"])}" d="{d}" fill="none" stroke="{stroke}" stroke-width="{_num(st.stroke_main)}"{dash}{head} '
            f'data-flow="{t}" data-from="{_esc(f["from"])}" data-to="{_esc(f["to"])}"/>'
        )
        if f.get("label"):
            pts = f["points"]
            best = max(range(1, len(pts)), key=lambda i: abs(pts[i][0] - pts[i - 1][0]) + abs(pts[i][1] - pts[i - 1][1]))
            lx, ly = (pts[best][0] + pts[best - 1][0]) / 2, (pts[best][1] + pts[best - 1][1]) / 2 - 6
            size = int(st.font_size_annot.split("-")[0].rstrip("pt"))
            out += f'<text id="{_esc(f["id"])}.label" x="{_num(lx)}" y="{_num(ly)}" font-size="{size}" text-anchor="middle" fill="{self.p.title_color}" data-kind="annot">{_esc(f["label"])}</text>'
        return out

    def end(self, program: Dict[str, Any]) -> str:
        return "</g></svg>"


def render_program(program: Dict[str, Any], renderer: Optional[Renderer] = None) -> str:
    """Render a program to SVG through a design. Containers first (outer to inner), nodes, flows."""
    r = renderer or HouseRenderer(program.get("canvas", {}).get("preset") or "teaching")
    parts = [r.begin(program)]
    for c in sorted(program.get("containers", []), key=lambda c: c.get("depth", 0)):
        parts.append(r.container(c))
    for n in program.get("nodes", []):
        parts.append(r.node(n))
    for f in program.get("flows", []):
        parts.append(r.flow(f))
    parts.append(r.end(program))
    return "".join(parts)


def main(argv: List[str]) -> int:
    import argparse

    ap = argparse.ArgumentParser(prog="figtree contract", description="FigureProgram contract: export an SVG to program JSON, validate, or render a program through a design")
    sub = ap.add_subparsers(dest="cmd", required=True)
    ex = sub.add_parser("export", help="SVG -> program JSON")
    ex.add_argument("svg")
    ex.add_argument("-o", "--output", required=True)
    ex.add_argument("--title", default="")
    ex.add_argument("--source", default="")
    va = sub.add_parser("validate", help="check a program JSON against the schema")
    va.add_argument("program")
    re_ = sub.add_parser("render", help="program JSON -> SVG through the house renderer")
    re_.add_argument("program")
    re_.add_argument("-o", "--output", required=True)
    re_.add_argument("--preset", choices=sorted(PRESETS), default=None)
    a = ap.parse_args(argv)
    if a.cmd == "export":
        with open(a.svg, encoding="utf-8") as fh:
            prog = program_from_svg(fh.read(), title=a.title, source=a.source)
        probs = validate_program(prog)
        with open(a.output, "w", encoding="utf-8") as fh:
            json.dump(prog, fh, indent=2)
        print(f"wrote {a.output}: {len(prog['nodes'])} nodes, {len(prog['containers'])} containers, {len(prog['flows'])} flows; {'valid' if not probs else str(len(probs)) + ' problems'}")
        for p in probs:
            print("  -", p)
        return 0 if not probs else 1
    with open(a.program, encoding="utf-8") as fh:
        prog = json.load(fh)
    probs = validate_program(prog)
    if a.cmd == "validate":
        print("valid" if not probs else "\n".join(probs))
        return 0 if not probs else 1
    if probs:
        print("\n".join(probs))
        return 1
    svg = render_program(prog, HouseRenderer(a.preset) if a.preset else None)
    with open(a.output, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"wrote {a.output}")
    return 0

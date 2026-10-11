"""Editability proof: a local edit must change only the intended element(s)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from figtree.geometry import final_segment_length, path_hits_boxes, points_to_path, route
from figtree.schemas import BBox
from figtree.svgmodel import MARKER_ID, extract_bboxes, extract_ports, iter_elements, local, parse_svg


@dataclass
class EditabilityProof:
    passed: bool
    diff_element_count: int
    changed: List[str] = field(default_factory=list)
    edit: Dict[str, Any] = field(default_factory=dict)
    ports_valid: bool = True
    bboxes_valid: bool = True
    requires_remerge: bool = False
    note: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "diff_element_count": self.diff_element_count,
            "changed": list(self.changed),
            "edit": dict(self.edit),
            "ports_valid": self.ports_valid,
            "bboxes_valid": self.bboxes_valid,
            "requires_remerge": self.requires_remerge,
            "note": self.note,
        }


def _signature_map(svg_text: str) -> Dict[str, str]:
    """Map element key -> canonical serialisation (ids when present, path otherwise)."""
    root = parse_svg(svg_text)
    out: Dict[str, str] = {}
    counters: Dict[str, int] = {}

    def walk(el, path: str) -> None:
        for child in list(el):
            tag = local(child.tag)
            if tag == "comment":
                key = f"{path}/comment:{(child.text or '').strip()}"
                out[key] = "comment"
                continue
            cid = child.get("id")
            if cid:
                key = f"#{cid}"
            else:
                counters[f"{path}/{tag}"] = counters.get(f"{path}/{tag}", 0) + 1
                key = f"{path}/{tag}[{counters[f'{path}/{tag}']}]"
            attrs = " ".join(f'{k}="{v}"' for k, v in sorted(child.attrib.items()) if k != "data-_abs")
            text = "".join(t.strip() for t in child.itertext()) if tag in ("text", "tspan", "title") else ""
            out[key] = f"<{tag} {attrs}>{text}"
            if tag in ("g", "svg", "defs"):
                walk(child, key)

    walk(root, "")
    return out


def element_diff(before: str, after: str) -> List[str]:
    a, b = _signature_map(before), _signature_map(after)
    changed = [k for k in b if k not in a or a[k] != b[k]]
    changed += [k for k in a if k not in b]
    return changed


def _find_port(ports: List[dict], component: str, side: str) -> Optional[dict]:
    """Find a port by component name (exact, else unique prefix such as "Critic" for "Critic Agent")."""
    want = component.lower()
    exact = [p for p in ports if p["component"].lower() == want and p["side"] == side]
    if exact:
        return exact[0]
    loose = {p["component"]: p for p in ports if p["side"] == side and p["component"].lower().startswith(want + " ")}
    if len(loose) == 1:
        return next(iter(loose.values()))
    return None


def apply_local_edit(svg_text: str, edit: Dict[str, Any]) -> Tuple[str, bool]:
    """Apply a local edit.  Returns ``(new_svg, requires_remerge)``.

    Supported edits:
      {"op": "recolor", "component": "Critic", "fill": "#F4A460"}
      {"op": "add_dashed_arrow", "from": "Critic", "to": "Generator"}
    """
    op = edit.get("op")
    if op == "recolor":
        comp = re.escape(edit.get("component", ""))
        fill = edit.get("fill", "#F4A460")
        alternates = ["#F4A460", "#7BA3C9", "#FFF3CD", "#D5D5D5"]

        def repl(m):
            new_fill = fill if m.group(2).upper() != fill.upper() else next(a for a in alternates if a.upper() != m.group(2).upper())
            return m.group(1) + new_fill + m.group(3)

        pattern = re.compile(rf'(<(?:rect|path) [^>]*?fill=")([^"]*)("[^>]*data-component="{comp}"[^>]*/>)')
        new, n = pattern.subn(repl, svg_text, count=1)
        if n == 0:  # fall back to the first block
            pattern = re.compile(r'(<(?:rect|path) [^>]*?fill=")([^"]*)("[^>]*data-role="block"[^>]*/>)')
            new, n = pattern.subn(repl, svg_text, count=1)
        return new, False
    if op == "add_dashed_arrow":
        ports = extract_ports(svg_text)
        src = _find_port(ports, edit["from"], edit.get("from_side", "bottom"))
        dst = _find_port(ports, edit["to"], edit.get("to_side", "bottom"))
        if src is None or dst is None:
            return svg_text, False
        root = parse_svg(svg_text)
        H = int(float(root.get("height", 0)))
        W = int(float(root.get("width", 0)))
        bboxes = extract_bboxes(svg_text)
        root_id = next(iter(bboxes))
        # leaf blocks (absolute) are the obstacles; candidate routes are tried in order
        blocks: List[BBox] = []
        for el, off in iter_elements(root):
            if local(el.tag) == "rect" and el.get("data-role") == "block":
                blocks.append(BBox(int(float(el.get("x", 0))) + off[0], int(float(el.get("y", 0))) + off[1], int(float(el.get("width", 0))), int(float(el.get("height", 0)))))

        def port(comp: str, side: str) -> Optional[dict]:
            return _find_port(ports, comp, side)

        sb, db = port(edit["from"], "bottom"), port(edit["to"], "bottom")
        st, dt = port(edit["from"], "top"), port(edit["to"], "top")
        sr, dl = port(edit["from"], "right"), port(edit["to"], "left")
        sl, dr = port(edit["from"], "left"), port(edit["to"], "right")
        lo, hi = sorted((src["abs_x"], dst["abs_x"]))
        spanned = [b for k, b in bboxes.items() if k != root_id and b.x <= hi and b.x2 >= lo]
        y_bus = max((b.y2 for b in spanned), default=max(src["abs_y"], dst["abs_y"])) + 16
        y_top = min((b.y for b in spanned), default=min(src["abs_y"], dst["abs_y"])) - 16
        candidates = []
        if sb and db:
            candidates.append(([(sb["abs_x"], sb["abs_y"]), (sb["abs_x"], y_bus), (db["abs_x"], y_bus), (db["abs_x"], db["abs_y"])], sb, db))
        if st and dt:
            candidates.append(([(st["abs_x"], st["abs_y"]), (st["abs_x"], y_top), (dt["abs_x"], y_top), (dt["abs_x"], dt["abs_y"])], st, dt))
        if sb and dl:  # left-margin lane
            candidates.append(([(sb["abs_x"], sb["abs_y"]), (sb["abs_x"], y_bus), (8, y_bus), (8, dl["abs_y"]), (dl["abs_x"], dl["abs_y"])], sb, dl))
        if sr and dr:  # right-margin lane
            candidates.append(([(sr["abs_x"], sr["abs_y"]), (W - 8, sr["abs_y"]), (W - 8, dr["abs_y"]), (dr["abs_x"], dr["abs_y"])], sr, dr))

        def clean(pts: List[Tuple[int, int]]) -> bool:
            ends = {pts[0], pts[-1]}
            obstacles = [b for b in blocks if not any(b.contains_point(x, y, strict=False) for x, y in ends)]
            return not path_hits_boxes(pts, obstacles) and final_segment_length(pts) >= 20

        chosen = next((c for c in candidates if clean(c[0])), candidates[0] if candidates else None)
        if chosen is None:
            return svg_text, False
        pts, src, dst = chosen
        # a lane in the padding zone keeps the edit local but means the parent should re-space
        requires_remerge = any(x < 24 or x > W - 24 or y < 24 or y > H - 24 for x, y in pts[1:-1])
        path = (
            f'<path id="edit.arrow" d="{points_to_path(pts)}" fill="none" stroke="#333333" stroke-width="1.2" '
            f'data-flow="control" stroke-dasharray="4 2" marker-end="url(#{MARKER_ID})" '
            f'data-from="{src["id"]}" data-to="{dst["id"]}" data-edit="residual"/>'
        )
        # insert as the last child of the root group (absolute frame)
        new = svg_text.replace("  </g>\n</svg>", f"    {path}\n  </g>\n</svg>", 1)
        return new, requires_remerge
    raise ValueError(f"unknown edit op {op!r}")


def validate_structure(svg_text: str) -> Tuple[bool, bool]:
    """Return ``(ports_valid, bboxes_valid)`` from the ports and bboxes embedded in the SVG."""
    ports = extract_ports(svg_text)
    # a port id re-exported at several tree levels must resolve to one absolute position
    positions: Dict[str, set] = {}
    for p in ports:
        positions.setdefault(p["id"], set()).add((p["abs_x"], p["abs_y"]))
    ports_valid = all(len(v) == 1 for v in positions.values()) and all(p["abs_x"] >= 0 and p["abs_y"] >= 0 for p in ports)
    bboxes = extract_bboxes(svg_text)
    root = parse_svg(svg_text)
    W = int(float(root.get("width", 0)))
    H = int(float(root.get("height", 0)))
    # sibling groups must not overlap; every bbox must stay inside the canvas
    parent_of: Dict[str, str] = {}

    def walk(el, parent: str) -> None:
        for child in list(el):
            if local(child.tag) == "g" and child.get("data-bbox"):
                parent_of[child.get("id")] = parent
                walk(child, child.get("id"))
            elif local(child.tag) in ("g", "svg"):
                walk(child, parent)

    walk(root, "root")
    bboxes_valid = all(0 <= b.x and 0 <= b.y and b.x2 <= W and b.y2 <= H for b in bboxes.values())
    items = list(bboxes.items())
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (ia, ba), (ib, bb) = items[i], items[j]
            if parent_of.get(ia) == parent_of.get(ib) and ba.intersects(bb):
                bboxes_valid = False
    return ports_valid, bboxes_valid


def prove_editability(svg_text: str, edit: Dict[str, Any]) -> EditabilityProof:
    try:
        edited, remerge = apply_local_edit(svg_text, edit)
    except Exception as exc:  # noqa: BLE001
        return EditabilityProof(False, 0, edit=edit, note=f"edit failed: {exc}")
    changed = element_diff(svg_text, edited)
    ports_ok, bboxes_ok = validate_structure(edited)
    intended = 1
    passed = len(changed) == intended and ports_ok and bboxes_ok and bool(changed)
    note = "" if passed else ("no element changed" if not changed else f"{len(changed)} elements changed")
    return EditabilityProof(passed, len(changed), changed, edit, ports_ok, bboxes_ok, remerge, note)

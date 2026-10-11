"""Editability proof: a local edit must change only the intended element(s)."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from figtree.geometry import points_to_path, route
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
        pattern = re.compile(rf'(<rect [^>]*?fill=")([^"]*)("[^>]*data-component="{comp}"[^>]*/>)')
        new, n = pattern.subn(lambda m: m.group(1) + fill + m.group(3), svg_text, count=1)
        if n == 0:  # fall back to the first block
            pattern = re.compile(r'(<rect [^>]*?fill=")([^"]*)("[^>]*data-role="block"[^>]*/>)')
            new, n = pattern.subn(lambda m: m.group(1) + fill + m.group(3), svg_text, count=1)
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
        max_bottom = max((b.y2 for k, b in bboxes.items() if k != next(iter(bboxes))), default=0)
        s = (src["abs_x"], src["abs_y"])
        d = (dst["abs_x"], dst["abs_y"])
        y = max_bottom + 16
        pts = [s, (s[0], y), (d[0], y), d]
        requires_remerge = y + 24 > H or any(x < 0 or x > W for x, _ in pts)
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

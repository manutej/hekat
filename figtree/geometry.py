"""Grid snapping and right-angle routing primitives."""

from __future__ import annotations

import math
from typing import Iterable, List, Sequence, Tuple

from figtree.schemas import BBox, Port

Point = Tuple[int, int]


def ceil_to_grid(v: float, grid: int = 8) -> int:
    """Ceil-snap ``v`` to a multiple of ``grid``."""
    if grid <= 0:
        return int(math.ceil(v))
    return int(math.ceil(v / grid - 1e-9) * grid)


def round_to_grid(v: float, grid: int = 8) -> int:
    if grid <= 0:
        return int(round(v))
    return int(round(v / grid) * grid)


def on_grid(v: float, grid: int = 8) -> bool:
    return abs(v / grid - round(v / grid)) < 1e-9


def manhattan(a: Point, b: Point) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def segments(points: Sequence[Point]) -> List[Tuple[Point, Point]]:
    return [(points[i], points[i + 1]) for i in range(len(points) - 1)]


def is_orthogonal(points: Sequence[Point]) -> bool:
    return all(a[0] == b[0] or a[1] == b[1] for a, b in segments(points))


def final_segment_length(points: Sequence[Point]) -> int:
    """Length of the last segment (the shaft that carries the arrow marker)."""
    if len(points) < 2:
        return 0
    (x1, y1), (x2, y2) = points[-2], points[-1]
    return abs(x2 - x1) + abs(y2 - y1)


def terminal_direction(points: Sequence[Point]) -> Point:
    """Unit direction of the final segment, e.g. (1, 0) for a right-pointing arrow."""
    (x1, y1), (x2, y2) = points[-2], points[-1]
    dx, dy = x2 - x1, y2 - y1
    return (int(math.copysign(1, dx)) if dx else 0, int(math.copysign(1, dy)) if dy else 0)


def segment_hits_box(a: Point, b: Point, box: BBox) -> bool:
    """True if the orthogonal segment a->b passes through the interior of ``box``."""
    (x1, y1), (x2, y2) = a, b
    if y1 == y2:  # horizontal
        if not (box.y < y1 < box.y2):
            return False
        lo, hi = sorted((x1, x2))
        return lo < box.x2 and hi > box.x
    if x1 == x2:  # vertical
        if not (box.x < x1 < box.x2):
            return False
        lo, hi = sorted((y1, y2))
        return lo < box.y2 and hi > box.y
    return True  # diagonal: treat as a hit


def path_hits_boxes(points: Sequence[Point], boxes: Iterable[BBox]) -> List[BBox]:
    hits = []
    for box in boxes:
        if any(segment_hits_box(a, b, box) for a, b in segments(points)):
            hits.append(box)
    return hits


def route(
    src: Point,
    dst: Point,
    src_side: str,
    dst_side: str,
    grid: int = 8,
    detour: int = 0,
) -> List[Point]:
    """Right-angle route from ``src`` (leaving via ``src_side``) to ``dst`` (entering ``dst_side``).

    ``detour`` offsets the free coordinate of the mid segment; it is used to route over or
    under blocks and to separate parallel detours.
    """
    sx, sy = src
    dx, dy = dst
    if src_side == "right" and dst_side == "left":
        if sy == dy:
            return [src, dst]
        midx = round_to_grid((sx + dx) / 2, grid)
        return [src, (midx, sy), (midx, dy), dst]
    if src_side == "bottom" and dst_side == "top":
        if sx == dx:
            return [src, dst]
        midy = round_to_grid((sy + dy) / 2, grid)
        return [src, (sx, midy), (dx, midy), dst]
    if src_side == "top" and dst_side == "top":
        # over-the-top detour: rise above both ports then drop into the target
        y = round_to_grid(min(sy, dy) - detour, grid)
        return [src, (sx, y), (dx, y), dst]
    if src_side == "bottom" and dst_side == "bottom":
        y = round_to_grid(max(sy, dy) + detour, grid)
        return [src, (sx, y), (dx, y), dst]
    if src_side == "right" and dst_side == "right":
        x = round_to_grid(max(sx, dx) + detour, grid)
        return [src, (x, sy), (x, dy), dst]
    if src_side == "left" and dst_side == "left":
        x = round_to_grid(min(sx, dx) - detour, grid)
        return [src, (x, sy), (x, dy), dst]
    # generic fallback: L-route
    return [src, (dx, sy), dst] if sx != dx and sy != dy else [src, dst]


def points_to_path(points: Sequence[Point]) -> str:
    """Serialise an orthogonal polyline as an SVG path using only H/V commands."""
    (x0, y0) = points[0]
    parts = [f"M{x0},{y0}"]
    cx, cy = x0, y0
    for x, y in points[1:]:
        if y == cy and x != cx:
            parts.append(f"H{x}")
        elif x == cx and y != cy:
            parts.append(f"V{y}")
        elif x == cx and y == cy:
            continue
        else:  # diagonal (only when semantically required and flagged)
            parts.append(f"L{x},{y}")
        cx, cy = x, y
    return " ".join(parts)


def path_to_points(d: str) -> List[Point]:
    """Parse the H/V/L/M path syntax emitted by :func:`points_to_path`."""
    import re

    pts: List[Point] = []
    cx = cy = 0
    for cmd, args in re.findall(r"([MHVLmhvl])\s*([-\d.,\s]*)", d):
        nums = [float(n) for n in re.findall(r"-?\d+(?:\.\d+)?", args)]
        if cmd == "M" and len(nums) >= 2:
            cx, cy = int(nums[0]), int(nums[1])
            pts.append((cx, cy))
        elif cmd == "H" and nums:
            cx = int(nums[0])
            pts.append((cx, cy))
        elif cmd == "V" and nums:
            cy = int(nums[0])
            pts.append((cx, cy))
        elif cmd == "L" and len(nums) >= 2:
            cx, cy = int(nums[0]), int(nums[1])
            pts.append((cx, cy))
    return pts


def port_point(p: Port, offset: Point = (0, 0)) -> Point:
    return (p.rel_x + offset[0], p.rel_y + offset[1])

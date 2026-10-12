"""Grid router: an orthogonal A* that never crosses a block.

The worker's heuristic routes (direct, Z, gap bus, bracket) cover almost every arrow; when all
of them collide with a block or a label this router finds a path on the 8 px grid around every
obstacle, with a halo so shafts never graze a border.  Cells under earlier arrows cost extra, so
two arrows share a shaft only when nothing else is possible, and bends cost extra, so the path
stays a few straight segments.  The result is the orthogonal polyline the worker emits as-is.

This exists because "an arrow drawn through a block or across a label" was the one defect every
small-model run reproduced; the critic flags it (``flow.through_block``, ``flow.through_text``),
but a figure should never need a repair round for it.
"""

from __future__ import annotations

import heapq
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from figtree.schemas import BBox

Point = Tuple[int, int]
_DIRS = ((1, 0), (-1, 0), (0, 1), (0, -1))
_SIDE_DIR = {"right": (1, 0), "left": (-1, 0), "top": (0, -1), "bottom": (0, 1)}


def _cells_of_box(box: BBox, grid: int, halo: int) -> Set[Point]:
    x0 = (box.x - halo) // grid
    x1 = (box.x2 + halo) // grid
    y0 = (box.y - halo) // grid
    y1 = (box.y2 + halo) // grid
    return {(cx, cy) for cx in range(x0, x1 + 1) for cy in range(y0, y1 + 1)}


def _cells_of_path(points: Sequence[Point], grid: int) -> Set[Point]:
    out: Set[Point] = set()
    for (x1, y1), (x2, y2) in zip(points, points[1:]):
        if y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1, grid):
                out.add((x // grid, y1 // grid))
        else:
            for y in range(min(y1, y2), max(y1, y2) + 1, grid):
                out.add((x1 // grid, y // grid))
    return out


def _simplify(points: List[Point]) -> List[Point]:
    out: List[Point] = []
    for p in points:
        if len(out) >= 2:
            (ax, ay), (bx, by) = out[-2], out[-1]
            if (ax == bx == p[0]) or (ay == by == p[1]):
                out[-1] = p
                continue
        if not out or out[-1] != p:
            out.append(p)
    return out


def astar_route(
    src: Point,
    dst: Point,
    src_side: str,
    dst_side: str,
    obstacles: Iterable[BBox],
    bounds: BBox,
    grid: int = 8,
    halo: int = 4,
    taken: Iterable[Sequence[Point]] = (),
    min_shaft: int = 20,
    bend_cost: int = 3,
    shared_cost: int = 6,
    max_nodes: int = 60000,
    src_box: Optional[BBox] = None,
    dst_box: Optional[BBox] = None,
) -> Optional[List[Point]]:
    """Orthogonal path from ``src`` (leaving via ``src_side``) to ``dst`` (entering via ``dst_side``)
    on the ``grid`` that avoids every obstacle interior plus ``halo`` and keeps the final segment
    at least ``min_shaft`` long.  Returns None when no path exists inside ``bounds``."""
    blocked: Set[Point] = set()
    for b in obstacles:
        blocked |= _cells_of_box(b, grid, halo)
    # the arrow's own blocks are obstacles as well (a path must not loop back through its source
    # or slice its target); only the exit lane and the approach lane through the ports stay open
    for b in (src_box, dst_box):
        if b is not None:
            blocked |= _cells_of_box(b, grid, halo)
    busy: Dict[Point, int] = {}
    for path in taken:
        for c in _cells_of_path(path, grid):
            busy[c] = busy.get(c, 0) + 1
    sd, dd = _SIDE_DIR[src_side], _SIDE_DIR[dst_side]
    # the first and last cells: one grid step out of the source port, one step before the target port
    s_cell = (src[0] // grid + sd[0], src[1] // grid + sd[1])
    steps_in = max(1, (min_shaft + grid - 1) // grid)
    # dd points OUT of the target through its port; the approach lane lies that way, and the
    # path arrives travelling against dd
    d_cell = (dst[0] // grid + dd[0] * steps_in, dst[1] // grid + dd[1] * steps_in)
    approach = [(dst[0] // grid + dd[0] * k, dst[1] // grid + dd[1] * k) for k in range(0, steps_in + 1)]
    exit_lane = [(src[0] // grid + sd[0] * k, src[1] // grid + sd[1] * k) for k in range(0, steps_in + 1)]
    blocked -= set(approach)
    blocked -= set(exit_lane)
    blocked.discard(s_cell)
    bx0, bx1 = bounds.x // grid - 2, bounds.x2 // grid + 2
    by0, by1 = bounds.y // grid - 2, bounds.y2 // grid + 2

    def h(c: Point) -> int:
        return abs(c[0] - d_cell[0]) + abs(c[1] - d_cell[1])

    start = (s_cell, sd)
    best: Dict[Tuple[Point, Point], int] = {start: 0}
    came: Dict[Tuple[Point, Point], Tuple[Point, Point]] = {}
    heap: List[Tuple[int, int, Point, Point]] = [(h(s_cell), 0, s_cell, sd)]
    goal_dir = (-dd[0], -dd[1])  # the direction of travel when arriving at d_cell must be towards the port
    expanded = 0
    found: Optional[Tuple[Point, Point]] = None
    while heap:
        f, g, cell, d = heapq.heappop(heap)
        state = (cell, d)
        if best.get(state, 1 << 30) < g:
            continue
        if cell == d_cell and d == goal_dir:
            found = state
            break
        expanded += 1
        if expanded > max_nodes:
            return None
        for nd in _DIRS:
            if nd == (-d[0], -d[1]):
                continue  # no U-turns
            nxt = (cell[0] + nd[0], cell[1] + nd[1])
            if not (bx0 <= nxt[0] <= bx1 and by0 <= nxt[1] <= by1):
                continue
            if nxt in blocked and nxt != d_cell:
                continue
            cost = 1 + (bend_cost if nd != d else 0) + shared_cost * busy.get(nxt, 0)
            ng = g + cost
            ns = (nxt, nd)
            if ng < best.get(ns, 1 << 30):
                best[ns] = ng
                came[ns] = state
                heapq.heappush(heap, (ng + h(nxt), ng, nxt, nd))
    if found is None:
        return None
    cells: List[Point] = []
    cur: Optional[Tuple[Point, Point]] = found
    while cur is not None:
        cells.append(cur[0])
        cur = came.get(cur)
    cells.reverse()
    pts = [src] + [(c[0] * grid, c[1] * grid) for c in cells] + [dst]
    # the port points are not on the grid in general: align the first/last grid points with them
    pts[1] = (pts[1][0], src[1]) if src_side in ("left", "right") else (src[0], pts[1][1])
    pts[-2] = (pts[-2][0], dst[1]) if dst_side in ("left", "right") else (dst[0], pts[-2][1])
    return _simplify(pts)

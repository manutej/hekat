"""The grid router never crosses a block, keeps the shaft, and the worker falls back to it."""
from __future__ import annotations

from figtree.geometry import path_hits_boxes, final_segment_length, is_orthogonal
from figtree.router import astar_route
from figtree.schemas import BBox


def test_route_goes_around_a_wall_of_blocks():
    src, dst = (104, 48), (400, 48)  # right port of A at x=104, left port of B at x=400
    wall = [BBox(200, 0, 96, 96)]  # a block straddling the straight line
    bounds = BBox(0, -64, 520, 224)
    pts = astar_route(src, dst, "right", "left", wall, bounds, grid=8, halo=4, min_shaft=24)
    assert pts and pts[0] == src and pts[-1] == dst
    assert is_orthogonal(pts)
    assert path_hits_boxes(pts, wall) == []
    assert final_segment_length(pts) >= 24


def test_route_avoids_sharing_a_shaft_when_it_can():
    src, dst = (104, 48), (400, 48)
    bounds = BBox(0, -64, 520, 224)
    first = astar_route(src, dst, "right", "left", [], bounds, grid=8, min_shaft=24)
    assert first == [src, dst]
    # a second arrow between neighbouring ports prefers its own lane over the taken cells
    second = astar_route((104, 56), (400, 56), "right", "left", [], bounds, grid=8, min_shaft=24, taken=[first])
    assert second and path_hits_boxes(second, []) == []


def test_route_returns_none_when_boxed_in():
    src, dst = (104, 48), (400, 48)
    cage = [BBox(120, -100, 16, 400)]  # a wall taller than the bounds
    bounds = BBox(0, -64, 520, 224)
    assert astar_route(src, dst, "right", "left", cage, bounds, grid=8) is None


SPEC = """# Memory flows

## Components
- **Chat Input** (kind: terminal, icon: user): in.
- **Session ID** (kind: document, icon: text): the key.
- **Langflow Storage** (kind: store, icon: database): the store.
- **Agent** (kind: block, icon: gear): the actor.
- **Chat Output** (kind: terminal, icon: image): out.
- **Message History** (kind: block, icon: layers): reads messages.
- **Prompt Template** (kind: block, icon: edit-script): fills the memory variable.

## Flows
Chat Input → Agent → Chat Output
Session ID → Message History
Session ID → Agent
Langflow Storage → Message History
Langflow Storage → Agent
Message History → Prompt Template → Agent
Chat Output → Message History (feedback): stored in Store mode.
"""


def test_worker_output_has_no_arrow_through_a_block_or_label():
    from figtree.generator import RuleBasedGenerator
    from figtree.orchestrator import FigTree, Limits
    from figtree.quality import QualityCritic
    from figtree.styles import get_preset
    from figtree.worker import Worker

    ft = FigTree(limits=Limits(), render=False, generator=RuleBasedGenerator(icons=True, shapes=True),
                 worker=Worker(spacing_iterations=Limits().spacing_iterations, max_aspect=2.4))
    ft.style_override = get_preset("teaching").style
    svg = ft.run(SPEC).final_svg
    report = QualityCritic("teaching").review(svg)
    bad = [i for i in report.issues if i.check_id in ("flow.through_block", "flow.through_text")]
    assert bad == [], [i.visual_description for i in bad]

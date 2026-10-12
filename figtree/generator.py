"""Rule-based Generator agent: Decompose or Draw.

Decision (hard rule from the specification): a node is drawn as a leaf when its description
contains at most one named component and at most 40 tokens, OR depth >= 8, OR it is
explicitly marked leaf.  Otherwise it is decomposed into exactly 2-4 semantic children,
level by level.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Tuple, Dict, List, Optional, Sequence, Set

from figtree.geometry import ceil_to_grid
from figtree.ingest import to_noun_phrase
from figtree.schemas import Flow, GlobalStyle, Node, Port, ResidualDefect
from figtree.elements import kind_for, shape_path, text_inset
from figtree.icons import ICONS, icon_for
from figtree.svgmodel import Fragment, PathEl, RectEl, ShapeEl, TextEl, UseEl

MAX_DEPTH = 8
LEAF_TOKEN_LIMIT = 40

# semantic role -> palette key (paper: attention/key mechanism, normalisation/residual, embedding/input)
_ROLE_FILL = {
    "attention": ("attention", "critic", "review", "judge", "verif", "validat", "evaluat"),
    "residual": ("residual", "norm", "memory", "store", "sheaf", "cache"),
    "input": ("input", "embedding", "source", "token", "document", "query"),
}


def fill_for(name: str, palette: Dict[str, str]) -> str:
    n = name.lower()
    for role, words in _ROLE_FILL.items():
        if any(w in n for w in words):
            return palette[role]
    return palette["processing"]


def is_atomic(node: Node, max_depth: int = MAX_DEPTH) -> bool:
    if node.marked_leaf or node.depth >= max_depth:
        return True
    tokens = len(node.description.split())
    return len(node.components) <= 1 and tokens <= LEAF_TOKEN_LIMIT



def _connected_components(components: Sequence[str], flows: Sequence[Flow]) -> List[List[str]]:
    """Connected components of the undirected flow graph, largest first, each in reading order."""
    order = {c: i for i, c in enumerate(components)}
    adj: Dict[str, set] = {c: set() for c in components}
    for f in flows:
        if f.src in adj and f.dst in adj:
            adj[f.src].add(f.dst)
            adj[f.dst].add(f.src)
    seen: set = set()
    out: List[List[str]] = []
    for c in components:
        if c in seen:
            continue
        stack, cc = [c], []
        while stack:
            x = stack.pop()
            if x in seen:
                continue
            seen.add(x)
            cc.append(x)
            stack.extend(sorted(adj[x] - seen, key=lambda n: order[n]))
        out.append(sorted(cc, key=lambda n: order[n]))
    return sorted(out, key=lambda cc: (-len(cc), order[cc[0]]))


def _satellites(components: Sequence[str], flows: Sequence[Flow]) -> List[Tuple[str, List[str]]]:
    """``[(source, [targets...])]``: targets reached only from ``source`` by control flows, with no
    outgoing flows, at least two per source (an agent's tools, a router's branches)."""
    comps = list(components)
    incoming: Dict[str, List[Flow]] = {c: [] for c in comps}
    outgoing: Dict[str, int] = {c: 0 for c in comps}
    for f in flows:
        if f.dst in incoming:
            incoming[f.dst].append(f)
        if f.src in outgoing:
            outgoing[f.src] += 1
    by_src: Dict[str, List[str]] = {}
    for c in comps:
        ins = incoming[c]
        if len(ins) == 1 and ins[0].type == "control" and outgoing[c] == 0 and ins[0].src != c:
            by_src.setdefault(ins[0].src, []).append(c)
    return [(src, ts) for src, ts in by_src.items() if len(ts) >= 2]


def _layers(components: Sequence[str], flows: Sequence[Flow]) -> List[List[str]]:
    """Longest-path layering of the components restricted to ``flows`` (back-edges ignored)."""
    comp = list(components)
    index = {c: i for i, c in enumerate(comp)}
    succ: Dict[str, List[str]] = {c: [] for c in comp}
    indeg: Dict[str, int] = {c: 0 for c in comp}
    # drop back-edges (edges from later to earlier in a DFS order) to make a DAG
    edges = [(f.src, f.dst) for f in flows if f.src in index and f.dst in index]
    adj: Dict[str, List[str]] = {c: [] for c in comp}
    for a, b in edges:
        adj[a].append(b)
    state: Dict[str, int] = {}
    kept: List[tuple] = []

    def dfs(u: str) -> None:
        state[u] = 1
        for v in adj[u]:
            if state.get(v, 0) == 0:
                kept.append((u, v))
                dfs(v)
            elif state[v] == 2:
                kept.append((u, v))
        state[u] = 2

    raw_indeg = {c: 0 for c in comp}
    for _, b in edges:
        raw_indeg[b] += 1
    # start the DFS from sources so that feedback edges (not forward edges) become back-edges
    for c in sorted(comp, key=lambda c: (raw_indeg[c] != 0, index[c])):
        if state.get(c, 0) == 0:
            dfs(c)
    for a, b in kept:
        succ[a].append(b)
        indeg[b] += 1
    layer: Dict[str, int] = {}
    queue = [c for c in comp if indeg[c] == 0]
    for c in queue:
        layer[c] = 0
    while queue:
        u = queue.pop(0)
        for v in succ[u]:
            layer[v] = max(layer.get(v, 0), layer[u] + 1)
            indeg[v] -= 1
            if indeg[v] == 0:
                queue.append(v)
    for c in comp:
        layer.setdefault(c, 0)
    n_layers = max(layer.values()) + 1 if layer else 0
    out: List[List[str]] = [[] for _ in range(n_layers)]
    for c in comp:
        out[layer[c]].append(c)
    return [l for l in out if l]


def _order_layers(layers: List[List[str]], flows: Sequence[Flow]) -> List[List[str]]:
    """Barycenter ordering: each layer sorted by the mean position of its sources in the previous
    layer, so arrows between adjacent layers do not cross (the Sugiyama ordering step)."""
    out: List[List[str]] = [list(layers[0])] if layers else []
    for i in range(1, len(layers)):
        prev = {c: k for k, c in enumerate(out[i - 1])}
        def key(c: str) -> float:
            srcs = [prev[f.src] for f in flows if f.dst == c and f.src in prev]
            return sum(srcs) / len(srcs) if srcs else float(layers[i].index(c))
        out.append(sorted(layers[i], key=key))
    return out


def _chunk(items: List[List[str]], k: int) -> List[List[str]]:
    """Group consecutive layers into ``k`` contiguous groups of balanced size."""
    total = sum(len(l) for l in items)
    target = total / k
    groups: List[List[str]] = []
    cur: List[str] = []
    for i, layer in enumerate(items):
        remaining_groups = k - len(groups)
        if cur and len(cur) + len(layer) > target and remaining_groups > 1 and len(items) - i >= remaining_groups:
            groups.append(cur)
            cur = []
        cur.extend(layer)
    if cur:
        groups.append(cur)
    while len(groups) > k:  # merge smallest neighbours
        i = min(range(len(groups) - 1), key=lambda j: len(groups[j]) + len(groups[j + 1]))
        groups[i : i + 2] = [groups[i] + groups[i + 1]]
    return groups


@dataclass
class RuleBasedGenerator:
    """Deterministic Decompose/Draw.  ``faults`` injects defects for critic-loop testing.

    ``icons`` places a library icon inside each block; ``shapes`` draws stores, documents,
    decisions, terminals and actors with their conventional silhouettes instead of plain
    rectangles.
    """

    faults: Set[str] = field(default_factory=set)
    max_depth: int = MAX_DEPTH
    icons: bool = False
    shapes: bool = False

    # -- Decompose -------------------------------------------------------
    def decompose(self, node: Node, next_id) -> List[Node]:
        comps = list(node.components)
        # satellites: two or more sinks that one node reaches by control flows and nothing else
        # reaches (an agent's tools, a router's branches) become one child of their own, so they
        # sit beside the main chain instead of being chunked into the chain's last layer
        # disconnected mechanisms (a spec that documents several independent chains) are drawn as
        # separate sub-figures: one child per connected component of the flow graph
        ccs = _connected_components(comps, node.flows)
        # (only when every component is small enough to be laid out as one row at depth 1,
        # where the worker does not fold rows; a large chain keeps the layer chunking below)
        if 2 <= len(ccs) <= 4 and len(comps) > 4 and node.depth == 0 and max(len(cc) for cc in ccs) <= 6:
            groups = [list(cc) for cc in ccs]
            return [
                Node(id=next_id(), parent_id=node.id, description=to_noun_phrase(", ".join(g)), depth=node.depth + 1,
                     style=node.style, components=list(g), flows=[f for f in node.flows if f.src in set(g) and f.dst in set(g)])
                for g in groups
            ]
        sats = _satellites(comps, node.flows)
        sat_targets = {t for _, ts in sats for t in ts}
        core = [c for c in comps if c not in sat_targets]
        core_flows = [f for f in node.flows if f.src in core and f.dst in core]
        layers = _order_layers(_layers(core, core_flows), core_flows)
        core = [c for layer in layers for c in layer]  # reading order follows the layering
        budget = max(1, 4 - len(sats))  # at most four children per split
        if len(core) <= budget:
            groups = [[c] for c in core]
        else:
            # one group per layer when there are 2-4 layers, else balance into the budget
            k = min(budget, max(2, len(layers)))
            groups = _chunk(layers, k)
            if len(groups) < 2 and len(core) > 1:  # single big layer (parallel block): split the layer itself
                half = (len(core) + 1) // 2
                groups = [core[:half], core[half:]]
        groups = [g for g in groups if g]
        # the satellite groups follow their source in reading order
        for src, ts in sats:
            at = next((i for i, g in enumerate(groups) if src in g), len(groups) - 1)
            groups.insert(at + 1, list(ts))
        children: List[Node] = []
        for g in groups:
            gset = set(g)
            internal = [f for f in node.flows if f.src in gset and f.dst in gset]
            child = Node(
                id=next_id(),
                parent_id=node.id,
                description=to_noun_phrase(", ".join(g)),
                depth=node.depth + 1,
                style=node.style,
                components=list(g),
                flows=internal,
            )
            children.append(child)
        return children

    # -- Draw ------------------------------------------------------------
    def draw(self, node: Node) -> Fragment:
        style = node.style
        grid = style.grid
        label_size = style.label_size
        if "wrong-font-size" in self.faults:
            label_size = 16
        names = node.components or [node.description or node.id]
        lines = [n for n in names]
        longest = max(lines, key=len)
        text_w = int(round(len(longest) * label_size * 0.5))
        from figtree.styles import PRESETS

        pr = PRESETS.get(getattr(style, "preset", "paper")) or PRESETS["paper"]
        hint = (getattr(self, "hints", None) or {}).get(names[0], {})
        kind = kind_for(names[0], hint.get("kind", "")) if (self.shapes or hint.get("kind")) else "block"
        icon = (hint.get("icon") if hint.get("icon") in ICONS else None) or (icon_for(names[0]) if self.icons else None)
        if kind == "actor":
            # a person is drawn as a pill with the user glyph: the silhouette shape has no room for a
            # label inside its bbox and collides with the icon
            kind, icon = "terminal", (icon or "user")
        inset_l, inset_r = text_inset(kind)
        icon_w = 20 if icon else 0  # glyph at x=8..24, label from x=32: 20px more than a plain block
        # compact academic blocks (paper: ~60-100px wide, 20-30px tall); 8-grid forces 32 tall
        w = ceil_to_grid(max(64, text_w + 2 * 12 + inset_l + inset_r + icon_w), 2 * grid)
        h = ceil_to_grid(max(32 if kind not in ("decision", "actor") else 48, int(label_size * 1.2) * len(lines) + 2 * 8), 2 * grid)
        if "ungrid" in self.faults:
            w += 3
        fill = fill_for(names[0], style.palette)
        if "gradient" in self.faults:
            fill = "url(#fake-gradient)"
        if kind == "block":
            rect = RectEl(
                id=f"{node.id}.block",
                x=0,
                y=0,
                w=w,
                h=h,
                fill=fill,
                stroke=style.palette["border"],
                stroke_width=style.stroke_main,
                role="block",
                rx=pr.block_rx,
                extra={"data-component": names[0]},
            )
        else:
            rect = ShapeEl(
                id=f"{node.id}.block",
                kind=kind,
                x=0,
                y=0,
                w=w,
                h=h,
                fill=fill if kind != "actor" else "none",
                stroke=style.palette["border"],
                stroke_width=style.stroke_main,
                extra={"data-component": names[0]},
            )
        if icon:  # a constant 8px gap after the glyph: label starts at x=32
            text_x, anchor = 32 + inset_l, "start"
        else:
            text_x = (w + inset_l - inset_r) // 2
            text_x = ceil_to_grid(text_x, grid) if text_x % grid else text_x
            anchor = "middle"
        text = TextEl(
            id=f"{node.id}.label",
            x=text_x,
            y=h // 2,
            text=lines[0],
            size=label_size,
            kind="label",
            font=style.font,
            anchor=anchor,
            fill=pr.label_color,
            max_width=w - icon_w - inset_l - inset_r,
            lines=lines if len(lines) > 1 else [],
        )
        if "text-overflow" in self.faults:
            rect.w = w = ceil_to_grid(text_w // 2, 2 * grid)
            text.x = w // 2
            text.max_width = w
        comp = names[0]
        nid = node.id
        ports = [
            Port(id=f"{nid}.left", side="left", rel_x=0, rel_y=h // 2, type="input", component=comp),
            Port(id=f"{nid}.right", side="right", rel_x=w, rel_y=h // 2, type="output", component=comp),
            Port(id=f"{nid}.top", side="top", rel_x=w // 2, rel_y=0, type="input", component=comp),
            Port(id=f"{nid}.bottom", side="bottom", rel_x=w // 2, rel_y=h, type="output", component=comp),
        ]
        # a forced multi-component leaf still exposes a port per component (same block edge)
        for k, extra_comp in enumerate(names[1:], start=1):
            ports.extend([
                Port(id=f"{nid}.{k}.left", side="left", rel_x=0, rel_y=h // 2, type="input", component=extra_comp),
                Port(id=f"{nid}.{k}.right", side="right", rel_x=w, rel_y=h // 2, type="output", component=extra_comp),
                Port(id=f"{nid}.{k}.top", side="top", rel_x=w // 2, rel_y=0, type="input", component=extra_comp),
                Port(id=f"{nid}.{k}.bottom", side="bottom", rel_x=w // 2, rel_y=h, type="output", component=extra_comp),
            ])
        elements: List = [rect, text]
        if icon:
            elements.insert(1, UseEl(id=f"{node.id}.icon", href=f"#icon-{icon}", x=8, y=(h - 16) // 2, w=16, h=16, color=pr.icon_color))
        frag = Fragment(node_id=node.id, w=w, h=h, elements=elements, ports=ports)
        if "diagonal" in self.faults:
            frag.elements.append(
                PathEl(id=f"{node.id}.diag", points=[(0, 0), (w, h)], marker=False, flow_type="data")
            )
        if len(names) > 1:
            node.residuals.append(
                ResidualDefect(
                    "warning",
                    f"forced leaf: {len(names)} components collapsed into one block",
                    rect.id,
                    "raise the node/depth cap to decompose further",
                )
            )
        return frag

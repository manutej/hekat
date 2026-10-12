"""Icon symbol library and the custom-icon vocabulary.

Every icon is drawn on a 24x24 grid with a 2px stroke in ``currentColor`` and no fill, so it
reads at 16px inside a block and at 48px in a legend, in light and dark themes alike.  Icons
are emitted as ``<symbol>`` definitions and placed with ``<use href="#icon-name">``.

The library is deliberately small and semantic (what a methodology figure needs); the
icon-smith loop (:mod:`figtree.iconsmith`) is how new icons are designed, scored and added.
"""

from __future__ import annotations

import re
from typing import Dict, Iterable, List, Optional

ICON_VIEWBOX = "0 0 24 24"

# name -> inner SVG (24x24, stroke 2, currentColor, round joins)
ICONS: Dict[str, str] = {
    "document": '<path d="M6 3h8l5 5v13H6z"/><path d="M14 3v5h5"/><path d="M9 13h7M9 17h7"/>',
    "search": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l5.5 5.5"/>',
    "tree": '<circle cx="12" cy="5" r="2.5"/><circle cx="5" cy="19" r="2.5"/><circle cx="19" cy="19" r="2.5"/><path d="M12 7.5v4M12 11.5L5 16.5M12 11.5l7 5"/>',
    "eye": '<path d="M2 12s4-7 10-7 10 7 10 7-4 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/>',
    "wrench": '<path d="M14.5 4a5 5 0 0 0-4.6 7l-7 7 2.1 2.1 7-7A5 5 0 0 0 19 8.5l-3 1-2-2 1-3z"/>',
    "image": '<rect x="3" y="4" width="18" height="16" rx="1"/><circle cx="8.5" cy="9.5" r="1.5"/><path d="M21 16l-5-5-8 8"/>',
    "database": '<ellipse cx="12" cy="5.5" rx="8" ry="2.5"/><path d="M4 5.5v13c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5v-13"/><path d="M4 12c0 1.4 3.6 2.5 8 2.5s8-1.1 8-2.5"/>',
    "gear": '<circle cx="12" cy="12" r="3"/><path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M17 17l2.1 2.1M4.9 19.1L7 17M17 7l2.1-2.1"/>',
    "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 3.6-7 8-7s8 3 8 7"/>',
    "chart": '<path d="M4 20V4M4 20h16"/><path d="M8 16v-5M12 16V8M16 16v-3"/>',
    "loop": '<path d="M4 12a8 8 0 0 1 13.7-5.7L20 8"/><path d="M20 4v4h-4"/><path d="M20 12a8 8 0 0 1-13.7 5.7L4 16"/><path d="M4 20v-4h4"/>',
    "split": '<path d="M4 12h6"/><path d="M10 12l6-6h4M10 12l6 6h4"/><path d="M17 3l3 3-3 3M17 15l3 3-3 3"/>',
    "merge": '<path d="M4 6h4l6 6-6 6H4"/><path d="M14 12h6"/><path d="M17 9l3 3-3 3"/>',
    "check": '<path d="M4 12.5l5 5L20 6.5"/>',
    "layers": '<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 13l9 5 9-5"/><path d="M3 17l9 5 9-5"/>',
    "grid": '<rect x="3" y="3" width="18" height="18" rx="1"/><path d="M3 9h18M3 15h18M9 3v18M15 3v18"/>',
    "arrow-right": '<path d="M4 12h15"/><path d="M13 6l6 6-6 6"/>',
    "bolt": '<path d="M13 2L5 14h6l-1 8 9-12h-6z"/>',
    "text": '<path d="M5 6h14M12 6v14M8 20h8"/>',
    "palette": '<path d="M12 3a9 9 0 1 0 0 18c1.5 0 2-.9 2-2 0-1.2-.9-1.6-.9-2.5 0-1 .9-1.5 2.4-1.5H17a4 4 0 0 0 4-4c0-4.5-4-8-9-8z"/><circle cx="7.5" cy="11.5" r="1.3"/><circle cx="10.5" cy="7.5" r="1.3"/><circle cx="15" cy="7.5" r="1.3"/>',
    # FigTree showcase family (designed with the icon-smith loop, examples/figtree/icons/)
    "grounder": '<path d="M9 21H5V3h8l6 6v1"/><path d="M13 3v6h6"/><circle cx="14.5" cy="15.5" r="3.5"/><path d="M17 18l3.5 3.5"/>',
    "decompose": '<circle cx="12" cy="5" r="2"/><circle cx="4.5" cy="19" r="2"/><circle cx="12" cy="19" r="2"/><circle cx="19.5" cy="19" r="2"/><line x1="12" y1="7" x2="12" y2="17"/><path d="M4.5 17v-4a3 3 0 0 1 3-3h9a3 3 0 0 1 3 3v4"/>',
    "draw-leaf": '<rect x="3" y="3" width="10" height="10" rx="1"/><path d="M11 21l.5-3.5L19 10l3 3-7.5 7.5z"/><path d="M17 12l3 3"/>',
    "merge": '<rect x="3" y="3" width="5" height="6" rx="1"/><rect x="3" y="15" width="5" height="6" rx="1"/><path d="M8 6h3v12H8"/><path d="M11 12h3"/><path d="M12.5 10l2 2-2 2"/><rect x="16.5" y="8" width="5" height="8" rx="1"/>',
    "render": '<rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="16" cy="8" r="1.5"/><polyline points="3 17 8.5 11.5 13 16 15.5 13.5 21 19"/>',
    "critic": '<path d="M3 8.5C6 3 18 3 21 8.5C18 14 6 14 3 8.5Z"/><circle cx="12" cy="8.5" r="2"/><polyline points="7 15.5 4 18.5 7 21.5"/><polyline points="17 15.5 20 18.5 17 21.5"/><line x1="10.5" y1="18.5" x2="13.5" y2="18.5"/>',
    "repair": '<rect x="3" y="16" width="5" height="5" rx="1"/><path d="M17.5 3a3.75 3.75 0 0 0-3.5 5.25l-5.25 5.25 1.5 1.5 5.25-5.25A3.75 3.75 0 0 0 21 6.5l-2.25.75-1.5-1.5.75-2.25z"/>',
    "residual": '<polygon points="12,3 20,16 4,16"/><line x1="12" y1="8" x2="12" y2="10.5"/><line x1="12" y1="13.5" x2="12" y2="13.5"/><line x1="12" y1="16" x2="12" y2="21"/>',
    "sheaf": '<polygon points="12,3 21,7.5 12,12 3,7.5"/><polyline points="3,12 12,16.5 21,12"/><polyline points="3,16.5 12,21 21,16.5"/>',
    "ports": '<path d="M10 5H5V10"/><path d="M14 5H19V10"/><path d="M19 14V19H14"/><path d="M10 19H5V14"/><circle cx="12" cy="5" r="2"/><circle cx="19" cy="12" r="2"/><circle cx="12" cy="19" r="2"/><circle cx="5" cy="12" r="2"/>',
    "edit-script": '<path d="M3 5h11M3 10h8M3 15h5"/><path d="M10 21l.5-3.5L18 10l3 3-7.5 7.5z"/><path d="M16 12l3 3"/>',
    "trajectory": '<circle cx="5" cy="18" r="1.5"/><circle cx="12" cy="12" r="1.5"/><circle cx="19" cy="6" r="1.5"/><line x1="6.5" y1="16.5" x2="10.5" y2="13.5"/><line x1="13.5" y1="10.5" x2="17.5" y2="7.5"/>',
}

# component keyword -> icon name (first match wins; order matters)
ICON_KEYWORDS: List[tuple] = [
    (("grounder", "ground", "extract", "search", "retriev"), "search"),
    (("critic", "review", "inspect", "judge", "evaluat", "verif", "validat"), "eye"),
    (("worker", "repair", "merge", "fix", "assembl"), "wrench"),
    (("render", "image", "raster", "pixel", "png"), "image"),
    (("tree", "decompos", "recurs", "hierarch", "split"), "tree"),
    (("memory", "store", "database", "cache", "sheaf", "db"), "database"),
    (("loop", "iterat", "repeat", "refine", "revalidat", "re-validate"), "loop"),
    (("user", "human", "author", "reader", "student"), "user"),
    (("chart", "metric", "score", "plot"), "chart"),
    (("parallel", "fan", "broadcast"), "split"),
    (("input", "source", "text", "document", "paper", "spec", "prompt", "token"), "document"),
    (("encoder", "decoder", "model", "layer", "transformer", "network"), "layers"),
    (("attention", "cross"), "grid"),
    (("classif", "output", "check", "done"), "check"),
    (("embed", "feature", "generator", "generat", "process", "compute", "transform"), "gear"),
]


def icon_for(component: str) -> Optional[str]:
    """Pick a library icon for a component name, or None when nothing fits."""
    n = component.lower()
    for keys, icon in ICON_KEYWORDS:
        if any(k in n for k in keys):
            return icon
    return None


def symbol(name: str, inner: Optional[str] = None) -> str:
    body = inner if inner is not None else ICONS[name]
    return (
        f'<symbol id="icon-{name}" viewBox="{ICON_VIEWBOX}" fill="none" stroke="currentColor" '
        f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{body}</symbol>'
    )


def symbol_defs(names: Iterable[str], extra: Optional[Dict[str, str]] = None) -> str:
    """``<symbol>`` definitions for the given icon names (library first, then ``extra``)."""
    out: List[str] = []
    seen = set()
    for n in names:
        if n in seen:
            continue
        seen.add(n)
        if n in ICONS:
            out.append(symbol(n))
        elif extra and n in extra:
            out.append(symbol(n, extra[n]))
    return "\n".join(out)


def standalone_icon(name: str, inner: Optional[str] = None, size: int = 48, color: str = "#333333") -> str:
    """A complete SVG document for one icon (for sheets, previews and the icon rubric)."""
    body = inner if inner is not None else ICONS[name]
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="{ICON_VIEWBOX}" '
        f'fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" data-icon="{name}">'
        f"{body}</svg>"
    )


def icons_used(svg_text: str) -> List[str]:
    return sorted(set(re.findall(r'href="#icon-([A-Za-z0-9_-]+)"', svg_text)))

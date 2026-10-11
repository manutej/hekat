"""Integration contracts (section 8).

* :func:`refine_step` exposes the generator as a recursive refine step for the HEKAT
  recursive-meta-prompting skill: one call, one JSON-friendly dict.
* :func:`to_work_graph` emits the layout tree with residual sections in a graph shape
  (nodes/edges) suitable for a Notion Work Graph, p5js, or an editorial dashboard.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from figtree.orchestrator import FigTree, FigTreeResult


def refine_step(source_text: str, edit: Optional[Dict[str, Any]] = None, render: bool = False) -> Dict[str, Any]:
    result = FigTree(render=render).run(source_text, edit=edit)
    return {
        "svg": result.final_svg,
        "residual_defects": [r.to_dict() for r in result.residual_defects],
        "layout_tree": result.layout_tree.to_dict(),
        "editability": result.editability_proof.to_dict(),
        "content_plan": result.content_plan.to_dict(),
        "faithfulness_failures": list(result.faithfulness_failures),
    }


def to_work_graph(result: FigTreeResult) -> Dict[str, Any]:
    nodes = []
    for node in result.layout_tree.stalks.values():
        nodes.append(
            {
                "id": node.id,
                "title": node.description,
                "depth": node.depth,
                "components": list(node.components),
                "canvas": dict(node.canvas),
                "residuals": [r.to_dict() for r in node.residuals],
                "leaf": node.is_leaf(),
            }
        )
    edges = [{"from": a, "to": b, "conserved": result.layout_tree.restriction.get(f"{a}->{b}", True)} for a, b in result.layout_tree.edges]
    return {"nodes": nodes, "edges": edges, "conserved": result.layout_tree.conserved(), "editability": result.editability_proof.to_dict()}

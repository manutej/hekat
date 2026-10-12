// Generated from design/contract/examples/figtree-loop.program.json (python -m figtree contract export). Do not edit by hand.
import type { FigureProgram } from '@hekat/figtree-ds';
export const figtreeLoop: FigureProgram = {
  "version": 1,
  "canvas": {
    "width": 904,
    "height": 377,
    "preset": "teaching",
    "grid": 8
  },
  "containers": [
    {
      "id": "n3",
      "bbox": {
        "x": 208.0,
        "y": 32.0,
        "w": 224.0,
        "h": 184.0
      },
      "depth": 0,
      "boxed": false
    },
    {
      "id": "n4",
      "bbox": {
        "x": 472.0,
        "y": 72.0,
        "w": 392.0,
        "h": 112.0
      },
      "depth": 0,
      "boxed": false
    },
    {
      "id": "n5",
      "bbox": {
        "x": 56.0,
        "y": 280.0,
        "w": 728.0,
        "h": 136.0
      },
      "depth": 0,
      "boxed": false
    }
  ],
  "nodes": [
    {
      "id": "n2",
      "label": "Grounder",
      "bbox": {
        "x": 56.0,
        "y": 104.0,
        "w": 112.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "processing",
      "icon": "search"
    },
    {
      "id": "n6",
      "label": "Generator",
      "bbox": {
        "x": 264.0,
        "y": 64.0,
        "w": 112.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "processing",
      "icon": "gear",
      "parent": "n3"
    },
    {
      "id": "n7",
      "label": "recursive tree",
      "bbox": {
        "x": 240.0,
        "y": 136.0,
        "w": 160.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "processing",
      "icon": "tree",
      "parent": "n3"
    },
    {
      "id": "n8",
      "label": "Decompose children",
      "bbox": {
        "x": 504.0,
        "y": 104.0,
        "w": 192.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "processing",
      "icon": "tree",
      "parent": "n4"
    },
    {
      "id": "n9",
      "label": "Merge",
      "bbox": {
        "x": 736.0,
        "y": 104.0,
        "w": 96.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "processing",
      "icon": "wrench",
      "parent": "n4"
    },
    {
      "id": "n10",
      "label": "Critic",
      "bbox": {
        "x": 112.0,
        "y": 312.0,
        "w": 96.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "attention",
      "icon": "eye",
      "parent": "n5"
    },
    {
      "id": "n11",
      "label": "Worker",
      "bbox": {
        "x": 248.0,
        "y": 312.0,
        "w": 96.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "processing",
      "icon": "wrench",
      "parent": "n5"
    },
    {
      "id": "n12",
      "label": "re-validate invariants",
      "bbox": {
        "x": 384.0,
        "y": 312.0,
        "w": 224.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "attention",
      "icon": "eye",
      "parent": "n5"
    },
    {
      "id": "n13",
      "label": "render",
      "bbox": {
        "x": 648.0,
        "y": 312.0,
        "w": 96.0,
        "h": 48.0
      },
      "kind": "block",
      "tone": "processing",
      "icon": "image",
      "parent": "n5"
    }
  ],
  "flows": [
    {
      "id": "n4.arrow0",
      "from": "n8",
      "to": "n9",
      "type": "data",
      "points": [
        [
          696.0,
          128.0
        ],
        [
          736.0,
          128.0
        ]
      ]
    },
    {
      "id": "n5.arrow0",
      "from": "n13",
      "to": "n10",
      "type": "data",
      "points": [
        [
          744.0,
          336.0
        ],
        [
          752.0,
          336.0
        ],
        [
          752.0,
          384.0
        ],
        [
          88.0,
          384.0
        ],
        [
          88.0,
          336.0
        ],
        [
          112.0,
          336.0
        ]
      ]
    },
    {
      "id": "n5.arrow1",
      "from": "n10",
      "to": "n11",
      "type": "data",
      "points": [
        [
          208.0,
          336.0
        ],
        [
          248.0,
          336.0
        ]
      ]
    },
    {
      "id": "n5.arrow2",
      "from": "n11",
      "to": "n12",
      "type": "data",
      "points": [
        [
          344.0,
          336.0
        ],
        [
          384.0,
          336.0
        ]
      ]
    },
    {
      "id": "n5.arrow3",
      "from": "n12",
      "to": "n13",
      "type": "control",
      "points": [
        [
          608.0,
          336.0
        ],
        [
          648.0,
          336.0
        ]
      ]
    },
    {
      "id": "n1.arrow0",
      "from": "n2",
      "to": "n6",
      "type": "data",
      "points": [
        [
          168.0,
          128.0
        ],
        [
          216.0,
          128.0
        ],
        [
          216.0,
          88.0
        ],
        [
          264.0,
          88.0
        ]
      ]
    },
    {
      "id": "n1.arrow1",
      "from": "n6",
      "to": "n8",
      "type": "data",
      "points": [
        [
          376.0,
          88.0
        ],
        [
          440.0,
          88.0
        ],
        [
          440.0,
          128.0
        ],
        [
          504.0,
          128.0
        ]
      ]
    },
    {
      "id": "n1.arrow2",
      "from": "n9",
      "to": "n10",
      "type": "data",
      "points": [
        [
          832.0,
          128.0
        ],
        [
          872.0,
          128.0
        ],
        [
          872.0,
          248.0
        ],
        [
          160.0,
          248.0
        ],
        [
          160.0,
          312.0
        ]
      ]
    },
    {
      "id": "n1.arrow3",
      "from": "n2",
      "to": "n7",
      "type": "data",
      "points": [
        [
          168.0,
          128.0
        ],
        [
          208.0,
          128.0
        ],
        [
          208.0,
          160.0
        ],
        [
          240.0,
          160.0
        ]
      ]
    },
    {
      "id": "n1.arrow4",
      "from": "n7",
      "to": "n10",
      "type": "data",
      "points": [
        [
          400.0,
          160.0
        ],
        [
          448.0,
          160.0
        ],
        [
          448.0,
          232.0
        ],
        [
          32.0,
          232.0
        ],
        [
          32.0,
          336.0
        ],
        [
          112.0,
          336.0
        ]
      ]
    }
  ],
  "ports": [
    {
      "id": "n2.left",
      "side": "left",
      "x": 56,
      "y": 96,
      "type": "input",
      "component": "Grounder"
    },
    {
      "id": "n2.right",
      "side": "right",
      "x": 168,
      "y": 96,
      "type": "output",
      "component": "Grounder"
    },
    {
      "id": "n2.top",
      "side": "top",
      "x": 112,
      "y": 72,
      "type": "input",
      "component": "Grounder"
    },
    {
      "id": "n2.bottom",
      "side": "bottom",
      "x": 112,
      "y": 120,
      "type": "output",
      "component": "Grounder"
    },
    {
      "id": "n6.left",
      "side": "left",
      "x": 264,
      "y": 56,
      "type": "input",
      "component": "Generator"
    },
    {
      "id": "n6.right",
      "side": "right",
      "x": 376,
      "y": 56,
      "type": "output",
      "component": "Generator"
    },
    {
      "id": "n6.top",
      "side": "top",
      "x": 320,
      "y": 32,
      "type": "input",
      "component": "Generator"
    },
    {
      "id": "n6.bottom",
      "side": "bottom",
      "x": 320,
      "y": 80,
      "type": "output",
      "component": "Generator"
    },
    {
      "id": "n7.left",
      "side": "left",
      "x": 240,
      "y": 128,
      "type": "input",
      "component": "recursive tree"
    },
    {
      "id": "n7.right",
      "side": "right",
      "x": 400,
      "y": 128,
      "type": "output",
      "component": "recursive tree"
    },
    {
      "id": "n7.top",
      "side": "top",
      "x": 320,
      "y": 104,
      "type": "input",
      "component": "recursive tree"
    },
    {
      "id": "n7.bottom",
      "side": "bottom",
      "x": 320,
      "y": 152,
      "type": "output",
      "component": "recursive tree"
    },
    {
      "id": "n8.left",
      "side": "left",
      "x": 504,
      "y": 96,
      "type": "input",
      "component": "Decompose children"
    },
    {
      "id": "n8.right",
      "side": "right",
      "x": 696,
      "y": 96,
      "type": "output",
      "component": "Decompose children"
    },
    {
      "id": "n8.top",
      "side": "top",
      "x": 600,
      "y": 72,
      "type": "input",
      "component": "Decompose children"
    },
    {
      "id": "n8.bottom",
      "side": "bottom",
      "x": 600,
      "y": 120,
      "type": "output",
      "component": "Decompose children"
    },
    {
      "id": "n9.left",
      "side": "left",
      "x": 736,
      "y": 96,
      "type": "input",
      "component": "Merge"
    },
    {
      "id": "n9.right",
      "side": "right",
      "x": 832,
      "y": 96,
      "type": "output",
      "component": "Merge"
    },
    {
      "id": "n9.top",
      "side": "top",
      "x": 784,
      "y": 72,
      "type": "input",
      "component": "Merge"
    },
    {
      "id": "n9.bottom",
      "side": "bottom",
      "x": 784,
      "y": 120,
      "type": "output",
      "component": "Merge"
    },
    {
      "id": "n10.left",
      "side": "left",
      "x": 112,
      "y": 304,
      "type": "input",
      "component": "Critic"
    },
    {
      "id": "n10.right",
      "side": "right",
      "x": 208,
      "y": 304,
      "type": "output",
      "component": "Critic"
    },
    {
      "id": "n10.top",
      "side": "top",
      "x": 160,
      "y": 280,
      "type": "input",
      "component": "Critic"
    },
    {
      "id": "n10.bottom",
      "side": "bottom",
      "x": 160,
      "y": 328,
      "type": "output",
      "component": "Critic"
    },
    {
      "id": "n11.left",
      "side": "left",
      "x": 248,
      "y": 304,
      "type": "input",
      "component": "Worker"
    },
    {
      "id": "n11.right",
      "side": "right",
      "x": 344,
      "y": 304,
      "type": "output",
      "component": "Worker"
    },
    {
      "id": "n11.top",
      "side": "top",
      "x": 296,
      "y": 280,
      "type": "input",
      "component": "Worker"
    },
    {
      "id": "n11.bottom",
      "side": "bottom",
      "x": 296,
      "y": 328,
      "type": "output",
      "component": "Worker"
    },
    {
      "id": "n12.left",
      "side": "left",
      "x": 384,
      "y": 304,
      "type": "input",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.right",
      "side": "right",
      "x": 608,
      "y": 304,
      "type": "output",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.top",
      "side": "top",
      "x": 496,
      "y": 280,
      "type": "input",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.bottom",
      "side": "bottom",
      "x": 496,
      "y": 328,
      "type": "output",
      "component": "re-validate invariants"
    },
    {
      "id": "n13.left",
      "side": "left",
      "x": 648,
      "y": 304,
      "type": "input",
      "component": "render"
    },
    {
      "id": "n13.right",
      "side": "right",
      "x": 744,
      "y": 304,
      "type": "output",
      "component": "render"
    },
    {
      "id": "n13.top",
      "side": "top",
      "x": 696,
      "y": 280,
      "type": "input",
      "component": "render"
    },
    {
      "id": "n13.bottom",
      "side": "bottom",
      "x": 696,
      "y": 328,
      "type": "output",
      "component": "render"
    },
    {
      "id": "n2.left",
      "side": "left",
      "x": 56,
      "y": 96,
      "type": "input",
      "component": "Grounder"
    },
    {
      "id": "n2.right",
      "side": "right",
      "x": 168,
      "y": 96,
      "type": "output",
      "component": "Grounder"
    },
    {
      "id": "n2.top",
      "side": "top",
      "x": 112,
      "y": 72,
      "type": "input",
      "component": "Grounder"
    },
    {
      "id": "n2.bottom",
      "side": "bottom",
      "x": 112,
      "y": 120,
      "type": "output",
      "component": "Grounder"
    },
    {
      "id": "n6.left",
      "side": "left",
      "x": 264,
      "y": 56,
      "type": "input",
      "component": "Generator"
    },
    {
      "id": "n6.right",
      "side": "right",
      "x": 376,
      "y": 56,
      "type": "output",
      "component": "Generator"
    },
    {
      "id": "n6.top",
      "side": "top",
      "x": 320,
      "y": 32,
      "type": "input",
      "component": "Generator"
    },
    {
      "id": "n6.bottom",
      "side": "bottom",
      "x": 320,
      "y": 80,
      "type": "output",
      "component": "Generator"
    },
    {
      "id": "n7.left",
      "side": "left",
      "x": 240,
      "y": 128,
      "type": "input",
      "component": "recursive tree"
    },
    {
      "id": "n7.right",
      "side": "right",
      "x": 400,
      "y": 128,
      "type": "output",
      "component": "recursive tree"
    },
    {
      "id": "n7.top",
      "side": "top",
      "x": 320,
      "y": 104,
      "type": "input",
      "component": "recursive tree"
    },
    {
      "id": "n7.bottom",
      "side": "bottom",
      "x": 320,
      "y": 152,
      "type": "output",
      "component": "recursive tree"
    },
    {
      "id": "n6.left",
      "side": "left",
      "x": 264,
      "y": 56,
      "type": "input",
      "component": "Generator"
    },
    {
      "id": "n6.right",
      "side": "right",
      "x": 376,
      "y": 56,
      "type": "output",
      "component": "Generator"
    },
    {
      "id": "n6.top",
      "side": "top",
      "x": 320,
      "y": 32,
      "type": "input",
      "component": "Generator"
    },
    {
      "id": "n6.bottom",
      "side": "bottom",
      "x": 320,
      "y": 80,
      "type": "output",
      "component": "Generator"
    },
    {
      "id": "n7.left",
      "side": "left",
      "x": 240,
      "y": 128,
      "type": "input",
      "component": "recursive tree"
    },
    {
      "id": "n7.right",
      "side": "right",
      "x": 400,
      "y": 128,
      "type": "output",
      "component": "recursive tree"
    },
    {
      "id": "n7.top",
      "side": "top",
      "x": 320,
      "y": 104,
      "type": "input",
      "component": "recursive tree"
    },
    {
      "id": "n7.bottom",
      "side": "bottom",
      "x": 320,
      "y": 152,
      "type": "output",
      "component": "recursive tree"
    },
    {
      "id": "n8.left",
      "side": "left",
      "x": 504,
      "y": 96,
      "type": "input",
      "component": "Decompose children"
    },
    {
      "id": "n8.right",
      "side": "right",
      "x": 696,
      "y": 96,
      "type": "output",
      "component": "Decompose children"
    },
    {
      "id": "n8.top",
      "side": "top",
      "x": 600,
      "y": 72,
      "type": "input",
      "component": "Decompose children"
    },
    {
      "id": "n8.bottom",
      "side": "bottom",
      "x": 600,
      "y": 120,
      "type": "output",
      "component": "Decompose children"
    },
    {
      "id": "n9.left",
      "side": "left",
      "x": 736,
      "y": 96,
      "type": "input",
      "component": "Merge"
    },
    {
      "id": "n9.right",
      "side": "right",
      "x": 832,
      "y": 96,
      "type": "output",
      "component": "Merge"
    },
    {
      "id": "n9.top",
      "side": "top",
      "x": 784,
      "y": 72,
      "type": "input",
      "component": "Merge"
    },
    {
      "id": "n9.bottom",
      "side": "bottom",
      "x": 784,
      "y": 120,
      "type": "output",
      "component": "Merge"
    },
    {
      "id": "n8.left",
      "side": "left",
      "x": 504,
      "y": 96,
      "type": "input",
      "component": "Decompose children"
    },
    {
      "id": "n8.right",
      "side": "right",
      "x": 696,
      "y": 96,
      "type": "output",
      "component": "Decompose children"
    },
    {
      "id": "n8.top",
      "side": "top",
      "x": 600,
      "y": 72,
      "type": "input",
      "component": "Decompose children"
    },
    {
      "id": "n8.bottom",
      "side": "bottom",
      "x": 600,
      "y": 120,
      "type": "output",
      "component": "Decompose children"
    },
    {
      "id": "n9.left",
      "side": "left",
      "x": 736,
      "y": 96,
      "type": "input",
      "component": "Merge"
    },
    {
      "id": "n9.right",
      "side": "right",
      "x": 832,
      "y": 96,
      "type": "output",
      "component": "Merge"
    },
    {
      "id": "n9.top",
      "side": "top",
      "x": 784,
      "y": 72,
      "type": "input",
      "component": "Merge"
    },
    {
      "id": "n9.bottom",
      "side": "bottom",
      "x": 784,
      "y": 120,
      "type": "output",
      "component": "Merge"
    },
    {
      "id": "n10.left",
      "side": "left",
      "x": 112,
      "y": 304,
      "type": "input",
      "component": "Critic"
    },
    {
      "id": "n10.right",
      "side": "right",
      "x": 208,
      "y": 304,
      "type": "output",
      "component": "Critic"
    },
    {
      "id": "n10.top",
      "side": "top",
      "x": 160,
      "y": 280,
      "type": "input",
      "component": "Critic"
    },
    {
      "id": "n10.bottom",
      "side": "bottom",
      "x": 160,
      "y": 328,
      "type": "output",
      "component": "Critic"
    },
    {
      "id": "n11.left",
      "side": "left",
      "x": 248,
      "y": 304,
      "type": "input",
      "component": "Worker"
    },
    {
      "id": "n11.right",
      "side": "right",
      "x": 344,
      "y": 304,
      "type": "output",
      "component": "Worker"
    },
    {
      "id": "n11.top",
      "side": "top",
      "x": 296,
      "y": 280,
      "type": "input",
      "component": "Worker"
    },
    {
      "id": "n11.bottom",
      "side": "bottom",
      "x": 296,
      "y": 328,
      "type": "output",
      "component": "Worker"
    },
    {
      "id": "n12.left",
      "side": "left",
      "x": 384,
      "y": 304,
      "type": "input",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.right",
      "side": "right",
      "x": 608,
      "y": 304,
      "type": "output",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.top",
      "side": "top",
      "x": 496,
      "y": 280,
      "type": "input",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.bottom",
      "side": "bottom",
      "x": 496,
      "y": 328,
      "type": "output",
      "component": "re-validate invariants"
    },
    {
      "id": "n13.left",
      "side": "left",
      "x": 648,
      "y": 304,
      "type": "input",
      "component": "render"
    },
    {
      "id": "n13.right",
      "side": "right",
      "x": 744,
      "y": 304,
      "type": "output",
      "component": "render"
    },
    {
      "id": "n13.top",
      "side": "top",
      "x": 696,
      "y": 280,
      "type": "input",
      "component": "render"
    },
    {
      "id": "n13.bottom",
      "side": "bottom",
      "x": 696,
      "y": 328,
      "type": "output",
      "component": "render"
    },
    {
      "id": "n10.left",
      "side": "left",
      "x": 112,
      "y": 304,
      "type": "input",
      "component": "Critic"
    },
    {
      "id": "n10.right",
      "side": "right",
      "x": 208,
      "y": 304,
      "type": "output",
      "component": "Critic"
    },
    {
      "id": "n10.top",
      "side": "top",
      "x": 160,
      "y": 280,
      "type": "input",
      "component": "Critic"
    },
    {
      "id": "n10.bottom",
      "side": "bottom",
      "x": 160,
      "y": 328,
      "type": "output",
      "component": "Critic"
    },
    {
      "id": "n11.left",
      "side": "left",
      "x": 248,
      "y": 304,
      "type": "input",
      "component": "Worker"
    },
    {
      "id": "n11.right",
      "side": "right",
      "x": 344,
      "y": 304,
      "type": "output",
      "component": "Worker"
    },
    {
      "id": "n11.top",
      "side": "top",
      "x": 296,
      "y": 280,
      "type": "input",
      "component": "Worker"
    },
    {
      "id": "n11.bottom",
      "side": "bottom",
      "x": 296,
      "y": 328,
      "type": "output",
      "component": "Worker"
    },
    {
      "id": "n12.left",
      "side": "left",
      "x": 384,
      "y": 304,
      "type": "input",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.right",
      "side": "right",
      "x": 608,
      "y": 304,
      "type": "output",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.top",
      "side": "top",
      "x": 496,
      "y": 280,
      "type": "input",
      "component": "re-validate invariants"
    },
    {
      "id": "n12.bottom",
      "side": "bottom",
      "x": 496,
      "y": 328,
      "type": "output",
      "component": "re-validate invariants"
    },
    {
      "id": "n13.left",
      "side": "left",
      "x": 648,
      "y": 304,
      "type": "input",
      "component": "render"
    },
    {
      "id": "n13.right",
      "side": "right",
      "x": 744,
      "y": 304,
      "type": "output",
      "component": "render"
    },
    {
      "id": "n13.top",
      "side": "top",
      "x": 696,
      "y": 280,
      "type": "input",
      "component": "render"
    },
    {
      "id": "n13.bottom",
      "side": "bottom",
      "x": 696,
      "y": 328,
      "type": "output",
      "component": "render"
    }
  ],
  "title": "FigTree loop",
  "source": "examples/figtree/figtree-spec.md",
  "caption": {
    "lead": "Figure 1.",
    "text": "The Grounder admits only evidenced components; the Generator decomposes and draws; the Critic reviews the render in code and image, and the Worker repairs with local edits."
  },
  "meta": {
    "generator": "python -m figtree generate --style teaching --icons; refined by the figtree-refine workflow (9.19 -> 10.0 in two rounds)"
  }
} as FigureProgram;

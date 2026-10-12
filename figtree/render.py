"""Optional raster rendering for the image side of the dual-space review."""

from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from typing import Optional


import glob


def _chromium() -> Optional[str]:
    env = os.environ.get("FIGTREE_CHROMIUM")
    if env and os.path.exists(env):
        return env
    for name in ("chromium", "chromium-browser", "google-chrome", "chrome"):
        found = shutil.which(name)
        if found:
            return found
    for pattern in (
        "/opt/pw-browsers/chromium_headless_shell-*/chrome-linux/headless_shell",
        os.path.expanduser("~/.cache/ms-playwright/chromium_headless_shell-*/chrome-linux/headless_shell"),
        "/opt/pw-browsers/chromium-*/chrome-linux/chrome",
        os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux/chrome"),
    ):
        hits = sorted(glob.glob(pattern))
        if hits:
            return hits[-1]
    return None


def available_renderer() -> Optional[str]:
    """Return the name of the first available rasteriser, or None (``no-vision`` mode)."""
    if os.environ.get("FIGTREE_NO_RENDER"):
        return None
    try:
        import cairosvg  # noqa: F401

        return "cairosvg"
    except Exception:  # noqa: BLE001
        pass
    if shutil.which("rsvg-convert"):
        return "rsvg-convert"
    if _chromium():
        return "chromium"
    return None


def render_png(svg_text: str, out_dir: Optional[str] = None, name: str = "node") -> Optional[str]:
    """Render ``svg_text`` to a PNG and return its path, or ``None`` when no renderer exists."""
    backend = available_renderer()
    if backend is None:
        return None
    out_dir = os.path.abspath(out_dir) if out_dir else tempfile.mkdtemp(prefix="figtree-")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{name}.png")
    if backend == "cairosvg":
        import cairosvg

        cairosvg.svg2png(bytestring=svg_text.encode("utf-8"), write_to=path)
        return path
    work_dir = tempfile.mkdtemp(prefix="figtree-render-")  # intermediates never land next to outputs
    svg_path = os.path.join(work_dir, f"{name}.svg")
    with open(svg_path, "w", encoding="utf-8") as fh:
        fh.write(svg_text)
    if backend == "rsvg-convert":
        subprocess.run(["rsvg-convert", "-o", path, svg_path], check=True, timeout=60)
        return path
    # chromium headless: wrap the SVG in a zero-margin page sized to the canvas
    import re

    w = int(float(re.search(r'width="(\d+)"', svg_text).group(1)))
    h = int(float(re.search(r'height="(\d+)"', svg_text).group(1)))
    html_path = os.path.join(work_dir, f"{name}.html")
    with open(html_path, "w", encoding="utf-8") as fh:
        fh.write(f"<!doctype html><html><head><meta charset='utf-8'><style>html,body{{margin:0;padding:0;background:#fff}}svg{{display:block}}</style></head><body>{svg_text}</body></html>")
    exe = _chromium()
    headless = [] if exe.endswith("headless_shell") else ["--headless=new"]
    cmd = [
        exe, *headless, "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--force-device-scale-factor=1", f"--window-size={w},{h}", f"--screenshot={path}", f"file://{html_path}",
    ]
    subprocess.run(cmd, check=True, timeout=120, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return path if os.path.exists(path) else None

#!/usr/bin/env python3
"""Render the Mermaid diagram sources to PNG (Stage 2.1).

Renders each assets/diagrams/src/*.mmd via kroki.io (the /mermaid-render skill's
primary path; works headless, no local Chromium), then contain-fits + centers the
result onto each slot's manifest canvas so the PNG matches the declared dimensions
exactly. Finally flips those manifest slots to status='real'.

This is a one-time build step: the PNGs are committed, so CI never depends on
kroki. Re-run only when a .mmd source changes (then commit the new PNG).

Usage: python tools/diagrams/render_diagrams.py
"""
from __future__ import annotations

import io
import sys
import urllib.request
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifest_util  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = REPO_ROOT / "assets" / "diagrams" / "src"
KROKI_URL = "https://kroki.io/mermaid/png"
BG = (255, 255, 255)

# manifest slot id -> source .mmd filename
DIAGRAMS = {
    "diagram-lineage": "lineage.mmd",
    "diagram-goal-vs-loop": "goal-vs-loop-flowchart.mmd",
    "diagram-anatomy": "anatomy-5-blocks.mmd",
    "diagram-maker-checker": "maker-checker.mmd",
    "diagram-durability-ladder": "durability-ladder.mmd",
}


def render_kroki(mmd_source: str, timeout: int = 40) -> Image.Image:
    req = urllib.request.Request(
        KROKI_URL,
        data=mmd_source.encode("utf-8"),
        headers={
            "Content-Type": "text/plain",
            # kroki's CDN 403s the default urllib User-Agent.
            "User-Agent": "loop-engineering-handbook/1.0 (mermaid render build step)",
            "Accept": "image/png",
        },
        method="POST",
    )
    # urlopen raises HTTPError on any non-2xx, so reaching here means success.
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return Image.open(io.BytesIO(resp.read())).convert("RGBA")


def fit_onto_canvas(img: Image.Image, width: int, height: int) -> Image.Image:
    """Scale `img` to fit within (width, height) preserving aspect, center it on a
    white canvas of exactly (width, height)."""
    scale = min(width / img.width, height / img.height)
    new_w = max(1, round(img.width * scale))
    new_h = max(1, round(img.height * scale))
    resized = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new("RGB", (width, height), BG)
    flat = Image.new("RGB", resized.size, BG)
    flat.paste(resized, mask=resized.split()[-1])  # composite over white using alpha
    canvas.paste(flat, ((width - new_w) // 2, (height - new_h) // 2))
    return canvas


def main() -> int:
    manifest = manifest_util.load()
    by_id = {s["id"]: s for s in manifest["slots"]}

    # Render everything into memory first; only write + mark real if ALL succeed,
    # so a mid-batch kroki failure never leaves the slots half-written.
    pending = []  # (out_path, image, slot)
    for slot_id, src_name in DIAGRAMS.items():
        slot = by_id[slot_id]
        src = SRC_DIR / src_name
        if not src.exists():
            print(f"[diagrams] MISSING source: {src}", file=sys.stderr)
            return 1
        try:
            img = render_kroki(src.read_text())
        except Exception as exc:  # network / kroki failure
            print(f"[diagrams] FAILED to render {src_name}: {exc} (no files written)", file=sys.stderr)
            return 2
        pending.append((REPO_ROOT / slot["path"], fit_onto_canvas(img, slot["width"], slot["height"]), slot))

    for out_path, out, slot in pending:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out.save(out_path, "PNG")
        print(f"[diagrams] {slot['id']} -> {slot['path']} ({slot['width']}x{slot['height']})")

    manifest_util.mark_real({sid: {} for sid in DIAGRAMS})
    print(f"[diagrams] rendered {len(pending)} diagrams; manifest slots marked real")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

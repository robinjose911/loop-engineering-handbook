#!/usr/bin/env python3
"""Placeholder-stub generator (Stage 0.4).

For every visual slot declared in ``assets/manifest.json`` whose status is
``placeholder``, emit a labeled PNG at the slot's declared dimensions. Real
assets (diagrams in Stage 2, banner/OG in Stage 6) later overwrite the same
path and the manifest flips that slot to ``real`` -- at which point this
generator leaves it alone. The point: the no-broken-image render-check is green
on an empty skeleton and *stays* green as each real asset replaces its stub.

Deterministic: no RNG, no timestamps. Re-running is a no-op on existing files
unless ``--force`` is passed.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = REPO_ROOT / "assets" / "manifest.json"

# Slot kind -> (background, border) colors. Screenshot slots get a distinct
# dashed-looking frame so a labeled placeholder never reads as a real capture.
KIND_COLORS = {
    "banner": ((30, 41, 59), (148, 163, 184)),
    "social": ((30, 41, 59), (148, 163, 184)),
    "diagram": ((241, 245, 249), (100, 116, 139)),
    "chart": ((248, 250, 252), (100, 116, 139)),
    "quote-card": ((254, 252, 232), (202, 138, 4)),
}
DEFAULT_COLORS = ((241, 245, 249), (100, 116, 139))


def _load_font(size: int):
    """Pillow's default bitmap font, scaled where supported."""
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # very old Pillow without size kwarg
        return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for word in words:
        trial = f"{line} {word}".strip()
        if draw.textlength(trial, font=font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def render_slot(slot: dict, out_path: Path) -> None:
    width, height = int(slot["width"]), int(slot["height"])
    bg, border = KIND_COLORS.get(slot.get("kind", ""), DEFAULT_COLORS)
    is_dark = sum(bg) < 384
    fg = (226, 232, 240) if is_dark else (51, 65, 85)

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    # Border frame.
    draw.rectangle([1, 1, width - 2, height - 2], outline=border, width=3)
    # Screenshot slots get a second inset frame to read as "slot, not real".
    if slot.get("kind") == "quote-card":
        draw.rectangle([12, 12, width - 13, height - 13], outline=border, width=1)

    # Scale by both width and height so a wide-but-short slot does not wrap its
    # label into more lines than fit vertically.
    font_size = max(12, min(40, width // 26, height // 6))
    font = _load_font(font_size)
    small = _load_font(max(11, font_size - 8))

    label = slot.get("label", slot.get("id", "PLACEHOLDER"))
    lines = _wrap(draw, label, font, int(width * 0.84))
    sub = f'{slot["width"]}x{slot["height"]}  ({slot.get("kind", "asset")})'

    line_h = font_size + 8
    total_h = line_h * len(lines) + (font_size)  # + sub line
    y = (height - total_h) // 2
    for ln in lines:
        w = draw.textlength(ln, font=font)
        draw.text(((width - w) / 2, y), ln, fill=fg, font=font)
        y += line_h
    sw = draw.textlength(sub, font=small)
    draw.text(((width - sw) / 2, y + 6), sub, fill=border, font=small)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Generate placeholder PNGs for every manifest slot.")
    parser.add_argument("--force", action="store_true", help="regenerate even if the file already exists")
    parser.add_argument("--manifest", default=str(MANIFEST), help="path to assets/manifest.json")
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        print(f"[stubs] manifest not found: {manifest_path}", file=sys.stderr)
        return 1
    manifest = json.loads(manifest_path.read_text())

    made, skipped, real = 0, 0, 0
    for slot in manifest.get("slots", []):
        out_path = REPO_ROOT / slot["path"]
        if slot.get("status") == "real":
            real += 1
            if not out_path.exists():
                print(f"[stubs] WARNING: slot '{slot['id']}' marked real but {slot['path']} is missing", file=sys.stderr)
            continue
        if out_path.exists() and not args.force:
            skipped += 1
            continue
        render_slot(slot, out_path)
        made += 1

    print(f"[stubs] generated {made}, skipped {skipped} existing, {real} real slot(s) left untouched")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

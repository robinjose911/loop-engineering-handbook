#!/usr/bin/env python3
"""Generate the real banner + social-preview art (Stage 6.1).

Renders assets/banner.png (1280x320) and assets/social-preview.png (1280x640,
GitHub's social-preview size) from repo.config.json (repoName + tagline, neutral
theme), then flips those manifest slots to status='real'. Deterministic; re-run
is a no-op diff. Usage: python tools/brand/make_brand.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifest_util  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = json.loads((REPO_ROOT / "repo.config.json").read_text())

# Neutral, owner-agnostic palette (matches the neutral diagram/chart theme).
BG = (15, 23, 42)        # slate-900
ACCENT = (96, 165, 250)  # blue-400
FG = (226, 232, 240)     # slate-200
MUTED = (148, 163, 184)  # slate-400


def display_title(cfg: dict) -> str:
    return cfg["repoName"].replace("-", " ").title()


def banner_lines(cfg: dict) -> dict:
    """The text the banner/OG art draws. Returned (not just drawn) so the unit
    test can assert the configured tagline is actually used."""
    return {
        "title": display_title(cfg),
        "tagline": cfg["tagline"],
        "kicker": "guide · prompt library · 7 worked examples with the receipts",
    }


def _font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def _wrap(draw, text, font, max_width):
    words, lines, line = text.split(), [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def _render(width: int, height: int, lines: dict, out_path: Path) -> None:
    img = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(img)
    # accent rule along the top
    draw.rectangle([0, 0, width, 8], fill=ACCENT)
    pad = int(width * 0.06)

    title_font = _font(max(28, width // 22))
    tag_font = _font(max(16, width // 46))
    kick_font = _font(max(13, width // 64))

    title_lines = _wrap(draw, lines["title"], title_font, width - 2 * pad)
    tag_lines = _wrap(draw, lines["tagline"], tag_font, width - 2 * pad)
    kick_lines = _wrap(draw, lines["kicker"], kick_font, width - 2 * pad)

    title_h = (title_font.size + 10) * len(title_lines)
    tag_h = (tag_font.size + 8) * len(tag_lines)
    kick_h = (kick_font.size + 4) * len(kick_lines)
    block_h = title_h + 18 + tag_h + 28 + kick_h
    y = (height - block_h) // 2

    for ln in title_lines:
        draw.text((pad, y), ln, fill=FG, font=title_font)
        y += title_font.size + 10
    y += 18
    for ln in tag_lines:
        draw.text((pad, y), ln, fill=MUTED, font=tag_font)
        y += tag_font.size + 8
    y += 28
    for ln in kick_lines:
        draw.text((pad, y), ln, fill=ACCENT, font=kick_font)
        y += kick_font.size + 4

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG")


def build() -> None:
    lines = banner_lines(CONFIG)
    slots = {s["id"]: s for s in manifest_util.load()["slots"]}
    for slot_id in ("banner", "social-preview"):
        s = slots[slot_id]
        _render(s["width"], s["height"], lines, REPO_ROOT / s["path"])
        print(f"[brand] {slot_id} -> {s['path']} ({s['width']}x{s['height']})")
    manifest_util.mark_real({"banner": {}, "social-preview": {}})
    print("[brand] banner + social-preview marked real")


if __name__ == "__main__":
    build()

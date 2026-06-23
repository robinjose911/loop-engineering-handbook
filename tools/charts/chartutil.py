"""Shared chart helpers (Stage 2.2).

matplotlib (Agg) configured to emit PNGs at EXACT manifest pixel dimensions.
Charts read each example's own Stage 1 CSV/headline so they are real receipts,
not decoration; the golden-data unit test asserts the plotted series equals the
source values.
"""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"
DPI = 100

# Neutral, owner-agnostic palette (matches the neutral diagram theme).
INK = "#1f2328"
GRID = "#d8dee4"
BLUE = "#3a5bbf"
GREEN = "#2f7d46"
RED = "#b3261e"
GOLD = "#c98a1a"
GRAY = "#5b6b7b"
PALETTE = [BLUE, GREEN, GOLD, RED, GRAY]


def new_fig(width: int, height: int):
    """A figure that will save to exactly width x height pixels (no tight bbox)."""
    fig = plt.figure(figsize=(width / DPI, height / DPI), dpi=DPI)
    return fig


def save_exact(fig, path: Path) -> None:
    """Save at exactly the figure's figsize*dpi (dimensions come from new_fig).
    No bbox_inches='tight', which would crop to a different size."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=DPI, facecolor="white")
    plt.close(fig)


def style_axes(ax) -> None:
    ax.set_facecolor("white")
    ax.grid(True, color=GRID, linewidth=0.8, axis="y")
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID)
    ax.tick_params(colors=GRAY)
    ax.title.set_color(INK)
    ax.xaxis.label.set_color(GRAY)
    ax.yaxis.label.set_color(GRAY)


def read_csv(path: Path) -> list[dict]:
    with path.open() as f:
        return list(csv.DictReader(f))


def headline(slug: str) -> dict:
    return json.loads((EXAMPLES / slug / "headline.json").read_text())

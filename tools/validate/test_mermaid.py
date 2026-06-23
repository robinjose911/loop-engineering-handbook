"""Unit test for the mermaid diagrams (Stage 2.1).

Offline (no kroki call): every declared .mmd source exists, is non-empty, and
opens with a valid mermaid diagram declaration; the committed PNG exists at the
manifest dimensions; and all five diagram slots are marked real.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "diagrams"))
import manifest_util  # noqa: E402
from render_diagrams import DIAGRAMS as SOURCES  # noqa: E402  (single source of truth)

SRC_DIR = REPO_ROOT / "assets" / "diagrams" / "src"
VALID_HEADERS = ("flowchart", "graph", "sequenceDiagram", "stateDiagram", "classDiagram", "erDiagram")

DIAGRAM_SLOTS = {s["id"]: s for s in manifest_util.slots_by_kind("diagram")}


def test_five_diagram_slots_all_real():
    assert len(DIAGRAM_SLOTS) == 5
    placeholders = [sid for sid, s in DIAGRAM_SLOTS.items() if s["status"] != "real"]
    assert not placeholders, f"diagram slots still placeholder: {placeholders}"


@pytest.mark.parametrize("slot_id,src_name", sorted(SOURCES.items()))
def test_source_and_png(slot_id, src_name):
    slot = DIAGRAM_SLOTS[slot_id]
    src = SRC_DIR / src_name
    assert src.exists(), f"missing mermaid source {src_name}"
    text = src.read_text().strip()
    assert text, f"{src_name} is empty"
    assert any(hdr in text for hdr in VALID_HEADERS), (
        f"{src_name} has no recognizable mermaid diagram header"
    )

    png = REPO_ROOT / slot["path"]
    assert png.exists(), f"missing rendered diagram {slot['path']}"
    with Image.open(png) as img:
        assert img.size == (slot["width"], slot["height"]), (
            f"{slot_id} is {img.size}, manifest says {slot['width']}x{slot['height']}"
        )

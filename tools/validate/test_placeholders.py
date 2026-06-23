"""Unit test for placeholder stubs (Stage 0.4).

Every slot in ``assets/manifest.json`` resolves to a file on disk with non-zero
dimensions matching the manifest, and every screenshot (quote-card) slot carries
a source URL + capture checklist + alt text so it is never mistaken for a real
capture.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads((REPO_ROOT / "assets" / "manifest.json").read_text())
SLOTS = MANIFEST["slots"]


@pytest.fixture(scope="session", autouse=True)
def _placeholders_ready():
    """(Re)generate placeholder stubs before these tests run.

    Runs at test time (not collection time) so importing/collecting this module
    never mutates the working tree. ``--force`` makes the suite self-healing: a
    stale or wrong-dimension PNG is regenerated to match the manifest rather
    than failing the dimension assertion. Real (status == "real") slots are left
    untouched by the generator.
    """
    subprocess.run(
        [sys.executable, str(REPO_ROOT / "tools" / "stubs" / "make_placeholders.py"), "--force"],
        cwd=REPO_ROOT,
        check=True,
    )


def test_manifest_has_slots():
    assert SLOTS, "manifest declares no slots"
    ids = [s["id"] for s in SLOTS]
    assert len(ids) == len(set(ids)), "slot ids must be unique"


@pytest.mark.parametrize("slot", SLOTS, ids=[s["id"] for s in SLOTS])
def test_slot_image_exists_with_expected_dimensions(slot):
    path = REPO_ROOT / slot["path"]
    assert path.exists(), f"slot '{slot['id']}' has no file at {slot['path']}"
    with Image.open(path) as img:
        w, h = img.size
    assert w > 0 and h > 0, f"slot '{slot['id']}' image has zero dimensions"
    assert (w, h) == (slot["width"], slot["height"]), (
        f"slot '{slot['id']}' is {w}x{h}, manifest declares {slot['width']}x{slot['height']}"
    )


@pytest.mark.parametrize(
    "slot",
    [s for s in SLOTS if s.get("kind") == "quote-card"],
    ids=[s["id"] for s in SLOTS if s.get("kind") == "quote-card"],
)
def test_screenshot_slot_is_attributed(slot):
    assert slot.get("sourceUrl"), f"quote-card '{slot['id']}' missing sourceUrl"
    assert slot.get("alt"), f"quote-card '{slot['id']}' missing alt text"
    checklist = slot.get("captureChecklist")
    assert isinstance(checklist, list) and checklist, (
        f"quote-card '{slot['id']}' missing capture checklist"
    )
    assert "SCREENSHOT SLOT" in slot.get("label", ""), (
        f"quote-card '{slot['id']}' label must mark it a SCREENSHOT SLOT"
    )

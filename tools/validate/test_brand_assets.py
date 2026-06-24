"""Unit test for banner + social preview + quote-card slots (Stage 6.1-6.2)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "brand"))
import make_brand  # noqa: E402
import manifest_util  # noqa: E402

SLOTS = {s["id"]: s for s in manifest_util.load()["slots"]}
SOURCES = (REPO_ROOT / "SOURCES.md").read_text()


def _ensure_brand():
    if any(SLOTS[s]["status"] != "real" or not (REPO_ROOT / SLOTS[s]["path"]).exists()
           for s in ("banner", "social-preview")):
        make_brand.build()


_ensure_brand()


def test_banner_real_at_size():
    s = manifest_util.slots_by_kind("banner")[0]
    assert s["status"] == "real"
    with Image.open(REPO_ROOT / s["path"]) as img:
        assert img.size == (s["width"], s["height"]) == (1280, 320)


def test_social_preview_meets_github_size():
    s = manifest_util.slots_by_kind("social")[0]
    assert s["status"] == "real"
    with Image.open(REPO_ROOT / s["path"]) as img:
        w, h = img.size
    assert (w, h) == (s["width"], s["height"])
    # GitHub's recommended social-preview is >= 1280x640 (min 1200x630).
    assert w >= 1200 and h >= 630


def test_banner_uses_configured_tagline():
    cfg = json.loads((REPO_ROOT / "repo.config.json").read_text())
    lines = make_brand.banner_lines(cfg)
    assert lines["tagline"] == cfg["tagline"], "banner must render the configured tagline"
    assert make_brand.display_title(cfg)  # non-empty title


def test_quote_card_slots_are_real_and_attributed():
    cards = manifest_util.slots_by_kind("quote-card")
    assert len(cards) == 5
    for s in cards:
        assert s["status"] == "real", f"{s['id']} should be a real captured screenshot"
        assert (REPO_ROOT / s["path"]).exists(), f"{s['id']} screenshot image missing"
        with Image.open(REPO_ROOT / s["path"]) as img:
            assert img.size == (s["width"], s["height"])
        assert s.get("alt"), f"{s['id']} missing alt text"
        assert s.get("sourceUrl"), f"{s['id']} missing sourceUrl"
        # the slot has a row in SOURCES.md: the Slot column backticks the id-tail
        # (e.g. `steinberger`), or the row carries the slot's sourceUrl.
        tail = s["id"].split("-")[-1]
        assert (f"`{tail}`" in SOURCES) or (s.get("sourceUrl", "") in SOURCES), (
            f"{s['id']} has no SOURCES.md row"
        )

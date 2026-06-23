"""SOURCES.md <-> in-text citation bijection (Stage 7.2).

Every section in SOURCES.md is referenced by at least one `SOURCES.md#anchor`
link somewhere in the repo, and every such reference resolves to a real section.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _docutil import HEADING_RE, LINK_RE, gh_slug, md_files  # noqa: E402

SOURCES = REPO_ROOT / "SOURCES.md"


def _sources_section_slugs() -> set[str]:
    text = SOURCES.read_text()
    return {gh_slug(m) for m in re.findall(r"^##\s+(.+?)\s*$", text, re.M)}


def _referenced_anchors() -> set[str]:
    """All #anchors pointed at SOURCES.md from anywhere in the repo."""
    anchors = set()
    for md in md_files():
        for target in LINK_RE.findall(md.read_text()):
            m = re.search(r"SOURCES\.md#([\w-]+)", target)
            if m:
                anchors.add(m.group(1))
    return anchors


def test_every_sources_section_is_referenced():
    sections = _sources_section_slugs()
    referenced = _referenced_anchors()
    assert sections, "SOURCES.md has no ## sections"
    unreferenced = sections - referenced
    assert not unreferenced, f"SOURCES.md sections never cited in-text: {unreferenced}"


def test_every_reference_resolves_to_a_section():
    sections = _sources_section_slugs()
    referenced = _referenced_anchors()
    dangling = referenced - sections
    assert not dangling, f"in-text SOURCES.md#anchor links with no matching section: {dangling}"

"""Unit test for the README hero (Stage 6.3)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _docutil import contract_block  # noqa: E402

README = (REPO_ROOT / "README.md").read_text()
CONTRACT_DOC = (REPO_ROOT / "docs" / "the-loop-contract.md").read_text()


def test_readme_loop_contract_matches_canonical():
    readme_block = contract_block(README)
    doc_block = contract_block(CONTRACT_DOC)
    assert readme_block, "README has no 'Loop in 30 seconds' contract block"
    assert doc_block, "docs/the-loop-contract.md has no contract block"
    assert readme_block == doc_block, "README hero contract must match the canonical template verbatim"


def test_readme_has_loop_in_30_seconds_and_banner():
    assert "Loop in 30 seconds" in README
    assert "![" in README and "assets/banner.png" in README, "README must embed the real banner"


def test_readme_relative_links_resolve():
    for target in re.findall(r"\]\(([^)]+)\)", README):
        if re.match(r"^(https?:)?//", target) or target.startswith("mailto:"):
            continue
        path = target.split("#")[0]
        if not path:
            continue
        assert (REPO_ROOT / path).exists(), f"README links to missing file: {target}"


def test_readme_has_three_nav_buttons():
    for target in ("docs/README.md", "library/README.md", "examples/README.md"):
        assert f"]({target})" in README, f"README missing a button to {target}"

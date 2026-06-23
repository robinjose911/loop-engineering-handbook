"""Unit test for loop-card format + coverage (Stage 4.1-4.2)."""
from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOPS_DIR = REPO_ROOT / "library" / "loops"
sys.path.insert(0, str(REPO_ROOT / "tools" / "library"))
from build_catalog import parse_front_matter  # noqa: E402

CATEGORIES = {"engineering", "operations", "content", "research", "data"}
PRIMITIVES = {"/goal", "/loop", "routine"}
REQUIRED_FM = {"id", "title", "category", "primitive", "use_when", "verify", "tags"}
REQUIRED_SECTIONS = ["## Use when", "## Prompt", "## Verify", "## Steps", "## Notes"]
CONTRACT_FIELDS = ["Goal:", "Context:", "Constraints:", "Done-when:", "Evidence:", "If-blocked:"]
ID_RE = re.compile(r"^[a-z0-9-]+$")

EXAMPLE_SLUGS = {
    "1-overnight-217-review", "2-two-loops-one-repo", "3-claim-ledger-security",
    "4-reproduce-before-fix", "5-ad-spend-reconciliation", "6-rfp-questionnaire-pack",
    "7-deliverability-rescue",
}

CARDS = sorted(LOOPS_DIR.rglob("*.md"))


def test_card_count_in_range():
    assert 15 <= len(CARDS) <= 25, f"expected 15-25 cards, found {len(CARDS)}"


def test_ids_unique():
    ids = [parse_front_matter(p.read_text()).get("id") for p in CARDS]
    assert all(ids), "every card needs an id"
    assert len(ids) == len(set(ids)), f"duplicate card ids: {[i for i in ids if ids.count(i) > 1]}"


def test_at_least_one_card_per_category():
    cats = {parse_front_matter(p.read_text()).get("category") for p in CARDS}
    missing = CATEGORIES - cats
    assert not missing, f"categories with no card: {missing}"


@pytest.mark.parametrize("path", CARDS, ids=[p.stem for p in CARDS])
def test_card_conforms(path):
    text = path.read_text()
    fm = parse_front_matter(text)
    missing = REQUIRED_FM - set(k for k in fm if fm[k] not in (None, "", []))
    assert not missing, f"{path.name} missing/empty front-matter keys: {missing}"
    assert ID_RE.match(fm["id"]), f"{path.name} id not kebab-case: {fm['id']}"
    assert fm["category"] in CATEGORIES, f"{path.name} bad category {fm['category']}"
    assert fm["primitive"] in PRIMITIVES, f"{path.name} bad primitive {fm['primitive']}"
    assert isinstance(fm["tags"], list) and fm["tags"], f"{path.name} tags must be a non-empty list"
    # the card filename matches its id, and lives under its category dir
    assert path.stem == fm["id"], f"{path.name} filename != id {fm['id']}"
    assert path.parent.name == fm["category"], f"{path.name} in wrong category dir"

    for section in REQUIRED_SECTIONS:
        assert section in text, f"{path.name} missing section '{section}'"
    # the Prompt block must reuse the canonical six-field loop contract. Anchor to
    # the '## Prompt' section so an earlier fence elsewhere can't be mistaken for it.
    prompt_section = text.split("## Prompt", 1)[1].split("\n## ", 1)[0]
    block = re.search(r"```(.*?)```", prompt_section, re.S)
    assert block, f"{path.name} has no fenced block in its Prompt section"
    missing_fields = [f for f in CONTRACT_FIELDS if f not in block.group(1)]
    assert not missing_fields, f"{path.name} prompt block missing contract fields: {missing_fields}"


def test_seven_examples_each_have_a_resolving_card():
    referenced = {}
    for p in CARDS:
        fm = parse_front_matter(p.read_text())
        ex = fm.get("example")
        if not ex:
            continue
        target = (p.parent / ex).resolve()
        assert target.exists(), f"{p.name} example link does not resolve: {ex}"
        m = re.search(r"examples/([^/]+)/artifacts\.md$", ex)
        assert m, f"{p.name} example link not an artifacts.md: {ex}"
        referenced[m.group(1)] = p.name
    assert set(referenced) == EXAMPLE_SLUGS, (
        f"example coverage mismatch: have {set(referenced)}, want {EXAMPLE_SLUGS}"
    )

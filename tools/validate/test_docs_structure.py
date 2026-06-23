"""Structure lint for the guide (Stage 3.1-3.5).

Each doc has its required H2 sections; the diagrams a doc claims to embed exist
on disk; the loop contract parses into its six labeled fields; glossary terms are
unique.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DOCS = REPO_ROOT / "docs"

# Required H2s, identified by a distinctive substring of the heading text.
REQUIRED_HEADINGS = {
    "01-what-is-loop-engineering.md": ["Definition", "Where the term came from", "harness"],
    "02-goal-and-loop-basics.md": ["/goal vs /loop", "The decision", "The tool matrix", "The durability ladder"],
    "03-benefits.md": ["Why it works", "Where it pays", "Usage in practice"],
    "04-risks-and-cost.md": ["The cost math", "The failure catalog", "Governance"],
    "05-recommendations-and-tips.md": ["The playbook"],
    "the-loop-contract.md": ["The contract"],
    "glossary.md": ["Loop engineering"],
}

# doc -> diagram PNGs it must embed (relative to repo root)
EMBEDDED_DIAGRAMS = {
    "01-what-is-loop-engineering.md": ["assets/diagrams/lineage.png"],
    "02-goal-and-loop-basics.md": ["assets/diagrams/goal-vs-loop-flowchart.png", "assets/diagrams/durability-ladder.png"],
    "03-benefits.md": ["assets/diagrams/maker-checker.png"],
    "the-loop-contract.md": ["assets/diagrams/anatomy-5-blocks.png"],
}

CONTRACT_FIELDS = ["Goal:", "Context:", "Constraints:", "Done-when:", "Evidence:", "If-blocked:"]


def _read(name: str) -> str:
    return (DOCS / name).read_text()


def _headings(text: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(r"^##\s+(.+?)\s*$", text, re.M)]


@pytest.mark.parametrize("name,required", REQUIRED_HEADINGS.items())
def test_required_headings_present(name, required):
    assert (DOCS / name).exists(), f"missing doc {name}"
    headings = _headings(_read(name))
    for req in required:
        assert any(req in h for h in headings), (
            f"{name} missing an H2 containing '{req}' (have: {headings})"
        )


@pytest.mark.parametrize("name,pngs", EMBEDDED_DIAGRAMS.items())
def test_embedded_diagrams_exist(name, pngs):
    text = _read(name)
    for png in pngs:
        basename = png.split("/")[-1]
        assert basename in text, f"{name} does not embed {basename}"
        assert (REPO_ROOT / png).exists(), f"embedded diagram {png} missing on disk"


def test_loop_contract_has_six_fields():
    text = _read("the-loop-contract.md")
    block = re.search(r"```(.*?)```", text, re.S)
    assert block, "the-loop-contract.md has no fenced contract block"
    body = block.group(1)
    missing = [f for f in CONTRACT_FIELDS if f not in body]
    assert not missing, f"loop contract missing fields: {missing}"


def test_glossary_terms_unique():
    terms = _headings(_read("glossary.md"))
    assert len(terms) >= 8, f"glossary unexpectedly small: {terms}"
    assert len(terms) == len(set(terms)), f"duplicate glossary terms: {terms}"

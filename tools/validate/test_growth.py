"""Unit test for the growth scaffolding (Stage 7.3)."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
GH = REPO_ROOT / ".github"
ISSUE_DIR = GH / "ISSUE_TEMPLATE"


def test_pull_request_template_exists():
    p = GH / "PULL_REQUEST_TEMPLATE.md"
    assert p.exists(), "missing .github/PULL_REQUEST_TEMPLATE.md"
    text = p.read_text()
    assert "loop contract" in text.lower()
    assert "build_catalog.py" in text  # the regenerate step


def test_issue_templates_parse():
    templates = [ISSUE_DIR / "submit-a-loop.md", ISSUE_DIR / "fix-or-bug.md"]
    for t in templates:
        assert t.exists(), f"missing {t}"
        text = t.read_text()
        m = re.match(r"---\n(.*?)\n---", text, re.S)
        assert m, f"{t.name} has no YAML front-matter"
        fm = m.group(1)
        assert re.search(r"^name:\s*\S", fm, re.M), f"{t.name} front-matter missing name"
        assert re.search(r"^about:\s*\S", fm, re.M), f"{t.name} front-matter missing about"
    assert (ISSUE_DIR / "config.yml").exists(), "missing ISSUE_TEMPLATE/config.yml"


def test_topics_listed():
    p = GH / "topics.txt"
    assert p.exists(), "missing .github/topics.txt"
    topics = [ln.strip() for ln in p.read_text().splitlines() if ln.strip() and not ln.startswith("#")]
    assert len(topics) >= 5, f"expected several topics, got {topics}"
    assert "loop-engineering" in topics


def test_agents_md_references_machine_readable_files():
    text = (REPO_ROOT / "AGENTS.md").read_text()
    assert "library/catalog.json" in text
    assert "library/llms.txt" in text


def test_faq_has_the_required_questions():
    faq = (REPO_ROOT / "docs" / "faq.md").read_text().lower()
    assert "is this just ralph" in faq
    assert "bankrupt" in faq
    assert "cowork" in faq


def test_readme_has_star_history_placeholder():
    assert "## Star history" in (REPO_ROOT / "README.md").read_text()


@pytest.mark.parametrize("name", ["submit-a-loop.md", "fix-or-bug.md"])
def test_issue_template_has_body(name):
    body = (ISSUE_DIR / name).read_text().split("---", 2)[-1].strip()
    assert len(body) > 40, f"{name} has no usable body"

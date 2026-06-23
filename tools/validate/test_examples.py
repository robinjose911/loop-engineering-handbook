"""Unit test for the 7 worked examples (Stage 5).

Every artifact/chart a README references exists; every headline number quoted in
the prose equals examples/<slug>/headline.json (the prose<->receipt gate); the
copy-paste prompt block matches the published library card; the teaching label is
present (defensive frame on #3); the index has exactly 7 rows (4 coding / 3 non).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _docutil import contract_block  # noqa: E402

CARD = {
    "1-overnight-217-review": "library/loops/engineering/overnight-217-review.md",
    "2-two-loops-one-repo": "library/loops/engineering/two-loops-one-repo.md",
    "3-claim-ledger-security": "library/loops/engineering/claim-ledger-security.md",
    "4-reproduce-before-fix": "library/loops/engineering/reproduce-before-fix.md",
    "5-ad-spend-reconciliation": "library/loops/operations/ad-spend-reconciliation.md",
    "6-rfp-questionnaire-pack": "library/loops/research/rfp-questionnaire-pack.md",
    "7-deliverability-rescue": "library/loops/content/deliverability-rescue.md",
}
# headline key -> format ("usd" | "int" | "float") that must appear in the README prose
EXPECT = {
    "1-overnight-217-review": [("ungoverned_total_usd", "usd"), ("governed_total_usd", "usd"),
                               ("ungoverned_passes", "int"), ("governed_passes", "int")],
    "2-two-loops-one-repo": [("phase1_conflicts", "int"), ("phase1_clobbers", "int"),
                             ("phase1_reverts", "int"), ("phase2_conflicts", "int"), ("token_ratio", "float")],
    "3-claim-ledger-security": [("raw_findings", "int"), ("reproduced", "int"),
                                ("dismissed", "int"), ("escalated", "int")],
    "4-reproduce-before-fix": [("commits_in_range", "int"), ("repro_attempts", "int"), ("fix_line_count", "int")],
    "5-ad-spend-reconciliation": [("start_variance_usd", "usd"), ("end_variance_usd", "usd"), ("cost_usd", "usd")],
    "6-rfp-questionnaire-pack": [("total_questions", "int"), ("answered", "int"), ("gaps", "int")],
    "7-deliverability-rescue": [("start_score", "int"), ("final_score", "int"), ("target_score", "int")],
}
SLUGS = sorted(CARD)


def _readme(slug: str) -> str:
    return (EXAMPLES / slug / "README.md").read_text()


def _headline(slug: str) -> dict:
    return json.loads((EXAMPLES / slug / "headline.json").read_text())


def _present(value: float, fmt: str, text: str) -> bool:
    """A headline figure counts as 'quoted' only if it appears in **bold** -- a
    deliberate receipt quote. This makes the prose<->receipt gate meaningful even
    for small ints (a bare `\\b1\\b` would match almost any prose)."""
    if fmt == "usd":
        return f"**${value:,.2f}**" in text
    if fmt == "float":
        return f"**{value}**" in text
    return f"**{int(value)}**" in text


@pytest.mark.parametrize("slug", SLUGS)
def test_readme_exists_and_labeled(slug):
    text = _readme(slug)
    assert text.lstrip().startswith("#"), f"{slug} README needs a title"
    assert "reconstruction" in text.lower(), f"{slug} missing the teaching-reconstruction label"
    if slug == "3-claim-ledger-security":
        assert "defensive" in text.lower(), "security example must carry the defensive frame"


@pytest.mark.parametrize("slug", SLUGS)
def test_referenced_files_exist(slug):
    text = _readme(slug)
    base = EXAMPLES / slug
    targets = re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text)
    for t in targets:
        if re.match(r"^([a-z]+:)?//", t) or t.startswith("mailto:"):
            continue
        path = t.split("#")[0]
        if not path:
            continue
        assert (base / path).resolve().exists(), f"{slug} README references missing file: {t}"
    # the chart embed must be present
    assert re.search(r"!\[[^\]]*\]\(\.\./\.\./assets/charts/[^)]+\)", text), f"{slug} README embeds no chart"


@pytest.mark.parametrize("slug", SLUGS)
def test_headline_numbers_quoted(slug):
    text = _readme(slug)
    h = _headline(slug)
    for key, fmt in EXPECT[slug]:
        assert key in h, f"{slug} headline missing key {key}"
        assert _present(h[key], fmt, text), (
            f"{slug} README does not quote {key}={h[key]} (as {fmt}) from headline.json"
        )


@pytest.mark.parametrize("slug", SLUGS)
def test_prompt_block_matches_card(slug):
    readme_block = contract_block(_readme(slug))
    card_block = contract_block((REPO_ROOT / CARD[slug]).read_text())
    assert readme_block, f"{slug} README has no contract block"
    assert card_block, f"{slug} card has no contract block"
    assert readme_block == card_block, f"{slug} README prompt block does not match its library card"


def test_index_has_seven_rows_with_locked_domains():
    text = (EXAMPLES / "README.md").read_text()
    rows = [ln for ln in text.splitlines()
            if ln.lstrip().startswith("|") and re.search(r"\]\([1-7]-[^)]*/README\.md\)", ln)]
    assert len(rows) == 7, f"index should list 7 examples, found {len(rows)}"
    for slug in SLUGS:
        assert (EXAMPLES / slug).is_dir()
        assert any(f"{slug}/README.md" in r for r in rows), f"index missing a row for {slug}"
    cells = [c.strip() for r in rows for c in r.split("|")]
    assert cells.count("coding") == 4, "expected 4 coding examples"
    assert cells.count("non-coding") == 3, "expected 3 non-coding examples"

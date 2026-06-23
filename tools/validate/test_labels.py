"""Label lint (Stage 3.1, reused in Stage 7.2).

Any documentation section that states a volatile fact (a dollar figure, a star
count, or a version string) must carry a label marker -- "as of <Month> <Year>",
"verify before relying", "self-reported", or "illustrative" -- so volatile
specifics are never presented as settled fact. Section-granular: one label marker
covers the section it sits in. Fenced code blocks are exempt.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

LABEL_RE = re.compile(
    r"(as of \w+ 20\d\d|verify before relying|self-reported|illustrative|reconstruction for teaching)",
    re.I,
)
DOLLAR_RE = re.compile(r"\$\s?([\d,]+(?:\.\d+)?)")          # capture the amount
STAR_RE = re.compile(r"\b\d[\d,]*\+?\s*(?:github\s+)?stars?\b", re.I)
VERSION_RE = re.compile(r"\bv\d+\.\d+\b")                    # version strings like v1.2


def _strip_fences(text: str) -> str:
    """Remove fenced code blocks (exempt from the lint). Done BEFORE section
    splitting so a '## ' line inside a fence can't tear the fence apart."""
    return re.sub(r"```.*?```", "", text, flags=re.S)


def _sections(text: str) -> list[tuple[str, str]]:
    """Split into (heading, body) sections at H2 boundaries; preamble first."""
    parts = re.split(r"^(##\s+.+)$", text, flags=re.M)
    sections = [("(preamble)", parts[0])]
    for i in range(1, len(parts), 2):
        sections.append((parts[i].strip(), parts[i + 1] if i + 1 < len(parts) else ""))
    return sections


def _has_volatile(body: str) -> bool:
    """A nonzero dollar figure, a star count, or a version string. $0 / $0.00
    (the 'balanced'/'free' sentinels) are settled, not volatile."""
    for m in DOLLAR_RE.finditer(body):
        try:
            if float(m.group(1).replace(",", "")) > 0:
                return True
        except ValueError:
            pass
    return bool(STAR_RE.search(body) or VERSION_RE.search(body) or "★" in body)


def unlabeled_volatile_sections(path: Path) -> list[str]:
    """Section-scoped (docs/): return headings of sections that state a volatile
    fact without a label in that same section."""
    text = _strip_fences(path.read_text())
    violations = []
    for heading, body in _sections(text):
        if _has_volatile(body) and not LABEL_RE.search(body):
            violations.append(heading)
    return violations


def file_is_unlabeled_volatile(path: Path) -> bool:
    """File-scoped (examples/, library/): a file that states a volatile fact must
    carry a label *somewhere* in it. These trees are wholly synthetic, so one
    teaching/illustrative frame per file is the right disclaimer."""
    text = _strip_fences(path.read_text())
    return _has_volatile(text) and not LABEL_RE.search(text)


DOCS = sorted((REPO_ROOT / "docs").glob("*.md")) + [REPO_ROOT / "README.md"]
SYNTHETIC = sorted((REPO_ROOT / "examples").rglob("*.md")) + sorted((REPO_ROOT / "library").rglob("*.md"))


@pytest.mark.parametrize("doc", DOCS, ids=[p.name for p in DOCS])
def test_docs_volatile_facts_are_labeled(doc):
    """docs/ + the root README: section-scoped (real-world volatility)."""
    violations = unlabeled_volatile_sections(doc)
    assert not violations, (
        f"{doc.name}: these sections state a volatile fact (\\$/stars/version) "
        f"without an 'as of ... / verify before relying / illustrative' label: {violations}"
    )


@pytest.mark.parametrize("doc", SYNTHETIC, ids=[str(p.relative_to(REPO_ROOT)) for p in SYNTHETIC])
def test_synthetic_files_carry_a_teaching_label(doc):
    """examples/ + library/: file-scoped teaching/illustrative frame required."""
    assert not file_is_unlabeled_volatile(doc), (
        f"{doc.relative_to(REPO_ROOT)} states a volatile fact (\\$/stars/version) with no "
        f"'illustrative / reconstruction for teaching / as of ...' label anywhere in the file"
    )


def test_lint_catches_an_unlabeled_fact(tmp_path):
    """Self-test: the lint must flag an unlabeled dollar figure and pass a labeled one."""
    bad = tmp_path / "bad.md"
    bad.write_text("# X\n\n## Cost\n\nIt costs $217.34 per night.\n")
    assert unlabeled_volatile_sections(bad) == ["## Cost"]

    good = tmp_path / "good.md"
    good.write_text("# X\n\n## Cost\n\nIt costs $217.34 per night (illustrative).\n")
    assert unlabeled_volatile_sections(good) == []

    # $0 / $0.00 are settled sentinels, not volatile (no label required).
    zero = tmp_path / "zero.md"
    zero.write_text("# X\n\n## Gate\n\nIt reconciles to `$0.00` and the governed path is $0.\n")
    assert unlabeled_volatile_sections(zero) == []

    # A volatile figure in inline code is still caught (not stripped).
    inline = tmp_path / "inline.md"
    inline.write_text("# X\n\n## Spend\n\nProduction hits `$5000/mo`.\n")
    assert unlabeled_volatile_sections(inline) == ["## Spend"]

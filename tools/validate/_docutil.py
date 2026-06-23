"""Shared markdown helpers for the validator suite (not a test module)."""
from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
IGNORE_DIRS = {".git", ".venv", "venv", "node_modules", "dist", "samples",
               ".pytest_cache", "__pycache__", ".claude"}
LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.+?)\s*$", re.M)


def md_files() -> list[Path]:
    """Every shipped .md (excludes git-ignored trees + CLAUDE.md)."""
    out = []
    for p in REPO_ROOT.rglob("*.md"):
        parts = p.relative_to(REPO_ROOT).parts
        if any(part in IGNORE_DIRS for part in parts) or p.name == "CLAUDE.md":
            continue
        out.append(p)
    return sorted(out)


def gh_slug(heading: str) -> str:
    """Approximate github-slugger: lowercase, drop punctuation (keep word chars,
    spaces, hyphens), each space -> one hyphen (no collapse)."""
    s = heading.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"\s", "-", s)
    return s


def heading_slugs(text: str) -> set[str]:
    return {gh_slug(m) for m in HEADING_RE.findall(text)}


def contract_block(text: str) -> str | None:
    """The fenced block holding the six-field loop contract (contains Goal: +
    If-blocked:), normalized by rstripping each line and trimming blank edges.
    Used to compare a README/example prompt block against the canonical template.
    """
    for m in re.finditer(r"```(.*?)```", text, re.S):
        body = m.group(1)
        if "Goal:" in body and "If-blocked:" in body:
            return "\n".join(line.rstrip() for line in body.strip("\n").splitlines())
    return None

"""Unit test for the repo skeleton + config (Stage 0.1 / 0.2).

Asserts every required top-level path exists, ``repo.config.json`` parses with
the required keys, and the build-context files are git-ignored.
"""
from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]

REQUIRED_PATHS = [
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "AGENTS.md",
    "SOURCES.md",
    "repo.config.json",
    ".gitignore",
    ".github",
    "assets",
    "assets/manifest.json",
    "assets/diagrams",
    "assets/diagrams/src",
    "assets/charts",
    "assets/quote-cards",
    "docs",
    "library",
    "library/loops/engineering",
    "library/loops/operations",
    "library/loops/content",
    "library/loops/research",
    "library/loops/data",
    "examples",
    "tools/preview",
    "tools/validate",
    "tools/stubs",
    "tools/links",
    "tools/requirements.txt",
    "tests/e2e",
]

REQUIRED_CONFIG_KEYS = {"owner", "repoName", "theme", "tagline", "badges", "buttons"}


@pytest.mark.parametrize("rel", REQUIRED_PATHS)
def test_required_path_exists(rel):
    assert (REPO_ROOT / rel).exists(), f"missing required path: {rel}"


def test_repo_config_parses_with_required_keys():
    cfg = json.loads((REPO_ROOT / "repo.config.json").read_text())
    missing = REQUIRED_CONFIG_KEYS - set(cfg)
    assert not missing, f"repo.config.json missing keys: {missing}"
    assert isinstance(cfg["badges"], list) and cfg["badges"], "badges must be a non-empty list"
    assert isinstance(cfg["buttons"], list) and cfg["buttons"], "buttons must be a non-empty list"


def test_gitignore_excludes_build_context():
    text = (REPO_ROOT / ".gitignore").read_text()
    assert "/samples/" in text, ".gitignore must exclude /samples/"
    assert "CLAUDE.md" in text, ".gitignore must exclude CLAUDE.md"


def test_build_context_is_git_ignored_when_git_available():
    """Once git is initialized, CLAUDE.md and samples/ must be ignored."""
    if shutil.which("git") is None or not (REPO_ROOT / ".git").exists():
        pytest.skip("git not initialized yet; covered by the .gitignore string check")
    for target in ("CLAUDE.md", "samples"):
        result = subprocess.run(
            ["git", "check-ignore", target],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"git does not ignore {target} (rc={result.returncode})"

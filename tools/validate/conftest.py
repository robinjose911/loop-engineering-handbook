"""Shared fixtures for the validator suite.

Ensure the synthetic artifacts exist before the artifact validators read them,
but **only generate when they are missing** -- so a normal `pytest tools` run
validates the *committed* artifact bytes rather than silently overwriting the
tracked working tree. (The dedicated determinism guard in test_datautil is the
one place that explicitly regenerates and asserts a no-op diff.) Runs at test
time, never at collection time.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXPECTED_EXAMPLES = 7


@pytest.fixture(scope="session", autouse=True)
def generated_artifacts():
    examples = REPO_ROOT / "examples"
    present = len(list(examples.glob("*/headline.json")))
    if present < EXPECTED_EXAMPLES:
        subprocess.run(
            [sys.executable, str(REPO_ROOT / "tools" / "data" / "generate_all.py")],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
        )
    return examples

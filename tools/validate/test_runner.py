"""Unit test for the validator runner (Stage 0.6).

The runner must discover and execute validators and exit non-zero when one
fails. We exercise the runner mechanism via ``all.py --select <fixture>`` so we
never recurse into the real suite: a passing fixture yields rc==0, a
deliberately-failing fixture yields rc!=0.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
ALL_PY = REPO_ROOT / "tools" / "validate" / "all.py"

PASSING = "def test_ok():\n    assert 1 + 1 == 2\n"
FAILING = "def test_bad():\n    assert 1 + 1 == 3\n"


def _run_runner_against(fixture_dir: Path) -> int:
    return subprocess.run(
        [sys.executable, str(ALL_PY), "--select", str(fixture_dir)],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
    ).returncode


def test_runner_passes_on_good_fixture(tmp_path):
    (tmp_path / "test_good_fixture.py").write_text(PASSING)
    assert _run_runner_against(tmp_path) == 0


def test_runner_fails_on_bad_fixture(tmp_path):
    (tmp_path / "test_bad_fixture.py").write_text(FAILING)
    assert _run_runner_against(tmp_path) != 0

#!/usr/bin/env python3
"""Validator runner (Stage 0.6).

Runs every unit validator and exits non-zero on any failure. By default it runs
the full Python validator suite (``pytest tools``) plus the Node preview unit
test (``tools/preview/test_build.mjs``). The ``--select`` flag runs pytest
against a single path instead -- used by ``test_runner.py`` to test the runner
mechanism itself without recursing into the real suite.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _python() -> str:
    return sys.executable or "python3"


def run_selected(target: str) -> int:
    return subprocess.call([_python(), "-m", "pytest", "-q", target], cwd=str(REPO_ROOT))


def run_full() -> int:
    steps = []

    # 1. Python validators.
    steps.append(("pytest tools/", subprocess.call(
        [_python(), "-m", "pytest", "-q", "tools"], cwd=str(REPO_ROOT))))

    # 2. Node preview unit test (skipped with a notice if node is unavailable).
    preview_test = REPO_ROOT / "tools" / "preview" / "test_build.mjs"
    node_modules = REPO_ROOT / "tools" / "preview" / "node_modules"
    if not node_modules.exists():
        print("[runner] NOTE: tools/preview/node_modules missing; "
              "run `npm --prefix tools/preview install` to enable the preview unit test.")
    else:
        try:
            rc = subprocess.call(["node", str(preview_test)], cwd=str(REPO_ROOT))
            steps.append(("node preview/test_build.mjs", rc))
        except FileNotFoundError:
            print("[runner] NOTE: `node` not found on PATH; skipping the preview unit test.")

    print("\n[runner] summary:")
    failed = False
    for name, rc in steps:
        status = "PASS" if rc == 0 else f"FAIL (rc={rc})"
        if rc != 0:
            failed = True
        print(f"  {status:>14}  {name}")
    return 1 if failed else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Run all unit validators.")
    parser.add_argument("--select", help="run pytest against this path only (tests the runner itself)")
    args = parser.parse_args(argv)
    if args.select:
        return run_selected(args.select)
    return run_full()


if __name__ == "__main__":
    raise SystemExit(main())

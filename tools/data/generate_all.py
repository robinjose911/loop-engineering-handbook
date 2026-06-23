#!/usr/bin/env python3
"""Run every synthetic-artifact generator (Stage 1). Deterministic: re-running is
a no-op diff. Usage: python tools/data/generate_all.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import ex1  # noqa: E402
import ex2  # noqa: E402
import ex3  # noqa: E402
import ex4  # noqa: E402
import ex5  # noqa: E402
import ex6  # noqa: E402
import ex7  # noqa: E402

GENERATORS = [ex1, ex2, ex3, ex4, ex5, ex6, ex7]


def main() -> int:
    for mod in GENERATORS:
        h = mod.generate()
        print(f"  example {h['example']}: {h['title']}")
    print(f"[data] generated {len(GENERATORS)} example artifact sets")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

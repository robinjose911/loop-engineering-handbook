#!/usr/bin/env python3
"""Render every chart from the Stage 1 data and mark the manifest slots real.

Usage: python tools/charts/render_all.py
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import charts  # noqa: E402
import manifest_util  # noqa: E402


def main() -> int:
    for slot_id, fn in charts.CHARTS.items():
        data = fn()
        print(f"  {slot_id}: {data}")
    manifest_util.mark_real({slot_id: {} for slot_id in charts.CHARTS})
    print(f"[charts] rendered {len(charts.CHARTS)} charts; manifest slots marked real")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

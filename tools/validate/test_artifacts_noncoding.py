"""Unit test for the non-coding-example artifacts (Stage 1.3): examples 5-7
(non-xlsx parts; the .xlsx gates live in test_xlsx.py)."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"


def _headline(slug: str) -> dict:
    return json.loads((EXAMPLES / slug / "headline.json").read_text())


def _csv(slug: str, name: str) -> list[dict]:
    with (EXAMPLES / slug / name).open() as f:
        return list(csv.DictReader(f))


def _sum_cost(rows: list[dict]) -> float:
    return round(sum(float(r["cost_usd"]) for r in rows), 2)


def _assert_cost_matches(rows: list[dict], expected: float):
    """Both the per-row sum and the running cumulative column must hit the headline."""
    assert _sum_cost(rows) == pytest.approx(expected, abs=0.005)
    assert float(rows[-1]["cumulative_usd"]) == pytest.approx(expected, abs=0.005)


# --- Example 5 (ad-spend) -----------------------------------------------------
def test_ex5_waterfall_and_exceptions():
    slug = "5-ad-spend-reconciliation"
    h = _headline(slug)
    assert h["start_variance_usd"] == 1402.88
    assert h["end_variance_usd"] == 0.00
    assert h["unmatched_rows"] == 0
    # waterfall deltas sum from start to zero
    assert sum(h["waterfall_deltas_usd"]) == pytest.approx(h["start_variance_usd"], abs=0.005)
    assert h["waterfall_usd"][0] == h["start_variance_usd"]
    assert h["waterfall_usd"][-1] == 0.00
    # each step = prior minus the matching delta
    wf, deltas = h["waterfall_usd"], h["waterfall_deltas_usd"]
    for i, delta in enumerate(deltas):
        assert wf[i] - delta == pytest.approx(wf[i + 1], abs=0.005)

    # exceptions-resolved.csv variance impacts sum to the initial variance
    exc = _csv(slug, "exceptions-resolved.csv")
    impact = sum(float(r["variance_impact_usd"]) for r in exc)
    assert impact == pytest.approx(h["start_variance_usd"], abs=0.005)
    _assert_cost_matches(_csv(slug, "cost.csv"), h["cost_usd"])


# --- Example 6 (RFP) ----------------------------------------------------------
def test_ex6_claim_ledger_and_progress():
    slug = "6-rfp-questionnaire-pack"
    h = _headline(slug)
    assert h["total_questions"] == 60
    assert h["answered"] == 58
    assert h["gaps"] == 2

    ledger = _csv(slug, "claim_ledger.csv")
    passes = sum(1 for r in ledger if r["verdict"] == "PASS")
    fails = sum(1 for r in ledger if r["verdict"] == "FAIL")
    assert passes == h["answered"] == 58
    assert fails == h["gaps"] == 2
    # cite-or-cut: every PASS has a source, every FAIL does not
    for r in ledger:
        if r["verdict"] == "PASS":
            assert r["has_source"] == "yes"
        else:
            assert r["has_source"] == "no"

    progress = (EXAMPLES / slug / "progress.md").read_text()
    assert "58/60" in progress
    _assert_cost_matches(_csv(slug, "cost.csv"), h["cost_usd"])


# --- Example 7 (deliverability) ----------------------------------------------
def test_ex7_score_climbs_past_gate():
    slug = "7-deliverability-rescue"
    h = _headline(slug)
    rows = _csv(slug, "score-ledger.csv")
    scores = [int(r["score"]) for r in rows]
    assert scores == h["scores"] == [41, 62, 78, 88, 93, 96]
    assert scores[-1] >= h["target_score"] >= 95
    assert scores[-1] == h["final_score"]
    # monotonic non-decreasing climb
    assert all(b >= a for a, b in zip(scores, scores[1:]))
    # only the final row passes the gate
    assert rows[-1]["gate_status"] == "PASS"
    assert all(r["gate_status"] != "PASS" for r in rows[:-1])
    _assert_cost_matches(_csv(slug, "cost.csv"), h["cost_usd"])

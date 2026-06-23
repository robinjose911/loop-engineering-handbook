"""Unit test for the coding-example artifacts (Stage 1.2): examples 1-4.

Counts reconcile (23 = 9+11+3); each cost.csv cumulative total equals the value
in headline.json; JSONL turns are monotonic with allowed statuses; example 2's
phase-1 token total is ~2.3x phase-2.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"
sys.path.insert(0, str(REPO_ROOT / "tools" / "data"))
from _util import ALLOWED_STATUSES  # noqa: E402


def _headline(slug: str) -> dict:
    return json.loads((EXAMPLES / slug / "headline.json").read_text())


def _csv(slug: str, name: str) -> list[dict]:
    with (EXAMPLES / slug / name).open() as f:
        return list(csv.DictReader(f))


def _jsonl(slug: str, name: str) -> list[dict]:
    return [json.loads(line) for line in (EXAMPLES / slug / name).read_text().splitlines() if line]


def _sum_cost(rows: list[dict]) -> float:
    return round(sum(float(r["cost_usd"]) for r in rows), 2)


def _assert_cost_matches(rows: list[dict], expected: float):
    assert _sum_cost(rows) == pytest.approx(expected, abs=0.005), (
        f"cost.csv sum {_sum_cost(rows)} != headline {expected}"
    )
    assert float(rows[-1]["cumulative_usd"]) == pytest.approx(expected, abs=0.005), (
        "last cumulative != headline"
    )


def _assert_monotonic_turns(records: list[dict]):
    turns = [r["turn"] for r in records]
    assert turns == sorted(turns), "turns not monotonic"
    assert len(turns) == len(set(turns)), "duplicate turns"
    for r in records:
        assert r["status"] in ALLOWED_STATUSES, f"disallowed status: {r['status']}"


# --- Example 1 ----------------------------------------------------------------
def test_ex1_costs_and_log():
    slug = "1-overnight-217-review"
    h = _headline(slug)
    _assert_cost_matches(_csv(slug, "cost.csv"), h["ungoverned_total_usd"])
    _assert_cost_matches(_csv(slug, "cost-governed.csv"), h["governed_total_usd"])
    assert h["ungoverned_total_usd"] == 217.34
    assert h["governed_total_usd"] == 11.20

    log = _jsonl(slug, "loop-log.jsonl")
    assert len(log) == h["ungoverned_passes"] == 91
    _assert_monotonic_turns(log)
    # no new work after pass 4
    for r in log:
        assert r["no_new_work"] == (r["turn"] > 4)


# --- Example 2 ----------------------------------------------------------------
def test_ex2_token_ratio_and_conflicts():
    slug = "2-two-loops-one-repo"
    h = _headline(slug)
    assert h["phase1_conflicts"] == 6
    assert h["phase1_clobbers"] == 2
    assert h["phase1_reverts"] == 1
    assert h["phase2_conflicts"] == 0
    # phase-1 tokens ~ 2.3x phase-2 (within tolerance)
    ratio = h["phase1_tokens"] / h["phase2_tokens"]
    assert abs(ratio - 2.3) < 0.05, f"token ratio {ratio} not ~2.3"
    _assert_cost_matches(_csv(slug, "cost.csv"), h["total_usd"])

    # conflicts.csv corroborates the headline counts
    rows = _csv(slug, "conflicts.csv")
    p1 = [r for r in rows if r["phase"].startswith("phase1")]
    assert sum(1 for r in p1 if r["event"] == "conflict") == 6
    assert sum(1 for r in p1 if r["event"] == "clobber") == 2
    assert sum(1 for r in p1 if r["event"] == "revert") == 1
    p2 = [r for r in rows if r["phase"].startswith("phase2")]
    assert sum(1 for r in p2 if r["event"] in ("conflict", "clobber", "revert")) == 0


# --- Example 3 ----------------------------------------------------------------
def test_ex3_counts_reconcile_and_repro_exists():
    slug = "3-claim-ledger-security"
    h = _headline(slug)
    rows = _csv(slug, "findings-ledger.csv")
    from collections import Counter

    counts = Counter(r["status"] for r in rows)
    assert len(rows) == h["raw_findings"] == 23
    assert counts["reproduced"] == h["reproduced"] == 9
    assert counts["dismissed"] == h["dismissed"] == 11
    assert counts["escalated"] == h["escalated"] == 3
    assert counts["reproduced"] + counts["dismissed"] + counts["escalated"] == 23

    # every reproduced/escalated row has a repro folder on disk
    for r in rows:
        if r["status"] in ("reproduced", "escalated"):
            assert r["repro_path"], f"{r['finding_id']} missing repro_path"
            assert (EXAMPLES / slug / r["repro_path"]).is_dir(), f"missing {r['repro_path']}"
        else:
            assert not r["repro_path"], f"dismissed {r['finding_id']} should have no repro_path"

    _assert_cost_matches(_csv(slug, "cost.csv"), h["total_usd"])
    assert h["repro_share_pct"] > h["triage_share_pct"], "repro should dominate spend"


# --- Example 4 ----------------------------------------------------------------
def test_ex4_repro_gate_and_costs():
    slug = "4-reproduce-before-fix"
    h = _headline(slug)
    assert h["commits_in_range"] == 60
    assert h["fix_line_count"] == 1
    _assert_cost_matches(_csv(slug, "cost.csv"), h["total_usd"])

    log = _jsonl(slug, "loop-log.jsonl")
    _assert_monotonic_turns(log)
    # the gate opens only on/after the reliably-red attempt
    repro_turns = [r for r in log if r["phase"] == "reproduce"]
    assert len(repro_turns) == h["repro_attempts"] == 5
    assert repro_turns[-1]["gate_open"] is True
    assert all(r["gate_open"] is False for r in repro_turns[:-1])
    assert h["repro_phase_share_pct"] > 50, "repro phase should dominate spend"

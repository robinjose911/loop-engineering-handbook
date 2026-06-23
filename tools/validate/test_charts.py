"""Golden-data unit test for the charts (Stage 2.2).

Each chart's extracted series must equal the source CSV/headline values
(independently re-derived here), and the committed PNG must exist at the manifest
dimensions. Charts are extracted with render=False so the test never re-renders
or mutates the tracked PNGs.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

import pytest
from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = REPO_ROOT / "examples"
sys.path.insert(0, str(REPO_ROOT / "tools"))
sys.path.insert(0, str(REPO_ROOT / "tools" / "charts"))
import charts  # noqa: E402
import manifest_util  # noqa: E402

CHART_SLOTS = {s["id"]: s for s in manifest_util.slots_by_kind("chart")}


def _csv(slug, name):
    with (EXAMPLES / slug / name).open() as f:
        return list(csv.DictReader(f))


def _headline(slug):
    return json.loads((EXAMPLES / slug / "headline.json").read_text())


def test_all_chart_slots_real_and_sized():
    assert len(CHART_SLOTS) == 9
    placeholders = [sid for sid, s in CHART_SLOTS.items() if s["status"] != "real"]
    assert not placeholders, f"chart slots still placeholder: {placeholders}"
    for sid, s in CHART_SLOTS.items():
        png = REPO_ROOT / s["path"]
        assert png.exists(), f"missing chart {s['path']}"
        with Image.open(png) as img:
            assert img.size == (s["width"], s["height"]), f"{sid} dim mismatch {img.size}"


def test_cost_curve_matches_csv():
    d = charts.cost_curve_217(render=False)
    ung = _csv("1-overnight-217-review", "cost.csv")
    gov = _csv("1-overnight-217-review", "cost-governed.csv")
    assert d["ungoverned_final"] == pytest.approx(float(ung[-1]["cumulative_usd"]), abs=0.005)
    assert d["governed_final"] == pytest.approx(float(gov[-1]["cumulative_usd"]), abs=0.005)
    h = _headline("1-overnight-217-review")
    assert d["ungoverned_final"] == h["ungoverned_total_usd"]
    assert d["governed_final"] == h["governed_total_usd"]
    assert d["passes"] == len(ung) == 91


def test_collision_matches_csv():
    d = charts.collision_vs_zipper(render=False)
    rows = _csv("2-two-loops-one-repo", "conflicts.csv")
    for cat in ("conflict", "clobber", "revert"):
        exp1 = sum(1 for r in rows if r["phase"].startswith("phase1") and r["event"] == cat)
        assert d["phase1"][cat] == exp1
        assert d["phase2"][cat] == 0
    assert (d["phase1"]["conflict"], d["phase1"]["clobber"], d["phase1"]["revert"]) == (6, 2, 1)


def test_security_funnel_matches_csv():
    d = charts.security_funnel(render=False)
    rows = _csv("3-claim-ledger-security", "findings-ledger.csv")
    assert d["total"] == len(rows) == 23
    assert d["reproduced"] == sum(1 for r in rows if r["status"] == "reproduced") == 9
    assert d["dismissed"] == sum(1 for r in rows if r["status"] == "dismissed") == 11
    assert d["escalated"] == sum(1 for r in rows if r["status"] == "escalated") == 3
    assert d["reproduced"] + d["dismissed"] + d["escalated"] == d["total"]


def test_reproduce_cost_by_phase_matches_csv():
    d = charts.reproduce_cost_by_phase(render=False)
    rows = _csv("4-reproduce-before-fix", "cost.csv")
    for phase in ("reproduce", "bisect", "fix", "verify"):
        exp = round(sum(float(r["cost_usd"]) for r in rows if r["phase"] == phase), 2)
        assert d["by_phase"][phase] == pytest.approx(exp, abs=0.005)
    assert d["by_phase"]["reproduce"] == max(d["by_phase"].values())


def test_ad_spend_waterfall_matches_csv():
    d = charts.ad_spend_waterfall(render=False)
    h = _headline("5-ad-spend-reconciliation")
    assert d["remaining"] == pytest.approx(h["waterfall_usd"], abs=0.005)
    assert d["deltas"] == pytest.approx(h["waterfall_deltas_usd"], abs=0.005)
    assert d["start"] == pytest.approx(h["start_variance_usd"], abs=0.005)
    assert d["remaining"][-1] == pytest.approx(0.0, abs=0.005)


def test_deliverability_climb_matches_csv():
    d = charts.deliverability_climb(render=False)
    rows = _csv("7-deliverability-rescue", "score-ledger.csv")
    assert d["scores"] == [int(r["score"]) for r in rows] == [41, 62, 78, 88, 93, 96]
    assert d["target"] == 95
    assert d["scores"][-1] >= d["target"]


def test_summary_charts_match_sources():
    cov = charts.summary_coverage_climb(render=False)
    h6 = _headline("6-rfp-questionnaire-pack")
    assert cov["ex6_coverage"] == h6["coverage_pct"] == round(100 * 58 / 60, 1)

    costs = charts.summary_cost_accumulation(render=False)["totals"]
    assert costs["Ex 1"] == _headline("1-overnight-217-review")["ungoverned_total_usd"]
    assert costs["Ex 5"] == _headline("5-ad-spend-reconciliation")["cost_usd"]
    assert len(costs) == 7

    fails = charts.summary_failures_over_time(render=False)["series"]
    h1, h2 = _headline("1-overnight-217-review"), _headline("2-two-loops-one-repo")
    assert fails["Ex 1 wasted re-reviews"] == [h1["wasted_passes"], 0]
    assert fails["Ex 2 collision incidents"][0] == (
        h2["phase1_conflicts"] + h2["phase1_clobbers"] + h2["phase1_reverts"]
    )
    assert fails["Ex 2 collision incidents"][1] == h2["phase2_conflicts"] == 0

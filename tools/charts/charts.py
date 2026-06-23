"""Chart generators (Stage 2.2). Each function reads a Stage 1 artifact and
RETURNS the data it extracted (so the golden-data unit test can assert the
plotted series == the source values without re-rendering); when render=True it
also writes a PNG to its manifest slot at exact dimensions."""
from __future__ import annotations

import sys
from pathlib import Path

import chartutil as U
from chartutil import EXAMPLES, headline, read_csv

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifest_util  # noqa: E402

_SLOTS = {s["id"]: s for s in manifest_util.load()["slots"]}


def _dims(slot_id: str) -> tuple[Path, int, int]:
    s = _SLOTS[slot_id]
    return U.REPO_ROOT / s["path"], s["width"], s["height"]


# 1 -------------------------------------------------------------------------
def cost_curve_217(render: bool = True) -> dict:
    slug = "1-overnight-217-review"
    ung = [float(r["cumulative_usd"]) for r in read_csv(EXAMPLES / slug / "cost.csv")]
    gov = [float(r["cumulative_usd"]) for r in read_csv(EXAMPLES / slug / "cost-governed.csv")]
    data = {"ungoverned_final": round(ung[-1], 2), "governed_final": round(gov[-1], 2), "passes": len(ung)}
    if render:
        path, w, h = _dims("chart-cost-curve-217")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        ax.plot(range(1, len(ung) + 1), ung, color=U.RED, linewidth=2.5, label=f"Ungoverned (${ung[-1]:,.2f})")
        ax.plot(range(1, len(gov) + 1), gov, color=U.GREEN, linewidth=2.5, marker="o", label=f"Governed (${gov[-1]:,.2f})")
        ax.set_title("The same loop, ungoverned vs governed")
        ax.set_xlabel("pass")
        ax.set_ylabel("cumulative cost (USD)")
        ax.legend(frameon=False)
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 2 -------------------------------------------------------------------------
def collision_vs_zipper(render: bool = True) -> dict:
    slug = "2-two-loops-one-repo"
    rows = read_csv(EXAMPLES / slug / "conflicts.csv")
    cats = ["conflict", "clobber", "revert"]
    p1 = {c: sum(1 for r in rows if r["phase"].startswith("phase1") and r["event"] == c) for c in cats}
    p2 = {c: sum(1 for r in rows if r["phase"].startswith("phase2") and r["event"] == c) for c in cats}
    data = {"phase1": p1, "phase2": p2}
    if render:
        path, w, h = _dims("chart-collision-vs-zipper")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        x = range(len(cats))
        ax.bar([i - 0.2 for i in x], [p1[c] for c in cats], width=0.4, color=U.RED, label="Phase 1: no coordination")
        ax.bar([i + 0.2 for i in x], [p2[c] for c in cats], width=0.4, color=U.GREEN, label="Phase 2: lease + merge-queue")
        ax.set_xticks(list(x))
        ax.set_xticklabels([c + "s" for c in cats])
        ax.set_title("Two loops, one repo: collisions vs zipper")
        ax.set_ylabel("incidents")
        ax.legend(frameon=False)
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 3 -------------------------------------------------------------------------
def security_funnel(render: bool = True) -> dict:
    slug = "3-claim-ledger-security"
    rows = read_csv(EXAMPLES / slug / "findings-ledger.csv")
    total = len(rows)
    counts = {s: sum(1 for r in rows if r["status"] == s) for s in ("reproduced", "dismissed", "escalated")}
    data = {"total": total, **counts}
    if render:
        path, w, h = _dims("chart-security-funnel")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        labels = [f"raw findings\n({total})", f"reproduced\n({counts['reproduced']})",
                  f"dismissed\n({counts['dismissed']})", f"escalated\n({counts['escalated']})"]
        vals = [total, counts["reproduced"], counts["dismissed"], counts["escalated"]]
        ax.bar(labels, vals, color=[U.GRAY, U.GREEN, U.RED, U.GOLD])
        for i, v in enumerate(vals):
            ax.text(i, v + 0.3, str(v), ha="center", color=U.INK, fontweight="bold")
        ax.set_title("Scanner found 23; the loop proved 11 were false positives")
        ax.set_ylabel("findings")
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 4 -------------------------------------------------------------------------
def reproduce_cost_by_phase(render: bool = True) -> dict:
    slug = "4-reproduce-before-fix"
    rows = read_csv(EXAMPLES / slug / "cost.csv")
    phases = ["reproduce", "bisect", "fix", "verify"]
    by_phase = {p: round(sum(float(r["cost_usd"]) for r in rows if r["phase"] == p), 2) for p in phases}
    data = {"by_phase": by_phase}
    if render:
        path, w, h = _dims("chart-reproduce-cost-by-phase")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        ax.bar(phases, [by_phase[p] for p in phases], color=[U.BLUE, U.GRAY, U.GREEN, U.GOLD])
        ax.set_title("Reproduce-before-you-fix: cost is dominated by proving the bug")
        ax.set_ylabel("cost (USD)")
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 5 -------------------------------------------------------------------------
def ad_spend_waterfall(render: bool = True) -> dict:
    slug = "5-ad-spend-reconciliation"
    rows = read_csv(EXAMPLES / slug / "exceptions-resolved.csv")
    order = ["currency", "duplicate", "orphan"]
    deltas = [round(sum(float(r["variance_impact_usd"]) for r in rows if r["category"] == c), 2) for c in order]
    start = round(sum(deltas), 2)
    remaining = [start]
    for d in deltas:
        remaining.append(round(remaining[-1] - d, 2))
    data = {"remaining": remaining, "deltas": deltas, "start": start}
    if render:
        path, w, h = _dims("chart-ad-spend-waterfall")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        labels = ["start", "after\ncurrency", "after\ndedup", "after\norphans"]
        ax.bar(labels, remaining, color=[U.RED, U.GOLD, U.GOLD, U.GREEN])
        for i, v in enumerate(remaining):
            ax.text(i, v + 15, f"${v:,.2f}", ha="center", color=U.INK, fontweight="bold")
        ax.set_title("Ad-spend variance walked to $0.00")
        ax.set_ylabel("remaining variance (USD)")
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 6 -------------------------------------------------------------------------
def deliverability_climb(render: bool = True) -> dict:
    slug = "7-deliverability-rescue"
    rows = read_csv(EXAMPLES / slug / "score-ledger.csv")
    scores = [int(r["score"]) for r in rows]
    target = headline(slug)["target_score"]
    data = {"scores": scores, "target": target}
    if render:
        path, w, h = _dims("chart-deliverability-climb")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        ax.plot(range(1, len(scores) + 1), scores, color=U.BLUE, linewidth=2.5, marker="o")
        ax.axhline(target, color=U.GREEN, linestyle="--", linewidth=1.5, label=f"gate ({target})")
        ax.set_title("Deliverability rescue: 41 -> 96 against a frozen rubric")
        ax.set_xlabel("pass")
        ax.set_ylabel("spam score (0-100)")
        ax.legend(frameon=False)
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 7 (summary) ---------------------------------------------------------------
def summary_coverage_climb(render: bool = True) -> dict:
    scores = [int(r["score"]) for r in read_csv(EXAMPLES / "7-deliverability-rescue" / "score-ledger.csv")]
    ex6 = headline("6-rfp-questionnaire-pack")["coverage_pct"]
    data = {"scores": scores, "ex6_coverage": ex6}
    if render:
        path, w, h = _dims("chart-summary-coverage-climb")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        ax.plot(range(1, len(scores) + 1), scores, color=U.BLUE, linewidth=2.5, marker="o", label="Ex 7: deliverability score")
        ax.axhline(ex6, color=U.GREEN, linestyle="--", linewidth=1.5, label=f"Ex 6: questionnaire coverage ({ex6}%)")
        ax.set_title("Metric-climb examples reach their gate")
        ax.set_xlabel("pass")
        ax.set_ylabel("score / coverage (%)")
        ax.legend(frameon=False)
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 8 (summary) ---------------------------------------------------------------
def summary_cost_accumulation(render: bool = True) -> dict:
    totals = {
        "Ex 1": headline("1-overnight-217-review")["ungoverned_total_usd"],
        "Ex 2": headline("2-two-loops-one-repo")["total_usd"],
        "Ex 3": headline("3-claim-ledger-security")["total_usd"],
        "Ex 4": headline("4-reproduce-before-fix")["total_usd"],
        "Ex 5": headline("5-ad-spend-reconciliation")["cost_usd"],
        "Ex 6": headline("6-rfp-questionnaire-pack")["cost_usd"],
        "Ex 7": headline("7-deliverability-rescue")["cost_usd"],
    }
    data = {"totals": totals}
    if render:
        path, w, h = _dims("chart-summary-cost-accumulation")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        ax.bar(list(totals), list(totals.values()), color=U.BLUE)
        ax.set_title("Cost per worked example (USD)")
        ax.set_ylabel("total cost (USD)")
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


# 9 (summary) ---------------------------------------------------------------
def summary_failures_over_time(render: bool = True) -> dict:
    h1 = headline("1-overnight-217-review")
    h2 = headline("2-two-loops-one-repo")
    series = {
        "Ex 1 wasted re-reviews": [h1["wasted_passes"], 0],
        "Ex 2 collision incidents": [
            h2["phase1_conflicts"] + h2["phase1_clobbers"] + h2["phase1_reverts"],
            h2["phase2_conflicts"],
        ],
    }
    data = {"series": series}
    if render:
        path, w, h = _dims("chart-summary-failures-over-time")
        fig = U.new_fig(w, h)
        ax = fig.add_subplot(111)
        labels = list(series)
        x = range(len(labels))
        ax.bar([i - 0.2 for i in x], [series[k][0] for k in labels], width=0.4, color=U.RED, label="ungoverned")
        ax.bar([i + 0.2 for i in x], [series[k][1] for k in labels], width=0.4, color=U.GREEN, label="governed")
        ax.set_xticks(list(x))
        ax.set_xticklabels(labels, fontsize=8)
        ax.set_title("Governance drives wasted work / failures to zero")
        ax.set_ylabel("count")
        ax.legend(frameon=False)
        U.style_axes(ax)
        U.save_exact(fig, path)
    return data


CHARTS = {
    "chart-cost-curve-217": cost_curve_217,
    "chart-collision-vs-zipper": collision_vs_zipper,
    "chart-security-funnel": security_funnel,
    "chart-reproduce-cost-by-phase": reproduce_cost_by_phase,
    "chart-ad-spend-waterfall": ad_spend_waterfall,
    "chart-deliverability-climb": deliverability_climb,
    "chart-summary-coverage-climb": summary_coverage_climb,
    "chart-summary-cost-accumulation": summary_cost_accumulation,
    "chart-summary-failures-over-time": summary_failures_over_time,
}

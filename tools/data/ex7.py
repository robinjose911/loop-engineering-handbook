"""Example 7: Deliverability Rescue, climb to 95 (non-coding, /goal).

Newsletter The Tradewind Brief re-engagement email scored by a SEPARATE evaluator
on a frozen spam rubric; rewrite -> re-score climbs 41 -> 62 -> 78 -> 88 -> 93 -> 96
to the >=95 gate. Pattern: metric-climb with an independent grader (writer != scorer).
"""
from __future__ import annotations

from _util import (
    EXAMPLES_DIR,
    cost_rows_from_cents,
    micros_to_usd,
    write_artifacts_index,
    write_csv,
    write_headline,
    write_text,
)

SLUG = "7-deliverability-rescue"
TARGET = 95
SCORES = [41, 62, 78, 88, 93, 96]
SIGNALS = [
    "baseline draft (ALL-CAPS subject, 6 exclamation marks, image-only body, no unsubscribe)",
    "rewrote the subject line in sentence case; removed ALL-CAPS",
    "cut spam-trigger phrases ('ACT NOW', 'FREE', 'limited time') and trimmed exclamations",
    "added a plaintext part and fixed the link-to-text ratio",
    "added a one-click unsubscribe header and sent from an authenticated domain",
    "tuned the preheader and reduced image-heaviness below the rubric threshold",
]
COST_CENTS = [30, 25, 25, 20, 15, 10]  # = 125c = $1.25


def generate() -> dict:
    d = EXAMPLES_DIR / SLUG
    d.mkdir(parents=True, exist_ok=True)

    # score-ledger.csv
    rows = []
    prev = None
    for i, score in enumerate(SCORES):
        delta = "" if prev is None else f"+{score - prev}"
        rows.append([i + 1, score, "PASS" if score >= TARGET else "below gate", delta, SIGNALS[i]])
        prev = score
    write_csv(d / "score-ledger.csv", ["pass", "score", "gate_status", "delta", "signal_fixed"], rows)

    # rubric.md (frozen scorer rules - the independent grader)
    write_text(
        d / "rubric.md",
        "# Spam-score rubric (FROZEN) - the independent grader\n\n"
        "> The writer never sees this file's weights while drafting; a **separate** evaluator\n"
        "> scores each draft. Writer != scorer. Frozen for the duration of the run.\n\n"
        "| Signal | Max points | Rule |\n"
        "|--------|-----------:|------|\n"
        "| Subject line | 20 | No ALL-CAPS, <=1 exclamation, <=60 chars |\n"
        "| Spam phrases | 20 | No known trigger phrases (FREE, ACT NOW, limited time...) |\n"
        "| Text/HTML balance | 20 | Plaintext part present; link-to-text ratio <= 1:20 |\n"
        "| Authentication | 15 | SPF + DKIM + DMARC aligned; authenticated sending domain |\n"
        "| List hygiene | 15 | One-click unsubscribe header present |\n"
        "| Image weight | 10 | <= 40% of body by area; alt text on all images |\n"
        "\n**Gate: a draft passes at a score >= 95 / 100.**\n",
    )

    write_text(
        d / "before.html",
        "<!doctype html><html><body style=\"background:#fee2e2\">\n"
        "<h1>ACT NOW!!! LIMITED TIME OFFER!!!</h1>\n"
        "<p>FREE GIFT!!! CLICK HERE!!! <a href=\"#\">CLICK</a> <a href=\"#\">CLICK</a> "
        "<a href=\"#\">CLICK</a></p>\n"
        "<img src=\"banner.png\" width=\"600\" height=\"800\">\n"
        "<!-- spam score: 41/100 - no unsubscribe, ALL-CAPS, image-only -->\n"
        "</body></html>\n",
    )
    write_text(
        d / "after.html",
        "<!doctype html><html><body style=\"background:#dcfce7\">\n"
        "<h1>We miss you - here's what's new at The Tradewind Brief</h1>\n"
        "<p>It's been a while. Here are three stories we think you'll like, and a quick "
        "way to tell us what to send next.</p>\n"
        "<p><a href=\"https://example.com/read\">Read this week's brief</a></p>\n"
        "<p style=\"font-size:12px\">You're receiving this because you subscribed. "
        "<a href=\"https://example.com/unsubscribe\">Unsubscribe in one click</a>.</p>\n"
        "<!-- spam score: 96/100 - INBOX -->\n"
        "</body></html>\n",
    )

    write_text(
        d / "loop-log.md",
        "# Loop log - The Tradewind Brief deliverability rescue\n\n"
        "> Synthetic reconstruction for teaching. Metric-climb with an independent grader.\n\n"
        "## /goal\n"
        f"Rewrite the re-engagement email until the **independent** spam scorer rates it "
        f">= {TARGET}/100 on the frozen rubric. The writer never edits the scorer.\n\n"
        "## Climb\n"
        + "\n".join(f"- Pass {i + 1}: **{s}/100** - {SIGNALS[i]}" for i, s in enumerate(SCORES))
        + f"\n\nReached **{SCORES[-1]}/100** (gate {TARGET}) on pass {len(SCORES)}. "
        "Red SPAM 41 -> green INBOX 96.\n",
    )

    rows_cost, total_micros = cost_rows_from_cents(COST_CENTS)
    write_csv(
        d / "cost.csv",
        ["pass", "input_tokens", "output_tokens", "cost_usd", "cumulative_usd"],
        [[i + 1, r["input_tokens"], r["output_tokens"], f'{r["cost_usd"]:.2f}', f'{r["cumulative_usd"]:.2f}']
         for i, r in enumerate(rows_cost)],
    )

    headline = {
        "example": 7,
        "title": "Deliverability Rescue (climb to 95)",
        "scores": SCORES,
        "start_score": SCORES[0],
        "final_score": SCORES[-1],
        "target_score": TARGET,
        "passes": len(SCORES),
        "cost_usd": micros_to_usd(total_micros),
    }
    write_headline(d, headline)

    write_artifacts_index(
        d,
        "Example 7 - Deliverability Rescue",
        [
            ("Score ledger (41 -> 96)", "score-ledger.csv"),
            ("Frozen rubric (the grader)", "rubric.md"),
            ("Before (SPAM 41)", "before.html"),
            ("After (INBOX 96)", "after.html"),
            ("Cost ledger", "cost.csv"),
            ("Loop log", "loop-log.md"),
            ("Headline numbers", "headline.json"),
        ],
        note="Synthetic reconstruction for teaching. Independent grader (writer != scorer).",
    )
    return headline


if __name__ == "__main__":
    print(generate())

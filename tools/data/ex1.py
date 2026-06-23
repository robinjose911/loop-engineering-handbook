"""Example 1: The $217 Overnight Code Review (coding, /loop).

Same loop run twice on fictional Meridian/payments-gateway:
- Ungoverned: re-reviews a 12-PR queue 91x overnight, burns $217.34. No new work
  after pass 4, but it never stops.
- Governed (Done-when: no PR changed since last pass; halt after 3 no-progress
  passes; $15/night cap): 4 passes, $11.20.

All costs are exact to the cent (see _util micro-dollar model).
"""
from __future__ import annotations

from pathlib import Path

from _util import (
    EXAMPLES_DIR,
    cost_rows_from_cents,
    micros_to_usd,
    time_seq,
    write_artifacts_index,
    write_csv,
    write_headline,
    write_jsonl,
    write_text,
)

SLUG = "1-overnight-217-review"
PR_QUEUE = 12

# Per-pass cost in cents. Passes 1-4 are productive (real findings); 5-91 are
# near-identical re-reviews that find nothing but still pay to re-read the queue.
UNGOVERNED_CENTS = [560, 528, 504, 480] + [226] * 87  # 91 passes -> 21734c = $217.34
# Governed: one full review, then cheap change-checks; halts after 3 no-progress.
GOVERNED_CENTS = [901, 73, 73, 73]  # 4 passes -> 1120c = $11.20


def generate() -> dict:
    d = EXAMPLES_DIR / SLUG
    d.mkdir(parents=True, exist_ok=True)

    ung_rows, ung_micros = cost_rows_from_cents(UNGOVERNED_CENTS)
    gov_rows, gov_micros = cost_rows_from_cents(GOVERNED_CENTS)

    # ungoverned cost.csv
    write_csv(
        d / "cost.csv",
        ["pass", "input_tokens", "output_tokens", "cost_usd", "cumulative_usd"],
        [[i + 1, r["input_tokens"], r["output_tokens"], f'{r["cost_usd"]:.2f}', f'{r["cumulative_usd"]:.2f}']
         for i, r in enumerate(ung_rows)],
    )
    # governed cost.csv
    write_csv(
        d / "cost-governed.csv",
        ["pass", "input_tokens", "output_tokens", "cost_usd", "cumulative_usd"],
        [[i + 1, r["input_tokens"], r["output_tokens"], f'{r["cost_usd"]:.2f}', f'{r["cumulative_usd"]:.2f}']
         for i, r in enumerate(gov_rows)],
    )

    # loop-log.jsonl (ungoverned): 91 timestamped passes; no_new_work after pass 4.
    ts = time_seq("2026-04-14T23:02:00", step_seconds=297)  # ~5 min between passes
    records = []
    for i, r in enumerate(ung_rows):
        turn = i + 1
        productive = turn <= 4
        records.append(
            {
                "turn": turn,
                "ts": next(ts),
                "pr_queue_size": PR_QUEUE,
                "prs_reviewed": PR_QUEUE,
                "new_findings": [3, 2, 1, 1][i] if productive else 0,
                "no_new_work": not productive,
                "status": "reviewing" if productive else "no_new_work",
                "cost_usd": r["cost_usd"],
                "cumulative_usd": r["cumulative_usd"],
            }
        )
    write_jsonl(d / "loop-log.jsonl", records)

    # comments-posted.md: the same PR commented on 91x.
    comment = (
        "**Automated review (Meridian/payments-gateway PR #482)**\n\n"
        "- Consider extracting the retry backoff into a helper.\n"
        "- `chargeCard()` lacks an idempotency key on the retry path.\n"
        "- Add a test for the partial-capture branch.\n"
    )
    write_text(
        d / "comments-posted.md",
        "# Comments posted (ungoverned run)\n\n"
        f"One PR (#482) received **{len(UNGOVERNED_CENTS)} near-identical** bot comments overnight - "
        "the loop re-reviewed the same unchanged queue every ~5 minutes.\n\n"
        "## Pass 1 (23:02)\n\n" + comment + "\n## Pass 2 (23:07)\n\n" + comment +
        f"\n_... repeated verbatim through pass {len(UNGOVERNED_CENTS)} (07:42). "
        "Passes 5-91 added zero new findings._\n",
    )

    # FIXED-loop-contract.md: the governed contract that stops the bleed.
    write_text(
        d / "FIXED-loop-contract.md",
        "# Governed loop contract (the fix)\n\n"
        "```\n"
        "Goal:       Review every open PR in Meridian/payments-gateway once per change.\n"
        "Context:    Repo at HEAD; the open-PR queue (currently 12).\n"
        "Constraints: Read-only. One comment per PR per *changed* revision.\n"
        "Done-when:  No PR has changed since the last pass.\n"
        "Evidence:   Per-pass diff of PR head SHAs; a posted-comments ledger.\n"
        "If-blocked: Halt after 3 consecutive no-progress passes; hard cap $15/night.\n"
        "```\n\n"
        f"Result: **{len(GOVERNED_CENTS)} passes, ${micros_to_usd(gov_micros):.2f}** "
        f"(vs **{len(UNGOVERNED_CENTS)} passes, ${micros_to_usd(ung_micros):.2f}** ungoverned).\n",
    )

    headline = {
        "example": 1,
        "title": "The $217 Overnight Code Review",
        "pr_queue_size": PR_QUEUE,
        "ungoverned_passes": len(UNGOVERNED_CENTS),
        "governed_passes": len(GOVERNED_CENTS),
        "ungoverned_total_usd": micros_to_usd(ung_micros),
        "governed_total_usd": micros_to_usd(gov_micros),
        "savings_usd": micros_to_usd(ung_micros - gov_micros),
        "wasted_passes": len(UNGOVERNED_CENTS) - 4,
        "pricing": "input $2.00/Mtok, output $8.00/Mtok (illustrative)",
    }
    write_headline(d, headline)

    write_artifacts_index(
        d,
        "Example 1 - The $217 Overnight Code Review",
        [
            ("Ungoverned cost ledger", "cost.csv"),
            ("Governed cost ledger", "cost-governed.csv"),
            ("Loop log (91 passes)", "loop-log.jsonl"),
            ("Comments posted", "comments-posted.md"),
            ("The governed loop contract", "FIXED-loop-contract.md"),
            ("Headline numbers", "headline.json"),
        ],
        note="Synthetic reconstruction for teaching. Circuit-breaker + cost-cap pattern.",
    )
    return headline


if __name__ == "__main__":
    print(generate())

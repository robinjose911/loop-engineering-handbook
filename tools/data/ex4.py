"""Example 4: Reproduce-Before-You-Fix (coding, /goal).

On fictional GridDesk: the loop binary-searches a 60-commit regression and is
forbidden to edit source until a test reliably reproduces the bug. The real fix
is a one-line cache-TTL change - found only after proving the bug was real.
Pattern: reproduction-gate.
"""
from __future__ import annotations

from _util import (
    EXAMPLES_DIR,
    cost_micros,
    micros_to_usd,
    time_seq,
    tokens_for_cents,
    write_artifacts_index,
    write_csv,
    write_headline,
    write_jsonl,
    write_text,
)

SLUG = "4-reproduce-before-fix"
COMMITS_IN_RANGE = 60

# (phase, status, cents). Repro phase dominates spend.
PASSES = (
    [("reproduce", "repro_attempt", 90)] * 5
    + [("bisect", "bisecting", 30)] * 6
    + [("fix", "fix_applied", 5)]
    + [("verify", "verified", 25)]
)
# The reliably-red attempt is the 5th (1-indexed).
RELIABLY_RED_ATTEMPT = 5


def generate() -> dict:
    d = EXAMPLES_DIR / SLUG
    d.mkdir(parents=True, exist_ok=True)

    # cost.csv + loop-log.jsonl share the pass sequence.
    ts = time_seq("2026-05-26T10:00:00", 360)
    rows = []
    records = []
    cum = 0
    repro_micros = 0
    attempt_no = 0
    for turn, (phase, status, cents) in enumerate(PASSES, start=1):
        in_tok, out_tok = tokens_for_cents(cents)
        m = cost_micros(in_tok, out_tok)
        cum += m
        if phase == "reproduce":
            repro_micros += m
            attempt_no += 1
        gate_open = phase != "reproduce" or attempt_no >= RELIABLY_RED_ATTEMPT
        rows.append([turn, phase, in_tok, out_tok, f"{micros_to_usd(m):.2f}", f"{micros_to_usd(cum):.2f}"])
        records.append(
            {
                "turn": turn,
                "ts": next(ts),
                "phase": phase,
                "status": status,
                "gate_open": bool(gate_open),
                "note": _note(phase, attempt_no),
                "cost_usd": micros_to_usd(m),
                "cumulative_usd": micros_to_usd(cum),
            }
        )
    write_csv(
        d / "cost.csv",
        ["turn", "phase", "input_tokens", "output_tokens", "cost_usd", "cumulative_usd"],
        rows,
    )
    write_jsonl(d / "loop-log.jsonl", records)
    total_micros = cum

    # repro-gate.log: 4 flaky attempts, then a reliably-red 5th opens the gate.
    fails = [3, 5, 6, 8, 10]
    gate_lines = ["# Reproduction gate log (GridDesk regression)\n"]
    gate_lines.append("# The gate stays CLOSED (no source edits allowed) until a test is RELIABLY RED.\n")
    for i, f in enumerate(fails, start=1):
        if f >= 10:
            gate_lines.append(f"attempt {i}: ran 10x, {f}/10 failed -> RELIABLY RED. GATE OPEN. source edits permitted.")
        else:
            gate_lines.append(f"attempt {i}: ran 10x, {f}/10 failed -> FLAKY (not reliable). GATE CLOSED.")
    write_text(d / "repro-gate.log", "\n".join(gate_lines))

    # git-bisect-trail.md: 60 -> 1.
    write_text(
        d / "git-bisect-trail.md",
        "# git bisect trail (60-commit regression range)\n\n"
        "Only run after the gate opened (the bug is now reliably reproducible).\n\n"
        "```\n"
        "git bisect start\n"
        "git bisect bad  griddesk@c160   # known bad (today)\n"
        "git bisect good griddesk@c100   # known good (60 commits earlier)\n"
        "bisect: 60 revisions left to test\n"
        "  -> test c130: GOOD   (30 left)\n"
        "  -> test c145: BAD    (15 left)\n"
        "  -> test c137: BAD    (8 left)\n"
        "  -> test c133: GOOD   (4 left)\n"
        "  -> test c135: BAD    (2 left)\n"
        "  -> test c134: BAD    (1 left)\n"
        "c134 is the first bad commit\n"
        "```\n\n"
        "**Culprit:** `c134` shrank a cache TTL from `300s` to `0s`, so a hot path "
        "recomputed on every request under load.\n\n"
        "**Fix (1 line):**\n```diff\n- const CACHE_TTL = 0;\n+ const CACHE_TTL = 300; // seconds\n```\n",
    )

    headline = {
        "example": 4,
        "title": "Reproduce-Before-You-Fix",
        "commits_in_range": COMMITS_IN_RANGE,
        "repro_attempts": RELIABLY_RED_ATTEMPT,
        "fix_line_count": 1,
        "total_usd": micros_to_usd(total_micros),
        "repro_phase_share_pct": round(100 * repro_micros / total_micros, 1),
    }
    write_headline(d, headline)

    write_artifacts_index(
        d,
        "Example 4 - Reproduce-Before-You-Fix",
        [
            ("Cost ledger (repro dominates)", "cost.csv"),
            ("Loop log (gate checks)", "loop-log.jsonl"),
            ("Reproduction gate log", "repro-gate.log"),
            ("git bisect trail (60 -> 1)", "git-bisect-trail.md"),
            ("Headline numbers", "headline.json"),
        ],
        note="Synthetic reconstruction for teaching. Reproduction-gate pattern.",
    )
    return headline


def _note(phase: str, attempt_no: int) -> str:
    if phase == "reproduce":
        return f"repro attempt {attempt_no}: trying to make the bug reliably red"
    if phase == "bisect":
        return "binary-searching the 60-commit regression range"
    if phase == "fix":
        return "one-line cache-TTL change (300s)"
    return "independent re-run confirms the fix; bug no longer reproduces"


if __name__ == "__main__":
    print(generate())

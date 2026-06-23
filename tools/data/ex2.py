"""Example 2: Two Loops, One Repo (coding, /loop x2).

On Solstice/api, a refactor loop + a docs loop.
- Phase 1 (no coordination): 6 conflicts, 2 clobbers, 1 revert; ~2.3x the tokens.
- Phase 2 (lease dir + heartbeat/TTL + merge-queue): 0 conflicts.
"""
from __future__ import annotations

from _util import (
    EXAMPLES_DIR,
    cost_micros,
    micros_to_usd,
    time_seq,
    write_artifacts_index,
    write_csv,
    write_headline,
    write_json,
    write_text,
)

SLUG = "2-two-loops-one-repo"

# (phase, loop, total_tokens) per turn. 80/20 input:output split (multiples of 5).
PHASE1 = [
    ("phase1-uncoordinated", "loop-A-refactor", 500_000),
    ("phase1-uncoordinated", "loop-B-docs", 400_000),
    ("phase1-uncoordinated", "loop-A-refactor", 450_000),
    ("phase1-uncoordinated", "loop-B-docs", 350_000),
    ("phase1-uncoordinated", "loop-A-refactor", 350_000),
    ("phase1-uncoordinated", "loop-B-docs", 250_000),
]  # = 2,300,000 tokens
PHASE2 = [
    ("phase2-coordinated", "loop-A-refactor", 350_000),
    ("phase2-coordinated", "loop-B-docs", 300_000),
    ("phase2-coordinated", "loop-A-refactor", 200_000),
    ("phase2-coordinated", "loop-B-docs", 150_000),
]  # = 1,000,000 tokens


def generate() -> dict:
    d = EXAMPLES_DIR / SLUG
    d.mkdir(parents=True, exist_ok=True)

    # Build a single cost.csv across both phases with a continuous cumulative.
    rows = []
    cum_micros = 0
    p1_tokens = p2_tokens = 0
    for phase_spec, is_p1 in ((PHASE1, True), (PHASE2, False)):
        for turn, (phase, loop, t) in enumerate(phase_spec, start=1):
            out_tok = t // 5
            in_tok = t - out_tok
            m = cost_micros(in_tok, out_tok)
            cum_micros += m
            if is_p1:
                p1_tokens += t
            else:
                p2_tokens += t
            rows.append([phase, loop, turn, in_tok, out_tok, f"{micros_to_usd(m):.2f}", f"{micros_to_usd(cum_micros):.2f}"])
    write_csv(
        d / "cost.csv",
        ["phase", "loop", "turn", "input_tokens", "output_tokens", "cost_usd", "cumulative_usd"],
        rows,
    )
    total_micros = cum_micros

    # conflicts.csv
    ts1 = time_seq("2026-05-02T01:00:00", 180)
    ts2 = time_seq("2026-05-02T02:30:00", 180)
    conflicts = [
        ["phase1-uncoordinated", next(ts1), "loop-B-docs", "src/api/router.ts", "conflict", "edited a file loop-A was mid-refactor on"],
        ["phase1-uncoordinated", next(ts1), "loop-A-refactor", "src/api/router.ts", "clobber", "overwrote loop-B's doc-comment block"],
        ["phase1-uncoordinated", next(ts1), "loop-A-refactor", "src/api/handlers.ts", "conflict", "merge conflict on shared import block"],
        ["phase1-uncoordinated", next(ts1), "loop-B-docs", "README.md", "conflict", "both loops appended to the same section"],
        ["phase1-uncoordinated", next(ts1), "loop-B-docs", "src/api/handlers.ts", "clobber", "reverted loop-A's extracted function"],
        ["phase1-uncoordinated", next(ts1), "loop-A-refactor", "src/api/router.ts", "revert", "human reverted a bad auto-merge"],
        ["phase1-uncoordinated", next(ts1), "loop-A-refactor", "src/api/types.ts", "conflict", "type rename collided with doc example"],
        ["phase1-uncoordinated", next(ts1), "loop-B-docs", "src/api/types.ts", "conflict", "doc snippet referenced a renamed type"],
        ["phase1-uncoordinated", next(ts1), "loop-A-refactor", "src/api/index.ts", "conflict", "export list edited by both loops"],
        ["phase2-coordinated", next(ts2), "loop-B-docs", "src/api/router.ts", "lock_denied", "path locked by loop-A-refactor (lease held)"],
        ["phase2-coordinated", next(ts2), "loop-B-docs", "src/api/router.ts", "backoff", "BACKOFF(30s) then retry after lease released"],
        ["phase2-coordinated", next(ts2), "loop-A-refactor", "src/api/handlers.ts", "lock_acquired", "lease acquired, ttl=120s"],
        ["phase2-coordinated", next(ts2), "loop-B-docs", "README.md", "merge_queued", "change queued; merged after loop-A landed"],
    ]
    write_csv(
        d / "conflicts.csv",
        ["phase", "ts", "loop", "file", "event", "detail"],
        conflicts,
    )

    p1_conflicts = sum(1 for r in conflicts if r[0].startswith("phase1") and r[4] == "conflict")
    p1_clobbers = sum(1 for r in conflicts if r[0].startswith("phase1") and r[4] == "clobber")
    p1_reverts = sum(1 for r in conflicts if r[0].startswith("phase1") and r[4] == "revert")
    p2_conflicts = sum(1 for r in conflicts if r[0].startswith("phase2") and r[4] in ("conflict", "clobber", "revert"))

    # .loop-lease.json snapshot (phase 2)
    lts = time_seq("2026-05-02T02:30:00", 30)
    write_json(
        d / "loop-lease.json",
        {
            "lease_dir": ".loop-lease/",
            "holder": "loop-A-refactor",
            "path_glob": "src/api/**",
            "acquired_ts": next(lts),
            "ttl_seconds": 120,
            "heartbeat_ts": next(lts),
            "merge_queue": ["loop-A-refactor#land", "loop-B-docs#queued"],
            "denied": [
                {
                    "loop": "loop-B-docs",
                    "ts": next(lts),
                    "reason": "path locked by loop-A-refactor",
                    "action": "BACKOFF(30s)",
                }
            ],
        },
    )

    write_text(d / "loop-log-A.md", _loop_log("A (refactor)", "extract retry/backoff helpers; rename types"))
    write_text(d / "loop-log-B.md", _loop_log("B (docs)", "regenerate API reference from source comments"))

    headline = {
        "example": 2,
        "title": "Two Loops, One Repo",
        "phase1_conflicts": p1_conflicts,
        "phase1_clobbers": p1_clobbers,
        "phase1_reverts": p1_reverts,
        "phase2_conflicts": p2_conflicts,
        "phase1_tokens": p1_tokens,
        "phase2_tokens": p2_tokens,
        "token_ratio": round(p1_tokens / p2_tokens, 2),
        "total_usd": micros_to_usd(total_micros),
    }
    write_headline(d, headline)

    write_artifacts_index(
        d,
        "Example 2 - Two Loops, One Repo",
        [
            ("Cost ledger (both phases)", "cost.csv"),
            ("Conflict/coordination events", "conflicts.csv"),
            ("Lease snapshot (phase 2)", "loop-lease.json"),
            ("Loop A log (refactor)", "loop-log-A.md"),
            ("Loop B log (docs)", "loop-log-B.md"),
            ("Headline numbers", "headline.json"),
        ],
        note="Synthetic reconstruction for teaching. Multi-loop coordination (file-lease + merge-queue).",
    )
    return headline


def _loop_log(name: str, goal: str) -> str:
    return (
        f"# Loop {name} log\n\n"
        f"Goal: {goal}.\n\n"
        "## Phase 1 (no coordination)\n"
        "- Edited shared files in `src/api/**` with no lock; collided with the other loop.\n"
        "- Several passes re-did work that the other loop had clobbered.\n\n"
        "## Phase 2 (lease dir + heartbeat/TTL + merge-queue)\n"
        "- Acquire a lease on the path glob before editing; heartbeat every 30s; TTL 120s.\n"
        "- On `LOCK DENIED`, `BACKOFF(30s)` and retry. Land via the merge queue.\n"
        "- Result: zero conflicts.\n"
    )


if __name__ == "__main__":
    print(generate())

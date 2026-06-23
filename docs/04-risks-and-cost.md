# Risks and cost

Loops fail in ways single prompts don't: they run while you sleep, and a small
per-pass cost times thousands of passes is a real bill. This page is the math and
the failure catalog.

## The cost math

> All dollar and token figures on this page use an **illustrative** cost model —
> input **$2.00 / 1M tokens**, output **$8.00 / 1M tokens** — *as of June 2026,
> verify before relying*. The same model generates the worked-example receipts
> (see [SOURCES.md](../SOURCES.md#figures-and-statistics)).

Per-pass cost is just `input_tokens × $2/1M + output_tokens × $8/1M`. Worked
examples (these are recomputed from the token counts by the validator):

<!-- cost-math-table -->

| scenario | input_tokens | output_tokens | cost_usd |
|----------|-------------:|--------------:|---------:|
| one re-review pass over a 12-PR queue | 565000 | 141250 | 2.26 |
| a heavier productive review pass | 1400000 | 350000 | 5.60 |
| a cheap "did anything change?" check | 182500 | 45625 | 0.73 |

The danger is **multiplication**. A 5-minute `/loop` over 3 days is about
`3 × 24 × 12 = 864` passes; at **$2.26** a pass that is roughly **$1,952** — for
work that may have finished on pass 4. The ungoverned run in
[example 1](../examples/1-overnight-217-review/artifacts.md) burned **$217.34**
over 91 passes — 87 of them re-reviewing an unchanged queue and finding nothing
new; the governed run did the same job in 4 passes for **$11.20**
(*illustrative — as of June 2026, verify before relying*).

## The failure catalog

Real ways loops go wrong (each has a governance answer in the next section):

- **Infinite text-gen** — the agent keeps "improving" output that's already done.
- **Unregistered-skill stop-hook** — a stop condition that never fires because
  it depends on a skill/command that isn't wired up.
- **Conflicting temporal constraints** — "every 5 min" + "wait for CI (20 min)"
  stack up overlapping runs.
- **Startup echo** — a loop that re-announces/re-does its first action each boot.
- **Mobile kickoff** — a loop started from a phone with no way to halt it.
- **Multi-loop collisions** — two loops editing the same files (see
  [example 2](../examples/2-two-loops-one-repo/artifacts.md): 6 conflicts, 2
  clobbers, 1 revert before coordination).
- **Termux groundhog-day** — a loop on a device that resets state each run, so it
  repeats pass 1 forever.

## Governance

The controls that turn "run until done" into something safe to leave alone:

- **Sandboxes / worktrees** — contain the blast radius; one loop, one worktree.
- **`max_consecutive_failures`** — halt after N no-progress or failing passes.
- **Wall-clock caps** — stop after N minutes/passes regardless.
- **Cost caps** — a hard `$/run` ceiling (example 1's governed run capped at
  **$15/night**, *illustrative — verify before relying*).
- **Approval gates** — pause for a human on irreversible or ambiguous steps
  (example 5 asks for a classification rule instead of guessing).
- **`LOOP.md`** — a small, durable memory file so a fresh-context pass knows what
  earlier passes already did.

Rule: **decide the stop condition and the cost cap before you start the loop**,
not after the bill arrives.

---

Next: [Recommendations and tips →](05-recommendations-and-tips.md)

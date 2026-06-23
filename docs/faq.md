# FAQ

## Is this just Ralph?

No — the bare "Ralph" loop (re-run a prompt in `while true` until done) is the
*seed*, and it's where the lineage starts (see
[the origin story](01-what-is-loop-engineering.md#where-the-term-came-from)).
Loop engineering is Ralph **plus governance**: a verifiable Done-when, a separate
evaluator (writer ≠ checker), a circuit-breaker, and a cost cap. The bare loop is
the engine; the contract and the governance are the brakes and the steering. The
worked examples are all governed loops, not bare `while true`.

## Won't it bankrupt me?

Only if you run it ungoverned. A small per-pass cost times thousands of passes is
a real bill — that's the whole point of
[example 1](../examples/1-overnight-217-review/README.md), where the ungoverned
run cost ~19× the governed one for the same work ($217.34 vs $11.20, illustrative). The fixes are boring and
effective: a Done-when the loop can't argue with, a no-progress halt, a hard cost
cap, and long intervals. See [the cost math](04-risks-and-cost.md#the-cost-math).

## Does Cowork (or my tool) support it?

The two primitives — *`/goal` with a separate evaluator* and *governed interval
`/loop`* — are tool-agnostic ideas; most agent tools can express them, with
varying durability (see the
[tool matrix](02-goal-and-loop-basics.md#the-tool-matrix) and the
[durability ladder](02-goal-and-loop-basics.md#the-durability-ladder)). The matrix
is *illustrative — as of June 2026, verify before relying* against each tool's
current docs. Bet on the primitives, not a specific wrapper.

## Is everything here real?

No — it's **synthetic and safe** by design: fictional orgs, toy repos, made-up
datasets, every example labeled "reconstruction for teaching." The *receipts*
(logs, ledgers, `.xlsx`) are generated and machine-checked to agree with the
prose, so the mechanics are real even though the data isn't.

---

Back to [the guide index](README.md).

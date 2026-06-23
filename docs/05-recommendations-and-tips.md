# Recommendations and tips

## The playbook

Opinionated defaults, learned from the worked examples:

1. **Verifier-first.** Write the done-condition and the evaluator *before* the
   prompt. If you can't state how a separate checker decides "done," you're not
   ready to loop.
2. **`/goal` first for babysat work.** If there's a verifiable finish line, run
   depth-first to it and stop — don't reach for an interval loop.
3. **`/loop` as a security camera.** Use the interval primitive for genuinely
   ongoing patrols (a queue, a regression watch), not for work that has an end.
4. **Long intervals beat short ones.** A 5-minute loop is almost always wrong;
   most "watch" jobs are fine at 30–60 minutes and cost a fraction (see the cost
   math in [risks and cost](04-risks-and-cost.md#the-cost-math)).
5. **Graduate to durable tools.** Once a loop is trustworthy, move it up the
   [durability ladder](02-goal-and-loop-basics.md#the-durability-ladder) — Codex
   → Automations, Claude Code → scheduled agents — so it survives you logging off.
6. **Contain the blast radius.** One loop per worktree/sandbox; read-only unless
   it has earned write; a cost cap on every loop.
7. **Bet on the primitives, not the wrapper.** Tools change; *goal-with-an-
   evaluator* and *governed-interval* are the durable ideas. Design to those.

## The loop contract

Every recommendation above collapses into one artifact: a filled-in
[loop contract](the-loop-contract.md). Copy it, fill the six fields, and you have
a governed loop. See also the [glossary](glossary.md) for the terms used here.

---

Back to [the guide index](README.md).

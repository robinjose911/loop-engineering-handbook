---
id: overnight-217-review
title: Overnight Code Review (governed)
category: engineering
primitive: /loop
use_when: You want an agent to review an open-PR queue continuously, without it re-reviewing unchanged PRs forever.
verify: No PR has changed head SHA since the last pass; cost stays under the nightly cap.
tags: [code-review, circuit-breaker, cost-cap]
example: ../../../examples/1-overnight-217-review/artifacts.md
---

# Overnight Code Review (governed)

> A patrol loop that reviews each PR once per change — with a circuit-breaker and a cost cap so it can't bill you for re-reviewing an unchanged queue. Primitive: `/loop` · Category: `engineering`

## Use when

You have an open-PR queue and want fresh review comments as PRs change, overnight or between standups — but you do not want the loop re-reading the whole queue every five minutes.

## Prompt

```
Goal:        Review every open PR in <repo> once per changed revision.
Context:     <repo> at HEAD; the open-PR queue and each PR's head SHA.
Constraints: Read-only. One comment per PR per changed SHA. Hard cap <$N>/night.
Done-when:   No PR has changed head SHA since the last pass.
Evidence:    A per-pass diff of PR head SHAs; a posted-comments ledger.
If-blocked:  Halt after 3 consecutive no-progress passes; never exceed the cost cap.
```

## Verify

A separate check compares each PR's head SHA to the prior pass. If none changed, the done-condition holds and the loop halts. The comments ledger must show at most one comment per PR per SHA.

## Steps

1. Snapshot the PR queue and head SHAs.
2. Review only PRs whose SHA changed since last pass.
3. Record cost and SHAs; halt on 3 no-progress passes or the cap.

## Notes

Ungoverned, this exact loop re-reviewed an unchanged 12-PR queue 91 times overnight; governed, it did the same job in 4 passes. See the worked example with the full cost receipts: [the overnight review](../../../examples/1-overnight-217-review/artifacts.md).

---
id: deliverability-rescue
title: Deliverability Rescue (climb to a gate)
category: content
primitive: /goal
use_when: An email/landing page must clear a spam/quality score and you want a writer-vs-scorer loop to climb to it.
verify: A separate scorer rates the final draft at or above the gate on a frozen rubric.
tags: [email, metric-climb, independent-grader]
example: ../../../examples/7-deliverability-rescue/artifacts.md
---

# Deliverability Rescue (climb to a gate)

> Rewrite -> re-score against a *separate* grader on a frozen rubric until the score clears the gate. Primitive: `/goal` · Category: `content`

## Use when

You have copy that must clear a threshold (spam score, readability, brand checklist) and you want the agent to improve it iteratively — without grading its own work.

## Prompt

```
Goal:        Rewrite <asset> until the independent scorer rates it >= <gate>/100.
Context:     The draft; a FROZEN rubric; a separate scorer that never sees the writer's reasoning.
Constraints: The writer may not edit the rubric or the scorer (writer != scorer).
Done-when:   The separate scorer returns a score >= <gate> on the frozen rubric.
Evidence:    A score ledger (one row per pass, with the signal fixed); before/after drafts.
If-blocked:  After <K> passes without improvement, stop and surface the stuck signal.
```

## Verify

A separate scorer — not the writer — evaluates the final draft against the frozen rubric and must return a score at or above the gate. The ledger must show a non-decreasing climb.

## Steps

1. Score the baseline draft with the independent scorer.
2. Fix the lowest-scoring signal; re-score; repeat.
3. Stop when the score clears the gate (or stalls).

## Notes

The worked example climbs a spam score from 41 to 96 against a frozen rubric. See [deliverability rescue](../../../examples/7-deliverability-rescue/artifacts.md).

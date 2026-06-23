---
id: data-quality-gate
title: Data-Quality Gate Patrol
category: data
primitive: /loop
use_when: You want a patrol that checks a dataset/table against quality rules and blocks or flags on violations.
verify: Every flagged row violates a stated rule; a clean pass reports zero violations against the rule set.
tags: [data-quality, validation-gate, patrol]
---

# Data-Quality Gate Patrol

> A patrol loop that runs a frozen rule set over a dataset and flags every violation — a quality gate, not a vibe check. Primitive: `/loop` · Category: `data`

## Use when

A table feeds downstream jobs and you want continuous assurance it meets quality rules (no nulls in keys, ranges, referential integrity) — with violations flagged precisely, not summarized.

## Prompt

```
Goal:        Enforce the data-quality rule set on <dataset> each pass.
Context:     The dataset; a FROZEN rule set (key non-null, ranges, FK integrity, uniqueness).
Constraints: Read-only. Flag only rows that violate a stated rule; cite the rule per flag.
Done-when:   This pass reports zero violations, or every violation is flagged with its rule.
Evidence:    A violations ledger (row id, rule, value); the pass summary (counts per rule).
If-blocked:  If a rule can't be evaluated (missing column), report it; don't pass silently.
```

## Verify

A separate check confirms each flagged row actually violates the cited rule, and that a "clean" pass genuinely produced zero violations across the whole rule set.

## Steps

1. Load the dataset and the frozen rule set.
2. Evaluate every rule; record violations with the rule cited.
3. Summarize counts per rule; block/alert on threshold breaches.

## Notes

Freeze the rule set the way the deliverability example freezes its rubric — the gate must be stable across passes, or "improvement" is unmeasurable.

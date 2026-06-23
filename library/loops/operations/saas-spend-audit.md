---
id: saas-spend-audit
title: SaaS Spend-Audit Circuit-Breaker
category: operations
primitive: /loop
use_when: You want a recurring audit of SaaS/cloud spend that flags anomalies but can't run up its own bill.
verify: Each flagged line exceeds its baseline by the configured threshold; the audit itself stays under a cost cap.
tags: [finops, anomaly, cost-cap]
---

# SaaS Spend-Audit Circuit-Breaker

> A recurring spend audit with a hard cost cap on the auditor itself — it flags overspend without becoming overspend. Primitive: `/loop` · Category: `operations`

## Use when

Cloud/SaaS bills drift and nobody notices until renewal. You want a periodic loop that compares current spend to a baseline and flags anomalies — governed so the audit never costs more than it saves.

## Prompt

```
Goal:        Flag SaaS/cloud line items that exceed their baseline by > <X>%.
Context:     The current billing export; a rolling baseline per line item.
Constraints: Read-only. Hard cap <$N>/run on the audit itself.
Done-when:   Every line item this pass is within threshold, or flagged with the delta.
Evidence:    An anomalies ledger (item, baseline, current, delta%); the run cost.
If-blocked:  Halt at the cost cap and report partial results rather than overrunning.
```

## Verify

A separate check confirms each flagged item's delta actually exceeds the threshold versus its baseline, and that the recorded run cost is under the cap.

## Steps

1. Pull the latest billing export.
2. Compare each line to its baseline; flag items over threshold.
3. Update baselines; stop at the cap.

## Notes

Run daily or weekly, not hourly. The circuit-breaker (cost cap) is the point — an ungoverned audit loop is itself a spend anomaly.

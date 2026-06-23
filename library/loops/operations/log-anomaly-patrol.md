---
id: log-anomaly-patrol
title: Log-Anomaly Patrol
category: operations
primitive: /loop
use_when: You want a security-camera loop that watches logs for new error signatures and opens an issue once per signature.
verify: Each opened issue maps to an error signature not seen in the prior window; no duplicate issues.
tags: [observability, patrol, dedupe]
---

# Log-Anomaly Patrol

> A patrol loop that watches a log stream for *new* error signatures and files one issue per signature. Primitive: `/loop` · Category: `operations`

## Use when

Errors scroll past faster than anyone reads them. You want a loop that clusters log lines into signatures and alerts only on genuinely new ones — not the same noisy error every interval.

## Prompt

```
Goal:        Open one tracking issue per NEW error signature in <log source>.
Context:     The log stream for the last interval; the set of signatures already seen.
Constraints: Read-only on logs. Dedupe by signature; never file a duplicate issue.
Done-when:   Every signature this window is either already-seen or has an issue filed.
Evidence:    A signatures ledger (signature -> first-seen, issue link); the per-pass diff.
If-blocked:  If a signature's volume spikes, escalate (page) instead of just filing.
```

## Verify

A separate check confirms each filed issue corresponds to a signature absent from the prior-window ledger, and that no signature has two issues.

## Steps

1. Cluster the window's log lines into signatures.
2. Diff against the seen-set; file an issue for each new signature.
3. Update the seen-set; escalate spikes.

## Notes

Long intervals are fine here — a 30–60 minute patrol catches new signatures without re-scanning the same noise every few minutes.

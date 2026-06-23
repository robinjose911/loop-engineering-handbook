---
id: two-loops-one-repo
title: Two Loops, One Repo (coordinated)
category: engineering
primitive: /loop
use_when: You want two agents (e.g. a refactor loop and a docs loop) working the same repo without clobbering each other.
verify: Zero merge conflicts, clobbers, or reverts across a run; every edit held a lease.
tags: [multi-loop, file-lease, merge-queue]
example: ../../../examples/2-two-loops-one-repo/artifacts.md
---

# Two Loops, One Repo (coordinated)

> Run two loops on one repo with a file-lease + merge-queue so they zip instead of collide. Primitive: `/loop` · Category: `engineering`

## Use when

Two independent loops need to edit overlapping paths (refactor + docs, code + tests). Without coordination they overwrite each other; with a lease they take turns.

## Prompt

```
Goal:        Make <change A> and <change B> on <repo> with two loops, no conflicts.
Context:     <repo>; a lease dir (.loop-lease/) holding path-glob leases with TTL.
Constraints: Acquire a lease on your path glob before editing; heartbeat every 30s.
Done-when:   Both changes landed via the merge queue with zero conflicts/clobbers.
Evidence:    A conflicts ledger (must be 0); lease snapshots; the merge-queue order.
If-blocked:  On LOCK DENIED, BACKOFF(30s) and retry; never edit a leased path.
```

## Verify

A separate check reads the conflicts ledger: conflicts, clobbers, and reverts must all be zero, and every edit must map to a held lease.

## Steps

1. Each loop requests a lease on its path glob (TTL + heartbeat).
2. On denial, back off and retry; on grant, edit then land via the merge queue.
3. Record every lease grant/denial and merge to the ledger.

## Notes

Uncoordinated, this scenario produced 6 conflicts, 2 clobbers, and 1 revert; coordinated, zero. See [two loops, one repo](../../../examples/2-two-loops-one-repo/artifacts.md).

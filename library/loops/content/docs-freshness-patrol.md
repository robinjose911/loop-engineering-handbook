---
id: docs-freshness-patrol
title: Docs-Freshness Patrol
category: content
primitive: /loop
use_when: You want a patrol that flags docs whose code examples or referenced APIs have drifted from the codebase.
verify: Each flagged doc references a symbol/path that no longer exists or a snippet that no longer compiles.
tags: [docs, drift, patrol]
---

# Docs-Freshness Patrol

> A patrol loop that flags docs whose examples or referenced symbols have drifted from the code. Primitive: `/loop` · Category: `content`

## Use when

Docs rot quietly: a renamed function, a removed flag, a snippet that no longer compiles. You want a loop that catches drift and files it, once per stale doc.

## Prompt

```
Goal:        Flag docs in <docs path> whose code references no longer match <repo>.
Context:     The docs tree; the current codebase (symbols, paths, runnable snippets).
Constraints: Read-only. Flag only verifiable drift (missing symbol/path, failing snippet).
Done-when:   Every doc this pass either verifies clean or has a drift issue filed.
Evidence:    A drift ledger (doc -> stale reference -> evidence); the per-pass diff.
If-blocked:  If a snippet can't be executed safely, flag it for manual review, don't guess.
```

## Verify

A separate check confirms each flagged item points to a symbol/path genuinely absent from the codebase, or a snippet that genuinely fails to compile/run.

## Steps

1. Extract code references and runnable snippets from each doc.
2. Check each against the current codebase.
3. File one drift issue per stale doc; dedupe across passes.

## Notes

Run on a slow cadence (daily). Pair with the changelog loop so docs and notes move together at release time.

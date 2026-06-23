---
id: schema-migration-backfill
title: Schema-Migration Backfill
category: data
primitive: /goal
use_when: You're backfilling a new column/table and need every affected row migrated with a verifiable invariant.
verify: Post-migration, the invariant holds for 100% of affected rows and counts match the pre-migration plan.
tags: [migration, backfill, invariant]
---

# Schema-Migration Backfill

> Backfill a migration to a verifiable invariant, in batches, with a row-count plan that must tie out. Primitive: `/goal` · Category: `data`

## Use when

You added a column or derived table and must backfill historical rows. You want the loop to migrate in safe batches and prove, at the end, that every affected row is correct — not just that the script ran.

## Prompt

```
Goal:        Backfill <column/table> for all affected rows in <dataset>.
Context:     The migration spec; the affected-row query; a batch size; the target invariant.
Constraints: Migrate in idempotent batches. Never exceed <batch> rows per pass.
Done-when:   The invariant holds for 100% of affected rows AND migrated count == planned count.
Evidence:    A per-batch ledger (range, rows, invariant-check); a final reconciliation.
If-blocked:  On any batch where the invariant fails, halt and report; do not continue blindly.
```

## Verify

A separate check runs the invariant query over all affected rows (must be 100% satisfied) and confirms the migrated row count equals the pre-migration plan's count.

## Steps

1. Compute the affected-row set and the planned count.
2. Migrate in idempotent batches; check the invariant per batch.
3. Reconcile final counts and the global invariant before declaring done.

## Notes

Idempotent batches make the loop safe to resume after a halt — a fresh-context pass re-runs a batch without double-applying.

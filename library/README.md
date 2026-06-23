# The prompt library

17 copy-paste **loop cards**, organized by category. Each card has a
Use-when, a fill-in-the-blanks prompt (the canonical six-field
[loop contract](../docs/the-loop-contract.md)), a Verify step, Steps, and Notes.

Machine-readable: [`catalog.json`](catalog.json) (validated against
[`catalog.schema.json`](catalog.schema.json)) · agent instructions:
[`llms.txt`](llms.txt).

## Engineering

| Card | Primitive | Use when | Example |
|------|-----------|----------|---------|
| [Claim-Ledger Security Triage](loops/engineering/claim-ledger-security.md) | `/goal` | A scanner dumped a pile of findings and you want only the ones backed by a runnable repro. | [worked](../examples/3-claim-ledger-security/artifacts.md) |
| [Flaky-Test Quarantine Warden](loops/engineering/flaky-test-quarantine.md) | `/loop` | Flaky tests are eroding trust in CI and you want a loop to detect, quarantine, and file them. | - |
| [Overnight Code Review (governed)](loops/engineering/overnight-217-review.md) | `/loop` | You want an agent to review an open-PR queue continuously, without it re-reviewing unchanged PRs forever. | [worked](../examples/1-overnight-217-review/artifacts.md) |
| [Reproduce-Before-You-Fix](loops/engineering/reproduce-before-fix.md) | `/goal` | A regression needs fixing and you want to forbid touching source until the bug is reliably reproduced. | [worked](../examples/4-reproduce-before-fix/artifacts.md) |
| [Two Loops, One Repo (coordinated)](loops/engineering/two-loops-one-repo.md) | `/loop` | You want two agents (e.g. a refactor loop and a docs loop) working the same repo without clobbering each other. | [worked](../examples/2-two-loops-one-repo/artifacts.md) |

## Operations

| Card | Primitive | Use when | Example |
|------|-----------|----------|---------|
| [Ad-Spend Reconciliation](loops/operations/ad-spend-reconciliation.md) | `/goal` | You need messy invoices reconciled against a bank export to a hard zero-variance gate. | [worked](../examples/5-ad-spend-reconciliation/artifacts.md) |
| [Log-Anomaly Patrol](loops/operations/log-anomaly-patrol.md) | `/loop` | You want a security-camera loop that watches logs for new error signatures and opens an issue once per signature. | - |
| [SaaS Spend-Audit Circuit-Breaker](loops/operations/saas-spend-audit.md) | `/loop` | You want a recurring audit of SaaS/cloud spend that flags anomalies but can't run up its own bill. | - |

## Content

| Card | Primitive | Use when | Example |
|------|-----------|----------|---------|
| [Changelog From Commits](loops/content/changelog-from-commits.md) | `/goal` | You want a release changelog drafted only from the actual commit/PR history, with every entry traceable. | - |
| [Deliverability Rescue (climb to a gate)](loops/content/deliverability-rescue.md) | `/goal` | An email/landing page must clear a spam/quality score and you want a writer-vs-scorer loop to climb to it. | [worked](../examples/7-deliverability-rescue/artifacts.md) |
| [Docs-Freshness Patrol](loops/content/docs-freshness-patrol.md) | `/loop` | You want a patrol that flags docs whose code examples or referenced APIs have drifted from the codebase. | - |

## Research

| Card | Primitive | Use when | Example |
|------|-----------|----------|---------|
| [Claim-Verify Research Brief](loops/research/claim-verify-research.md) | `/goal` | You want a research brief where every claim is independently verified before it is allowed to stay. | - |
| [Competitive-Intel Digest](loops/research/competitive-intel-digest.md) | `routine` | You want a scheduled digest of changes to a watchlist of competitor pages, with each claim linked to its source. | - |
| [RFP / Security Questionnaire Pack](loops/research/rfp-questionnaire-pack.md) | `/goal` | You must answer a long questionnaire and every answer has to cite an approved source or be left as a gap. | [worked](../examples/6-rfp-questionnaire-pack/artifacts.md) |

## Data

| Card | Primitive | Use when | Example |
|------|-----------|----------|---------|
| [Messy-CSV Normalizer](loops/data/csv-normalizer.md) | `/goal` | You have messy CSVs (mixed formats, currencies, dates, encodings) to normalize to a target schema. | - |
| [Data-Quality Gate Patrol](loops/data/data-quality-gate.md) | `/loop` | You want a patrol that checks a dataset/table against quality rules and blocks or flags on violations. | - |
| [Schema-Migration Backfill](loops/data/schema-migration-backfill.md) | `/goal` | You're backfilling a new column/table and need every affected row migrated with a verifiable invariant. | - |

[Back to the handbook](../README.md)

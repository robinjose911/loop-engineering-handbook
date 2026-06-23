---
id: competitive-intel-digest
title: Competitive-Intel Digest
category: research
primitive: routine
use_when: You want a scheduled digest of changes to a watchlist of competitor pages, with each claim linked to its source.
verify: Every digest item links to the specific source page and quotes the changed text; nothing is unsourced.
tags: [monitoring, digest, routine]
---

# Competitive-Intel Digest

> A scheduled routine that diffs a competitor watchlist and digests only what changed, each item linked to its source. Primitive: `routine` · Category: `research`

## Use when

You track a handful of competitor pages (pricing, changelog, docs) and want a periodic digest of real changes — not a re-summary of unchanged pages — with every claim traceable to the page it came from.

## Prompt

```
Goal:        Produce a <cadence> digest of CHANGES to the watchlist pages.
Context:     The watchlist URLs; the previously captured snapshot of each.
Constraints: Report only changed content. Every item must link + quote the source.
Done-when:   Every changed page has a digest item; unchanged pages are omitted.
Evidence:    A digest (item, source URL, quoted change); the snapshot diff per page.
If-blocked:  If a page is unreachable, note it as "could not fetch", don't infer changes.
```

## Verify

A separate check confirms each digest item maps to a page whose snapshot actually changed, and that the quoted text appears on the source page.

## Steps

1. Re-fetch each watchlist page; diff against the prior snapshot.
2. Digest only the changed pages, quoting + linking the change.
3. Save new snapshots for next run.

## Notes

This is a `routine` (durable, scheduled), not a session `/loop` — it should keep running after you log off. Weekly or daily is plenty; sub-hourly just re-fetches unchanged pages.

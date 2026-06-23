---
id: csv-normalizer
title: Messy-CSV Normalizer
category: data
primitive: /goal
use_when: You have messy CSVs (mixed formats, currencies, dates, encodings) to normalize to a target schema.
verify: Every output row conforms to the target schema; a round-trip check reproduces source totals.
tags: [etl, normalization, validation-gate]
---

# Messy-CSV Normalizer

> Normalize messy CSVs to a target schema with a round-trip total check, so nothing is silently dropped. Primitive: `/goal` · Category: `data`

## Use when

You receive CSV exports with inconsistent date formats, currency strings, encodings, and column names, and you need them coerced into one clean schema — provably, without losing rows or money.

## Prompt

```
Goal:        Normalize <input csvs> to the target schema <schema>.
Context:     The input files; the target schema; the type/format coercion rules.
Constraints: No row dropped silently. Currency/date normalization must be reversible-checkable.
Done-when:   Every output row conforms to the schema AND a round-trip total matches the source.
Evidence:    The normalized file; a reconciliation (source row count + key totals == output).
If-blocked:  If a row can't be coerced, route it to a rejects file with a reason, not /dev/null.
```

## Verify

A separate check validates every output row against the target schema and confirms a round-trip total (row counts and key numeric sums) matches the source plus the rejects file.

## Steps

1. Infer/normalize types, dates, currencies, encodings to the schema.
2. Route uncoercible rows to a rejects file with reasons.
3. Reconcile output + rejects against the source totals.

## Notes

Same validation-gate spirit as the ad-spend reconciliation: the loop is done only when the numbers tie out, not when the file "looks" clean.

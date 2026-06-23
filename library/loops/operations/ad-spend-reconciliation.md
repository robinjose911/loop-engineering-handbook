---
id: ad-spend-reconciliation
title: Ad-Spend Reconciliation
category: operations
primitive: /goal
use_when: You need messy invoices reconciled against a bank export to a hard zero-variance gate.
verify: The reconciliation workbook shows variance of zero and zero unmatched rows.
tags: [reconciliation, validation-gate, spreadsheet]
example: ../../../examples/5-ad-spend-reconciliation/artifacts.md
---

# Ad-Spend Reconciliation

> Reconcile invoices vs a bank export to a hard gate (zero variance, zero unmatched), asking for a rule instead of guessing. Primitive: `/goal` · Category: `operations`

## Use when

You have invoices and a bank export that almost match — mismatched dates, duplicates, mixed currencies, orphan charges — and you need them reconciled to the cent, with every exception explained.

## Prompt

```
Goal:        Reconcile <period> invoices against the bank export to zero variance.
Context:     The invoices file and the bank export; the chart-of-accounts/fee rules.
Constraints: Do not invent matches. If a charge cannot be classified, ASK for a rule.
Done-when:   Summary variance == 0 and unmatched rows == 0.
Evidence:    A workbook (Raw / Normalized / Matched / Exceptions / Summary) that balances.
If-blocked:  Pause and ask the human for a classification rule; then re-run to zero.
```

## Verify

A separate check opens the workbook's Summary tab: the variance cell must read zero and unmatched rows must be zero; every exception must carry a resolution.

## Steps

1. Normalize currencies/dates and de-duplicate.
2. Match invoices to bank charges; collect the rest as exceptions.
3. Resolve exceptions (ask for rules as needed) until variance is zero.

## Notes

The worked example walks variance down step by step to a balanced workbook for a couple of dollars of agent time. See [ad-spend reconciliation](../../../examples/5-ad-spend-reconciliation/artifacts.md).

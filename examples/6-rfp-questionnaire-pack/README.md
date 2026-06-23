# 6. RFP / Security Questionnaire Pack

> **Reconstruction for teaching.** Fictional vendor (`Castora Analytics`) and buyer (`Meridian Bank`), synthetic binder; the receipts are generated, not from a real run.

**Pattern:** citation claim-ledger (cite-or-cut) · **Primitive:** `/goal` · **Domain:** non-coding

## Use when

You must answer a long security/RFP questionnaire and every answer has to cite an approved source — or be left as an explicit gap for a human, never fabricated.

## The loop (copy-paste)

This is the [library card](../../library/loops/research/rfp-questionnaire-pack.md) for this example. Copy the contract and fill the brackets:

```
Goal:        Answer the <N>-question questionnaire for <buyer> from the approved binder only.
Context:     The approved source-of-truth binder; the questionnaire.
Constraints: Every answer must cite a source line. No citation -> delete the claim, mark GAP.
Done-when:   Every question is ANSWERED-with-citation or marked GAP (needs human).
Evidence:    An answer pack (question, answer, source_id, source_quote, status); a claim ledger.
If-blocked:  If the binder lacks support, write "GAP - needs human"; do not guess.
```

## Verify

A separate check reads the [`ANSWER_PACK.xlsx`](ANSWER_PACK.xlsx): every `ANSWERED` row must carry a non-empty `source_id` and `source_quote` that exist in the binder; `GAP` rows must have no fabricated source. See the [claim ledger](claim_ledger.csv).

## Steps

1. Draft each answer strictly from the [approved binder](inputs/source_of_truth/security.md).
2. Attach a source line to each claim; auto-delete anything unsupported.
3. Mark unsupported questions GAP and hand them to a human.

## What happened

Of **60** questions, the loop answered **58** with a cited source line and left **2** as GAPs. The memorable one: it drafted "we're FedRAMP authorized," found **no** supporting line in the binder, **self-deleted** the claim, and wrote "GAP — needs human." Cite-or-cut, enforced on every answer. *(Illustrative — as of June 2026, verify before relying.)*

![Coverage climb across the metric-climb examples](../../assets/charts/summary-coverage-climb.png)

## The receipts

- [`ANSWER_PACK.xlsx`](ANSWER_PACK.xlsx) — question, answer, source_id, source_quote, confidence, status.
- [Approved binder](inputs/source_of_truth/security.md) — the only citable corpus.
- [Claim ledger (PASS/FAIL)](claim_ledger.csv) · [loop log](loop-log.jsonl) (the self-deleted claim) · [progress](progress.md) · [all artifacts](artifacts.md).

## Notes

The honesty comes from a **closed corpus + cite-or-cut**: the binder is the only source of truth, and any claim without a source line is deleted and surfaced as a gap rather than hallucinated.

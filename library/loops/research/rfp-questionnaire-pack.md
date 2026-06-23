---
id: rfp-questionnaire-pack
title: RFP / Security Questionnaire Pack
category: research
primitive: /goal
use_when: You must answer a long questionnaire and every answer has to cite an approved source or be left as a gap.
verify: Every answered row cites a source line from the approved binder; unsupported claims are marked GAP, not invented.
tags: [rfp, cite-or-cut, claim-ledger]
example: ../../../examples/6-rfp-questionnaire-pack/artifacts.md
---

# RFP / Security Questionnaire Pack

> Answer a questionnaire drafting only from an approved binder; cite a source line or auto-delete the claim and mark it GAP. Primitive: `/goal` · Category: `research`

## Use when

A buyer sends a 60-question security/RFP questionnaire. You want accurate answers grounded in approved material, with unsupported claims surfaced as gaps for a human — never fabricated.

## Prompt

```
Goal:        Answer the <N>-question questionnaire for <buyer> from the approved binder only.
Context:     The approved source-of-truth binder; the questionnaire.
Constraints: Every answer must cite a source line. No citation -> delete the claim, mark GAP.
Done-when:   Every question is ANSWERED-with-citation or marked GAP (needs human).
Evidence:    An answer pack (question, answer, source_id, source_quote, status); a claim ledger.
If-blocked:  If the binder lacks support, write "GAP - needs human"; do not guess.
```

## Verify

A separate check reads the answer pack: every ANSWERED row must carry a non-empty source_id and source_quote that exist in the binder; GAP rows must have no fabricated source.

## Steps

1. Draft each answer strictly from the binder.
2. Attach a source line to each claim; auto-delete anything unsupported.
3. Mark unsupported questions GAP and hand them to a human.

## Notes

In the worked example the loop drafted "we're FedRAMP authorized," found no source, self-deleted it, and wrote GAP. See [RFP questionnaire pack](../../../examples/6-rfp-questionnaire-pack/artifacts.md).

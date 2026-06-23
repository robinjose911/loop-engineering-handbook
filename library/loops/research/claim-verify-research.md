---
id: claim-verify-research
title: Claim-Verify Research Brief
category: research
primitive: /goal
use_when: You want a research brief where every claim is independently verified before it is allowed to stay.
verify: Each surviving claim has >= 2 independent supporting sources; unverified claims were cut or flagged.
tags: [research, verification, cite-or-cut]
---

# Claim-Verify Research Brief

> Draft a brief, then make a *separate* verifier try to refute each claim; keep only what survives. Primitive: `/goal` · Category: `research`

## Use when

You need a research summary you can trust. A drafting pass tends to assert plausible-but-wrong claims; a separate verification pass that tries to refute each one keeps the brief honest.

## Prompt

```
Goal:        Produce a verified brief on <question> where every claim is independently supported.
Context:     The allowed sources; a separate verifier that tries to REFUTE each drafted claim.
Constraints: A claim stays only if >= 2 independent sources support it (writer != verifier).
Done-when:   Every claim in the brief is verified; unverified claims are cut or flagged.
Evidence:    A claim ledger (claim -> sources -> verdict); the final brief.
If-blocked:  If a key claim can't be verified, flag it as "unverified" rather than dropping silently.
```

## Verify

A separate verifier re-checks each claim against the sources and tries to refute it; only claims with sufficient independent support survive into the final brief.

## Steps

1. Draft the brief with candidate claims.
2. For each claim, an independent verifier attempts to refute it.
3. Keep verified claims; cut or flag the rest.

## Notes

The maker-checker pattern applied to prose: the drafter and the verifier are different roles, so the brief can't grade its own confidence.

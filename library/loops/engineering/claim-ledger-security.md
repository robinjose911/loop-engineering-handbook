---
id: claim-ledger-security
title: Claim-Ledger Security Triage
category: engineering
primitive: /goal
use_when: A scanner dumped a pile of findings and you want only the ones backed by a runnable repro.
verify: Every accepted finding has a PoC that fails before the patch and passes after; an independent verifier re-ran each.
tags: [security, maker-checker, executable-evidence]
example: ../../../examples/3-claim-ledger-security/artifacts.md
---

# Claim-Ledger Security Triage

> Prove-or-dismiss each scanner finding with executable evidence; no finding ships without a runnable repro. Primitive: `/goal` · Category: `engineering`

> **Defensive / teaching use only.** Run PoCs in a local sandbox; never against systems you do not own.

## Use when

A scanner reports many "criticals" and you suspect most are false positives. You want a ledger that separates reproduced issues from noise, with evidence for each.

## Prompt

```
Goal:        Prove or dismiss every scanner finding on <target> with executable evidence.
Context:     The scanner output; a local sandbox of <target>; the patch branch.
Constraints: Defensive only, local sandbox. No finding is "real" without a runnable PoC.
Done-when:   Every finding is reproduced (PoC red->green on patch), dismissed, or escalated.
Evidence:    A findings ledger + a repro/ folder; an independent verifier re-ran each PoC.
If-blocked:  If a PoC cannot be made reliably red, mark the finding dismissed with a reason.
```

## Verify

An independent verifier (not the agent that wrote the PoC) re-runs each repro against the patch: reproduced findings go red-before / green-after; dismissed findings carry a falsifiable reason.

## Steps

1. Triage each finding into the ledger.
2. For candidates, build a sandbox PoC that reliably reproduces the issue.
3. Patch, re-run via an independent verifier, and record the verdict.

## Notes

In the worked example, 23 raw findings resolved to 9 reproduced / 11 dismissed / 3 escalated — the loop proved 11 were false positives. See [claim-ledger security fix](../../../examples/3-claim-ledger-security/artifacts.md).

---
id: reproduce-before-fix
title: Reproduce-Before-You-Fix
category: engineering
primitive: /goal
use_when: A regression needs fixing and you want to forbid touching source until the bug is reliably reproduced.
verify: A test reproduces the bug on 10/10 runs before any source edit; the fix makes it green.
tags: [regression, reproduction-gate, git-bisect]
example: ../../../examples/4-reproduce-before-fix/artifacts.md
---

# Reproduce-Before-You-Fix

> A reproduction-gate: the loop may not edit source until a test reliably reproduces the bug. Primitive: `/goal` · Category: `engineering`

## Use when

You have a flaky-seeming regression and want to avoid "fixes" that don't address a proven cause. The gate forces a reliable repro first, then a bisect, then the minimal fix.

## Prompt

```
Goal:        Fix the regression in <repo> only after proving it is real.
Context:     <repo>; the suspected bad range; a way to run the failing scenario repeatedly.
Constraints: FORBIDDEN to edit source until a test is reliably red (e.g. 10/10 runs fail).
Done-when:   The reproducing test was red pre-fix and is green post-fix.
Evidence:    A repro-gate log (attempts until reliably red); a git-bisect trail; the diff.
If-blocked:  If the bug will not reproduce reliably, stop and report — do not guess a fix.
```

## Verify

A separate check confirms the gate log shows a reliably-red test before the first source edit, and that the same test is green after the fix.

## Steps

1. Try to reproduce until the test is reliably red; keep the gate closed until then.
2. Bisect the range to the culprit commit.
3. Apply the minimal fix; re-run to green.

## Notes

The worked example binary-searched a 60-commit range to a one-line cache-TTL fix — found only after the bug was proven. See [reproduce-before-you-fix](../../../examples/4-reproduce-before-fix/artifacts.md).

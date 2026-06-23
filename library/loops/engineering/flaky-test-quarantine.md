---
id: flaky-test-quarantine
title: Flaky-Test Quarantine Warden
category: engineering
primitive: /loop
use_when: Flaky tests are eroding trust in CI and you want a loop to detect, quarantine, and file them.
verify: Each quarantined test failed intermittently across N reruns; the suite's flake rate trends down.
tags: [ci, flaky-tests, quarantine]
---

# Flaky-Test Quarantine Warden

> A patrol that reruns suspected-flaky tests, quarantines the genuinely flaky ones, and opens a tracking issue. Primitive: `/loop` · Category: `engineering`

## Use when

CI is red intermittently and people have started re-running until green. You want a loop that proves flakiness statistically and quarantines offenders instead of letting them rot the signal.

## Prompt

```
Goal:        Keep <repo>'s test suite trustworthy by quarantining proven-flaky tests.
Context:     CI history; the test suite; a quarantine tag/list; the issue tracker.
Constraints: Only quarantine a test that fails intermittently across >= 10 reruns.
Done-when:   No un-quarantined test shows intermittent failure this pass.
Evidence:    A rerun ledger per suspect (pass/fail counts); the quarantine list diff.
If-blocked:  If a test fails 10/10 (not flaky, just broken), escalate instead of quarantining.
```

## Verify

A separate check reads the rerun ledger: a quarantined test must show a mix of pass and fail across the reruns (intermittent), not a clean fail (broken) or clean pass (fine).

## Steps

1. Collect candidates from recent CI flips.
2. Rerun each many times; record pass/fail counts.
3. Quarantine the intermittent ones and file an issue; leave the rest.

## Notes

Run this on a long interval (hourly+). A short interval reruns the suite constantly and is expensive for little signal.

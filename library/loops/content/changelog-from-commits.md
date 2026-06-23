---
id: changelog-from-commits
title: Changelog From Commits
category: content
primitive: /goal
use_when: You want a release changelog drafted only from the actual commit/PR history, with every entry traceable.
verify: Every changelog line cites a real commit or PR in the range; no entry is unsourced.
tags: [release, changelog, cite-or-cut]
---

# Changelog From Commits

> Draft a release changelog where every entry traces to a real commit or PR — cite-or-cut. Primitive: `/goal` · Category: `content`

## Use when

You need user-facing release notes and want them grounded in what actually shipped, not in the model's guess about what "probably" changed.

## Prompt

```
Goal:        Draft the <version> changelog for <repo> from the commits/PRs in <range>.
Context:     The commit/PR log for <range> only; the prior changelog for style.
Constraints: Every entry must cite a commit SHA or PR number from the range. No invented items.
Done-when:   Every user-visible change in the range has exactly one cited entry.
Evidence:    A changelog draft + a coverage table mapping entries <-> commits/PRs.
If-blocked:  If a commit's intent is unclear, mark the entry NEEDS-AUTHOR rather than guessing.
```

## Verify

A separate check confirms each changelog entry references a SHA/PR that exists in the range, and that no user-visible PR in the range is missing an entry.

## Steps

1. Collect the commit/PR log for the range.
2. Group into user-visible changes; draft one cited entry each.
3. Flag ambiguous commits for the author instead of guessing.

## Notes

Same cite-or-cut discipline as the questionnaire pack — the source of truth is the commit log, and anything unsourced is cut or flagged.

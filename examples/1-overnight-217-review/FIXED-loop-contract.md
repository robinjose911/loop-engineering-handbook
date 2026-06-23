# Governed loop contract (the fix)

> Synthetic reconstruction for teaching; figures illustrative - as of June 2026, verify before relying.

```
Goal:       Review every open PR in Meridian/payments-gateway once per change.
Context:    Repo at HEAD; the open-PR queue (currently 12).
Constraints: Read-only. One comment per PR per *changed* revision.
Done-when:  No PR has changed since the last pass.
Evidence:   Per-pass diff of PR head SHAs; a posted-comments ledger.
If-blocked: Halt after 3 consecutive no-progress passes; hard cap $15/night.
```

Result: **4 passes, $11.20** (vs **91 passes, $217.34** ungoverned).

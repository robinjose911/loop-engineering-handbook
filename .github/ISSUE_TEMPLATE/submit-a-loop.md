---
name: Submit a loop
about: Propose a new loop card for the prompt library
title: "[loop] <short name>"
labels: ["loop-submission"]
---

## The loop

- **Category:** <engineering | operations | content | research | data>
- **Primitive:** </goal | /loop | routine>
- **Use when:** <one line>

## The contract

```
Goal:        <the outcome, in one sentence>
Context:     <repo / inputs / the source of truth>
Constraints: <read-only? sandbox? cost cap?>
Done-when:   <the single verifiable stop condition a separate checker can test>
Evidence:    <the artifacts that prove Done-when>
If-blocked:  <halt rule + escalation>
```

## Verify

<How a separate evaluator (not the agent) confirms Done-when is met.>

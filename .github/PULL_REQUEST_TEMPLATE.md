<!-- Thanks for contributing to the Loop Engineering Handbook. -->

## What this PR adds

<!-- A new loop card? a worked example? a guide fix? -->

## Submitting a loop?

If you're adding a loop card or example, confirm:

- [ ] The card reuses the six-field [loop contract](../docs/the-loop-contract.md) (Goal / Context / Constraints / Done-when / Evidence / If-blocked).
- [ ] It states a **verifiable Done-when** and a separate **Verify** step (writer ≠ checker).
- [ ] `category` ∈ {engineering, operations, content, research, data} and `primitive` ∈ {/goal, /loop, routine}.
- [ ] I regenerated the index: `python tools/library/build_catalog.py`.

## The rules (everything else follows from these)

- [ ] **Synthetic only** — no real orgs/data; a "reconstruction for teaching" label where applicable.
- [ ] **Receipts match prose** — any headline number is generated from an artifact and labeled illustrative.
- [ ] **Volatile facts labeled** — versions / `$` / star counts carry an "as of <month> <year> — verify before relying" label.
- [ ] Tests pass: `python tools/validate/all.py` and `npx playwright test` (see [AGENTS.md](../AGENTS.md)).

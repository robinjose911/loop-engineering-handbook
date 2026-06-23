# Contributing

Thanks for wanting to add to the Loop Engineering Handbook. This repo has one hard rule that everything else follows from:

> **The receipts must match the prose.** Every headline number in a guide page or example README is generated from, then machine-checked against, an underlying artifact (a `cost.csv`, a ledger, an `.xlsx`). A prose number that drifts from its artifact is a failing test, not a typo.

## Ground rules

- **Synthetic only.** Fictional orgs, toy repos, made-up datasets. No real third-party data, no tie to real ventures. Every example carries a "reconstruction for teaching" label.
- **Label volatile facts.** Version strings, star counts, and dollar figures must sit inside a labeled span (`as of June 2026 - verify before relying`, or `self-reported / illustrative`). The label lint enforces this.
- **Cite externals.** Every external claim has an entry in [SOURCES.md](SOURCES.md).
- **Deterministic generators.** Data and chart scripts are seeded; no `now()`, no RNG. Re-running a generator must be a no-op diff.

## How the tests work

This repo is mostly markdown + images, so "tests" are reinterpreted &mdash; but the discipline is a TDD app build:

- **Unit (per section):** Python validators under `tools/validate/`, run with `pytest tools/`.
- **Integration (per stage):** a Playwright spec under `tests/e2e/` run against a locally rendered preview (`tools/preview/`). The backbone assertions are `assertNoBrokenImages` and `assertNoDeadInternalLinks`.

See the full commands in [AGENTS.md](AGENTS.md) and the CI workflow in [.github/workflows/ci.yml](.github/workflows/ci.yml).

## Submitting a loop

The "submit a loop" PR template and issue templates land with the growth scaffolding (Stage 7). Until then: open an issue describing the loop, its primitive (`/goal`, `/loop`, or a routine), and the verifiable done-condition.

# For agents

This repo is built to be read by humans *and* agents. If you are an AI agent working in or learning from this repo, start here.

## What this repo is

A handbook for **loop engineering**: running an AI coding agent in a governed, verifiable loop until a clearly defined goal is met. It ships a guide, a copy-paste prompt library, and seven worked examples that include the logs, the cost ledgers, and the real output of each run.

## Machine-readable entry points

- `library/catalog.json` &mdash; machine-readable index of every loop card (lands in Stage 4).
- `library/llms.txt` &mdash; agent instructions for using the library (lands in Stage 4).
- `assets/manifest.json` &mdash; every visual slot and whether it is a placeholder or a real asset.
- `repo.config.json` &mdash; owner, theme, tagline, badges (single source of truth).

## How to run the tests

```bash
# one-time per session
npm --prefix tools/preview install     # markdown renderer + static server
npm --prefix tests/e2e install         # @playwright/test
pip install -r tools/requirements.txt  # openpyxl, matplotlib, jsonschema, pytest, Pillow

# unit (per section)
python tools/validate/all.py           # runs every validator + the preview unit test

# integration (per stage) -- run from the repo root with an explicit config,
# or `cd tests/e2e && npx playwright test <spec>`
npx --prefix tests/e2e playwright test --config tests/e2e/playwright.config.ts tests/e2e/stage0-harness.spec.ts
```

## Conventions you must follow

- **Synthetic data only.** No real orgs, datasets, or third-party data.
- **Receipts match prose.** Headline numbers are generated from artifacts and machine-checked.
- **Label volatile facts** (`as of June 2026 - verify before relying`).
- **Diagrams** are Mermaid sources in `assets/diagrams/src/*.mmd`, rendered to PNG.
- **Charts** are generated from each example's own CSV, not drawn by hand.

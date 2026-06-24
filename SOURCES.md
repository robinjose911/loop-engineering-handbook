# Sources

Every external claim, version number, dollar figure, and quote-card in this repo
is cited here. This file and the in-text citations are kept in **bijection** by a
lint (Stage 7): every external claim links to an entry here, and every entry here
is referenced somewhere.

> **Accuracy stance:** label-and-cite. Volatile specifics are included but marked
> *as of June 2026 — verify before relying*. Self-reported figures are marked
> illustrative. Quote-card screenshots are captured and each links to its
> originating post.

## Origin and lineage

The timeline in [docs/01](docs/01-what-is-loop-engineering.md) is recorded
*as of June 2026 — verify before relying*. The people and dates are recorded from
secondary recollection and should be confirmed against primary posts before
publication; some are **illustrative** reconstructions for teaching.

| Claim | Attribution | Source | Status |
|-------|-------------|--------|--------|
| The bare "Ralph" loop (re-run a prompt in `while true`) | Geoffrey Huntley | https://ghuntley.com/ralph/ | primary |
| Viral thread on long unattended agent loops | Steinberger | https://x.com/steipete/status/2063697162748260627 | primary (X) |
| Framing loops inside coding-agent tooling | Boris Cherny | https://officechai.com/ai/i-now-just-write-loops-to-prompt-claude-code-claude-code-creator-boris-cherny/ | secondary (OfficeChai) |
| Named + defined "loop engineering" | Addy Osmani | https://addyosmani.com/blog/loop-engineering/ | primary |
| Governed "Ralph loop++" | Greg Brockman | https://x.com/gdb/status/2050194039077495089 | primary (X) |

## Tooling

The tool matrix in [docs/02](docs/02-goal-and-loop-basics.md) is *illustrative of
the shape, not a feature contract — as of June 2026, verify before relying*.

| Claim | Source | Status |
|-------|--------|--------|
| Claude Code / Codex / Cowork / OpenCode loop & scheduling capabilities | each tool's official docs | verify before relying |

## Quote-card sources

These rows back the attributed screenshots in `assets/quote-cards/`. Each card in
the README credits links to its originating post below.

| Slot | Attribution | Source URL | Status |
|------|-------------|------------|--------|
| `steinberger` | Steinberger (Ralph loop) | https://x.com/steipete/status/2063697162748260627 | linked |
| `cherny` | Boris Cherny (Claude Code) | https://officechai.com/ai/i-now-just-write-loops-to-prompt-claude-code-claude-code-creator-boris-cherny/ | linked |
| `osmani` | Addy Osmani (loop engineering) | https://addyosmani.com/blog/loop-engineering/ | linked |
| `huntley` | Geoffrey Huntley (original Ralph) | https://ghuntley.com/ralph/ | linked |
| `brockman` | Greg Brockman ("Ralph loop++") | https://x.com/gdb/status/2050194039077495089 | linked |

> Each quote card in the README credits links to its source post above. The two
> X.com URLs are allowlisted for the link-checker in `tools/links/allowlist.json`
> (x.com returns 403 to automated checkers).

## Figures and statistics

All figures below are **illustrative — as of June 2026, verify before relying**.

| Figure | Where | Basis | Status |
|--------|-------|-------|--------|
| Cost model: input $2.00/1M, output $8.00/1M tokens | docs/04, all examples | illustrative model, not a vendor price | illustrative |
| `$217.34` ungoverned vs `$11.20` governed | docs/04, example 1 | generated from `examples/1-*/cost.csv` | illustrative |
| `$15/night` cost cap (governed run) | docs/04 | asserted governance cap, not derived from the receipts | illustrative — verify |
| Usage split ~56% / 17% / 13% | docs/03 | self-reported, directional | illustrative — verify |

#!/usr/bin/env python3
"""Generate the prompt-library index from the loop cards (Stage 4.3).

Reads the front-matter of every card under library/loops/**/*.md and writes,
deterministically (sorted by category then id):
  - library/catalog.json   (machine-readable index, validated against the schema)
  - library/README.md      (the human index table; row count == card count)
  - library/llms.txt        (agent instructions, references real paths)

Cards are the source of truth; these three files are derived. Re-running is a
no-op diff. Usage: python tools/library/build_catalog.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
LOOPS_DIR = REPO_ROOT / "library" / "loops"
CATEGORY_ORDER = ["engineering", "operations", "content", "research", "data"]
PRIMITIVES = ["/goal", "/loop", "routine"]
FRONT_MATTER_KEYS = ["id", "title", "category", "primitive", "use_when", "verify", "tags"]


def parse_front_matter(text: str) -> dict:
    """Return the YAML front-matter of a card as a dict (empty if none).

    Line-based: the front-matter is between an opening `---` line and the next
    line that is exactly `---` at column 0, so a `---` inside a YAML scalar or a
    horizontal rule in the body can't truncate it.
    """
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        return {}
    for i in range(1, len(lines)):
        if lines[i] == "---":
            return yaml.safe_load("\n".join(lines[1:i])) or {}
    return {}


def load_cards() -> list[dict]:
    cards = []
    for path in sorted(LOOPS_DIR.rglob("*.md")):
        fm = parse_front_matter(path.read_text())
        entry = {k: fm.get(k) for k in FRONT_MATTER_KEYS}
        entry["path"] = str(path.relative_to(REPO_ROOT))
        if fm.get("example"):
            entry["example"] = fm["example"]
        cards.append(entry)
    # deterministic order: category (by canonical order), then id. `or ""` guards
    # against a malformed card with a missing category/id (the validators are the
    # real gate; this just keeps the builder from crashing with an opaque error).
    cards.sort(key=lambda c: (
        CATEGORY_ORDER.index(c["category"]) if c["category"] in CATEGORY_ORDER else 99,
        c["id"] or "",
    ))
    return cards


def build_catalog(cards: list[dict]) -> dict:
    cats = [c for c in CATEGORY_ORDER if any(card["category"] == c for card in cards)]
    return {
        "version": 1,
        "generated_from": "library/loops/**/*.md front-matter",
        "count": len(cards),
        "categories": cats,
        "primitives": PRIMITIVES,
        "cards": cards,
    }


def build_readme(cards: list[dict]) -> str:
    lines = [
        "# The prompt library",
        "",
        f"{len(cards)} copy-paste **loop cards**, organized by category. Each card has a",
        "Use-when, a fill-in-the-blanks prompt (the canonical six-field",
        "[loop contract](../docs/the-loop-contract.md)), a Verify step, Steps, and Notes.",
        "",
        "Machine-readable: [`catalog.json`](catalog.json) (validated against",
        "[`catalog.schema.json`](catalog.schema.json)) · agent instructions:",
        "[`llms.txt`](llms.txt).",
        "",
    ]
    for cat in CATEGORY_ORDER:
        in_cat = [c for c in cards if c["category"] == cat]
        if not in_cat:
            continue
        lines.append(f"## {cat.capitalize()}")
        lines.append("")
        lines.append("| Card | Primitive | Use when | Example |")
        lines.append("|------|-----------|----------|---------|")
        for c in in_cat:
            rel = c["path"][len("library/"):]  # card link relative to library/README.md
            ex = "-"
            if c.get("example"):
                # The card's example is relative to the card; rebase it to library/.
                card_dir = (REPO_ROOT / c["path"]).parent
                target = (card_dir / c["example"]).resolve()
                ex = f"[worked]({os.path.relpath(target, REPO_ROOT / 'library')})"
            lines.append(f"| [{c['title']}]({rel}) | `{c['primitive']}` | {c['use_when']} | {ex} |")
        lines.append("")
    lines.append("[Back to the handbook](../README.md)")
    return "\n".join(lines) + "\n"


def build_llms_txt(cards: list[dict]) -> str:
    by_cat = {cat: [c for c in cards if c["category"] == cat] for cat in CATEGORY_ORDER}
    lines = [
        "# Loop Engineering Handbook - prompt library (for agents)",
        "",
        "This directory is a catalog of governed-loop recipes ('cards').",
        "",
        "## How to use",
        "- Read `catalog.json` for the machine-readable index (schema: `catalog.schema.json`).",
        "- Each card lives at its `path` and contains a fill-in-the-blanks prompt that reuses",
        "  the canonical six-field loop contract (`../docs/the-loop-contract.md`).",
        "- Pick a card by `category` and `primitive`, copy its Prompt block, fill the brackets,",
        "  and obey its Done-when + Verify before treating the loop as finished.",
        "",
        f"## Cards ({len(cards)})",
    ]
    for cat in CATEGORY_ORDER:
        if not by_cat[cat]:
            continue
        lines.append(f"### {cat}")
        for c in by_cat[cat]:
            lines.append(f"- {c['id']} ({c['primitive']}): {c['use_when']} -> {c['path']}")
    return "\n".join(lines) + "\n"


def build(out_dir: Path) -> dict:
    cards = load_cards()
    catalog = build_catalog(cards)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "catalog.json").write_text(json.dumps(catalog, indent=2) + "\n")
    (out_dir / "README.md").write_text(build_readme(cards))
    (out_dir / "llms.txt").write_text(build_llms_txt(cards))
    return catalog


def main() -> int:
    catalog = build(REPO_ROOT / "library")
    print(f"[library] built catalog.json, README.md, llms.txt for {catalog['count']} cards")
    return 0


if __name__ == "__main__":
    sys.exit(main())

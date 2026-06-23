"""Unit test for catalog.json + llms.txt (Stage 4.3).

catalog.json validates against its JSON schema; it is a verified bijection with
the card files; the generated files are in sync with the cards (regenerating to a
temp dir reproduces the committed bytes); llms.txt references real paths.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import jsonschema

REPO_ROOT = Path(__file__).resolve().parents[2]
LIBRARY = REPO_ROOT / "library"
LOOPS_DIR = LIBRARY / "loops"
sys.path.insert(0, str(REPO_ROOT / "tools" / "library"))
import build_catalog  # noqa: E402

CATALOG = json.loads((LIBRARY / "catalog.json").read_text())
SCHEMA = json.loads((LIBRARY / "catalog.schema.json").read_text())


def test_catalog_validates_against_schema():
    jsonschema.validate(CATALOG, SCHEMA)


def test_catalog_is_a_bijection_with_card_files():
    catalog_paths = {c["path"] for c in CATALOG["cards"]}
    disk_paths = {str(p.relative_to(REPO_ROOT)) for p in LOOPS_DIR.rglob("*.md")}
    assert catalog_paths == disk_paths, (
        f"catalog/cards mismatch: only-in-catalog={catalog_paths - disk_paths}, "
        f"only-on-disk={disk_paths - catalog_paths}"
    )
    assert CATALOG["count"] == len(disk_paths)
    # every catalog path resolves on disk
    for c in CATALOG["cards"]:
        assert (REPO_ROOT / c["path"]).exists(), f"catalog path missing: {c['path']}"


def test_generated_files_in_sync_with_cards(tmp_path):
    """Regenerating to a temp dir must reproduce the committed catalog/README/llms."""
    build_catalog.build(tmp_path)
    for name in ("catalog.json", "README.md", "llms.txt"):
        assert (tmp_path / name).read_text() == (LIBRARY / name).read_text(), (
            f"library/{name} is stale - re-run tools/library/build_catalog.py"
        )


def test_readme_row_count_equals_card_count():
    readme = (LIBRARY / "README.md").read_text()
    # count table rows that link to a card under loops/
    rows = [ln for ln in readme.splitlines() if ln.startswith("| [") and "(loops/" in ln]
    assert len(rows) == CATALOG["count"], f"README lists {len(rows)} cards, catalog has {CATALOG['count']}"


def test_llms_txt_references_real_paths():
    llms = (LIBRARY / "llms.txt").read_text()
    assert "catalog.json" in llms
    # the loop-contract path it points agents to must exist
    assert (REPO_ROOT / "docs" / "the-loop-contract.md").exists()
    # every card path it lists exists on disk
    for c in CATALOG["cards"]:
        assert c["path"] in llms, f"llms.txt does not reference {c['path']}"
        assert (REPO_ROOT / c["path"]).exists()

"""Cost-math lint (Stage 3.4).

The worked cost-math table in docs/04 is recomputed from its stated token counts
using the SAME pricing the receipts engine uses (tools/data/_util), and must
match the cost_usd the prose claims. A drift between the doc's arithmetic and the
pricing model is a failing test.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "data"))
import _util  # noqa: E402

DOC = REPO_ROOT / "docs" / "04-risks-and-cost.md"
MARKER = "<!-- cost-math-table -->"


def _parse_cost_table() -> list[dict]:
    text = DOC.read_text()
    assert MARKER in text, f"{DOC.name} missing the {MARKER} marker"
    after = text.split(MARKER, 1)[1]
    rows = []
    header = None
    seen_separator = False
    for line in after.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            if header is not None:
                break  # table ended
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if header is None:
            header = cells
            continue
        if not seen_separator:
            # The row immediately after the header is the markdown separator.
            assert set("".join(cells)) <= set("-: "), f"expected separator row, got {cells}"
            seen_separator = True
            continue
        rows.append(dict(zip(header, cells)))
    return rows


def test_cost_table_recomputes():
    rows = _parse_cost_table()
    assert rows, "no cost-math rows parsed"
    for r in rows:
        in_tok = int(r["input_tokens"])
        out_tok = int(r["output_tokens"])
        # Exact integer comparison in micro-dollars (no float ==).
        stated_micros = round(float(r["cost_usd"]) * 1_000_000)
        recomputed_micros = _util.cost_micros(in_tok, out_tok)
        assert stated_micros == recomputed_micros, (
            f"row '{r['scenario']}': stated ${r['cost_usd']} but {in_tok} in + {out_tok} out "
            f"recompute to ${_util.micros_to_usd(recomputed_micros)} under the "
            f"${_util.PRICING['input_usd_per_mtok']}/${_util.PRICING['output_usd_per_mtok']} per-Mtok model"
        )


def test_pricing_label_present():
    """The doc must label its cost model as illustrative (the label lint covers
    the section, this pins the specific pricing statement)."""
    text = DOC.read_text().lower()
    assert "$2.00 / 1m tokens" in text and "$8.00 / 1m tokens" in text
    assert "illustrative" in text

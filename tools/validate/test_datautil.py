"""Unit test for the shared data lib + determinism guard (Stage 1.1)."""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "data"))

import _util  # noqa: E402


def test_tokens_for_cents_is_exact():
    for cents in (1, 8, 73, 226, 901, 1402):
        in_tok, out_tok = _util.tokens_for_cents(cents)
        assert _util.cost_micros(in_tok, out_tok) == cents * 10_000
        assert _util.micros_to_usd(cents * 10_000) == round(cents / 100, 2)


def test_cost_rows_cumulative_equals_sum():
    cents = [560, 528, 504, 480] + [226] * 87
    rows, total_micros = _util.cost_rows_from_cents(cents)
    assert _util.micros_to_usd(total_micros) == 217.34
    assert rows[-1]["cumulative_usd"] == 217.34
    assert round(sum(r["cost_usd"] for r in rows), 2) == 217.34


def test_writers_are_byte_deterministic(tmp_path):
    rows = [["a", 1, 2.5], ["b", 3, 4.0]]
    p1, p2 = tmp_path / "a.csv", tmp_path / "b.csv"
    _util.write_csv(p1, ["x", "y", "z"], rows)
    _util.write_csv(p2, ["x", "y", "z"], rows)
    assert p1.read_bytes() == p2.read_bytes()

    j1, j2 = tmp_path / "a.jsonl", tmp_path / "b.jsonl"
    recs = [{"b": 2, "a": 1}, {"z": 9, "m": 5}]
    _util.write_jsonl(j1, recs)
    _util.write_jsonl(j2, recs)
    assert j1.read_bytes() == j2.read_bytes()
    # sort_keys makes ordering independent of insertion order
    assert j1.read_text().splitlines()[0] == '{"a":1,"b":2}'


def test_time_seq_is_deterministic_and_monotonic():
    seq = _util.time_seq("2026-04-14T23:02:00", 297)
    first = [next(seq) for _ in range(3)]
    seq2 = _util.time_seq("2026-04-14T23:02:00", 297)
    second = [next(seq2) for _ in range(3)]
    assert first == second
    assert first[0] < first[1] < first[2]


def _hash_dir(d: Path) -> dict:
    return {str(p.relative_to(d)): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(d.rglob("*")) if p.is_file()}


def test_regenerating_is_a_noop_diff():
    """Re-running every generator must not change any file (the no-op-diff gate),
    including the two .xlsx workbooks (timestamp-normalized)."""
    import ex1, ex2, ex3, ex4, ex5, ex6, ex7  # noqa: E402

    examples = REPO_ROOT / "examples"
    before = _hash_dir(examples)
    for mod in (ex1, ex2, ex3, ex4, ex5, ex6, ex7):
        mod.generate()
    after = _hash_dir(examples)
    added = sorted(set(after) - set(before))
    removed = sorted(set(before) - set(after))
    changed = sorted(k for k in (set(before) & set(after)) if before[k] != after[k])
    assert not (added or removed or changed), (
        f"non-deterministic regeneration: changed={changed} added={added} removed={removed}"
    )

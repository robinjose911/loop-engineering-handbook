"""Shared, fully-deterministic helpers for the synthetic receipts engine (Stage 1).

No ``now()``, no RNG anywhere. Every generator passes in a fixed base time and
derives everything from constants, so re-running any generator is a no-op diff.

Cost model (illustrative, labeled): input $2.00 / 1M tokens, output $8.00 / 1M
tokens. Costs are computed in **integer micro-dollars** (1e-6 USD) per token so
sums are exact -- a headline like ``$217.34`` is reproduced to the cent, never a
float-rounding artifact. ``tokens_for_cents`` derives token counts from a target
cost at a fixed 4:1 input:output ratio (re-reads dominate real agent loops), and
the math is exact: out = 625 * cents, in = 2500 * cents.
"""
from __future__ import annotations

import csv
import json
import os
import re
import zipfile
from datetime import datetime, timedelta
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
EXAMPLES_DIR = REPO_ROOT / "examples"

# --- pricing (illustrative; labeled everywhere it surfaces in prose) ----------
IN_MICRO_PER_TOKEN = 2  # $2.00 / 1,000,000 tokens
OUT_MICRO_PER_TOKEN = 8  # $8.00 / 1,000,000 tokens
PRICING = {
    "input_usd_per_mtok": 2.00,
    "output_usd_per_mtok": 8.00,
    "label": "illustrative cost model - not a quoted vendor price (as of June 2026 - verify before relying)",
}

# Statuses a loop-log JSONL line may carry (validated by the unit tests).
ALLOWED_STATUSES = {
    "reviewing",
    "no_new_work",
    "halted",
    "cap_reached",
    "drafting",
    "gap_marked",
    "repro_attempt",
    "gate_open",
    "gate_closed",
    "bisecting",
    "fix_applied",
    "verified",
    "reproduced",
    "dismissed",
    "escalated",
}


# --- cost helpers -------------------------------------------------------------
def cost_micros(input_tokens: int, output_tokens: int) -> int:
    """Exact cost in micro-dollars for a pass."""
    return IN_MICRO_PER_TOKEN * input_tokens + OUT_MICRO_PER_TOKEN * output_tokens


def micros_to_usd(micros: int) -> float:
    return round(micros / 1_000_000, 2)


def tokens_for_cents(cents: int) -> tuple[int, int]:
    """(input_tokens, output_tokens) whose exact cost equals ``cents`` cents.

    At 4:1 input:output and 2/8 micro$ pricing: cost_micros = 2*(4o) + 8*o = 16o,
    and cents*10000 = 16o  ->  o = 625*cents, in = 2500*cents (always integers).
    """
    if cents < 0:
        raise ValueError("cents must be non-negative")
    out_tokens = 625 * cents
    in_tokens = 2500 * cents
    assert cost_micros(in_tokens, out_tokens) == cents * 10_000
    return in_tokens, out_tokens


def cost_rows_from_cents(cents_list: list[int]) -> tuple[list[dict], int]:
    """Build per-pass cost rows (with derived tokens + running cumulative).

    Returns (rows, total_micros). Each row: input_tokens, output_tokens,
    cost_usd, cumulative_usd. The final cumulative_usd == sum, exact to the cent.
    """
    rows: list[dict] = []
    cum_micros = 0
    for cents in cents_list:
        in_tok, out_tok = tokens_for_cents(cents)
        m = cost_micros(in_tok, out_tok)
        cum_micros += m
        rows.append(
            {
                "input_tokens": in_tok,
                "output_tokens": out_tok,
                "cost_usd": micros_to_usd(m),
                "cumulative_usd": micros_to_usd(cum_micros),
            }
        )
    return rows, cum_micros


# --- time ---------------------------------------------------------------------
def time_seq(base_iso: str, step_seconds: int):
    """Infinite generator of ISO timestamps from a fixed base, deterministic."""
    base = datetime.fromisoformat(base_iso)
    i = 0
    while True:
        yield (base + timedelta(seconds=step_seconds * i)).isoformat()
        i += 1


# --- writers (byte-deterministic) ---------------------------------------------
def write_csv(path: Path, header: list[str], rows: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(header)
        for r in rows:
            w.writerow(r)


def write_jsonl(path: Path, records: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [json.dumps(r, sort_keys=True, separators=(",", ":")) for r in records]
    path.write_text("\n".join(lines) + "\n")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text)


def write_headline(example_dir: Path, data: dict) -> None:
    """The single source of truth a README's prose must match (Stage 5 gate)."""
    write_json(example_dir / "headline.json", data)


def write_artifacts_index(example_dir: Path, title: str, artifacts: list[tuple[str, str]], note: str = "") -> None:
    """Generated listing of an example's artifacts (links checked by Stage 1's
    Playwright spec). Stage 5 adds the full narrative README.md alongside it."""
    lines = [f"# {title} - generated artifacts", ""]
    if note:
        lines += [f"> {note}", ""]
    lines.append("| Artifact | File |")
    lines.append("|----------|------|")
    for label, rel in artifacts:
        lines.append(f"| {label} | [{rel}]({rel}) |")
    lines.append("")
    lines.append("<sub>Auto-generated by `tools/data/`. Synthetic reconstruction for teaching.</sub>")
    write_text(example_dir / "artifacts.md", "\n".join(lines))


def fixed_doc_datetime() -> datetime:
    """A constant timestamp for .xlsx document properties (determinism)."""
    return datetime(2026, 6, 1, 9, 0, 0)


_FIXED_ZIP_DATE = (2026, 6, 1, 0, 0, 0)
_FIXED_ISO = "2026-06-01T09:00:00Z"


def _normalize_core_xml(data: bytes) -> bytes:
    """openpyxl rewrites <dcterms:modified> to now() at save time; pin both the
    created and modified timestamps to a constant so docProps/core.xml is stable."""
    text = data.decode("utf-8")
    text = re.sub(r"(<dcterms:created[^>]*>)[^<]*(</dcterms:created>)", rf"\g<1>{_FIXED_ISO}\g<2>", text)
    text = re.sub(r"(<dcterms:modified[^>]*>)[^<]*(</dcterms:modified>)", rf"\g<1>{_FIXED_ISO}\g<2>", text)
    return text.encode("utf-8")


def normalize_xlsx(path: Path) -> None:
    """Rewrite an .xlsx (a zip) with fixed member timestamps and a pinned
    docProps/core.xml so the file is byte-identical across runs. openpyxl stamps
    each zip member with the current time and resets the modified property to
    now() at save, which would otherwise break the no-op-diff guarantee.
    """
    tmp = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(path, "r") as zin:
        infos = zin.infolist()  # preserves openpyxl's deterministic member order
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            for info in infos:
                data = zin.read(info.filename)
                if info.filename == "docProps/core.xml":
                    data = _normalize_core_xml(data)
                zi = zipfile.ZipInfo(filename=info.filename, date_time=_FIXED_ZIP_DATE)
                zi.compress_type = info.compress_type  # preserve stored vs deflated
                zi.external_attr = info.external_attr
                zi.internal_attr = info.internal_attr
                zi.flag_bits = info.flag_bits  # preserve e.g. the UTF-8 filename flag
                zi.create_system = 3  # constant (unix) regardless of host OS
                zout.writestr(zi, data)
    os.replace(tmp, path)


def save_xlsx_deterministic(wb, path: Path) -> None:
    """Save an openpyxl workbook with fixed doc properties + zip timestamps."""
    wb.properties.created = fixed_doc_datetime()
    wb.properties.modified = fixed_doc_datetime()
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    normalize_xlsx(path)

"""Shared helpers for reading/updating assets/manifest.json (Stage 2+)."""
from __future__ import annotations

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = REPO_ROOT / "assets" / "manifest.json"


def load() -> dict:
    return json.loads(MANIFEST_PATH.read_text())


def save(manifest: dict) -> None:
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2) + "\n")


def slots_by_kind(kind: str) -> list[dict]:
    return [s for s in load()["slots"] if s.get("kind") == kind]


def mark_real(updates: dict[str, dict]) -> None:
    """Flip slots to status='real' (and optionally update width/height).

    `updates` maps slot id -> {"width": int, "height": int} (dims optional).
    Loads + saves the manifest once.
    """
    manifest = load()
    by_id = {s["id"]: s for s in manifest["slots"]}
    for slot_id, fields in updates.items():
        slot = by_id.get(slot_id)
        if slot is None:
            raise KeyError(f"unknown manifest slot: {slot_id}")
        slot["status"] = "real"
        if "width" in fields:
            slot["width"] = int(fields["width"])
        if "height" in fields:
            slot["height"] = int(fields["height"])
    save(manifest)

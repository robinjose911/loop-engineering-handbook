"""Shared markdown helpers for the validator suite (not a test module)."""
from __future__ import annotations

import re


def contract_block(text: str) -> str | None:
    """The fenced block holding the six-field loop contract (contains Goal: +
    If-blocked:), normalized by rstripping each line and trimming blank edges.
    Used to compare a README/example prompt block against the canonical template.
    """
    for m in re.finditer(r"```(.*?)```", text, re.S):
        body = m.group(1)
        if "Goal:" in body and "If-blocked:" in body:
            return "\n".join(line.rstrip() for line in body.strip("\n").splitlines())
    return None

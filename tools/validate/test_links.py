"""Full-repo link + render integrity (Stage 7.1).

Offline: every relative link + image + #anchor in every shipped .md resolves on
disk; every external URL is either allowlisted (tools/links/allowlist.json) or
would be live-checked (there are none outside the allowlist today, so this stays
network-free in CI).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from _docutil import LINK_RE, heading_slugs, md_files  # noqa: E402

ALLOWLIST = [e["pattern"] for e in json.loads((REPO_ROOT / "tools" / "links" / "allowlist.json").read_text())["allow"]]
MD_FILES = md_files()


@pytest.mark.parametrize("md", MD_FILES, ids=[str(p.relative_to(REPO_ROOT)) for p in MD_FILES])
def test_internal_links_and_anchors_resolve(md):
    text = md.read_text()
    dead = []
    for target in LINK_RE.findall(text):
        if re.match(r"^(https?:)?//", target) or target.startswith(("mailto:", "tel:", "data:")):
            continue
        path_part, _, anchor = target.partition("#")
        if path_part:
            resolved = (md.parent / path_part).resolve()
            if not resolved.exists():
                dead.append(f"{target} -> missing file")
                continue
            anchor_source = resolved
        else:
            anchor_source = md  # in-page anchor
        if anchor and anchor_source.suffix == ".md":
            if anchor not in heading_slugs(anchor_source.read_text()):
                dead.append(f"{target} -> no heading slugs to #{anchor}")
    assert not dead, f"{md.relative_to(REPO_ROOT)} dead internal links:\n  " + "\n  ".join(dead)


def test_external_urls_are_allowlisted():
    offenders = {}
    for md in MD_FILES:
        for target in LINK_RE.findall(md.read_text()):
            if not re.match(r"^https?://", target):
                continue
            if not any(pat in target for pat in ALLOWLIST):
                offenders.setdefault(str(md.relative_to(REPO_ROOT)), []).append(target)
    assert not offenders, (
        "external URLs not in tools/links/allowlist.json (add an allowlist entry "
        f"or a live-check exception): {offenders}"
    )

"""Example 3: Claim-Ledger Security Fix (coding, /goal).

DEFENSIVE / TEACHING RECONSTRUCTION. Fictional advisory IDs, synthetic CVSS,
local teaching PoCs only (descriptions, not runnable exploit code).

On fictional VaultDesk: 23 raw scanner hits -> 9 reproduced (runnable PoC) /
11 dismissed (false positive) / 3 escalated. An independent verifier re-runs each
PoC against the patch. Pattern: maker-checker on executable evidence.
"""
from __future__ import annotations

from _util import (
    EXAMPLES_DIR,
    cost_micros,
    micros_to_usd,
    tokens_for_cents,
    write_artifacts_index,
    write_csv,
    write_headline,
    write_text,
)

SLUG = "3-claim-ledger-security"

DEFENSIVE_BANNER = (
    "> **DEFENSIVE / TEACHING RECONSTRUCTION.** Fictional advisory IDs, synthetic "
    "CVSS scores, and local teaching PoCs only (descriptions, not runnable exploit "
    "code). No real product, no real vulnerability. Synthetic - for teaching the "
    "maker-checker-on-evidence pattern."
)

# 9 reproduced, 11 dismissed, 3 escalated = 23.
REPRODUCED = [
    ("VD-2026-001", "SQL injection in report filter", "CRITICAL", 9.1),
    ("VD-2026-002", "Stored XSS in comment render", "HIGH", 7.4),
    ("VD-2026-003", "IDOR on invoice download", "HIGH", 8.2),
    ("VD-2026-004", "Path traversal in export path", "HIGH", 7.7),
    ("VD-2026-005", "Missing authz on admin route", "CRITICAL", 9.0),
    ("VD-2026-006", "SSRF in webhook validator", "HIGH", 7.9),
    ("VD-2026-007", "Open redirect in OAuth return", "MEDIUM", 5.4),
    ("VD-2026-008", "Weak JWT signature check", "HIGH", 8.0),
    ("VD-2026-009", "CSV formula injection in export", "MEDIUM", 6.1),
]
DISMISSED = [
    ("VD-2026-010", "SQLi (scanner)", "CRITICAL", 9.1, "parameterized query; input never concatenated"),
    ("VD-2026-011", "XSS (scanner)", "HIGH", 7.0, "output auto-escaped by template engine"),
    ("VD-2026-012", "Hardcoded secret", "HIGH", 7.5, "value is a public test fixture, not a secret"),
    ("VD-2026-013", "Insecure deserialization", "CRITICAL", 9.8, "path unreachable; no untrusted input"),
    ("VD-2026-014", "Command injection", "CRITICAL", 9.3, "args passed as a list, no shell"),
    ("VD-2026-015", "Weak crypto (MD5)", "MEDIUM", 5.0, "MD5 used only for a cache key, not security"),
    ("VD-2026-016", "Missing CSRF token", "HIGH", 7.1, "endpoint is GET-only and read-only"),
    ("VD-2026-017", "Directory listing", "LOW", 3.1, "static dir is empty and behind auth"),
    ("VD-2026-018", "Verbose error", "MEDIUM", 4.4, "stack traces disabled in prod config"),
    ("VD-2026-019", "Outdated dependency", "HIGH", 7.2, "vulnerable code path not imported"),
    ("VD-2026-020", "CORS misconfig", "MEDIUM", 5.9, "wildcard only on a public, unauthenticated API"),
]
ESCALATED = [
    ("VD-2026-021", "Auth bypass via header spoof", "CRITICAL", 9.4),
    ("VD-2026-022", "RCE in image thumbnailer", "CRITICAL", 9.6),
    ("VD-2026-023", "Privilege escalation in role check", "HIGH", 8.3),
]


def generate() -> dict:
    d = EXAMPLES_DIR / SLUG
    d.mkdir(parents=True, exist_ok=True)

    # findings-ledger.csv
    ledger = []
    for fid, title, sev, cvss in REPRODUCED:
        ledger.append([fid, title, sev, cvss, "reproduced", f"repro/{fid}/", "PoC exploited the issue; patch closes it"])
    for fid, title, sev, cvss, why in DISMISSED:
        ledger.append([fid, title, sev, cvss, "dismissed", "", f"false positive: {why}"])
    for fid, title, sev, cvss in ESCALATED:
        ledger.append([fid, title, sev, cvss, "escalated", f"repro/{fid}/", "reproduced; patch insufficient - escalated to vendor"])
    write_csv(
        d / "findings-ledger.csv",
        ["finding_id", "title", "scanner_severity", "cvss", "status", "repro_path", "verifier_result"],
        ledger,
    )

    # repro/ folders for the 9 reproduced + 3 escalated (failing-then-passing).
    for fid, title, *_ in REPRODUCED:
        _write_repro(d, fid, title, escalated=False)
    for fid, title, *_ in ESCALATED:
        _write_repro(d, fid, title, escalated=True)

    # cost.csv: triage (cheap, all 23) -> reproduce (expensive, 12) -> verify (12).
    triage_c, repro_c, verify_c = 8, 120, 40
    repro_ids = [r[0] for r in REPRODUCED] + [e[0] for e in ESCALATED]
    rows = []
    cum = 0
    for fid, *_ in (REPRODUCED + [(x[0],) for x in DISMISSED] + ESCALATED):
        in_tok, out_tok = tokens_for_cents(triage_c)
        cum += cost_micros(in_tok, out_tok)
        rows.append(["triage", fid, in_tok, out_tok, f"{micros_to_usd(cost_micros(in_tok, out_tok)):.2f}", f"{micros_to_usd(cum):.2f}"])
    for fid in repro_ids:
        in_tok, out_tok = tokens_for_cents(repro_c)
        cum += cost_micros(in_tok, out_tok)
        rows.append(["reproduce", fid, in_tok, out_tok, f"{micros_to_usd(cost_micros(in_tok, out_tok)):.2f}", f"{micros_to_usd(cum):.2f}"])
    for fid in repro_ids:
        in_tok, out_tok = tokens_for_cents(verify_c)
        cum += cost_micros(in_tok, out_tok)
        rows.append(["verify", fid, in_tok, out_tok, f"{micros_to_usd(cost_micros(in_tok, out_tok)):.2f}", f"{micros_to_usd(cum):.2f}"])
    write_csv(
        d / "cost.csv",
        ["phase", "finding_id", "input_tokens", "output_tokens", "cost_usd", "cumulative_usd"],
        rows,
    )
    total_micros = cum
    repro_micros = sum(cost_micros(*tokens_for_cents(repro_c)) for _ in repro_ids)
    triage_micros = sum(cost_micros(*tokens_for_cents(triage_c)) for _ in ledger)

    write_text(
        d / "loop-log.md",
        f"# Loop log - VaultDesk security triage\n\n{DEFENSIVE_BANNER}\n\n"
        "## /goal\n"
        "Prove or dismiss every scanner finding with executable evidence; no finding "
        "ships without a runnable repro, and an independent verifier re-runs each PoC "
        "against the patch.\n\n"
        "## What happened\n"
        f"- Triaged **{len(ledger)}** raw scanner hits.\n"
        f"- **{len(REPRODUCED)} reproduced** (a PoC exploited the issue, then the patch closed it).\n"
        f"- **{len(DISMISSED)} dismissed** as false positives (the loop tried to exploit each and failed).\n"
        f"- **{len(ESCALATED)} escalated** (reproduced, but the patch was insufficient).\n\n"
        "The scanner reported 23 'criticals/highs'; the loop proved 11 were lies - by "
        "trying to exploit each and failing.\n",
    )

    headline = {
        "example": 3,
        "title": "Claim-Ledger Security Fix",
        "raw_findings": len(ledger),
        "reproduced": len(REPRODUCED),
        "dismissed": len(DISMISSED),
        "escalated": len(ESCALATED),
        "total_usd": micros_to_usd(total_micros),
        "repro_share_pct": round(100 * repro_micros / total_micros, 1),
        "triage_share_pct": round(100 * triage_micros / total_micros, 1),
    }
    write_headline(d, headline)

    write_artifacts_index(
        d,
        "Example 3 - Claim-Ledger Security Fix",
        [
            ("Findings ledger (23 -> 9/11/3)", "findings-ledger.csv"),
            ("Cost ledger (repro dominates)", "cost.csv"),
            ("Loop log", "loop-log.md"),
            ("Headline numbers", "headline.json"),
        ],
        note="DEFENSIVE / TEACHING RECONSTRUCTION. Maker-checker on executable evidence.",
    )
    return headline


def _write_repro(d, fid, title, escalated: bool) -> None:
    base = d / "repro" / fid
    write_text(
        base / "poc.md",
        f"# {fid} - {title} (teaching PoC)\n\n{DEFENSIVE_BANNER}\n\n"
        "This is a **description** of how the issue was reproduced locally, not "
        "runnable exploit code. The loop ran the real PoC in a sandbox; here we record "
        "only the shape of the evidence.\n\n"
        "1. Set up the vulnerable code path in a local sandbox.\n"
        "2. Send the crafted input that triggers the issue.\n"
        "3. Observe the unsafe behavior (the test goes RED).\n"
        "4. Apply the patch and re-run (the test goes GREEN).\n",
    )
    if escalated:
        result = (
            "BEFORE PATCH: FAIL (issue reproduced in sandbox)\n"
            "AFTER PATCH:  FAIL (patch insufficient) -> ESCALATED to vendor\n"
        )
    else:
        result = (
            "BEFORE PATCH: FAIL (issue reproduced in sandbox)\n"
            "AFTER PATCH:  PASS (issue mitigated)\n"
        )
    write_text(base / "result.txt", result)


if __name__ == "__main__":
    print(generate())

# VD-2026-002 - Stored XSS in comment render (teaching PoC)

> **DEFENSIVE / TEACHING RECONSTRUCTION.** Fictional advisory IDs, synthetic CVSS scores, and local teaching PoCs only (descriptions, not runnable exploit code). No real product, no real vulnerability. Synthetic - for teaching the maker-checker-on-evidence pattern.

This is a **description** of how the issue was reproduced locally, not runnable exploit code. The loop ran the real PoC in a sandbox; here we record only the shape of the evidence.

1. Set up the vulnerable code path in a local sandbox.
2. Send the crafted input that triggers the issue.
3. Observe the unsafe behavior (the test goes RED).
4. Apply the patch and re-run (the test goes GREEN).

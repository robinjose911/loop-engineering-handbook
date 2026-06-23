# Loop B (docs) log

Goal: regenerate API reference from source comments.

## Phase 1 (no coordination)
- Edited shared files in `src/api/**` with no lock; collided with the other loop.
- Several passes re-did work that the other loop had clobbered.

## Phase 2 (lease dir + heartbeat/TTL + merge-queue)
- Acquire a lease on the path glob before editing; heartbeat every 30s; TTL 120s.
- On `LOCK DENIED`, `BACKOFF(30s)` and retry. Land via the merge queue.
- Result: zero conflicts.

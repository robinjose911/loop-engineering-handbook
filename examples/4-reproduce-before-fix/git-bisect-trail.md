# git bisect trail (60-commit regression range)

Only run after the gate opened (the bug is now reliably reproducible).

```
git bisect start
git bisect bad  griddesk@c160   # known bad (today)
git bisect good griddesk@c100   # known good (60 commits earlier)
bisect: 60 revisions left to test
  -> test c130: GOOD   (30 left)
  -> test c145: BAD    (15 left)
  -> test c137: BAD    (8 left)
  -> test c133: GOOD   (4 left)
  -> test c135: BAD    (2 left)
  -> test c134: BAD    (1 left)
c134 is the first bad commit
```

**Culprit:** `c134` shrank a cache TTL from `300s` to `0s`, so a hot path recomputed on every request under load.

**Fix (1 line):**
```diff
- const CACHE_TTL = 0;
+ const CACHE_TTL = 300; // seconds
```

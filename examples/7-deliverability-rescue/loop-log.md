# Loop log - The Tradewind Brief deliverability rescue

> Synthetic reconstruction for teaching. Metric-climb with an independent grader.

## /goal
Rewrite the re-engagement email until the **independent** spam scorer rates it >= 95/100 on the frozen rubric. The writer never edits the scorer.

## Climb
- Pass 1: **41/100** - baseline draft (ALL-CAPS subject, 6 exclamation marks, image-only body, no unsubscribe)
- Pass 2: **62/100** - rewrote the subject line in sentence case; removed ALL-CAPS
- Pass 3: **78/100** - cut spam-trigger phrases ('ACT NOW', 'FREE', 'limited time') and trimmed exclamations
- Pass 4: **88/100** - added a plaintext part and fixed the link-to-text ratio
- Pass 5: **93/100** - added a one-click unsubscribe header and sent from an authenticated domain
- Pass 6: **96/100** - tuned the preheader and reduced image-heaviness below the rubric threshold

Reached **96/100** (gate 95) on pass 6. Red SPAM 41 -> green INBOX 96.

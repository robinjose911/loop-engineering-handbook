# Loop log - Lumen Goods Q2 ad-spend reconciliation

> Synthetic reconstruction for teaching. Validation-gate over messy data.

## /goal
Reconcile Q2 ad invoices against the bank export until **variance = $0.00 and 0 unmatched rows**. If a charge cannot be classified, **ask for a rule** instead of guessing.

## Variance trajectory
- Start: **$1,402.88** (currencies not normalized, a duplicate, 3 orphan charges)
- After normalizing EUR/GBP invoices: **$410.10** (-$992.78)
- After de-duplicating INV-1006: **$88.40** (-$321.70)
- After resolving 3 orphan charges: **$0.00** BALANCED (-$88.40)

## Human ask-for-rule step
The loop could not classify `AD CREDIT ADJUSTMENT` on its own. It **paused and asked**: "Is a negative ad-credit a bank fee, a refund, or a contra-revenue line?" Human rule: *treat ad credits as a credit to the fees bucket.* The loop applied the rule and re-ran to $0.00.

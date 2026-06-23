# Spam-score rubric (FROZEN) - the independent grader

> The writer never sees this file's weights while drafting; a **separate** evaluator
> scores each draft. Writer != scorer. Frozen for the duration of the run.

| Signal | Max points | Rule |
|--------|-----------:|------|
| Subject line | 20 | No ALL-CAPS, <=1 exclamation, <=60 chars |
| Spam phrases | 20 | No known trigger phrases (FREE, ACT NOW, limited time...) |
| Text/HTML balance | 20 | Plaintext part present; link-to-text ratio <= 1:20 |
| Authentication | 15 | SPF + DKIM + DMARC aligned; authenticated sending domain |
| List hygiene | 15 | One-click unsubscribe header present |
| Image weight | 10 | <= 40% of body by area; alt text on all images |

**Gate: a draft passes at a score >= 95 / 100.**

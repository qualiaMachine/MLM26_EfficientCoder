---
name: mean-review
description: Adversarial review of a finished implementation — hunt for problems instead of confirming it works
---

# Mean Review

A different posture than building: given finished code (and the spec it was built against),
actively hunt for problems rather than confirm it works.

## Procedure

- Find every problem — readability, missed edge cases, error handling, anything the spec
  implied but the code didn't actually do
- State findings plainly; don't soften them into vague suggestions
- Distinguish must-fix from nice-to-have, but report both

Re-run tests after fixes — changing behavior without re-verifying just trades one bug for
another.

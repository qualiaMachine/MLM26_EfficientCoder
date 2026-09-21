---
name: goldfish-test
description: Test a spec for zero-context comprehension in a genuinely fresh session
---

# Goldfish Test

Only works in a session with no memory of the discussion that produced the spec. If this
session already has that context, say so and tell the user to start a fresh session first —
don't fake the test.

## What to load

- The specific spec file being tested
- The context hierarchy relevant to that feature — same scope `design-discussion` would load

Nothing else: not the conversation that produced the spec, not raw source beyond what the
context hierarchy describes, and not files outside this feature's scope. "Zero-context" means
free of the *discussion*, not free of the codebase's own standing documentation — a real
implementer would have that too. The question is whether the spec captures the decisions that
were made, given the context anyone would already have.

## The three checks

1. **Comprehension** — explain the feature back. Does it match what was agreed?
2. **Critic** — what holes does the spec have? Ambiguous cases, unstated assumptions?
3. **Readiness** — could implementation start right now, precisely, no follow-up needed?

Stay read-only (Plan Mode). Any gap found goes back into the spec, revised, before
implementation starts.

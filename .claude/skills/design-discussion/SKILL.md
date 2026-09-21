---
name: design-discussion
description: Scope a new feature, load only the relevant context, and discuss its design in prose before any code is written
---

# Design Discussion

Design discussion only — no implementation (see the `no-code-during-design` rule). Run in Plan
Mode.

## 1. Scope the feature

Ask what the feature touches if it isn't obvious. Identify which module(s) it most likely lives
in or affects — don't load the whole context hierarchy.

## 2. Load only the relevant context

Read that module's `CLAUDE.md` plus its ancestors up to the root of the context hierarchy — not
sibling modules unless the feature genuinely spans them, and not raw source beyond what's
needed to confirm a summary is still accurate.

## 3. First draft

Describe an approach in prose, not code. Say what's still uncertain, not just what you'd do.

## 4. Hand off

Once the design is settled, capture it durably (see `write-spec`) before it lives only in this
conversation.

(The `sycophant-challenge` rule already covers pushing back on step 3 — no need to repeat that
logic here.)

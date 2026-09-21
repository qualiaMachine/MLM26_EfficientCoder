---
name: context-sync
description: Keep the context hierarchy (nested CLAUDE.md files) from going stale as source changes
paths:
  - "backend/**"
---

# Keep the Context Hierarchy in Sync

After any change to a file under a directory that has its own `CLAUDE.md`, check whether that
file still accurately describes the directory — then say so and offer to update it, rather
than waiting to be asked. A parent directory's `CLAUDE.md` only needs revisiting if the change
affects what a reader would be told from the top down (a new module, a changed
responsibility) — not for every line-level edit.

Never regenerate a `CLAUDE.md` by re-reading the whole directory's source from scratch — read
the existing file first and edit only what's actually stale.

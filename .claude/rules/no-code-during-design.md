---
name: no-code-during-design
description: Enforce the EGM No Code Rule during design and spec phases
---

# No Code Rule

While discussing a feature's design (`design-discussion`), writing its spec (`write-spec`), or
running a Goldfish test (`goldfish-test`), do not write or edit source code — not even a small
"quick fix" the user didn't ask for. Deciding what to build stays separate from building it.

If asked to write code during one of these phases, check first whether the design is actually
agreed and speced yet. If it genuinely is time to implement, say so explicitly and point the
user at leaving Plan Mode (`Shift+Tab`) rather than just doing it — Auto mode's classifier may
approve a small edit automatically, so this check has to be yours, not the tool's.

# Agent safety

The full safety policy lives in the [challenge README](https://github.com/qualiaMachine/MLM26#safety). The short version for daily work:

**Terminal-Bench's sandbox does the heavy lifting.** Every task runs in a fresh Docker container with no host access, destroyed afterward. Inside `harbor run`, your agent can't hurt you. Don't undo that:

- Don't mount your home directory, SSH keys, or `~/.gitconfig` into containers.
- Don't bake real credentials into images or `.env` files you commit. Use throwaway keys.
- `.env` is gitignored here — keep it that way.

**The danger zone is your own dev loop.** When you test agent code *outside* Harbor (e.g., pointing your loop at a local shell "just to see"), it has whatever access you have:

- Develop in a scratch directory, never your home directory or a repo you care about.
- Never give a dev agent access to directories containing `.git` remotes, credentials, or anything you can't lose.
- Remember the classics: `git clean -fdx`, `docker system prune`, `find ... -exec rm`, `>` truncation. An agent will eventually try one.

**If your agent does something unexpected and concerning, tell us.** Novel failure modes are findings, not embarrassments — they're also great writeup material.

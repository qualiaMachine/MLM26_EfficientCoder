# starter/scripts/

## Purpose
Launchers for running the agent under Harbor, plus dev/verification utilities (job dashboard, VRAM checks).

## Contents
- `run_baseline.sh` — runs the agent on the 10-task `terminal-bench-sample@2.0` set, or one task if a name is given as `$1`; remaining args pass through to `harbor run`. `N_CONCURRENT` defaults to 1.
- `run_subset.sh` — runs the official public subset: reads `../eval/public_subset.txt`, builds `-i <task>` flags (strips `#` comments), runs against `terminal-bench@2.0`. `N_CONCURRENT` defaults to 2. Self-reported leaderboard score comes from this.
- `build_dashboard.py` — `python build_dashboard.py <job_dir> [-o out.html] [--open]`; renders every trial's `result.json` plus full transcript into one static, dependency-free HTML file (default `<job_dir>/dashboard.html`).
- `estimate_vram.py` — estimates a model's "reported VRAM" = Hub weight file sizes + 16k-token fp16 KV cache + 2 GB headroom. Needs network to huggingface.co.
- `check_vram_table.py` — parses the approved-model table in the *root* `README.md` and compares each row against `estimate_vram.py`; exits nonzero on gaps over `--tolerance` (default 4 GB).

## How it fits in
The `.sh` scripts are thin wrappers that point Harbor at `agent.agent:BaselineAgent` (so they
depend on the editable install) and are the entry points for measuring agent changes. The Python
scripts are independent of the agent at runtime: `build_dashboard.py` only reads job output;
the two VRAM scripts serve competition model-eligibility questions, not agent development.

## Gotchas
- Both `.sh` scripts `cd` to `starter/` first, so run them from anywhere; `harbor` must be on PATH (activated venv). For the hosted endpoint, wrap them: `op run --env-file=starter/.env.op -- ./starter/scripts/run_baseline.sh ...`.
- `run_subset.sh` pulls the full `terminal-bench@2.0` dataset, not the sample one.
- `../eval/public_subset.txt` (one task name per line, `#` comments ignored) currently holds 3 **placeholder** tasks; the official list is announced at kickoff, so don't treat its score as the real leaderboard number. The script errors only if the file yields zero names — unknown names aren't checked here.
- `build_dashboard.py` re-declares `CODE_BLOCK_RE`, `NUDGE_MESSAGE`, and the observation prefix/suffix from `agent/tools.py` and `agent/prompts.py`; it silently mis-renders transcripts if those change and this file isn't updated.
- Dashboards contain raw transcripts (anything the agent `cat`'d, possibly secrets) — local only, never upload or publish (`starter/docs/safety.md`).
- `check_vram_table.py` imports `estimate_vram` via `sys.path` and locates the README as `parents[2]` (repo root) — moving either script breaks it.
- The table value stays canonical for scoring; the VRAM scripts are transparency tools, and small gaps are expected.

# MVP Plan — badger_agent (Efficient Coder)

## Why this plan, not the original draft

The original draft MVP (test Qwen3.8-27B on terminal-bench 2.1, read up on ReAct, build a naive agent harness, implement an "LLM as a verifier" repo) has two issues:

- **Step "build a harness" is redundant.** `starter/agent/agent.py`'s `BaselineAgent` is already a complete, working, naive ReAct loop — build messages → one action via `tools.parse_action()` → `environment.exec()` in Docker → truncated observation → repeat. There's nothing to build; the remaining work is pointing `.env` at a model and running it.
- **"LLM as a verifier" is an architecture-level enhancement, not an MVP component.** Per `starter/README.md`'s own improvement-lever ordering, self-critique/verification is lever #4, after prompts, context management, and error recovery. It's exactly the kind of thing that should be A/B'd *against* a working baseline, not bundled into the first pass — and pulling in an external repo before a baseline exists adds integration/license risk and risk of breaking the "one system prompt, one agent loop, no task-specific logic" rule.
- **The draft never produces an actual baseline score.** Without `TB_score` / `total_tokens` / `leaderboard_score`, there's nothing to A/B later work against.

There's also already relevant evidence in the repo: `jobs/2026-09-12__21-32-36/` contains a 10-task sample run on the previously-configured hosted model. Verified from `result.json`: **mean reward 0.4** (4/10 pass), **5/10 tasks hit `AgentTimeoutError`**, and token usage is large (e.g. `build-cython-ext` took 87 turns and ~2.17M total tokens for one task — the naive loop resends the full growing conversation every turn with no summarization). This plan treats that as a head start.

**Decisions locked in:** the baseline score below runs on the 10-task sample (`terminal-bench-sample@2.0`), not the full 89 or the placeholder `public_subset.txt` (only 3 stub task names — official list "announced at kickoff"). `.env` switches from the previously-active `qwen3.8-27b` (`llm-gw01.doit.wisc.edu`) to the documented "official" endpoint, `Qwen3.6-27B-FP8` (matching the README's approved-model table), before the baseline run — so the first number is submission-safe. That endpoint's API key comes from the kickoff email; Step 1 treats getting it as a blocking check, not a silent assumption.

## Steps

### Step 0 — Zero-LLM sanity check
- **In:** `harbor run -d terminal-bench-sample@2.0 -a oracle`
- **Out:** confirms Docker/Harbor/grading pipeline works, independent of any model.
- **Model/data:** none; 10-task sample.
- **Works when:** all 10 tasks pass via reference solutions. (Skip if already done — check for a prior oracle job before rerunning.)

### Step 1 — Switch to the official endpoint
- **In:** `starter/.env` — comment out the `qwen3.8-27b` lines, uncomment the `Qwen3.6-27B-FP8` block, add the kickoff API key.
- **Out:** `.env` pointed at the approved, submission-safe model.
- **Model/data:** none (config only).
- **Works when:** `harbor run -d terminal-bench-sample@2.0 --agent-import-path agent.agent:BaselineAgent -i log-summary-date-ranges` completes without auth/connection errors. **Blocking check:** if the kickoff key isn't available yet, fall back to the current `qwen3.8-27b` config for now and clearly label any resulting scores as non-submission-safe until the switch happens.

### Step 2 — Read the working ReAct loop (not abstract theory)
- **In:** `starter/agent/agent.py`, `prompts.py`, `tools.py`, `llm.py`.
- **Out:** shared team understanding of the loop and its known gaps (prompting, context management, error recovery, self-critique — in that order), plus where `AGENT_MAX_TURNS` / `AGENT_COMMAND_TIMEOUT_SEC` live.
- **Model/data:** none.
- **Works when:** someone on the team can narrate the loop end-to-end and explain the Sept-12 run's timeout pattern from the code, without re-reading it.

### Step 3 — One task, confirm the new endpoint works
- **In:** the Step 1 command output (single task, hosted `Qwen3.6-27B-FP8`).
- **Out:** one `result.json` with a real reward + token counts; optionally viewed via `python starter/scripts/build_dashboard.py`.
- **Model/data:** hosted Qwen3.6-27B-FP8, 1 task.
- **Works when:** the run finishes cleanly with a reward (0 or 1) and non-zero token counts — this is the "first end-to-end pass."

### Step 4 — Full 10-task sample → baseline score
- **In:** `./starter/scripts/run_baseline.sh` on the new endpoint. Before running, weigh whether to raise `AGENT_COMMAND_TIMEOUT_SEC` / `AGENT_MAX_TURNS`, given the Sept-12 run's 5/10 timeout rate — or run as-is and treat the timeout rate itself as a baseline data point.
- **Out:** mean reward, total tokens, and `leaderboard_score = TB_score − 0.01×(total_tokens/1,000,000)` computed from the 10-task result set (per the `jq` recipe in the root README). This is a **10-task proxy**, not the official subset score — label it as such.
- **Model/data:** hosted Qwen3.6-27B-FP8, 10-task sample.
- **Works when:** the run completes, and the reward/timeout profile is comparable to (or better than) the Sept-12 baseline (0.4 mean reward, 5 timeouts) — giving a real number to A/B against.

### Step 5 — Document the baseline artifact
- **In:** Step 4's `result.json` files.
- **Out:** a short note, shaped like the `WRITEUP_TEMPLATE.md` submission card (model + quantization, tb_score, total_tokens, leaderboard_score, endpoint, wallclock, git commit) — not a formal submission, just the number everything else gets compared against.
- **Works when:** rerunning the same commit + task list reproduces a similar score.

### Step 6 — Candidate next experiments (in order, A/B'd against Step 5's baseline)
1. `prompts.py` — enforce "verify before TASK_COMPLETE," tighter output discipline (cheapest lever, and directly addresses the huge per-task token counts seen in the Sept-12 run).
2. Context management — summarize/drop old turns as the conversation grows (directly addresses the 87-turn / 2.17M-token `build-cython-ext` case).
3. Error recovery — detect repeated failing commands / timeouts, force a different approach (directly addresses the 5/10 `AgentTimeoutError` pattern).
4. Planning/self-critique, **including the "LLM as a verifier" idea** — the first architecture-level experiment to run once Step 5's baseline exists, and must still respect "one system prompt, one agent loop" to avoid disqualification risk.
5. Model/quantization choice, then broader architecture changes — later still, once cheaper levers are exhausted.

## Verification

- Step 0 and Step 3 are self-verifying (Harbor's own pass/fail + non-empty `result.json`).
- Step 4/5's score should be computed with the `jq` one-liners already documented in the root `README.md` ("Computing your submission numbers"), not hand-derived, to avoid transcription errors.
- Before treating any post-MVP experiment (Step 6) as an improvement, rerun the same 10-task sample and compare `leaderboard_score` deltas against the Step 5 baseline — that comparison *is* the A/B test the team is after.

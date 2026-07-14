"""MLM26: EfficientCoder — Kaggle leaderboard metric.

    leaderboard_score = tb_score − 0.01 × (total_tokens / 1,000,000)

Scores are self-reported: participants run Terminal-Bench 2.0 themselves
(via Harbor) and submit the resulting numbers. This metric therefore does
NOT compare against ground truth — the solution file is a placeholder that
exists because Kaggle requires one. What the metric does instead:

1. Validate the submission: exactly one row, all required columns, an
   approved (model, quantization) pair, sane numeric ranges, and non-empty
   repo / commit / writeup links.
2. Compute the score from the submission's own columns.

Honesty is enforced outside the metric: the top 5 teams are re-run and
code-reviewed after the deadline (see the competition rules), and the
repo + commit + writeup links on every submission are public.

Expected submission.csv (exactly this header, one data row):

    id,github_repo,commit_ref,model,quantization,tb_score,total_tokens,gpu,mean_wallclock_per_task,writeup_url

- id                       — literally 1 (matches the solution file)
- github_repo              — public repo with your agent code
- commit_ref               — tag or SHA of the exact code you ran
- model                    — approved checkpoint id (see the approved list
                             in the competition README)
- quantization             — FP8 | AWQ 4-bit | GGUF Q4_K_M
                             (GPTQ-Int4 counts as AWQ 4-bit)
- tb_score                 — mean Terminal-Bench reward across all 89
                             tasks, single attempt each, in [0, 1]
- total_tokens             — n_input_tokens + n_output_tokens summed
                             across all 89 tasks
- gpu                      — informational, not scored
- mean_wallclock_per_task  — informational, not scored
- writeup_url              — your writeup posted in the Discussion tab

Local self-test (no Kaggle needed):  python mlm26_metric.py
"""

import pandas as pd


class ParticipantVisibleError(Exception):
    """Raised for submission problems; the message is shown to the participant."""


TOKEN_PENALTY_PER_MILLION = 0.01

# Approved (model, quantization) pairs — keep in sync with the
# "Approved models" table in the competition README.
APPROVED = {
    ("Qwen/Qwen3.6-27B-FP8", "FP8"),
    ("Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8", "FP8"),
    ("Qwen/Qwen3-Coder-30B-A3B-Instruct", "GGUF Q4_K_M"),
    ("Qwen/Qwen2.5-Coder-32B-Instruct-AWQ", "AWQ 4-bit"),
    ("Qwen/Qwen2.5-Coder-14B-Instruct-AWQ", "AWQ 4-bit"),
    ("Qwen/Qwen2.5-Coder-7B-Instruct-AWQ", "AWQ 4-bit"),
}
# Accepted spellings that normalize onto an approved pair. Keys are
# lowercase (model, quantization); values are the canonical pair.
ALIASES = {
    # Ollama tag for the GGUF entry
    ("qwen3-coder:30b", "gguf q4_k_m"): ("Qwen/Qwen3-Coder-30B-A3B-Instruct", "GGUF Q4_K_M"),
    # GPTQ-Int4 counts as the AWQ 4-bit entry (per the rules)
    ("qwen/qwen2.5-coder-32b-instruct-awq", "gptq-int4"): ("Qwen/Qwen2.5-Coder-32B-Instruct-AWQ", "AWQ 4-bit"),
    ("qwen/qwen2.5-coder-14b-instruct-awq", "gptq-int4"): ("Qwen/Qwen2.5-Coder-14B-Instruct-AWQ", "AWQ 4-bit"),
    ("qwen/qwen2.5-coder-7b-instruct-awq", "gptq-int4"): ("Qwen/Qwen2.5-Coder-7B-Instruct-AWQ", "AWQ 4-bit"),
}

REQUIRED_COLUMNS = [
    "github_repo", "commit_ref", "model", "quantization",
    "tb_score", "total_tokens", "writeup_url",
]

# An 89-task run cannot plausibly use fewer tokens than this; a nonzero
# score with a near-zero token count is a malformed (or dishonest) row.
MIN_PLAUSIBLE_TOKENS = 10_000


def _clean(value) -> str:
    return str(value).strip()


def _normalized_pair(model: str, quantization: str):
    pair = (model, quantization)
    if pair in APPROVED:
        return pair
    return ALIASES.get((model.lower(), quantization.lower()))


def score(solution: pd.DataFrame, submission: pd.DataFrame, row_id_column_name: str) -> float:
    """Kaggle entry point. The solution frame is a placeholder and is only
    used for row alignment on the id column."""
    if len(submission) != len(solution):
        raise ParticipantVisibleError(
            f"Submission must have exactly {len(solution)} data row(s), got {len(submission)}."
        )

    missing = [c for c in REQUIRED_COLUMNS if c not in submission.columns]
    if missing:
        raise ParticipantVisibleError(
            f"Submission is missing required column(s): {', '.join(missing)}. "
            "See the sample submission for the expected header."
        )

    row = submission.iloc[0]

    for col in ("github_repo", "commit_ref", "writeup_url"):
        if not _clean(row[col]) or _clean(row[col]).lower() in ("nan", "none"):
            raise ParticipantVisibleError(
                f"'{col}' must be non-empty — it's how your result is verified."
            )

    model = _clean(row["model"])
    quantization = _clean(row["quantization"])
    if _normalized_pair(model, quantization) is None:
        raise ParticipantVisibleError(
            f"({model!r}, {quantization!r}) is not on the approved model list. "
            "See the Approved models section of the competition README; "
            "additions can be requested via the Discussion tab."
        )

    try:
        tb_score = float(_clean(row["tb_score"]))
    except ValueError:
        raise ParticipantVisibleError("'tb_score' must be a number between 0 and 1.")
    if not 0.0 <= tb_score <= 1.0:
        raise ParticipantVisibleError(f"'tb_score' must be in [0, 1], got {tb_score}.")

    try:
        # tolerate thousands separators, e.g. "1,263,800"
        total_tokens = int(float(_clean(row["total_tokens"]).replace(",", "")))
    except ValueError:
        raise ParticipantVisibleError("'total_tokens' must be a non-negative integer.")
    if total_tokens < 0:
        raise ParticipantVisibleError("'total_tokens' cannot be negative.")
    if tb_score > 0 and total_tokens < MIN_PLAUSIBLE_TOKENS:
        raise ParticipantVisibleError(
            f"A nonzero tb_score with total_tokens={total_tokens} is not plausible "
            f"for an 89-task run (minimum {MIN_PLAUSIBLE_TOKENS:,}). "
            "Report the token count from Harbor's result.json files."
        )

    return tb_score - TOKEN_PENALTY_PER_MILLION * (total_tokens / 1_000_000)


if __name__ == "__main__":
    # Self-test: run `python mlm26_metric.py` — prints nothing on success.
    sol = pd.DataFrame({"id": [1], "placeholder": ["-"]})

    def sub(**overrides):
        base = {
            "id": 1,
            "github_repo": "https://github.com/team/agent",
            "commit_ref": "v1.0-submission",
            "model": "Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
            "quantization": "AWQ 4-bit",
            "tb_score": 0.42,
            "total_tokens": "1,263,800",
            "gpu": "RTX A6000 48 GB",
            "mean_wallclock_per_task": "3m 12s",
            "writeup_url": "https://kaggle.com/competitions/MLM26-EfficientCoder/discussion/1",
        }
        base.update(overrides)
        return pd.DataFrame([base])

    def expect_error(fragment, **overrides):
        try:
            score(sol, sub(**overrides), "id")
        except ParticipantVisibleError as e:
            assert fragment in str(e), (fragment, str(e))
        else:
            raise AssertionError(f"expected error containing {fragment!r}")

    # Worked example from the README: 0.42 − 0.01 × 1.2638 = 0.407362
    assert abs(score(sol, sub(), "id") - 0.407362) < 1e-9
    # Aliases normalize
    assert score(sol, sub(model="qwen3-coder:30b", quantization="GGUF Q4_K_M",
                          tb_score=0.3, total_tokens=500_000), "id") == 0.295
    assert score(sol, sub(quantization="GPTQ-Int4"), "id") > 0
    # Zero score, zero tokens is a legal (if sad) submission
    assert score(sol, sub(tb_score=0.0, total_tokens=0), "id") == 0.0
    # Rejections
    expect_error("not on the approved model list", model="gpt-4o")
    expect_error("not on the approved model list", quantization="bf16")
    expect_error("must be in [0, 1]", tb_score=1.2)
    expect_error("not plausible", total_tokens=5)
    expect_error("non-empty", writeup_url="")
    bad = sub().drop(columns=["writeup_url"])
    try:
        score(sol, bad, "id")
    except ParticipantVisibleError as e:
        assert "missing required column" in str(e)
    else:
        raise AssertionError("expected missing-column error")
    two_rows = pd.concat([sub(), sub()], ignore_index=True)
    try:
        score(sol, two_rows, "id")
    except ParticipantVisibleError as e:
        assert "exactly 1" in str(e)
    else:
        raise AssertionError("expected row-count error")
    print("all self-tests passed")

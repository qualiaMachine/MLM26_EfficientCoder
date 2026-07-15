"""Maintainer notes (participants see score()'s docstring instead).

- APPROVED / ALIASES must stay in sync with the "Approved models" table on
  the competition Overview page (README.md in the challenge repo).
- The solution file is a placeholder: id=1 Usage=Public, id=2 Usage=Private
  (Kaggle requires Private rows for final rankings). Participants submit two
  identical data rows; each leaderboard scores its own one-row slice, so
  public and private scores are equal by construction. Scores come from the
  submission's own columns — there is no ground truth.
- Local checks: `python mlm26_metric.py` runs doctests + self-tests and
  prints "all self-tests passed" on success.
"""

import pandas as pd


class ParticipantVisibleError(Exception):
    """Raised for submission problems; the message is shown to the participant."""


TOKEN_PENALTY_PER_MILLION = 0.01

# Approved (model, quantization) pairs — keep in sync with the
# "Approved models" table on the competition Overview page (README.md in the repo).
APPROVED = {
    ("Qwen/Qwen3.6-27B-FP8", "FP8"),
    ("Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8", "FP8"),
    ("Qwen/Qwen3-Coder-30B-A3B-Instruct", "GGUF Q4_K_M"),
    ("Qwen/Qwen2.5-Coder-32B-Instruct-AWQ", "AWQ 4-bit"),
    ("Qwen/Qwen2.5-Coder-14B-Instruct-AWQ", "AWQ 4-bit"),
    ("Qwen/Qwen2.5-Coder-7B-Instruct-AWQ", "AWQ 4-bit"),
}
# Accepted spellings that normalize onto an approved pair — equivalent
# quantizations (GGUF Q4_K_M, GPTQ-Int4) count as the model's AWQ 4-bit
# entry per the rules, and people should be able to write what they
# actually ran. Keys are lowercase (model, quantization); values are the
# canonical pair.
ALIASES = {
    # Ollama tag for the Qwen3-Coder MoE GGUF entry
    ("qwen3-coder:30b", "gguf q4_k_m"): ("Qwen/Qwen3-Coder-30B-A3B-Instruct", "GGUF Q4_K_M"),
}
for _size in ("32b", "14b", "7b"):
    _canon = (f"Qwen/Qwen2.5-Coder-{_size.upper()}-Instruct-AWQ", "AWQ 4-bit")
    _awq_id = _canon[0].lower()
    _gptq_id = _awq_id.replace("-awq", "-gptq-int4")
    for _model, _quant in [
        (_awq_id, "gptq-int4"),               # AWQ id, GPTQ spelling
        (_gptq_id, "gptq-int4"),              # the actual GPTQ checkpoint id
        (_awq_id, "gguf q4_k_m"),             # AWQ id, GGUF spelling
        (f"qwen2.5-coder:{_size}", "gguf q4_k_m"),   # Ollama tag
        (f"qwen2.5-coder:{_size}", "gptq-int4"),
    ]:
        ALIASES[(_model, _quant)] = _canon
del _size, _canon, _awq_id, _gptq_id, _model, _quant

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
    """Efficient Coding Agent leaderboard score.

        leaderboard_score = tb_score - 0.01 * (total_tokens / 1,000,000)

    Scores are self-reported: participants run Terminal-Bench 2.0 themselves
    (via Harbor) and submit the resulting numbers, so this metric does NOT
    compare against ground truth — the solution file is a placeholder used
    only for row alignment. The metric validates the submission and computes
    the score from its own columns:

    - two identical data rows, ids 1 and 2 (Kaggle scores one per
      leaderboard), with all required columns present
    - (model, quantization) on the approved list — equivalent quantizations
      (GGUF Q4_K_M, GPTQ-Int4, Ollama tags) normalize to the model's
      approved entry
    - tb_score in [0, 1]; total_tokens a plausible non-negative integer
    - non-empty github_repo, commit_ref, and writeup_url (verification links)

    Honesty is enforced outside the metric: the top 5 teams are re-run and
    code-reviewed after the deadline, per the competition rules.

    Example — the worked example from the Overview page, as Kaggle passes it
    to the metric (the aligned one-row slice for one leaderboard):

    >>> import pandas as pd
    >>> sol = pd.DataFrame({"id": [1]})
    >>> sub = pd.DataFrame([{
    ...     "id": 1,
    ...     "github_repo": "https://github.com/team/agent",
    ...     "commit_ref": "v1.0-submission",
    ...     "model": "Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
    ...     "quantization": "AWQ 4-bit",
    ...     "tb_score": 0.42,
    ...     "total_tokens": 1263800,
    ...     "gpu": "RTX A6000 48 GB",
    ...     "mean_wallclock_per_task": "3m 12s",
    ...     "writeup_url": "https://kaggle.com/competitions/efficient-coding-agent/discussion/1",
    ... }])
    >>> round(score(sol, sub, "id"), 6)
    0.407362
    """
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
            "See the Approved models section of the Overview page; "
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

    return float(tb_score - TOKEN_PENALTY_PER_MILLION * (total_tokens / 1_000_000))


if __name__ == "__main__":
    import doctest
    failures, _ = doctest.testmod()
    assert failures == 0, f"{failures} doctest failure(s)"

    # Self-tests: `python mlm26_metric.py` prints "all self-tests passed".
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
            "writeup_url": "https://kaggle.com/competitions/efficient-coding-agent/discussion/1",
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
    assert score(sol, sub(model="Qwen/Qwen2.5-Coder-32B-Instruct-GPTQ-Int4",
                          quantization="GPTQ-Int4"), "id") > 0
    assert score(sol, sub(model="qwen2.5-coder:14b",
                          quantization="GGUF Q4_K_M"), "id") > 0
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

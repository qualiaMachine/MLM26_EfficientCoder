"""Scoring metric for the Archival Document Transcription Challenge.

Leaderboard score = Character Error Rate (CER), macro-averaged across
document categories. Lower is better.

    page CER     = levenshtein(prediction, reference) / len(reference), capped at 1.0
    category CER = mean of page CERs within the category
    score        = mean of category CERs

Comparison is verbatim — casing, punctuation, and historical spelling all
count. The only normalization applied to BOTH sides before comparison:
  * literal two-character "\\n" escapes become newlines,
  * Unicode NFC normalization,
  * all whitespace runs collapse to a single space; leading/trailing stripped.
See docs/transcription_conventions.md for the ground-truth conventions.

Kaggle usage: `score(solution, submission, "page_id")`, where
  solution   columns: page_id, text, category  (+ optional Usage)
  submission columns: page_id, text

Self-test: `python evaluation/metric.py`
"""

import unicodedata

import pandas as pd


class ParticipantVisibleError(Exception):
    """Raised for submission problems; the message is shown to the participant."""


def normalize_text(text) -> str:
    """Apply the (only) normalizations scoring allows. Everything else is verbatim."""
    if text is None or (isinstance(text, float) and pd.isna(text)):
        return ""
    text = str(text)
    # Line breaks may be submitted as literal backslash-n escapes.
    text = text.replace("\\n", "\n")
    text = unicodedata.normalize("NFC", text)
    return " ".join(text.split())


def levenshtein(a: str, b: str) -> int:
    """Edit distance, two-row DP; O(len(a) * len(b)) time, O(min) memory."""
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            curr.append(min(
                prev[j] + 1,        # deletion
                curr[j - 1] + 1,    # insertion
                prev[j - 1] + (ca != cb),  # substitution
            ))
        prev = curr
    return prev[-1]


def page_cer(prediction: str, reference: str) -> float:
    """Per-page CER against the normalized reference, capped at 1.0.

    An empty reference would divide by zero; reference pages are curated to be
    non-empty, but guard anyway: empty reference scores 0.0 for an empty
    prediction and 1.0 otherwise.
    """
    pred = normalize_text(prediction)
    ref = normalize_text(reference)
    if not ref:
        return 0.0 if not pred else 1.0
    return min(1.0, levenshtein(pred, ref) / len(ref))


def page_wer(prediction: str, reference: str) -> float:
    """Word Error Rate — diagnostic only, never used for ranking."""
    pred = normalize_text(prediction).split()
    ref = normalize_text(reference).split()
    if not ref:
        return 0.0 if not pred else 1.0
    # Reuse levenshtein over word sequences via a sentinel join.
    dist = _seq_levenshtein(pred, ref)
    return min(1.0, dist / len(ref))


def _seq_levenshtein(a, b) -> int:
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ta in enumerate(a, start=1):
        curr = [i]
        for j, tb in enumerate(b, start=1):
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + (ta != tb)))
        prev = curr
    return prev[-1]


def per_category_cer(solution: pd.DataFrame, submission: pd.DataFrame,
                     row_id_column_name: str = "page_id") -> "pd.Series":
    """Mean page CER per category; index = category. Shared by score() and score_local."""
    for col in (row_id_column_name, "text", "category"):
        if col not in solution.columns:
            raise ValueError(f"solution is missing required column '{col}'")
    if row_id_column_name not in submission.columns:
        raise ParticipantVisibleError(f"Submission is missing the '{row_id_column_name}' column.")
    if "text" not in submission.columns:
        raise ParticipantVisibleError("Submission is missing the 'text' column.")

    sub = submission.drop_duplicates(subset=row_id_column_name, keep="last")
    if len(sub) < len(submission):
        raise ParticipantVisibleError("Submission contains duplicate page_id rows.")
    merged = solution.merge(sub[[row_id_column_name, "text"]],
                            on=row_id_column_name, how="left",
                            suffixes=("_ref", "_pred"))
    missing = merged["text_pred"].isna() & merged["text_ref"].notna()
    # Missing rows are allowed but score CER 1.0 (same as an empty prediction).
    merged.loc[missing, "text_pred"] = ""

    merged["cer"] = [
        page_cer(p, r) for p, r in zip(merged["text_pred"], merged["text_ref"])
    ]
    return merged.groupby("category")["cer"].mean()


def score(solution: pd.DataFrame, submission: pd.DataFrame,
          row_id_column_name: str = "page_id") -> float:
    """Kaggle entry point. Returns macro-averaged CER (lower is better)."""
    if "Usage" in solution.columns:
        solution = solution.drop(columns=["Usage"])
    return float(per_category_cer(solution, submission, row_id_column_name).mean())


if __name__ == "__main__":
    # Self-test: run `python evaluation/metric.py`
    sol = pd.DataFrame({
        "page_id": ["a1", "a2", "b1", "b2"],
        "text": ["Meandered the Lake", "N 40 E 12.50", "Lieber Bruder,\nes geht", "To 3 chairs 0.7.6"],
        "category": ["survey_notes", "survey_notes", "kade_letters", "dominy_accounts"],
    })

    perfect = sol[["page_id", "text"]].copy()
    assert score(sol, perfect) == 0.0

    # Whitespace layout is free: \n escapes and extra spaces score identically.
    ws = perfect.copy()
    ws.loc[2, "text"] = "Lieber   Bruder, \\n es geht"
    assert score(sol, ws) == 0.0

    # Case matters (verbatim scoring).
    cased = perfect.copy()
    cased.loc[0, "text"] = "meandered the lake"
    assert score(sol, cased) > 0.0

    # Garbage and empty predictions both cap at CER 1.0 for the page.
    garbage = perfect.copy()
    garbage.loc[1, "text"] = "x" * 500
    empty = perfect.copy()
    empty.loc[1, "text"] = ""
    assert score(sol, garbage) == score(sol, empty)

    # Macro average: one bad page in a 2-page category = 0.5 category CER / 3 categories.
    assert abs(score(sol, empty) - (0.5 / 3)) < 1e-9

    # Missing row scores like an empty prediction, not an error.
    blank_b2 = perfect.assign(text=perfect["text"].where(perfect["page_id"] != "b2", ""))
    assert score(sol, perfect.iloc[:3]) == score(sol, blank_b2)

    # Duplicate ids are rejected.
    try:
        score(sol, pd.concat([perfect, perfect.iloc[:1]]))
        raise AssertionError("duplicate ids should raise")
    except ParticipantVisibleError:
        pass

    assert levenshtein("kitten", "sitting") == 3
    assert page_wer("the cat sat", "the cat sat") == 0.0
    assert abs(page_wer("the dog sat", "the cat sat") - 1 / 3) < 1e-9

    print("all metric self-tests passed")

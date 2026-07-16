# Maintainer notes

Internal working notes for organizers (Chris, Scott, Kevin). Participants can ignore this file — nothing here changes the rules.

## Decision log

Decisions settled in the planning doc + email thread (June–July 2026):

- **Challenge dataset is UW samples only.** External public datasets moved from "benchmark components" to a suggested-resources section participants pull themselves. Rationale: effort savings, and assembling a calibration set becomes part of the challenge itself. Fallback if in-house sample prep falls flat: pivot back to building in auxiliary data (Bentham/IAM subsets).
- **Ground truth strategy:** at least one transcribed sample from as many collections as staff time allows this year; Sternberger & Seifert letters already have MKI Kurrent-group transcriptions (free GT for the Kade category). Sample selection aims for diversity: different hands, tabular vs. prose, microfilm vs. direct scans. Scoring may weight UW docs more heavily if needed — currently moot since the eval set is 100% UW.
- **Resources list:** Bentham, BLN600, NARA RG 109 as best matches; IAM kept as calibration-only with its modern-handwriting limitation noted; Alfred Escher correspondence added for period German (Kurrent).
- **Metric:** CER primary, verbatim (no normalization), whitespace collapsed; macro-average across categories; WER as diagnostic only. Cap per-page CER at 1.0.
- **Rules:** open-weight <70B per model, honor-system up front, top-10 code review before winners announced; code link (public GitHub, pinned commit) required with every submission; no prize, collaborative framing.
- **Starter notebooks (Kevin):** (1) traditional pipeline from scratch (layout detection → language routing → recognition), (2) open-source tools (Kraken segmentation + PyLaia recognition), (3) small open-weight VLM. Optional fine-tuning angle: ~100 curated drawn-table pages from the survey notebooks.
- **Kaggle Hackathon format, not a scored competition (July 2026, Chris).** The Writeup is the submission — same format Efficient Coder landed on. Rationale: the writeup/documented-process is the whole point for the Libraries; no prize means no need for adversarial-grade scoring infrastructure. Consequence: the UW GT sample is **released** (images + solution.csv) as the public evaluation set teams tune toward with auxiliary data; scores are self-reported from `score_local.py` on submission cards, spot-checked, top 10 re-run/code-reviewed. No hidden test set, no auto-scored leaderboard, no submission CSV upload; standings kept as a Discussion-tab post. New rule carrying the weight: evaluation pages are for measuring, not training.

## Open questions

- [ ] Reading-order convention for marginalia (survey notebooks) — Chris, with Scott
- [ ] Whether `#` illegibility markers count toward reference length in scoring — Chris
- [ ] Final collection list: do all four categories get enough GT pages this year, or does a category drop? — Scott
- [ ] Kaggle slug + launch dates (kickoff Fall 2026) — Chris
- [ ] License file for this repo (code MIT? UW image derivatives need their own rights statement) — Chris + Scott
- [ ] Whether hosted endpoints serving named open-weight checkpoints count for the *submitted* run or prototyping only (FAQ currently says prototyping; on-prem spirit suggests submitted runs should at least be reproducible on-prem) — Chris

## Launch checklist

- [ ] GT pages transcribed + double-checked per `docs/transcription_conventions.md`; conventions doc updated with per-collection quirks and de-drafted
- [ ] Package Kaggle dataset (`eval/images/`, `metadata.csv`, `solution.csv`) — well under the 20 GB cap; JPEG derivatives of the TIFFs
- [ ] Sanity-check the released `solution.csv` through `score_local.py` (perfect submission scores 0.0; per-category counts look right)
- [ ] Set up the Kaggle Hackathon: Writeup submission flow, Open track, cover-image note; seed the standings post in Discussion
- [ ] Kevin: fill in the three starter notebooks against the released evaluation pages; run end-to-end on Kaggle Notebooks free tier; record baseline CERs per category (also gives us the difficulty read and seeds the standings post)
- [ ] Baseline comparison table (Tesseract / Kraken+PyLaia / small VLM) posted to Discussion at launch
- [ ] Copy README sections to the Kaggle Overview/Data tabs; RULES.md to the rules section
- [ ] Everyone joined the ML+X Kaggle organization (invite link in the planning doc — not committed here)
- [ ] Announce soft launch; official UW–Madison kickoff Fall 2026

## Repo conventions

- README.md mirrors the Kaggle home-page section layout (same convention as the Efficient Coder repo); DATA.md is the Data tab; RULES.md the rules section.
- `evaluation/metric.py` is the single source of truth for scoring — `score_local.py` wraps it, participants self-report from it, and verification re-runs it; it carries a self-test (`python evaluation/metric.py`).
- Placeholders that must be resolved before launch are marked `TBD` or tracked above.

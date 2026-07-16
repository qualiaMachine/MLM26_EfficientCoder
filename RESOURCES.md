# Resources

No training set ships with this challenge — assembling calibration and training data that resembles the test material is part of the work. This page lists public datasets matched to the UW collections, the collections' own public browsers, and the main open-source tooling families.

## Suggested public datasets

Each entry notes its ground-truth (GT) type and how it maps to the test categories. Every dataset is governed by its own upstream license — check before use.

### Historical English handwriting (→ survey notes, Dominy accounts, treaty documents)

- **Bentham** (Transcribe Bentham) — 18th–19th-c. English manuscripts with crowd-sourced page/line transcriptions. The closest public match to the UW English handwriting. GT: line/page transcripts. Reported CERs for Bentham sit around 5–10% even for strong systems ([baseline survey, 2025](https://arxiv.org/pdf/2503.15195)) — a realistic difficulty anchor. https://www.jamesphawkins.com/bentham/
- **NARA citizen-transcription datasets** — U.S. National Archives crowd-transcribed record groups; the Civil-War-era **RG 109** series is a strong match for 19th-c. American institutional hands and degraded originals. GT: page transcripts; needs some manipulation. https://www.archives.gov/files/developer/nara-datasets-for-artificial-intelligence-machine-learning.pdf

### Historical German handwriting (→ Max Kade letters)

- **Alfred Escher correspondence** — thousands of 19th-c. German letters with transcriptions, same period and Kurrent-family script as the Kade letters. Pre-1940 German handwriting is a genuinely different script from English cursive — do not expect an English-tuned recognizer to transfer. GT: transcripts. https://zenodo.org/records/439811

### Historical print and degraded scans (→ treaties microfilm, printed records)

- **BLN600** — 19th-c. British Library newspapers, 600 excerpts with transcriptions. Excerpt-level (no line breaks) and small, but real historical print with real degradation. https://eprints.whiterose.ac.uk/id/eprint/217296/

### Calibration-only (limitations noted)

- **IAM Handwriting Database** — the classic line-level English handwriting benchmark (~266 MB, easy to work with). **Caveat: modern handwriting** — foundation models report 1–2% CER on it, so treat it as a pipeline-plumbing and sanity-check resource, not a difficulty proxy for archival material. https://huggingface.co/datasets/Teklia/IAM-line · https://fki.tic.heia-fr.ch/databases/iam-handwriting-database
- **OCRBench v2** — broad OCR benchmark with handwriting and multilingual sub-tasks. Much of it is VQA / key-information extraction, which is *not* this task — cherry-pick the pure transcription sub-tasks only. https://github.com/Yuliang-Liu/MultimodalOCR · https://huggingface.co/datasets/lmms-lab/OCRBench-v2

### Layout / structure (→ hand-drawn tables, forms), secondary

- **FUNSD** — 199 scanned forms with annotations; small, form-focused. https://guillaumejaume.github.io/FUNSD/
- **DocLayNet** — large layout-detection dataset (born-digital, modern), useful only for the layout-detection stage of a traditional pipeline. https://huggingface.co/datasets/docling-project/DocLayNet

## Curate your own UW samples

The source collections are publicly browsable — transcribing a small sample yourself (e.g., ~100 lines of survey-notebook tables) is a legitimate and possibly winning move for fine-tuning, and the kind of "interesting data find" this challenge is designed to surface. Test-set pages themselves are off-limits for training (see [RULES.md](RULES.md)).

- Wisconsin Land Survey Field Notes: https://search.library.wisc.edu/digital/ASurveyNotes
- Max Kade Institute German letters: https://digital.library.wisc.edu/1711.dl/KadeLetters
- Dominy Craftsmen account books: https://digital.library.wisc.edu/1711.dl/Dominy
- Native American treaty documents: https://digital.library.wisc.edu/1711.dl/TreatiesMicro

## Tooling

- **Traditional / open-source HTR**: [Kraken](https://kraken.re/) (layout + line segmentation), [PyLaia](https://gitlab.teklia.com/atr/pylaia) (line recognition), [Tesseract](https://github.com/tesseract-ocr/tesseract) (print), [TrOCR](https://huggingface.co/docs/transformers/model_doc/trocr) (transformer line recognizer, fine-tunable).
- **Open-weight VLMs** (all well under the 70B cap): Qwen2.5-VL (3B/7B/32B), InternVL, Pixtral-12B, Llama 3.2 Vision 11B — prompt for page-level transcription or fine-tune on curated lines.
- Starter notebooks for each family are in [`notebooks/`](notebooks/).

## Compute

Everything here runs on a single consumer/workstation GPU: the starter VLM notebook targets a 7B model (fits in 16–24 GB), and Kraken/PyLaia/TrOCR train and run on far less. No-GPU options: Kaggle Notebooks' free GPU quota covers inference-scale experiments, and hosted endpoints that serve *named open-weight checkpoints* are fine for prototyping (the submitted run must still satisfy the model rules in [RULES.md](RULES.md)). UW–Madison participants: hosted-LLM details will be shared at kickoff.

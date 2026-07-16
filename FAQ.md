# FAQ

**Can I use GPT / Claude / Gemini anywhere in my pipeline?**
Not in the submitted run — closed-weight API models are out of scope, including "just for post-correction." The point of the challenge is a pipeline a library can run on-prem; a solution that routes pages through a frontier API doesn't transfer. Prototype against anything you like; the submitted pipeline must be open-weight models under 70B parameters throughout.

**Is the 70B limit per model or for the whole pipeline?**
Per model. A pipeline chaining a layout detector, two recognizers, and a 7B post-corrector is fine — every individual model must be open-weight and under 70B parameters.

**There's no training data. What do I train on?**
Whatever you can find or make — that's deliberately part of the challenge. [RESOURCES.md](RESOURCES.md) maps public datasets (Bentham, NARA RG 109, Alfred Escher, BLN600, IAM…) to the test categories, and the UW collections are publicly browsable if you want to transcribe your own fine-tuning sample. Note that with modern pretrained VLMs, training is increasingly optional — but you'll still want calibration data to measure yourself against before spending your daily submissions.

**Can I fine-tune?**
Yes, encouraged — even ~100 curated pages of the survey notebooks' drawn tables might yield significant gains on that category. The fine-tuned model counts against the 70B cap via its base model, and your weights must be public or reproducible from the public base plus your published adapter. Document your data in the writeup.

**Can I just transcribe the test pages by hand?**
No. Predictions must come from your pipeline; manual transcription or manual correction of test pages disqualifies the entry (and is checked in the top-10 code review). Hand-transcribing *other* pages from the same collections to build training data is fine and encouraged.

**The Kade letters are in German — do I have to handle that?**
Yes, if you want a good score: the leaderboard macro-averages across categories, so tanking the German category costs you a full quarter of the weight. Pre-1940 German handwriting (Kurrent) is a different script from English cursive; see the Alfred Escher dataset in [RESOURCES.md](RESOURCES.md).

**How exactly is my text compared to the ground truth?**
Verbatim — casing, punctuation, and historical spelling all count, and "corrections" of the original spelling count as errors. The only normalization is collapsing whitespace runs to single spaces before scoring. Read [`docs/transcription_conventions.md`](docs/transcription_conventions.md) and [`evaluation/metric.py`](evaluation/metric.py); you can score yourself locally with `evaluation/score_local.py`.

**I don't have a GPU.**
The starter notebooks target models that fit Kaggle Notebooks' free GPU quota, and hosted endpoints serving named open-weight checkpoints are fine for prototyping. See the Compute section of [RESOURCES.md](RESOURCES.md).

**My team is just me. / My team is five people.**
Both fine. Teams of 1–5. Reflect honestly on contributions in the writeup.

**I'm not at UW–Madison.**
Welcome — the challenge is fully open, and the leaderboard is the leaderboard. You won't have access to UW-only hosted compute, but nothing here requires it.

**What happens to the winning pipelines?**
Code review of the top 10, then winners announced — and the real payoff: the UW Digital Collections Center is looking for a process it can adopt for production transcription of its collections, with minimal staff effort. The best outcome for this challenge is your pipeline running in an actual library.

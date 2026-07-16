# Challenge rules

## 1. Sponsor

This challenge is organized by the [ML+X](https://hub.datascience.wisc.edu/communities/mlx/) community at UW–Madison together with the UW Digital Collections Center, with support from ML+X sponsors.

## 2. Prizes

This is a non-monetary educational challenge. There are no cash or material prizes. Top teams may be invited to present at the ML+X showcase, and strong pipelines may be adopted for production transcription work at the UW Libraries.

## 3. Team limits

- Maximum team size: 5 participants.
- Team mergers are allowed as long as the merged team stays within the submission limits and the maximum team size.

## 4. Submission integrity

- **Open-weight models under 70B parameters only.** Every model in your submitted pipeline — recognizer, layout detector, language router, post-corrector, all of it — must be an open-weight model under 70B parameters, deployable on-prem. Closed-weight API models (GPT, Claude, Gemini) are out of scope anywhere in the submitted pipeline, including "just the post-correction step." Development and prototyping on any model is fine — the rule binds the submitted run. The limit is honor-system during the challenge and verified by code review at the end.
- **No human transcription of test images.** Predictions must be produced by your pipeline. Manually transcribing (or manually correcting) test pages defeats the purpose and disqualifies the entry. Humans building, tuning, and debugging the pipeline is of course fine — that's the challenge.
- **External data is allowed and encouraged** for training, fine-tuning, and calibration, provided it is publicly available or lawfully licensed and documented in your writeup. Curating your own transcribed samples from the public UWDC image browsers is explicitly encouraged — but test-set pages themselves may not be used for training or tuning.
- **Code sharing is part of participating.** Every submission links a public GitHub repo, pinned to the exact commit or tag that produced the predictions, in its submission card.
- **Results must be reproducible.** Before winners are announced, organizers code-review the top 10 leaderboard entries: model-size limit respected, no manual transcription, and predictions reproducible from the posted code (LLM sampling is stochastic; normal run-to-run variation is expected and fine). Significant discrepancies disqualify, and fabricated entries are removed whenever found.

## 5. Submission limits

- Up to 5 prediction submissions per team per day; the best-scoring submission counts.
- The writeup with the submission card must be posted before the deadline for the entry to be eligible.

## 6. Data

Test images come from the University of Wisconsin–Madison Digital Collections and are provided for challenge use; respect any rights statements accompanying the source collections. Suggested external datasets listed in [RESOURCES.md](RESOURCES.md) are governed by their own upstream licenses — check them before use.

## 7. License

Submission repos must be public and licensed MIT or Apache 2.0.

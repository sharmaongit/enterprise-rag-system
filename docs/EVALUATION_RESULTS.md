# Evaluation results (executed in the current build environment)

Date: 2026-10-23. Python: 3.13.5.

## Automated tests

Command: `PYTHONPATH=src python -m pytest -q`

Result: **14 passed**. Covered dataset schema/row count, routing, CRAG grading and retry bounds, unrelated-evidence rejection, SQL read-only restrictions, Self-RAG-style empty-evidence abstention, citation verification, retrieval metric helpers, structured cancellation-rate query against an independently calculated pandas result, API health and query flow, and a basic prompt-injection prompt-construction check.

## Smoke evaluation

Command: `PYTHONPATH=src python scripts/run_evaluation.py`

Result: **4/4 passed**.

- Count question: 2,510 flight records.
- Average duration: 179.86 minutes over 2,510 records with a duration value.
- Highest cancellation rate: Lufthansa, 4.39% (14 of 319 records).
- Flight lookup: FL10002 returned a British Airways record with status `Delayed`.

These are four deterministic smoke cases, not a broad RAG benchmark. They do not establish semantic retrieval quality, general factual accuracy, or production readiness.

## Data inspection

The supplied CSV has 2,510 rows and 13 columns. The report found 10 exact duplicate rows, 10 repeated `flight_id` values, 25 missing altitude values, 25 missing speed values, 12 missing latitude values, and 280 records where origin and destination are identical. No latitude or longitude values exceeded conventional numeric bounds. See `DATA_QUALITY_REPORT.md`.

## Additional checks

- `python -m compileall -q src scripts tests`: passed.
- FastAPI `TestClient`: `/` returned HTTP 200; `/query` returned HTTP 200 for a supported SQL question.
- Editable package installation was validated with `python -m pip install -e . --no-build-isolation --no-deps`. Standard isolated build dependency installation could not access the package index in this environment because outbound network access was unavailable.

## Not run / not verified

- Ruff linting: executable not installed in the environment.
- Ollama/Qwen model integration: not run; Ollama was not available, and no model inference was verified.
- Gemini Argon integration: not run; this project does not require a Gemini-specific API to function.
- Docker build or deployment: not run; Docker was not available.
- Load, concurrency, penetration, dependency vulnerability, and formal enterprise compliance tests: not run.
- Neural embeddings, learned reranking, semantic entailment, and robust contradiction detection: not implemented in this baseline.

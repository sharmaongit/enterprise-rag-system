# Testing strategy

Run `python -m pytest -q` for unit, integration, and basic security tests. Run `python scripts/run_evaluation.py` for a deterministic smoke evaluation against the supplied dataset. Run `python scripts/inspect_data.py` for a schema and quality report.

Tests currently cover CSV schema/row count, routing, retrieval grading, bounded corrective retries, read-only SQL protections, empty-evidence abstention, a structured cancellation-rate query, and prompt-injection wording in the optional model prompt. This is not exhaustive enterprise validation. Add labelled semantic retrieval data, claim-level grounding benchmarks, authentication endpoint tests, load tests, and real provider integration tests before production.

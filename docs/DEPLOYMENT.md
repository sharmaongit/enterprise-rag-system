# Deployment

## Local

1. Use Python 3.11 or newer.
2. Create and activate a virtual environment.
3. Install with `python -m pip install -e '.[dev]'`.
4. Run `python scripts/inspect_data.py` and `python scripts/ingest_data.py`.
5. Run tests with `python -m pytest -q`.
6. Start with `uvicorn enterprise_rag.main:app --host 127.0.0.1 --port 8000`.

## Optional Ollama

Install and start Ollama separately, pull a model that is actually available in your installation, set `ENABLE_OLLAMA=true` and `OLLAMA_MODEL` to its exact installed identifier, then restart the API. The example model identifier is configurable and must be verified with your Ollama installation. If the provider is unavailable, semantic generation can fail; the API will return a safe error rather than silently claiming success.

## Production gate

Do not deploy publicly until TLS, identity integration, RBAC, rate limiting, secret management, monitoring, backups, dependency scanning, load tests, threat-model review, and dataset-specific access controls are complete. Container packaging is not included in this initial verified build; deployment should be added and tested against the target environment rather than assumed to work.

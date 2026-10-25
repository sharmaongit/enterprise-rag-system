# API reference

- `GET /`: minimal query UI.
- `GET /health`: service and database row-count status.
- `GET /ready`: readiness check; returns HTTP 503 if database is not initialized.
- `GET /dataset/summary`: basic dataset metadata. Protected when `REQUIRE_API_KEY=true`.
- `POST /query`: accepts `{"question":"..."}` and returns answer, route, citations, correction attempts, Self-RAG-style diagnostics, and abstention status. Protected when `REQUIRE_API_KEY=true`.

When authentication is enabled, send `X-API-Key` with the configured key. Query body is validated to 3–2000 characters. Error messages intentionally do not reveal internal exception details. Interactive OpenAPI docs are available at `/docs` in local development; consider disabling or protecting them in production.

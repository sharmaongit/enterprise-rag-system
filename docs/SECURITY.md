# Security and deployment checklist

- The API key check is optional for local development. Set `REQUIRE_API_KEY=true` and a strong unique `API_KEY` before shared use. Prefer an enterprise identity provider, short-lived tokens, and role-based authorization for real deployments.
- Do not expose the local development server, SQLite file, or Ollama port directly to the public internet.
- Use HTTPS and a reverse proxy in deployments; configure CORS narrowly if a separate frontend is deployed.
- Keep secrets in a secret manager; `.env` is ignored by Git but is not itself a secret manager.
- The SQLite query helper only allows read-only SELECT operations and has a bounded result count. Do not add unrestricted natural-language-to-SQL execution without a parser and policy layer.
- Retrieved text is untrusted. The optional model prompt says not to follow instructions embedded in evidence, but prompt wording alone is not a security boundary.
- Do not let the model execute shell commands or arbitrary tools.
- Add request-rate limits, payload limits, user-level audit logging, monitoring, backups, retention controls, and dependency scanning before production.
- The sample service has no enterprise SSO, granular RBAC, tenant isolation, formal compliance assessment, or external security certification.
- Keep synthetic and real datasets clearly separated. Check access rights, privacy classification, retention, and data residency before ingestion.

## Threat model summary

Assets: source data, query results, API credentials, model prompts, logs, and index content. Trust boundaries: browser/API, API/database, API/model provider, and ingestion/file uploads. Threats include unauthorized queries, prompt injection, data exfiltration, denial of service, malformed input, dependency compromise, and misleading generated answers. Existing controls are a minimal baseline; residual risks remain significant until the deployment-specific controls above are implemented and tested.

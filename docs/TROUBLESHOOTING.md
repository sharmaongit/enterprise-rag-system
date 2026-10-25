# Troubleshooting

- **Dataset not found:** run commands from the repository root and check `DATA_PATH`.
- **Missing package:** activate the virtual environment and run `python -m pip install -e '.[dev]'`.
- **Database not initialized:** run `python scripts/ingest_data.py`; the API also initializes it on startup.
- **Ollama request failed:** confirm Ollama is running, the base URL is reachable, and the exact configured model is installed. Keep `ENABLE_OLLAMA=false` to use the local non-LLM baseline.
- **A question gets a weak answer:** inspect its route and citations. The rule-based router supports only a bounded set of structured intents; rephrase or add a reviewed query template.
- **Tests fail after changing data:** update the expected schema or test fixture only after verifying the source data change is intended.
- **Port already in use:** run Uvicorn with another port, such as `--port 8001`.

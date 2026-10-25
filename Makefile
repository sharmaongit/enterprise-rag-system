.PHONY: install test run lint ingest evaluate
install:
	python -m pip install -e '.[dev]'
test:
	python -m pytest -q
run:
	uvicorn enterprise_rag.main:app --reload
lint:
	ruff check src tests scripts
ingest:
	python scripts/ingest_data.py
evaluate:
	python scripts/run_evaluation.py

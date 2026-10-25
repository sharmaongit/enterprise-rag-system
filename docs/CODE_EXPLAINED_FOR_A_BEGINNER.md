# The whole project explained for a beginner

This guide describes the actual starter implementation. It does not claim that the system is perfect or that the lightweight CRAG/Self-RAG checks are the original research systems.

## 1. The big idea

Imagine a librarian helping you answer questions about a spreadsheet of flights. There are two ways to find answers:

- **SQL** is like asking a calculator to count, group, or average exact values. It is the right tool for “How many flights are cancelled?”
- **Retrieval** is like asking the librarian to find records whose words resemble your question. It can help find a particular flight or supporting context, but similar words do not prove a statement is true.

**RAG** means retrieval-augmented generation: find useful source material first, then use it to formulate an answer. **CRAG-style correction** checks whether retrieval seems relevant and retries when it looks weak. **Self-RAG-style reflection** checks whether an answer seems related to and supported by the evidence. In this project, the last two checks are deliberately simple word-overlap heuristics. They are not magic truth detectors.

## 2. What happens when the program starts

`src/enterprise_rag/main.py` creates the FastAPI application. FastAPI is a Python library that exposes functions as HTTP endpoints. During application startup, its `lifespan` function checks whether the SQLite database exists. If not, it reads the CSV and imports it. It then creates a `RAGService`, which builds an in-memory text search index.

A browser can open `/` to see a simple form, `/docs` to see API documentation, and `/health` to check whether the database is ready.

## 3. Configuration: `config.py`

Configuration is a collection of settings such as file paths, model names, timeouts, and retry limits. `os.getenv("NAME", "default")` reads an environment variable; if it is absent, the default is used. The `_bool` helper converts values such as `true` or `1` into Python `True`.

The `Settings` dataclass groups these settings together. A **dataclass** is a convenient way to create a class whose main purpose is holding values. The retry settings are clamped to safe ranges so a typo cannot create an unlimited retry loop.

## 4. Dataset loading: `data/flight_data.py`

`load_flights(path)` checks that the file exists, reads it with pandas, and verifies that required column names are present. A **DataFrame** is like a spreadsheet in Python: rows are records and columns are fields. If a file is missing or malformed, the function raises an exception instead of pretending it worked.

`quality_report(frame)` calculates basic checks: row and column counts, missing values, duplicate records, repeated flight IDs, statuses, airline labels, same-origin/destination rows, and coordinates outside expected latitude/longitude bounds. A flagged row is not automatically wrong: synthetic data may contain unusual values by design.

## 5. Database: `database/store.py`

SQLite is a small database stored in a file. `ingest_frame` copies the CSV rows into a table named `flights` and adds indexes to commonly filtered columns. An index is similar to a book's index: it can make certain lookups faster.

`query_readonly` opens the database in read-only mode and rejects SQL that is not a simple `SELECT`, along with common prohibited keywords. The analytical queries in this project are fixed templates. The application does **not** ask the model to invent arbitrary SQL. This is safer and more predictable.

The check is a baseline, not a complete SQL parser. Keep the database read-only and do not expose arbitrary SQL to users.

## 6. Ingestion: `ingestion/pipeline.py`

`flight_documents(frame)` walks through the DataFrame one row at a time. For each row, it creates a readable sentence like “Flight FL10000 operated by ...” and keeps the original values in a metadata dictionary. `source_id` holds the flight ID so a search result can be traced back to the record.

The `pd.isna` check handles missing values. A missing value is converted to `None` in metadata rather than turning into confusing text like `nan`.

## 7. Search index: `embeddings/tfidf.py`

TF-IDF means “term frequency–inverse document frequency.” In simple terms, it gives weight to words that help distinguish one record from another. `TfidfVectorizer` turns text into numerical vectors. `cosine_similarity` compares a question vector with document vectors. The result is a similarity score, not a probability that the document answers the question.

This is an offline baseline and does not download a neural embedding model. It can miss synonyms and meaning. A production system should compare it with suitable embedding models using labelled questions and relevance judgments.

## 8. Routing: `routing/router.py`

`route_query(question)` uses transparent word patterns. Terms like “how many,” “average,” “highest,” and “rate” are treated as signs of a numerical question, so the application tries structured SQL. A flight ID such as `FL10002` is also routed to the database. Other questions go to semantic retrieval.

This is intentionally simple. It does not understand every possible phrasing. When the router does not recognize an analytical intent, a more advanced version should either ask a clarification question or use a validated structured-query planner.

## 9. Exact answers: `generation/answer.py`

`sql_answer` contains a small set of fixed analytical templates. For a cancellation rate, the SQL groups records by airline, counts cancelled records, divides by total records, and sorts from the highest percentage downward. The formula is:

`cancellation rate (%) = cancelled records / all records for that airline × 100`

The denominator matters: the airline with the most cancellations is not necessarily the airline with the highest cancellation rate. The code includes the number cancelled and the total number of records to make the percentage easier to interpret.

Other templates count all records, average recorded duration, summarize statuses, or retrieve one flight by ID. Unknown questions are not automatically translated into SQL.

## 10. CRAG-style correction: `crag/corrective.py`

The `tokens` function extracts lowercase words and removes a small list of common words. `grade_retrieval` compares the words in the question with the words in retrieved text. It labels the evidence adequate, uncertain, or inadequate according to thresholds.

`CorrectiveRetriever.run` attempts retrieval. If evidence is weak, it retries with a rewritten query. `max_retries` puts a hard limit on the number of attempts. The returned object includes the evidence, grade, attempt count, whether correction was used, and the query used.

This is a CRAG-inspired mechanism, not the original CRAG model. Word overlap can be fooled by text that repeats the question but does not answer it. Thresholds must be tested on real labelled examples.

## 11. Self-RAG-style reflection: `self_rag/reflect.py`

`evaluate_answer` checks whether evidence exists, whether answer words overlap evidence words, and whether question words overlap answer words. It returns a dictionary of diagnostics such as `claim_support`, `answer_relevance`, and `abstention_recommended`.

These scores are heuristic signals, not calibrated probabilities. The current implementation does not reliably detect contradictions and does not perform deep semantic entailment. It must not be treated as a guarantee of truth.

## 12. Optional model: `generation/provider.py`

`OllamaProvider` sends an HTTP request to a local Ollama server using Python's standard-library HTTP utilities. It sends a prompt, model name, and temperature setting, then reads the response text. If the server is down, times out, or returns malformed data, the provider raises a controlled `ModelProviderError`.

Ollama must be installed and running separately. The configured model identifier must match a model actually available on that machine. The model is optional and disabled by default. The model prompt tells it to treat retrieved text as untrusted, but a prompt is not a substitute for access controls.

## 13. Main orchestration: `service.py`

`RAGService.answer` connects the steps:

1. Classify the question.
2. If the question appears analytical, try one of the supported SQL templates.
3. If a template answers it, return the calculated result and its query citation.
4. Otherwise, retrieve relevant records through the corrective retrieval loop.
5. If evidence remains weak, return an abstention message.
6. If evidence is usable, create an answer, optionally with Ollama.
7. Run the Self-RAG-style reflection check.
8. If the check says evidence is insufficient, abstain; otherwise return the answer and source records.

For a question like “Which airline has the highest cancellation rate?”, SQL calculates the rate directly from the dataset. The response includes the airline, cancellation percentage, cancelled count, total records, and a `SQL:airline_cancellation_rate` citation.

For a semantic question, the TF-IDF index finds similar flight records. CRAG-style logic can retry the search. The answer identifies a source record, but the application warns that lexical similarity alone does not prove the record fully answers the question.

## 14. API and security: `main.py` and `auth/security.py`

`POST /query` accepts a JSON object with a `question` field. Pydantic checks the request's type and length. The endpoint passes the question to `RAGService` and returns a structured response. Internal exceptions are not copied into client-facing error messages.

When `REQUIRE_API_KEY=true`, `require_auth` checks the `X-API-Key` header. `hmac.compare_digest` compares keys in a way designed to avoid timing leaks. This is only a minimal shared-key mechanism; enterprise systems should integrate their identity provider and enforce roles and permissions.

## 15. Citations and provenance

Each semantic evidence item includes a source ID, source type, text, score, and metadata. Structured SQL results use stable labels such as `SQL:flight_count`. This makes it possible to inspect where an answer came from. Citation checking in `citations/verify.py` is a small helper and is not currently wired as a strict final-answer gate for every response; that is a known improvement item.

## 16. Tests and scripts

- `scripts/inspect_data.py`: prints data quality and numeric summaries.
- `scripts/ingest_data.py`: loads the CSV into SQLite.
- `scripts/verify_installation.py`: checks Python packages and data loading.
- `scripts/run_evaluation.py`: runs a few deterministic end-to-end smoke cases.
- `tests/unit/`: tests individual functions and safety checks.
- `tests/integration/`: tests a full structured-answer path.
- `tests/security/`: contains a basic prompt-injection prompt construction check.

A passing test means that specific assertion passed in that environment. It does not prove the entire application is flawless or enterprise-ready. Expand the tests whenever a bug is found.

## 17. Run it

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -e '.[dev]'
python scripts/inspect_data.py
python scripts/ingest_data.py
python -m pytest -q
python scripts/run_evaluation.py
uvicorn enterprise_rag.main:app --reload
```

Visit `http://127.0.0.1:8000`. Do not expose the development server to the internet.

## 18. Glossary

- **API:** a defined way for programs to communicate.
- **CSV:** a text file where commas separate values.
- **Database:** an organized place to store and query records.
- **SQL:** a language for asking databases questions.
- **RAG:** retrieve source material, then generate an answer using it.
- **CRAG:** a corrective approach that evaluates retrieval and attempts recovery.
- **Self-RAG:** a reflective approach that checks retrieval decisions and answer support.
- **Embedding/vector:** a numerical representation of text used for similarity comparisons.
- **TF-IDF:** a word-weighting method for text retrieval.
- **Citation/provenance:** information that points back to the evidence behind a claim.
- **Abstention:** refusing to give a confident answer when evidence is insufficient.
- **Regression test:** a test that helps ensure a previously fixed bug does not return.
- **RBAC:** role-based access control; users receive permissions based on assigned roles.
- **Prompt injection:** text attempting to manipulate an AI system into ignoring its intended rules.

## 19. What is not yet complete for enterprise production

This repository is a useful functioning foundation, not a finished compliance-grade service. It still needs stronger semantic evaluators, a larger labelled benchmark, strict citation gating, authentication tests, role-based permissions, rate limiting, load tests, real-provider tests, security scanning, deployment-specific monitoring, backups, and review by the organization responsible for the data.

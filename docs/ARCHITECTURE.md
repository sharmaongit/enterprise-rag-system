# Architecture

```text
User / browser
   | HTTP + validation
   v
FastAPI API ---- optional API-key guard
   |
   v
RAGService -> rule-based query router
   |                         |
   | structured / hybrid     | semantic / fallback
   v                         v
Read-only SQLite SQL      TF-IDF retrieval index
   |                         |
   | exact computed result   v
   |                    CRAG-style grade
   |                    -> bounded rewrite/retry
   |                         |
   +----------+--------------+
              v
       Answer construction
       (optional Ollama model for semantic answers)
              |
              v
       Self-RAG-style reflection
       + citation provenance
              |
              v
       answer / abstention
```

## Data flow

1. The original CSV is validated by `data.flight_data` and never edited.
2. `database.store.ingest_frame` copies rows into SQLite and creates basic indexes.
3. `ingestion.pipeline` converts each row into a human-readable search document while preserving `flight_id` and original metadata.
4. `embeddings.tfidf.TfidfIndex` builds an in-memory TF-IDF index at application startup.
5. `routing.router` chooses a bounded structured route or semantic route using transparent rules.
6. Supported analytical intents run deterministic SQL. SQL results are cited as `SQL:<query-name>`.
7. Semantic requests use `CorrectiveRetriever`, which grades lexical overlap and retries with a rewritten query up to the configured limit.
8. Answers are checked with `evaluate_answer`. Weak evidence can cause abstention.
9. The API returns the answer, route, citations, attempt count, and evaluation metadata.

## Sequence diagram

```text
Client -> API: question
API -> Router: classify
Router -> SQL: supported analytic intent?
SQL --> API: computed result + query provenance
API -> Self-RAG check: evaluate result
Self-RAG check --> API: validated structured result
API --> Client: answer + citation

Client -> API: semantic question
API -> Retriever: retrieve candidates
Retriever -> CRAG: grade relevance
CRAG -> Retriever: rewrite/retrieve (bounded, if weak)
CRAG --> Generator: selected evidence
Generator -> Self-RAG: draft answer + evidence
Self-RAG --> Generator: supported / revise / abstain
API --> Client: answer + source IDs or abstention
```

## Design limitations

The default retrieval evaluator is lexical rather than semantic, and contradiction detection is not implemented beyond a placeholder boolean. The optional Ollama adapter is a local inference integration, not a guarantee of factuality. Replace heuristic evaluators with calibrated models and a labelled benchmark before enterprise-critical use.

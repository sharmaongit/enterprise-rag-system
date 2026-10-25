"""Small deterministic smoke evaluation; not a substitute for a large labelled benchmark."""
from enterprise_rag.config import settings
from enterprise_rag.database.store import table_ready, ingest_frame
from enterprise_rag.data.flight_data import load_flights
from enterprise_rag.service import RAGService

CASES = [
    ("How many flights are in the dataset?", "structured_sql"),
    ("What is the average flight duration?", "structured_sql"),
    ("Which airline has the highest cancellation rate?", "structured_sql"),
    ("Tell me about flight FL10002", "structured_sql"),
]
if __name__ == "__main__":
    if not table_ready(settings.sqlite_path): ingest_frame(load_flights(settings.data_path), settings.sqlite_path)
    service = RAGService(); passed = 0
    for question, expected_route in CASES:
        result = service.answer(question)
        ok = result["route"] == expected_route and bool(result["answer"])
        print(("PASS" if ok else "FAIL"), question, "->", result["route"], result["answer"])
        passed += int(ok)
    print(f"Smoke evaluation: {passed}/{len(CASES)} passed")
    if passed != len(CASES): raise SystemExit(1)

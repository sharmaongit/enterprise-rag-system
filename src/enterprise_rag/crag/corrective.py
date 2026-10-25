"""CRAG-inspired retrieval evaluation and bounded recovery. Heuristics are explicit, not an LLM judge."""
import re
from collections import Counter

STOP = {"what", "which", "when", "where", "does", "that", "with", "from", "have", "this", "there", "flight", "flights", "data", "dataset", "the", "and", "for", "are", "was", "were", "show", "tell", "about", "is", "on", "in", "at", "of", "to", "it", "be", "as", "by", "or", "an", "a", "me", "my", "you", "can", "could", "would", "should", "do", "did", "not", "please", "give", "explain", "describe", "record", "records"}
def tokens(text: str) -> set[str]:
    return {t for t in re.findall(r"[a-z0-9]+", text.lower()) if len(t) > 1 and t not in STOP}

def grade_retrieval(question: str, evidence: list[dict]) -> dict:
    qt = tokens(question)
    if not evidence or not qt: return {"grade": "inadequate", "score": 0.0, "reason": "No usable evidence or no informative query terms"}
    overlap = [len(qt & tokens(item.get("text", ""))) / max(1, len(qt)) for item in evidence]
    score = max(overlap, default=0.0)
    grade = "adequate" if score >= 0.20 else "uncertain" if score >= 0.08 else "inadequate"
    return {"grade": grade, "score": round(score, 4), "reason": "Lexical query-evidence overlap heuristic; validate against labelled evaluation data"}

def rewrite_query(question: str, attempt: int) -> str:
    q = question.strip().rstrip("?.! ")
    variants = [f"flight record airline airport status {q}", f"flight_id airline origin destination date status {q}"]
    return variants[min(max(attempt - 1, 0), len(variants) - 1)]

class CorrectiveRetriever:
    def __init__(self, retriever, max_retries=2): self.retriever, self.max_retries = retriever, max_retries
    def run(self, question: str) -> dict:
        current = question
        evidence, grade, attempts = [], {"grade":"inadequate","score":0.0}, 0
        for attempt in range(self.max_retries + 1):
            attempts += 1
            evidence = self.retriever.retrieve(current, top_k=min(30, 8 + attempt * 4))
            grade = grade_retrieval(question, evidence)
            if grade["grade"] == "adequate": break
            if attempt < self.max_retries: current = rewrite_query(question, attempt + 1)
        return {"evidence": evidence, "grade": grade, "attempts": attempts, "correction_used": attempts > 1, "query_used": current}

"""Self-RAG-inspired post-generation checks using explicit, testable heuristics."""
from enterprise_rag.crag.corrective import tokens

def evaluate_answer(question: str, answer: str, evidence: list[dict]) -> dict:
    q = tokens(question)
    a = tokens(answer)
    evidence_text = " ".join(item.get("text", "") for item in evidence)
    supported = tokens(evidence_text)
    claim_tokens = {t for t in a if len(t) > 2}
    support_ratio = len(claim_tokens & supported) / max(1, len(claim_tokens))
    relevance = len(q & a) / max(1, len(q))
    has_evidence = bool(evidence)
    return {
        "retrieval_needed": bool(q - {"hello", "hi", "thanks"}),
        "evidence_relevance": bool(has_evidence and relevance > 0),
        "claim_support": round(support_ratio, 4),
        "answer_relevance": round(relevance, 4),
        "contradiction_detected": False,
        "needs_revision": (not has_evidence) or support_ratio < 0.15,
        "abstention_recommended": not has_evidence or support_ratio < 0.08,
        "method": "lexical heuristic; not a semantic entailment model"
    }

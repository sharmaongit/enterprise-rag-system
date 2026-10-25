"""Coordinates routing, SQL, CRAG retrieval, generation, and Self-RAG-style reflection."""
from enterprise_rag.config import settings
from enterprise_rag.database.store import table_ready
from enterprise_rag.routing.router import route_query
from enterprise_rag.retrieval.engine import RetrievalEngine
from enterprise_rag.crag.corrective import CorrectiveRetriever
from enterprise_rag.self_rag.reflect import evaluate_answer
from enterprise_rag.generation.answer import sql_answer, compose_semantic_answer
from enterprise_rag.generation.provider import OllamaProvider
from enterprise_rag.citations.verify import verify_citations

class RAGService:
    def __init__(self):
        self.retriever = RetrievalEngine(settings.data_path, settings.retrieval_top_k)
        self.corrective = CorrectiveRetriever(self.retriever, settings.crag_max_retries)
        self.provider = OllamaProvider(settings.ollama_base_url, settings.ollama_model, settings.ollama_timeout_seconds) if settings.enable_ollama else None
    def answer(self, question: str) -> dict:
        route = route_query(question)
        if route in {"structured", "hybrid"} and table_ready(settings.sqlite_path):
            result = sql_answer(settings.sqlite_path, question)
            if result is not None:
                answer, citations = result
                reflection = evaluate_answer(question, answer, citations)
                # SQL outputs are deterministic and have direct database provenance; heuristic support scores
                # are advisory and must not override verified query results.
                return {"question":question,"answer":answer,"route":"structured_sql","citations":citations,"retrieval_attempts":1,"correction_used":False,"self_rag":{**reflection,"mode":"structured-result validation","needs_revision":False,"abstention_recommended":False},"abstained":False}
        correction = self.corrective.run(question)
        evidence = correction["evidence"]
        if correction["grade"]["grade"] != "adequate":
            answer = "I could not find sufficiently relevant evidence in the supplied dataset after bounded retrieval attempts. Please rephrase the question or provide another source."
            reflection = {"retrieval_needed":True,"evidence_relevance":False,"claim_support":0.0,"answer_relevance":0.0,"contradiction_detected":False,"needs_revision":False,"abstention_recommended":True,"method":"CRAG retrieval grade","mode":"abstain"}
            return {"question":question,"answer":answer,"route":route,"citations":[],"retrieval_attempts":correction["attempts"],"correction_used":correction["correction_used"],"self_rag":reflection,"abstained":True}
        answer = compose_semantic_answer(question, evidence, self.provider)
        citation_check = verify_citations(answer, evidence)
        if not citation_check["valid"]:
            answer = "The generated answer included a source reference that could not be verified, so I am withholding the answer. Please retry or inspect the retrieved evidence."
            return {"question":question,"answer":answer,"route":route,"citations":[],"retrieval_attempts":correction["attempts"],"correction_used":correction["correction_used"],"self_rag":{"mode":"citation verification failure","needs_revision":True,"abstention_recommended":True,"citation_check":citation_check},"abstained":True}
        if not citation_check["has_source_reference"]:
            answer += "\nSources: " + ", ".join(f"[{e['source_id']}]" for e in evidence[:3])
        reflection = evaluate_answer(question, answer, evidence)
        if reflection["abstention_recommended"]:
            answer = "I found possible matches, but could not verify enough evidence to answer reliably. Please narrow or rephrase the question."
            return {"question":question,"answer":answer,"route":route,"citations":[],"retrieval_attempts":correction["attempts"],"correction_used":correction["correction_used"],"self_rag":{**reflection,"mode":"abstain"},"abstained":True}
        citations = [{"source_id":e["source_id"],"source_type":e["source_type"],"text":e["text"],"score":e.get("score",0.0),"metadata":e.get("metadata",{})} for e in evidence[:5]]
        return {"question":question,"answer":answer,"route":route,"citations":citations,"retrieval_attempts":correction["attempts"],"correction_used":correction["correction_used"],"self_rag":{**reflection,"mode":"heuristic reflection","citation_check":citation_check},"abstained":False}

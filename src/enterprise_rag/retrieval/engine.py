from enterprise_rag.embeddings.tfidf import TfidfIndex
from enterprise_rag.ingestion.pipeline import flight_documents
from enterprise_rag.data.flight_data import load_flights

class RetrievalEngine:
    def __init__(self, data_path, top_k=8):
        self.data_path, self.top_k = data_path, top_k
        self.index = TfidfIndex()
        self.rebuild()
    def rebuild(self):
        frame = load_flights(self.data_path)
        self.index.build(flight_documents(frame))
    def retrieve(self, question: str, top_k: int | None = None) -> list[dict]:
        return self.index.search(question, top_k or self.top_k)

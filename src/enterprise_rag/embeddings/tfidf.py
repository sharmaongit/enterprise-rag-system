"""Offline semantic-ish baseline using TF-IDF. Replaceable with neural embeddings later."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

class TfidfIndex:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), strip_accents="unicode", sublinear_tf=True)
        self.documents: list[dict] = []
        self.matrix = None
    def build(self, documents: list[dict]) -> None:
        self.documents = documents
        self.matrix = self.vectorizer.fit_transform([d["text"] for d in documents]) if documents else None
    def search(self, query: str, top_k: int = 8) -> list[dict]:
        if self.matrix is None or not self.documents: return []
        vector = self.vectorizer.transform([query])
        scores = cosine_similarity(vector, self.matrix).ravel()
        indexes = sorted(range(len(scores)), key=lambda i: float(scores[i]), reverse=True)[:top_k]
        return [{**self.documents[i], "score": float(scores[i])} for i in indexes if scores[i] > 0]

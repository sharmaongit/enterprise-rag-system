"""Transparent query router; conservative rules avoid model-generated SQL."""
import re

ANALYTIC_TERMS = ("how many", "count", "average", "avg", "highest", "lowest", "most", "least", "rate", "percentage", "total", "compare", "sum", "maximum", "minimum", "number of", "distribution", "breakdown")
FLIGHT_ID = re.compile(r"\bFL\d{4,}\b", re.I)

def route_query(question: str) -> str:
    q = question.lower()
    if any(re.search(r"\b" + re.escape(term) + r"\b", q) for term in ANALYTIC_TERMS): return "structured"
    if FLIGHT_ID.search(question): return "structured"
    if any(term in q for term in ("why", "explain", "what does the dataset say", "describe")) and any(term in q for term in ("rate", "average", "most", "cancel", "delay")):
        return "hybrid"
    return "semantic"

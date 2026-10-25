# CRAG-style correction

Corrective RAG asks whether the retrieved evidence is useful enough and attempts recovery if it is not. This implementation uses token overlap as a transparent baseline: it compares informative words in the question with words in retrieved record text. If the score is too low, it retries with a query expanded by flight-related vocabulary. Retries are bounded by `CRAG_MAX_RETRIES`.

This is **CRAG-inspired**, not a reproduction of the original CRAG research model. Token overlap can miss synonyms and can score misleading evidence highly. Before production use, label queries and relevant documents, measure precision/recall, calibrate thresholds, and evaluate an appropriate learned relevance grader. An inadequate final grade leads to abstention instead of an invented answer.

"""Small pure functions for labelled retrieval evaluation."""
def precision_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if k <= 0: raise ValueError("k must be positive")
    selected = retrieved_ids[:k]
    if not selected: return 0.0
    return sum(item in relevant_ids for item in selected) / len(selected)

def recall_at_k(retrieved_ids: list[str], relevant_ids: set[str], k: int) -> float:
    if k <= 0: raise ValueError("k must be positive")
    if not relevant_ids: return 0.0
    return len(set(retrieved_ids[:k]) & relevant_ids) / len(relevant_ids)

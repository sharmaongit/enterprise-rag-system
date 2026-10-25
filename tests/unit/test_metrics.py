import pytest
from enterprise_rag.evaluation.metrics import precision_at_k, recall_at_k

def test_retrieval_metrics():
    ids = ["a", "x", "b"]
    relevant = {"a", "b"}
    assert precision_at_k(ids, relevant, 2) == 0.5
    assert recall_at_k(ids, relevant, 2) == 0.5
    with pytest.raises(ValueError): precision_at_k(ids, relevant, 0)

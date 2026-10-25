from enterprise_rag.self_rag.reflect import evaluate_answer

def test_reflection_marks_empty_evidence_for_abstention():
    result = evaluate_answer("What is the flight status?", "It is on-time", [])
    assert result["abstention_recommended"] is True
    assert result["needs_revision"] is True

def test_citation_verifier_rejects_unknown_source():
    from enterprise_rag.citations.verify import verify_citations
    result = verify_citations("Unsupported claim [NOT_A_REAL_SOURCE]", [{"source_id":"FL10000"}])
    assert result["valid"] is False
    assert result["invalid_ids"] == ["NOT_A_REAL_SOURCE"]

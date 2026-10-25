from enterprise_rag.crag.corrective import grade_retrieval, CorrectiveRetriever

def test_grader_rejects_empty_evidence():
    assert grade_retrieval("Which airline is cancelled?", [])["grade"] == "inadequate"

def test_grader_accepts_relevant_evidence():
    evidence = [{"text":"Airline Emirates flight status Cancelled airport route", "source_id":"FL1"}]
    assert grade_retrieval("Emirates airline flight status cancelled", evidence)["grade"] == "adequate"

class FakeRetriever:
    def __init__(self): self.calls = 0
    def retrieve(self, question, top_k=None):
        self.calls += 1
        return [] if self.calls == 1 else [{"text":"Emirates airline cancelled flight status", "source_id":"FL1"}]

def test_corrective_retriever_is_bounded_and_retries():
    fake = FakeRetriever()
    result = CorrectiveRetriever(fake, max_retries=2).run("Emirates airline cancelled flight status")
    assert result["attempts"] == 2
    assert result["correction_used"] is True
    assert result["evidence"]

def test_grader_does_not_accept_unrelated_evidence_for_weather_question():
    evidence = [{"text":"Flight FL10000 operated by Emirates. Status On-time.", "source_id":"FL10000"}]
    assert grade_retrieval("What is the weather on Mars?", evidence)["grade"] == "inadequate"

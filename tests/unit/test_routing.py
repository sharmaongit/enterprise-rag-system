from enterprise_rag.routing.router import route_query

def test_routes_analytics_to_structured():
    assert route_query("Which airline has the highest cancellation rate?") == "structured"
    assert route_query("How many flights are in the dataset?") == "structured"

def test_routes_general_question_to_semantic():
    assert route_query("Tell me about flight records for Emirates") == "semantic"

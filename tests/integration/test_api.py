from fastapi.testclient import TestClient
from enterprise_rag.main import app

def test_health_and_query_end_to_end():
    with TestClient(app) as client:
        health = client.get("/health")
        assert health.status_code == 200
        assert health.json()["database_ready"] is True
        response = client.post("/query", json={"question":"How many flights are in the dataset?"})
        assert response.status_code == 200
        body = response.json()
        assert body["route"] == "structured_sql"
        assert "2510" in body["answer"]
        assert body["citations"]

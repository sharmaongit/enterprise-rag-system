from dataclasses import replace
from enterprise_rag.config import settings
from enterprise_rag.database.store import ingest_frame
from enterprise_rag.data.flight_data import load_flights
from enterprise_rag.service import RAGService

def test_structured_cancellation_rate(tmp_path, monkeypatch):
    import enterprise_rag.service as service_module
    import enterprise_rag.config as config_module
    # Replace the immutable settings object with a copy using a temporary database.
    test_settings = replace(settings, sqlite_path=tmp_path / "flights.sqlite3")
    monkeypatch.setattr(config_module, "settings", test_settings)
    monkeypatch.setattr(service_module, "settings", test_settings)
    ingest_frame(load_flights(settings.data_path), tmp_path / "flights.sqlite3")
    service = RAGService()
    result = service.answer("Which airline has the highest cancellation rate?")
    assert result["route"] == "structured_sql"
    assert result["citations"]
    assert "cancellation rate" in result["answer"].lower()
    import pandas as pd
    frame = load_flights(settings.data_path)
    grouped = frame.assign(cancelled=frame.status.str.lower().eq("cancelled")).groupby("airline").agg(total=("flight_id", "size"), cancelled=("cancelled", "sum"))
    grouped["rate"] = grouped.cancelled / grouped.total * 100
    expected_airline = grouped.sort_values(["rate"], ascending=False).index[0]
    expected_rate = round(float(grouped.loc[expected_airline, "rate"]), 2)
    assert expected_airline in result["answer"]
    assert f"{expected_rate}%" in result["answer"]

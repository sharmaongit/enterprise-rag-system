from enterprise_rag.data.flight_data import load_flights, quality_report
from pathlib import Path

def test_dataset_schema_and_rows():
    path = Path(__file__).parents[2] / "data" / "synthetic_flightradar24.csv"
    frame = load_flights(path)
    assert len(frame) == 2510
    assert len(frame.columns) == 13
    assert "flight_id" in frame.columns
    assert quality_report(frame)["rows"] == 2510

import pandas as pd
import pytest
from enterprise_rag.database.store import ingest_frame, query_readonly

def test_readonly_sql_and_parameters(tmp_path):
    path = tmp_path / "test.sqlite3"
    ingest_frame(pd.DataFrame([{"flight_id":"FL10000","airline":"A","origin_airport":"AAA","destination_airport":"BBB","departure_time":"2025-01-01","arrival_time":"2025-01-01","flight_duration":60,"altitude":30000,"speed":500,"latitude":10,"longitude":20,"status":"On-time","date":"2025-01-01"}]), path)
    assert query_readonly(path, "SELECT flight_id FROM flights WHERE flight_id = ?", ("FL10000",))[0]["flight_id"] == "FL10000"
    with pytest.raises(ValueError): query_readonly(path, "DELETE FROM flights")
    with pytest.raises(ValueError): query_readonly(path, "SELECT * FROM flights; DROP TABLE flights")

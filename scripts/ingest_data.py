from enterprise_rag.config import settings
from enterprise_rag.data.flight_data import load_flights
from enterprise_rag.database.store import ingest_frame

if __name__ == "__main__":
    frame = load_flights(settings.data_path)
    count = ingest_frame(frame, settings.sqlite_path)
    print(f"Ingested {count} rows into {settings.sqlite_path}")

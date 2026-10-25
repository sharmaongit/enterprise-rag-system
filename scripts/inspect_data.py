import json
from enterprise_rag.config import settings
from enterprise_rag.data.flight_data import load_flights, quality_report

if __name__ == "__main__":
    frame = load_flights(settings.data_path)
    print(json.dumps(quality_report(frame), indent=2))
    print("\nNumeric summary:\n", frame.select_dtypes(include="number").describe().to_string())

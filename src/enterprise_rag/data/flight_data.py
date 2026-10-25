"""Load and validate the supplied CSV without modifying its source values."""
from pathlib import Path
import pandas as pd
from enterprise_rag.exceptions import DataValidationError

REQUIRED_COLUMNS = ["flight_id", "airline", "origin_airport", "destination_airport", "departure_time", "arrival_time", "flight_duration", "altitude", "speed", "latitude", "longitude", "status", "date"]

def load_flights(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Dataset not found: {path}")
    try:
        frame = pd.read_csv(path)
    except Exception as exc:
        raise DataValidationError(f"Could not parse CSV: {exc}") from exc
    missing = sorted(set(REQUIRED_COLUMNS) - set(frame.columns))
    if missing:
        raise DataValidationError(f"Dataset is missing required columns: {missing}")
    if frame.empty:
        raise DataValidationError("Dataset contains no records")
    return frame

def quality_report(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)), "columns": int(len(frame.columns)),
        "column_names": list(frame.columns),
        "null_counts": {str(k): int(v) for k, v in frame.isna().sum().items()},
        "duplicate_rows": int(frame.duplicated().sum()),
        "duplicate_flight_ids": int(frame["flight_id"].duplicated().sum()),
        "unique_statuses": sorted(frame["status"].dropna().astype(str).unique().tolist()),
        "unique_airlines": sorted(frame["airline"].dropna().astype(str).unique().tolist()),
        "same_origin_destination": int((frame["origin_airport"] == frame["destination_airport"]).sum()),
        "invalid_latitude": int(((pd.to_numeric(frame["latitude"], errors="coerce") < -90) | (pd.to_numeric(frame["latitude"], errors="coerce") > 90)).sum()),
        "invalid_longitude": int(((pd.to_numeric(frame["longitude"], errors="coerce") < -180) | (pd.to_numeric(frame["longitude"], errors="coerce") > 180)).sum()),
    }

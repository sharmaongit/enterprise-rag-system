"""Build source-preserving text documents from structured flight rows."""
import pandas as pd

def flight_documents(frame: pd.DataFrame) -> list[dict]:
    docs = []
    for _, row in frame.iterrows():
        values = {str(k): (None if pd.isna(v) else v.item() if hasattr(v, "item") else v) for k, v in row.to_dict().items()}
        text = (f"Flight {values.get('flight_id')} operated by {values.get('airline')}, from "
                f"{values.get('origin_airport')} to {values.get('destination_airport')}. "
                f"Departure {values.get('departure_time')}; arrival {values.get('arrival_time')}; "
                f"duration {values.get('flight_duration')} minutes; status {values.get('status')}; "
                f"date {values.get('date')}; altitude {values.get('altitude')}; speed {values.get('speed')}; "
                f"position latitude {values.get('latitude')}, longitude {values.get('longitude')}.")
        docs.append({"source_id": str(values.get("flight_id")), "source_type": "flight_record", "text": text, "metadata": values})
    return docs

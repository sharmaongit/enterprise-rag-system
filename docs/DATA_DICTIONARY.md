# Data dictionary

Source file: `data/synthetic_flightradar24.csv` from the supplied ZIP. It is labelled synthetic and should not be interpreted as verified real-world flight telemetry.

| Column | Expected meaning | Handling |
|---|---|---|
| `flight_id` | Record identifier | Preserve as string; used for provenance. |
| `airline` | Airline label | Categorical text. |
| `origin_airport` | Origin airport code | Categorical text; codes are not independently validated. |
| `destination_airport` | Destination airport code | Categorical text; codes are not independently validated. |
| `departure_time` | Departure timestamp | Stored as source text; parse/validate before time arithmetic. |
| `arrival_time` | Arrival timestamp | Stored as source text; timezone semantics are not specified. |
| `flight_duration` | Duration in minutes (inferred from values/schema) | Numeric; compare to timestamps only after clarifying timezone and generation rules. |
| `altitude` | Altitude (unit not explicitly documented) | Numeric; do not assume feet without source confirmation. |
| `speed` | Speed (unit not explicitly documented) | Numeric; do not assume knots or km/h without source confirmation. |
| `latitude` | Position latitude | Expected range -90 to 90. |
| `longitude` | Position longitude | Expected range -180 to 180. |
| `status` | Flight status label | Categorical text such as On-time, Delayed, Cancelled. |
| `date` | Record date | Date string; validate format before date analysis. |

The application preserves original data and reports obvious quality indicators. Same-origin/destination records and unusual coordinate patterns are flagged for human review, not silently corrected. Units, timezone, and whether coordinates represent a snapshot or route location remain unverified.

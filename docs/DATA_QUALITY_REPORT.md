# Data quality report

Generated from the supplied `synthetic_flightradar24.csv` using pandas. Original data was not modified.

- Rows: **2510**
- Columns: **13**
- Exact duplicate rows: **10**
- Duplicate `flight_id` values: **10**
- Records with identical origin and destination: **280**

## Missing values

- `altitude`: 25 missing
- `speed`: 25 missing
- `latitude`: 12 missing

## Status distribution

| Status | Records |
|---|---:|
| On-time | 2027 |
| Delayed | 406 |
| Cancelled | 77 |

## Airline record counts

| Airline | Records | Cancelled | Cancellation rate |
|---|---:|---:|---:|
| Lufthansa | 319 | 14 | 4.39% |
| Qatar | 359 | 14 | 3.90% |
| Turkish | 373 | 11 | 2.95% |
| American | 345 | 10 | 2.90% |
| Emirates | 380 | 11 | 2.89% |
| British Airways | 369 | 10 | 2.71% |
| PIA | 365 | 7 | 1.92% |

## Interpretation notes

- The file is synthetic and does not establish live or historical real-world flight facts.
- 25 records have missing altitude; 25 have missing speed; 12 have missing latitude.
- There are 10 exact duplicate rows and 10 repeated flight IDs; investigate before treating IDs as unique keys.
- 280 records have the same origin and destination airport. This may be synthetic-data behavior; it was not corrected.
- Latitude and longitude have no values outside the conventional numeric bounds in this dataset, but this does not validate whether the positions are geographically plausible.
- Altitude and speed units, timestamp timezone, and the meaning of the coordinate snapshot are not documented in the source and must not be guessed.

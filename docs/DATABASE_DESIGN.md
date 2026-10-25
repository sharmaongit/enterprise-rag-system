# Database design

SQLite table `flights` mirrors the supplied CSV columns. Ingestion uses pandas `to_sql` to load the dataset, replacing the generated table on an explicit ingestion run. The application creates indexes for `airline`, `date`, and `status`.

Analytical SQL is currently selected from fixed, reviewed query templates. The public helper `query_readonly` opens the database in SQLite read-only mode, rejects non-SELECT statements and common prohibited keywords, and caps results at 500 rows. Do not expose arbitrary model-generated SQL as a production feature. If query generation is added, use a SQL parser, strict table/column allowlists, query time/resource limits, and isolated read-only credentials.

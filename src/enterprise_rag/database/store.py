"""SQLite persistence and tightly constrained, read-only analytical query helpers."""
import sqlite3
from pathlib import Path
import pandas as pd

TABLE = "flights"

def connect(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(path, check_same_thread=False)
    con.row_factory = sqlite3.Row
    return con

def ingest_frame(frame: pd.DataFrame, path: Path) -> int:
    con = connect(path)
    try:
        frame.to_sql(TABLE, con, if_exists="replace", index=False)
        con.execute("CREATE INDEX IF NOT EXISTS idx_flights_airline ON flights(airline)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_flights_date ON flights(date)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_flights_status ON flights(status)")
        con.commit()
        return int(con.execute("SELECT COUNT(*) FROM flights").fetchone()[0])
    finally:
        con.close()

def table_ready(path: Path) -> bool:
    if not path.exists(): return False
    try:
        with connect(path) as con:
            return con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='flights'").fetchone() is not None
    except sqlite3.Error:
        return False

def row_count(path: Path) -> int:
    if not table_ready(path): return 0
    with connect(path) as con:
        return int(con.execute("SELECT COUNT(*) FROM flights").fetchone()[0])

def query_readonly(path: Path, sql: str, params: tuple = ()) -> list[dict]:
    """Execute a single SELECT against the known flights table using SQLite read-only mode."""
    normalized = sql.strip().lower()
    if not normalized.startswith("select") or ";" in normalized.rstrip(";"):
        raise ValueError("Only a single SELECT statement is allowed")
    if any(word in normalized for word in (" attach ", " pragma ", " insert ", " update ", " delete ", " drop ", " alter ", " create ", " replace ")):
        raise ValueError("SQL contains a prohibited operation")
    uri = f"file:{path.resolve().as_posix()}?mode=ro"
    con = sqlite3.connect(uri, uri=True)
    con.row_factory = sqlite3.Row
    def authorize(action, arg1, arg2, database_name, trigger_name):
        # Allow only SELECT operations reading the known data table. This is a
        # second layer of defense in addition to opening the file read-only.
        allowed_actions = {sqlite3.SQLITE_SELECT, sqlite3.SQLITE_READ, sqlite3.SQLITE_FUNCTION}
        if action not in allowed_actions:
            return sqlite3.SQLITE_DENY
        if action == sqlite3.SQLITE_READ and arg1 != TABLE:
            return sqlite3.SQLITE_DENY
        return sqlite3.SQLITE_OK
    con.set_authorizer(authorize)
    try:
        # Limit returned rows to reduce accidental resource exhaustion.
        cur = con.execute(sql, params)
        if cur.description is None: raise ValueError("Query did not return rows")
        return [dict(row) for row in cur.fetchmany(500)]
    finally:
        con.close()

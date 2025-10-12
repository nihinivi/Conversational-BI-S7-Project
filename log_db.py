import sqlite3
import json
from typing import List, Optional, Tuple
from datetime import datetime

DB_SCHEMA = '''
CREATE TABLE IF NOT EXISTS logs (
    timestamp INTEGER PRIMARY KEY,
    jsonschema TEXT NOT NULL,
    dbfilename TEXT NOT NULL
);
'''


def _get_conn(db_path: str = 'logs.sqlite3') -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _ensure_schema(db_path: str = 'logs.sqlite3') -> None:
    conn = _get_conn(db_path)
    try:
        # If table does not exist, create with new schema
        cur = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='logs'")
        if not cur.fetchone():
            conn.executescript(DB_SCHEMA)
            conn.commit()
            return

        # If table exists, check whether timestamp is PRIMARY KEY
        cols = conn.execute("PRAGMA table_info('logs')").fetchall()
        ts_is_pk = False
        for c in cols:
            # c['name'], c['pk'] available via row factory
            if c['name'] == 'timestamp' and int(c['pk']) == 1:
                ts_is_pk = True
                break

        if ts_is_pk:
            # already correct schema
            return

        # Otherwise, rebuild table with new schema and migrate data
        conn.execute('BEGIN')
        try:
            conn.execute('CREATE TABLE IF NOT EXISTS logs_new (timestamp INTEGER PRIMARY KEY, jsonschema TEXT NOT NULL, dbfilename TEXT NOT NULL)')
            # copy & convert rows
            old_rows = conn.execute('SELECT * FROM logs').fetchall()
            for row in old_rows:
                # attempt to get timestamp value from row by name
                try:
                    ts_raw = row['timestamp']
                except Exception:
                    # fallback: try index 0
                    ts_raw = row[0]
                try:
                    ts_epoch = _to_epoch(ts_raw)
                except Exception:
                    # skip rows that cannot be parsed
                    continue
                js = row['jsonschema'] if 'jsonschema' in row.keys() else row[2] if len(row) > 2 else '{}'
                dbfn = row['dbfilename'] if 'dbfilename' in row.keys() else row[3] if len(row) > 3 else ''
                try:
                    conn.execute('INSERT OR IGNORE INTO logs_new (timestamp, jsonschema, dbfilename) VALUES (?, ?, ?)', (int(ts_epoch), js, dbfn))
                except Exception:
                    # skip problematic rows
                    continue
            # drop old table and rename new
            conn.execute('DROP TABLE logs')
            conn.execute('ALTER TABLE logs_new RENAME TO logs')
            conn.commit()
        except Exception:
            conn.rollback()
            raise
    finally:
        conn.close()


def _migrate_timestamps(db_path: str = 'logs.sqlite3') -> None:
    """Migrate any non-integer timestamp values (e.g., ISO strings) to epoch integers.

    This function attempts to parse existing timestamp values and update them to
    integer epoch seconds. If converting a timestamp would conflict with an
    existing row (unique constraint), the migration for that row is skipped.
    """
    conn = _get_conn(db_path)
    try:
        cur = conn.execute('SELECT id, timestamp FROM logs')
        rows = cur.fetchall()
        for row in rows:
            rid = row['id']
            ts = row['timestamp']
            # If timestamp already an integer (sqlite may still return as int), skip
            if isinstance(ts, int):
                continue
            # If it's bytes, decode
            if isinstance(ts, (bytes, bytearray)):
                try:
                    ts = ts.decode()
                except Exception:
                    continue
            # If it's a string of digits, likely already an integer stored as text
            if isinstance(ts, str) and ts.isdigit():
                # try updating to integer form
                try:
                    with conn:
                        conn.execute('UPDATE logs SET timestamp = ? WHERE id = ?', (int(ts), rid))
                except sqlite3.IntegrityError:
                    # conflict - skip
                    continue
                continue
            # Otherwise, try parsing to epoch
            try:
                ts_epoch = _to_epoch(ts)
            except Exception:
                # cannot parse, skip
                continue
            # Attempt update; if conflict occurs, skip this row
            try:
                with conn:
                    conn.execute('UPDATE logs SET timestamp = ? WHERE id = ?', (int(ts_epoch), rid))
            except sqlite3.IntegrityError:
                # conflict with existing timestamp - skip
                continue
    finally:
        conn.close()


def _to_epoch(ts) -> int:
    """Convert various timestamp input types to epoch integer seconds."""
    if isinstance(ts, int):
        return ts
    if isinstance(ts, float):
        return int(ts)
    if isinstance(ts, str):
        try:
            # try ISO format
            dt = datetime.fromisoformat(ts)
            return int(dt.timestamp())
        except Exception:
            try:
                return int(float(ts))
            except Exception:
                raise ValueError(f"Cannot parse timestamp: {ts}")
    if isinstance(ts, datetime):
        return int(ts.timestamp())
    raise ValueError(f"Unsupported timestamp type: {type(ts)}")


def insert(timestamp, jsonschema: dict, dbfilename: str, db_path: str = 'logs.sqlite3') -> bool:
    """Insert a new log row into the database.

    Args:
        timestamp: ISO-format timestamp string (should be unique)
        jsonschema: A dict representing the JSON schema/log
        dbfilename: A filename or identifier for the database or source
        db_path: Path to the sqlite database file

    Returns:
        True if insert succeeded, False otherwise
    """
    _ensure_schema(db_path)
    ts_epoch = _to_epoch(timestamp)
    conn = _get_conn(db_path)
    try:
        with conn:
            conn.execute(
                'INSERT INTO logs (timestamp, jsonschema, dbfilename) VALUES (?, ?, ?)',
                (ts_epoch, json.dumps(jsonschema), dbfilename)
            )
        return True
    except sqlite3.IntegrityError:
        # Timestamp already exists (unique constraint)
        return False
    except Exception:
        return False
    finally:
        conn.close()


def getlogs(db_path: str = 'logs.sqlite3') -> List[int]:
    """Retrieve all log timestamps as epoch integers (ordered by timestamp asc)."""
    _ensure_schema(db_path)
    conn = _get_conn(db_path)
    try:
        cur = conn.execute('SELECT timestamp FROM logs ORDER BY timestamp ASC')
        out = []
        for row in cur.fetchall():
            ts = row['timestamp']
            try:
                out.append(int(ts))
            except Exception:
                try:
                    out.append(_to_epoch(ts))
                except Exception:
                    # skip unparsable
                    continue
        return out
    finally:
        conn.close()


def getdata(timestamp, db_path: str = 'logs.sqlite3') -> Optional[Tuple[dict, str]]:
    """Given a timestamp (or epoch-parsable input), return (jsonschema_dict, dbfilename) or None if not found."""
    _ensure_schema(db_path)
    ts_epoch = _to_epoch(timestamp)
    conn = _get_conn(db_path)
    try:
        cur = conn.execute('SELECT jsonschema, dbfilename FROM logs WHERE timestamp = ?', (ts_epoch,))
        row = cur.fetchone()
        if not row:
            return None
        return (json.loads(row['jsonschema']), row['dbfilename'])
    finally:
        conn.close()


def getdata_interactive(db_path: str = 'logs.sqlite3') -> None:
    """Prompt the user for a timestamp (epoch or ISO) and print the stored jsonschema and dbfilename."""
    inp = input('Enter timestamp (epoch seconds or ISO string): ').strip()
    try:
        res = getdata(inp, db_path=db_path)
    except ValueError as e:
        print('Invalid timestamp input:', e)
        return
    if not res:
        print('No entry found for that timestamp')
        return
    jsonschema, dbfilename = res
    print('jsonschema:')
    print(json.dumps(jsonschema, indent=4))
    print('dbfilename:', dbfilename)


if __name__ == '__main__':
    # Demo showing different ways to use timestamps
    dbfile = 'e:/CONVERSATIONAL_BI/logs.sqlite3'
    
    # 1. Insert using epoch timestamp (integer seconds since Unix epoch)
    ts1 = int(datetime.now().timestamp())
    print(f"\n1. Inserting with epoch timestamp: {ts1}")
    js1 = {'query': 'Show me sales by region', 'plotly_code': "px.bar(df, x='Region', y='Sales')"}
    inserted = insert(ts1, js1, 'query_log.json', db_path=dbfile)
    print('Inserted:', inserted)
    
    # 2. Insert using ISO string (automatically converted to epoch)
    ts2 = datetime.now().isoformat()
    print(f"\n2. Inserting with ISO timestamp: {ts2}")
    js2 = {'query': 'Show me customers by city', 'plotly_code': "px.bar(df, x='City', y='Customers')"}
    inserted = insert(ts2, js2, 'query_log.json', db_path=dbfile)
    print('Inserted:', inserted)
    
    # 3. Show all stored timestamps (as epoch integers)
    print("\n3. All stored timestamps (epoch):")
    timestamps = getlogs(db_path=dbfile)
    for ts in timestamps[-5:]:  # Show last 5
        dt = datetime.fromtimestamp(ts)
        print(f"  {ts} -> {dt.isoformat()}")
    
    # 4. Demonstrate getdata with both epoch and ISO format
    print("\n4. Retrieving data:")
    print("By epoch timestamp:")
    data1 = getdata(ts1, db_path=dbfile)
    if data1:
        print("  JSON schema:", data1[0])
        print("  DB filename:", data1[1])
    
    # 5. Interactive demo
    print("\n5. Interactive query demo:")
    getdata_interactive(db_path=dbfile)

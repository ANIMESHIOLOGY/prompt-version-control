import sqlite3
import time
from pathlib import Path
from contextlib import contextmanager
from typing import Generator

PROMPTVC_DIR = ".promptvc"
DB_FILE = "store.db"


def get_db_path() -> Path:
    """Walk up directory tree to find .promptvc/store.db."""
    current = Path.cwd()
    while current != current.parent:
        candidate = current / PROMPTVC_DIR / DB_FILE
        if candidate.exists():
            return candidate
        current = current.parent
    raise FileNotFoundError(
        "No .promptvc directory found. Run `promptvc init` first."
    )


def get_promptvc_dir() -> Path:
    """Return the .promptvc directory path."""
    return get_db_path().parent


@contextmanager
def get_connection() -> Generator[sqlite3.Connection, None, None]:
    db_path = get_db_path()
    retries = 3
    delay = 0.2

    for attempt in range(retries):
        try:
            conn = sqlite3.connect(str(db_path), timeout=5.0)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower() and attempt < retries - 1:
                time.sleep(delay)
                continue
            raise

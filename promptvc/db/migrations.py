import sqlite3


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS prompts (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            name        TEXT NOT NULL UNIQUE,
            description TEXT,
            created_at  TEXT NOT NULL DEFAULT (datetime('now')),
            updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS versions (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            prompt_id     INTEGER NOT NULL REFERENCES prompts(id) ON DELETE CASCADE,
            version_num   INTEGER NOT NULL,
            content       TEXT NOT NULL,
            content_hash  TEXT NOT NULL,
            message       TEXT NOT NULL DEFAULT '',
            environment   TEXT NOT NULL DEFAULT 'dev',
            token_count   INTEGER,
            model_hint    TEXT,
            author        TEXT,
            created_at    TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(prompt_id, version_num)
        );

        CREATE TABLE IF NOT EXISTS tags (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id INTEGER NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
            tag_name   TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (datetime('now')),
            UNIQUE(version_id, tag_name)
        );

        CREATE TABLE IF NOT EXISTS config (
            key        TEXT PRIMARY KEY,
            value      TEXT NOT NULL
        );

        CREATE VIRTUAL TABLE IF NOT EXISTS versions_fts USING fts5(
            content,
            message,
            content=versions,
            content_rowid=id
        );
    """)
    conn.commit()

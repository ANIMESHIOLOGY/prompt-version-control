import sqlite3
from pathlib import Path

import pytest

from promptvc.db.migrations import create_schema


@pytest.fixture
def db(tmp_path: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(str(tmp_path / "store.db"))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    create_schema(conn)
    return conn


def test_schema_creates_all_tables(db: sqlite3.Connection) -> None:
    tables = {
        row[0]
        for row in db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' OR type='shadow'"
        ).fetchall()
    }
    assert "prompts" in tables
    assert "versions" in tables
    assert "tags" in tables
    assert "config" in tables


def test_prompt_insert_and_fetch(db: sqlite3.Connection) -> None:
    db.execute("INSERT INTO prompts (name) VALUES (?)", ("summarizer",))
    db.commit()
    row = db.execute("SELECT * FROM prompts WHERE name = ?", ("summarizer",)).fetchone()
    assert row is not None
    assert row["name"] == "summarizer"


def test_prompt_name_unique(db: sqlite3.Connection) -> None:
    db.execute("INSERT INTO prompts (name) VALUES (?)", ("dup",))
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO prompts (name) VALUES (?)", ("dup",))
        db.commit()


def test_version_insert(db: sqlite3.Connection) -> None:
    db.execute("INSERT INTO prompts (name) VALUES (?)", ("p",))
    db.commit()
    prompt_id = db.execute("SELECT id FROM prompts WHERE name='p'").fetchone()["id"]
    db.execute(
        """INSERT INTO versions
           (prompt_id, version_num, content, content_hash, message, environment, author)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (prompt_id, 1, "hello world", "abc123", "initial", "dev", "tester"),
    )
    db.commit()
    ver = db.execute(
        "SELECT * FROM versions WHERE prompt_id = ? AND version_num = ?",
        (prompt_id, 1),
    ).fetchone()
    assert ver is not None
    assert ver["content"] == "hello world"
    assert ver["environment"] == "dev"


def test_version_num_unique_per_prompt(db: sqlite3.Connection) -> None:
    db.execute("INSERT INTO prompts (name) VALUES (?)", ("p",))
    db.commit()
    pid = db.execute("SELECT id FROM prompts WHERE name='p'").fetchone()["id"]
    db.execute(
        "INSERT INTO versions (prompt_id, version_num, content, content_hash, message) "
        "VALUES (?, 1, 'a', 'h1', 'm')",
        (pid,),
    )
    db.commit()
    with pytest.raises(sqlite3.IntegrityError):
        db.execute(
            "INSERT INTO versions (prompt_id, version_num, content, content_hash, message) "
            "VALUES (?, 1, 'b', 'h2', 'm')",
            (pid,),
        )
        db.commit()


def test_tag_insert_and_unique(db: sqlite3.Connection) -> None:
    db.execute("INSERT INTO prompts (name) VALUES (?)", ("p",))
    db.commit()
    pid = db.execute("SELECT id FROM prompts WHERE name='p'").fetchone()["id"]
    db.execute(
        "INSERT INTO versions (prompt_id, version_num, content, content_hash, message) "
        "VALUES (?, 1, 'x', 'h', 'm')",
        (pid,),
    )
    db.commit()
    vid = db.execute("SELECT id FROM versions WHERE prompt_id=?", (pid,)).fetchone()["id"]
    db.execute("INSERT INTO tags (version_id, tag_name) VALUES (?, ?)", (vid, "stable"))
    db.commit()
    tag = db.execute("SELECT * FROM tags WHERE version_id=? AND tag_name=?", (vid, "stable")).fetchone()
    assert tag is not None

    with pytest.raises(sqlite3.IntegrityError):
        db.execute("INSERT INTO tags (version_id, tag_name) VALUES (?, ?)", (vid, "stable"))
        db.commit()


def test_cascade_delete(db: sqlite3.Connection) -> None:
    db.execute("INSERT INTO prompts (name) VALUES (?)", ("p",))
    db.commit()
    pid = db.execute("SELECT id FROM prompts WHERE name='p'").fetchone()["id"]
    db.execute(
        "INSERT INTO versions (prompt_id, version_num, content, content_hash, message) "
        "VALUES (?, 1, 'x', 'h', 'm')",
        (pid,),
    )
    db.commit()
    db.execute("DELETE FROM prompts WHERE id = ?", (pid,))
    db.commit()
    count = db.execute("SELECT COUNT(*) FROM versions WHERE prompt_id=?", (pid,)).fetchone()[0]
    assert count == 0

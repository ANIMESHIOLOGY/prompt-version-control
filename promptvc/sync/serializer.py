import sqlite3
from typing import Any, Dict


def export_to_dict(conn: sqlite3.Connection) -> Dict[str, Any]:
    """Serialize entire local store to a JSON-serializable dict."""
    prompts = conn.execute("SELECT * FROM prompts ORDER BY id").fetchall()
    result: Dict[str, Any] = {"version": 1, "prompts": []}

    for p in prompts:
        versions = conn.execute(
            "SELECT * FROM versions WHERE prompt_id = ? ORDER BY version_num",
            (p["id"],),
        ).fetchall()

        prompt_data: Dict[str, Any] = {
            "name": p["name"],
            "description": p["description"],
            "created_at": p["created_at"],
            "versions": [],
        }

        for v in versions:
            tags = [
                r["tag_name"]
                for r in conn.execute(
                    "SELECT tag_name FROM tags WHERE version_id = ?", (v["id"],)
                ).fetchall()
            ]
            prompt_data["versions"].append(
                {
                    "version_num": v["version_num"],
                    "content": v["content"],
                    "content_hash": v["content_hash"],
                    "message": v["message"],
                    "environment": v["environment"],
                    "token_count": v["token_count"],
                    "model_hint": v["model_hint"],
                    "author": v["author"],
                    "created_at": v["created_at"],
                    "tags": tags,
                }
            )

        result["prompts"].append(prompt_data)

    return result


def import_from_dict(conn: sqlite3.Connection, data: Dict[str, Any]) -> Dict[str, int]:
    """Merge remote data into local DB. Returns counts of newly added rows."""
    added_prompts = 0
    added_versions = 0

    for p in data.get("prompts", []):
        row = conn.execute(
            "SELECT id FROM prompts WHERE name = ?", (p["name"],)
        ).fetchone()
        if row is None:
            conn.execute(
                "INSERT INTO prompts (name, description, created_at) VALUES (?, ?, ?)",
                (p["name"], p.get("description"), p.get("created_at")),
            )
            row = conn.execute(
                "SELECT id FROM prompts WHERE name = ?", (p["name"],)
            ).fetchone()
            added_prompts += 1

        prompt_id = row["id"]

        for v in p.get("versions", []):
            existing = conn.execute(
                "SELECT id FROM versions WHERE prompt_id = ? AND content_hash = ?",
                (prompt_id, v["content_hash"]),
            ).fetchone()
            if existing is not None:
                continue

            max_ver = conn.execute(
                "SELECT MAX(version_num) as mv FROM versions WHERE prompt_id = ?",
                (prompt_id,),
            ).fetchone()
            new_ver = (max_ver["mv"] or 0) + 1

            conn.execute(
                """INSERT INTO versions
                   (prompt_id, version_num, content, content_hash, message,
                    environment, token_count, model_hint, author, created_at)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    prompt_id,
                    new_ver,
                    v["content"],
                    v["content_hash"],
                    v["message"],
                    v["environment"],
                    v["token_count"],
                    v.get("model_hint"),
                    v.get("author"),
                    v.get("created_at"),
                ),
            )
            ver_id = conn.execute(
                "SELECT id FROM versions WHERE prompt_id = ? AND version_num = ?",
                (prompt_id, new_ver),
            ).fetchone()["id"]

            conn.execute(
                "INSERT INTO versions_fts(rowid, content, message) VALUES (?, ?, ?)",
                (ver_id, v["content"], v["message"]),
            )

            for tag in v.get("tags", []):
                conn.execute(
                    "INSERT OR IGNORE INTO tags (version_id, tag_name) VALUES (?, ?)",
                    (ver_id, tag),
                )

            added_versions += 1

    return {"prompts": added_prompts, "versions": added_versions}

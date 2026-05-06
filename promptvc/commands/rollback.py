import os
import subprocess
from typing import Optional

import typer

from promptvc.core.hasher import sha256
from promptvc.core.tokenizer import count_tokens
from promptvc.db.connection import get_connection
from promptvc.utils.console import check_init, console, find_prompt


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    version: int = typer.Option(..., "--version", "-v", help="Version to roll back to"),
    message: Optional[str] = typer.Option(None, "--message", "-m", help="Commit message"),
) -> None:
    """Non-destructively roll back a prompt to a previous version (creates a new version)."""
    check_init()

    author = _detect_author()
    new_ver = 0

    with get_connection() as conn:
        prompt = find_prompt(conn, name)
        if prompt is None:
            raise typer.Exit(1)

        target = conn.execute(
            "SELECT * FROM versions WHERE prompt_id = ? AND version_num = ?",
            (prompt["id"], version),
        ).fetchone()
        if target is None:
            console.print(
                f'[bold red]✗[/] Version [bold]{version}[/] of [cyan]"{name}"[/] not found.'
            )
            raise typer.Exit(1)

        content = target["content"]
        content_hash = sha256(content)

        last = conn.execute(
            "SELECT content_hash, version_num FROM versions "
            "WHERE prompt_id = ? ORDER BY version_num DESC LIMIT 1",
            (prompt["id"],),
        ).fetchone()

        if last and last["content_hash"] == content_hash:
            console.print(
                f"[yellow]⚠[/]  Version [bold]{version}[/] content is identical to the current "
                f"version [bold]{last['version_num']}[/] — nothing to roll back."
            )
            raise typer.Exit(0)

        max_ver = conn.execute(
            "SELECT MAX(version_num) as mv FROM versions WHERE prompt_id = ?",
            (prompt["id"],),
        ).fetchone()
        new_ver = (max_ver["mv"] or 0) + 1
        commit_msg = message or f"rollback to v{version}"
        token_count, _ = count_tokens(content, target["model_hint"] or "gpt-4o")

        conn.execute(
            """INSERT INTO versions
               (prompt_id, version_num, content, content_hash, message,
                environment, token_count, model_hint, author)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                prompt["id"],
                new_ver,
                content,
                content_hash,
                commit_msg,
                target["environment"],
                token_count,
                target["model_hint"],
                author,
            ),
        )
        conn.execute(
            "UPDATE prompts SET updated_at = datetime('now') WHERE id = ?",
            (prompt["id"],),
        )
        version_id = conn.execute(
            "SELECT id FROM versions WHERE prompt_id = ? AND version_num = ?",
            (prompt["id"], new_ver),
        ).fetchone()["id"]
        conn.execute(
            "INSERT INTO versions_fts(rowid, content, message) VALUES (?, ?, ?)",
            (version_id, content, commit_msg),
        )

    console.print(
        f'[bold green]✓[/] Rolled back [cyan]"{name}"[/] to v{version} content '
        f"→ saved as [bold]v{new_ver}[/]"
    )


def _detect_author() -> str:
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=3,
        )
        name = result.stdout.strip()
        if name:
            return name
    except Exception:
        pass
    return os.environ.get("USER", os.environ.get("USERNAME", "unknown"))

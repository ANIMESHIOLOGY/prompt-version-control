import os
import subprocess
from typing import Optional

import typer
from rich.table import Table

from promptvc.core.hasher import sha256
from promptvc.core.tokenizer import count_tokens
from promptvc.db.connection import get_connection, get_promptvc_dir
from promptvc.utils.console import check_init, console


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    message: str = typer.Option(..., "--message", "-m", help="Commit message"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Override environment"),
    model: Optional[str] = typer.Option(None, "--model", help="Override model hint"),
) -> None:
    """Commit staged prompt content with a message."""
    check_init()

    promptvc_dir = get_promptvc_dir()
    staged_dir = promptvc_dir / ".staged"
    staged_path = staged_dir / f"{name}.txt"

    if not staged_path.exists():
        console.print(
            f'[yellow]⚠[/]  Nothing staged for [cyan]"{name}"[/]. '
            f"Run [bold]promptvc add {name}[/] first."
        )
        raise typer.Exit(0)

    content = staged_path.read_text(encoding="utf-8")
    meta_path = staged_dir / f"{name}.meta"
    staged_env, staged_model = _read_meta(meta_path)

    final_env = env or staged_env
    final_model = model or staged_model
    content_hash = sha256(content)
    author = _detect_author()

    duplicate = False
    version_num = 0
    token_count = 0
    is_exact = True

    with get_connection() as conn:
        prompt_row = conn.execute(
            "SELECT id FROM prompts WHERE name = ?", (name,)
        ).fetchone()
        if prompt_row is None:
            conn.execute("INSERT INTO prompts (name) VALUES (?)", (name,))
            prompt_row = conn.execute(
                "SELECT id FROM prompts WHERE name = ?", (name,)
            ).fetchone()

        prompt_id = prompt_row["id"]

        last = conn.execute(
            "SELECT content_hash FROM versions WHERE prompt_id = ? ORDER BY version_num DESC LIMIT 1",
            (prompt_id,),
        ).fetchone()

        if last and last["content_hash"] == content_hash:
            duplicate = True
        else:
            max_ver = conn.execute(
                "SELECT MAX(version_num) as mv FROM versions WHERE prompt_id = ?",
                (prompt_id,),
            ).fetchone()
            version_num = (max_ver["mv"] or 0) + 1
            token_count, is_exact = count_tokens(content, final_model)

            conn.execute(
                """INSERT INTO versions
                   (prompt_id, version_num, content, content_hash, message,
                    environment, token_count, model_hint, author)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    prompt_id,
                    version_num,
                    content,
                    content_hash,
                    message,
                    final_env,
                    token_count,
                    final_model,
                    author,
                ),
            )
            conn.execute(
                "UPDATE prompts SET updated_at = datetime('now') WHERE id = ?",
                (prompt_id,),
            )
            version_id = conn.execute(
                "SELECT id FROM versions WHERE prompt_id = ? AND version_num = ?",
                (prompt_id, version_num),
            ).fetchone()["id"]
            conn.execute(
                "INSERT INTO versions_fts(rowid, content, message) VALUES (?, ?, ?)",
                (version_id, content, message),
            )

    if duplicate:
        console.print("[yellow]⚠[/]  Content unchanged — nothing to commit.")
        raise typer.Exit(0)

    staged_path.unlink(missing_ok=True)
    meta_path.unlink(missing_ok=True)

    token_str = str(token_count) if is_exact else f"~{token_count} words"
    table = Table(border_style="dim", show_header=False)
    table.add_column("Field", style="bold cyan")
    table.add_column("Value")
    table.add_row("Prompt", name)
    table.add_row("Version", str(version_num))
    table.add_row("Message", message)
    table.add_row("Environment", final_env)
    table.add_row("Tokens", token_str)
    table.add_row("Hash", content_hash[:12] + "...")
    table.add_row("Author", author)

    console.print(f'[bold green]✓[/] Committed version [bold]{version_num}[/] of [cyan]"{name}"[/]')
    console.print(table)


def _read_meta(meta_path: object) -> tuple:
    env, model = "dev", "gpt-4o"
    try:
        for line in meta_path.read_text(encoding="utf-8").splitlines():  # type: ignore[union-attr]
            if line.startswith("env="):
                env = line[4:]
            elif line.startswith("model="):
                model = line[6:]
    except Exception:
        pass
    return env, model


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

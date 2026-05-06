from typing import Optional

import typer
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

from promptvc.db.connection import get_connection
from promptvc.utils.config import read_config
from promptvc.utils.console import check_init, console, find_prompt


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    version: Optional[int] = typer.Option(None, "--version", "-v", help="Version number"),
    tag: Optional[str] = typer.Option(None, "--tag", "-t", help="Tag name"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Show prompt content at a specific version (defaults to latest)."""
    check_init()
    cfg = read_config()
    theme = cfg.get("display", {}).get("syntax_theme", "monokai")

    with get_connection() as conn:
        prompt = find_prompt(conn, name)
        if prompt is None:
            raise typer.Exit(1)

        row = _fetch_version(conn, prompt["id"], version, tag, name)

    if row is None:
        raise typer.Exit(1)

    if json_output:
        import json
        print(json.dumps({
            "version_num": row["version_num"],
            "content": row["content"],
            "message": row["message"],
            "environment": row["environment"],
            "token_count": row["token_count"],
            "model_hint": row["model_hint"],
            "author": row["author"],
            "content_hash": row["content_hash"],
            "created_at": row["created_at"],
        }))
        return

    meta = Table(border_style="dim", show_header=False)
    meta.add_column("Field", style="bold cyan")
    meta.add_column("Value")
    meta.add_row("Version", f"v{row['version_num']}")
    meta.add_row("Message", row["message"])
    meta.add_row("Environment", row["environment"])
    tokens = str(row["token_count"]) if row["token_count"] is not None else "—"
    meta.add_row("Tokens", tokens)
    meta.add_row("Model", row["model_hint"] or "—")
    meta.add_row("Author", row["author"] or "—")
    meta.add_row("Hash", row["content_hash"][:16] + "...")
    date = row["created_at"][:16].replace("T", " ")
    meta.add_row("Date", date)

    console.print(meta)
    syntax = Syntax(row["content"], "text", theme=theme, word_wrap=True)
    console.print(Panel(syntax, title=f"[cyan]{name}[/] v{row['version_num']}", border_style="dim"))


def _fetch_version(conn, prompt_id: int, version: Optional[int], tag: Optional[str], name: str):
    if tag is not None:
        row = conn.execute(
            """SELECT v.* FROM versions v
               JOIN tags t ON t.version_id = v.id
               WHERE v.prompt_id = ? AND t.tag_name = ?
               ORDER BY v.version_num DESC LIMIT 1""",
            (prompt_id, tag),
        ).fetchone()
        if row is None:
            console.print(f'[bold red]✗[/] No version of [cyan]"{name}"[/] tagged [yellow]"{tag}"[/].')
        return row

    if version is not None:
        row = conn.execute(
            "SELECT * FROM versions WHERE prompt_id = ? AND version_num = ?",
            (prompt_id, version),
        ).fetchone()
        if row is None:
            console.print(
                f'[bold red]✗[/] Version [bold]{version}[/] of [cyan]"{name}"[/] not found.'
            )
        return row

    row = conn.execute(
        "SELECT * FROM versions WHERE prompt_id = ? ORDER BY version_num DESC LIMIT 1",
        (prompt_id,),
    ).fetchone()
    if row is None:
        console.print(f'[bold red]✗[/] No versions found for [cyan]"{name}"[/].')
    return row

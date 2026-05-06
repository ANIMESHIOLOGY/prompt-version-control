import difflib
import sqlite3
from typing import Optional

import typer
from rich.console import Console

console = Console()


def check_init() -> None:
    """Exit with a friendly error if .promptvc hasn't been initialized."""
    from promptvc.db.connection import get_db_path

    try:
        get_db_path()
    except FileNotFoundError:
        console.print(
            "[bold red]✗[/] No .promptvc directory found. "
            "Run [bold]promptvc init[/] first."
        )
        raise typer.Exit(1)


def find_prompt(conn: sqlite3.Connection, name: str) -> Optional[sqlite3.Row]:
    """Fetch a prompt row by name; print a helpful error with suggestions if missing."""
    row = conn.execute("SELECT * FROM prompts WHERE name = ?", (name,)).fetchone()
    if row is None:
        all_names = [r["name"] for r in conn.execute("SELECT name FROM prompts").fetchall()]
        similar = difflib.get_close_matches(name, all_names, n=3, cutoff=0.6)
        console.print(f'[bold red]✗[/] No prompt named [cyan]"{name}"[/] found.')
        if similar:
            console.print(f"[dim]Did you mean: {', '.join(similar)}?[/]")
    return row

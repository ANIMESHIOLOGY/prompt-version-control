from typing import Optional

import typer
from rich.text import Text

from promptvc.core.differ import unified_diff
from promptvc.db.connection import get_connection
from promptvc.utils.console import check_init, console, find_prompt


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    from_version: Optional[int] = typer.Option(None, "--from", help="From version number"),
    to_version: Optional[int] = typer.Option(None, "--to", help="To version number"),
) -> None:
    """Show unified diff between two versions (defaults to last two)."""
    check_init()

    with get_connection() as conn:
        prompt = find_prompt(conn, name)
        if prompt is None:
            raise typer.Exit(1)

        all_versions = conn.execute(
            "SELECT version_num, content, token_count FROM versions "
            "WHERE prompt_id = ? ORDER BY version_num DESC",
            (prompt["id"],),
        ).fetchall()

    if len(all_versions) < 2 and (from_version is None or to_version is None):
        console.print(
            f'[yellow]⚠[/]  [cyan]"{name}"[/] has fewer than 2 versions — nothing to diff.'
        )
        raise typer.Exit(0)

    version_map = {r["version_num"]: r for r in all_versions}

    to_num = to_version if to_version is not None else all_versions[0]["version_num"]
    from_num = from_version if from_version is not None else all_versions[1]["version_num"]

    old = version_map.get(from_num)
    new = version_map.get(to_num)

    if old is None:
        console.print(f"[bold red]✗[/] Version [bold]{from_num}[/] not found.")
        raise typer.Exit(1)
    if new is None:
        console.print(f"[bold red]✗[/] Version [bold]{to_num}[/] not found.")
        raise typer.Exit(1)

    diff = unified_diff(old["content"], new["content"], f"v{from_num}", f"v{to_num}")

    if not diff:
        console.print("[yellow]⚠[/]  Versions are identical — no diff.")
        raise typer.Exit(0)

    text = Text()
    for line in diff.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            text.append(line + "\n", style="bold")
        elif line.startswith("+"):
            text.append(line + "\n", style="green")
        elif line.startswith("-"):
            text.append(line + "\n", style="red")
        elif line.startswith("@@"):
            text.append(line + "\n", style="cyan")
        else:
            text.append(line + "\n")

    console.print(text)

    old_tokens = old["token_count"] or 0
    new_tokens = new["token_count"] or 0
    delta = new_tokens - old_tokens
    sign = "+" if delta >= 0 else ""
    console.print(f"[dim]Token delta: {sign}{delta} tokens[/]")

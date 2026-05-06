from typing import Optional

import typer
from rich.table import Table

from promptvc.db.connection import get_connection
from promptvc.utils.console import check_init, console, find_prompt


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Filter by environment"),
    limit: int = typer.Option(20, "--limit", "-n", help="Max versions to show"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """Show version history for a prompt."""
    check_init()

    with get_connection() as conn:
        prompt = find_prompt(conn, name)
        if prompt is None:
            raise typer.Exit(1)

        query = """
            SELECT v.version_num, v.created_at, v.author, v.environment,
                   v.token_count, v.model_hint, v.message,
                   GROUP_CONCAT(t.tag_name, ', ') as tags
            FROM versions v
            LEFT JOIN tags t ON t.version_id = v.id
            WHERE v.prompt_id = ?
        """
        params: list = [prompt["id"]]
        if env:
            query += " AND v.environment = ?"
            params.append(env)
        query += " GROUP BY v.id ORDER BY v.version_num DESC LIMIT ?"
        params.append(limit)

        rows = conn.execute(query, params).fetchall()

    if json_output:
        import json
        print(json.dumps([
            {
                "version_num": r["version_num"],
                "message": r["message"],
                "author": r["author"],
                "environment": r["environment"],
                "token_count": r["token_count"],
                "created_at": r["created_at"],
                "tags": r["tags"],
            }
            for r in rows
        ]))
        return

    if not rows:
        console.print(f'[yellow]⚠[/]  No versions found for [cyan]"{name}"[/].')
        raise typer.Exit(0)

    table = Table(title=f"[bold cyan]{name}[/] history", border_style="dim")
    table.add_column("Ver", style="bold", justify="right")
    table.add_column("Date")
    table.add_column("Author")
    table.add_column("Env")
    table.add_column("Tokens", justify="right")
    table.add_column("Message")
    table.add_column("Tags", style="yellow")

    for row in rows:
        ver_str = f"v{row['version_num']}"
        tokens = str(row["token_count"]) if row["token_count"] is not None else "—"
        date = row["created_at"][:16].replace("T", " ")
        tags = row["tags"] or ""
        table.add_row(
            ver_str, date, row["author"] or "—", row["environment"],
            tokens, row["message"], tags,
        )

    console.print(table)

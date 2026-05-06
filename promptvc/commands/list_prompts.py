from typing import Optional

import typer
from rich.table import Table

from promptvc.db.connection import get_connection
from promptvc.utils.console import check_init, console


def run(
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Filter by environment"),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
) -> None:
    """List all tracked prompts."""
    check_init()

    with get_connection() as conn:
        query = """
            SELECT p.name, p.description, p.updated_at,
                   COUNT(v.id) as version_count,
                   MAX(v.version_num) as latest_version,
                   MAX(v.environment) as last_env
            FROM prompts p
            LEFT JOIN versions v ON v.prompt_id = p.id
        """
        params: list = []
        if env:
            query += " WHERE v.environment = ?"
            params.append(env)
        query += " GROUP BY p.id ORDER BY p.updated_at DESC"
        rows = conn.execute(query, params).fetchall()

    if json_output:
        import json
        print(json.dumps([
            {
                "name": r["name"],
                "description": r["description"],
                "version_count": r["version_count"] or 0,
                "latest_version": r["latest_version"],
                "last_env": r["last_env"],
                "updated_at": r["updated_at"] or "",
            }
            for r in rows
        ]))
        return

    if not rows:
        console.print("[dim]No prompts tracked yet. Run [bold]promptvc add <name>[/] to start.[/]")
        raise typer.Exit(0)

    table = Table(title="Tracked prompts", border_style="dim")
    table.add_column("Name", style="bold cyan")
    table.add_column("Versions", justify="right")
    table.add_column("Latest", justify="right")
    table.add_column("Env")
    table.add_column("Last Updated")
    table.add_column("Description")

    for row in rows:
        date = (row["updated_at"] or "")[:16].replace("T", " ")
        table.add_row(
            row["name"],
            str(row["version_count"]) if row["version_count"] else "0",
            f"v{row['latest_version']}" if row["latest_version"] else "—",
            row["last_env"] or "—",
            date,
            row["description"] or "—",
        )

    console.print(table)

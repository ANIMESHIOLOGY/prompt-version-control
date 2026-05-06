import json
from pathlib import Path
from typing import Optional

import typer

from promptvc.db.connection import get_connection
from promptvc.utils.console import check_init, console, find_prompt


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    format: str = typer.Option("json", "--format", "-f", help="Output format: json, yaml"),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output file path"),
) -> None:
    """Export full version history for a prompt to JSON or YAML."""
    check_init()

    if format not in ("json", "yaml"):
        console.print(f"[bold red]✗[/] Unknown format [cyan]{format}[/]. Use: json, yaml")
        raise typer.Exit(1)

    if format == "yaml":
        try:
            import yaml  # noqa: F401
        except ImportError:
            console.print(
                "[bold red]✗[/] PyYAML not installed. Run: [bold]pip install promptvc[yaml][/]"
            )
            raise typer.Exit(1)

    with get_connection() as conn:
        prompt = find_prompt(conn, name)
        if prompt is None:
            raise typer.Exit(1)

        versions = conn.execute(
            """SELECT v.version_num, v.content, v.message, v.environment,
                      v.token_count, v.model_hint, v.author, v.content_hash, v.created_at,
                      GROUP_CONCAT(t.tag_name, ', ') as tags
               FROM versions v
               LEFT JOIN tags t ON t.version_id = v.id
               WHERE v.prompt_id = ?
               GROUP BY v.id
               ORDER BY v.version_num ASC""",
            (prompt["id"],),
        ).fetchall()

    data = {
        "name": name,
        "description": prompt["description"],
        "created_at": prompt["created_at"],
        "versions": [
            {
                "version_num": r["version_num"],
                "content": r["content"],
                "message": r["message"],
                "environment": r["environment"],
                "token_count": r["token_count"],
                "model_hint": r["model_hint"],
                "author": r["author"],
                "content_hash": r["content_hash"],
                "created_at": r["created_at"],
                "tags": [t.strip() for t in (r["tags"] or "").split(",") if t.strip()],
            }
            for r in versions
        ],
    }

    if format == "json":
        serialized = json.dumps(data, indent=2, ensure_ascii=False)
    else:
        import yaml

        serialized = yaml.dump(data, allow_unicode=True, default_flow_style=False)

    if output:
        output.write_text(serialized, encoding="utf-8")
        console.print(f"[bold green]✓[/] Exported [cyan]{name}[/] to [bold]{output}[/]")
    else:
        console.print(serialized)

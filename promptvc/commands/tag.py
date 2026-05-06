import typer

from promptvc.db.connection import get_connection
from promptvc.utils.console import check_init, console, find_prompt


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    version: int = typer.Argument(..., help="Version number to tag"),
    tag_name: str = typer.Argument(..., help="Tag label (e.g. stable, gold, v1.0)"),
) -> None:
    """Add a tag label to a specific prompt version."""
    check_init()

    with get_connection() as conn:
        prompt = find_prompt(conn, name)
        if prompt is None:
            raise typer.Exit(1)

        ver_row = conn.execute(
            "SELECT id FROM versions WHERE prompt_id = ? AND version_num = ?",
            (prompt["id"], version),
        ).fetchone()
        if ver_row is None:
            console.print(
                f'[bold red]✗[/] Version [bold]{version}[/] of [cyan]"{name}"[/] not found.'
            )
            raise typer.Exit(1)

        existing = conn.execute(
            "SELECT id FROM tags WHERE version_id = ? AND tag_name = ?",
            (ver_row["id"], tag_name),
        ).fetchone()
        if existing:
            console.print(
                f'[yellow]⚠[/]  Tag [yellow]"{tag_name}"[/] already exists on '
                f'[cyan]"{name}"[/] v{version}.'
            )
            raise typer.Exit(0)

        conn.execute(
            "INSERT INTO tags (version_id, tag_name) VALUES (?, ?)",
            (ver_row["id"], tag_name),
        )

    console.print(
        f'[bold green]✓[/] Tagged [cyan]"{name}"[/] v{version} as [yellow]"{tag_name}"[/]'
    )

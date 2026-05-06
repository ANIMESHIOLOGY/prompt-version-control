import typer
from rich.table import Table

from promptvc.db.connection import get_connection
from promptvc.utils.console import check_init, console


def run(
    query: str = typer.Argument(..., help="Search query (supports FTS5 syntax)"),
) -> None:
    """Full-text search across all prompt content and commit messages."""
    check_init()

    with get_connection() as conn:
        try:
            rows = conn.execute(
                """SELECT p.name as prompt_name, v.version_num, v.content,
                          v.message, v.created_at, v.environment
                   FROM versions_fts
                   JOIN versions v ON versions_fts.rowid = v.id
                   JOIN prompts p ON p.id = v.prompt_id
                   WHERE versions_fts MATCH ?
                   ORDER BY rank
                   LIMIT 50""",
                (query,),
            ).fetchall()
        except Exception as e:
            console.print(f"[bold red]✗[/] Search error: {e}")
            raise typer.Exit(1)

    if not rows:
        console.print(f"[dim]No results for [bold]{query}[/][/]")
        raise typer.Exit(0)

    table = Table(title=f'Search: "[bold]{query}[/]"', border_style="dim")
    table.add_column("Prompt", style="bold cyan")
    table.add_column("Ver", justify="right")
    table.add_column("Env")
    table.add_column("Date")
    table.add_column("Message")
    table.add_column("Snippet")

    for row in rows:
        snippet = _snippet(row["content"], query)
        date = (row["created_at"] or "")[:16].replace("T", " ")
        table.add_row(
            row["prompt_name"],
            f"v{row['version_num']}",
            row["environment"],
            date,
            row["message"],
            snippet,
        )

    console.print(table)


def _snippet(content: str, query: str, width: int = 60) -> str:
    """Extract a short snippet around the first query term match."""
    lower = content.lower()
    term = query.lower().split()[0].strip('"')
    idx = lower.find(term)
    if idx == -1:
        return content[:width] + ("..." if len(content) > width else "")
    start = max(0, idx - 20)
    end = min(len(content), idx + width)
    snippet = content[start:end].replace("\n", " ")
    if start > 0:
        snippet = "..." + snippet
    if end < len(content):
        snippet = snippet + "..."
    return snippet

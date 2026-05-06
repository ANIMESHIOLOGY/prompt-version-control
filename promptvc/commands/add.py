import sys
from pathlib import Path
from typing import Optional

import typer

from promptvc.core.editor import open_in_editor
from promptvc.db.connection import get_connection, get_promptvc_dir
from promptvc.utils.console import check_init, console


def run(
    name: str = typer.Argument(..., help="Prompt name"),
    file: Optional[Path] = typer.Option(None, "--file", "-f", help="Read content from file"),
    env: str = typer.Option("dev", "--env", "-e", help="Environment (dev/staging/prod)"),
    model: str = typer.Option("gpt-4o", "--model", help="Model hint for token counting"),
) -> None:
    """Stage a prompt for commit (opens $EDITOR if no --file or stdin)."""
    check_init()

    promptvc_dir = get_promptvc_dir()
    staged_dir = promptvc_dir / ".staged"
    staged_dir.mkdir(exist_ok=True)

    content = _read_content(name, file, env, model)
    if not content.strip():
        console.print("[yellow]⚠[/]  Empty content — nothing staged.")
        raise typer.Exit(0)

    staged_path = staged_dir / f"{name}.txt"
    staged_path.write_text(content, encoding="utf-8")

    meta_path = staged_dir / f"{name}.meta"
    meta_path.write_text(f"env={env}\nmodel={model}\n", encoding="utf-8")

    console.print(
        f'[bold green]✓[/] Staged [cyan]"{name}"[/]. '
        f"Run [bold]promptvc commit {name} -m \"your message\"[/] to save."
    )


def _read_content(name: str, file: Optional[Path], env: str, model: str) -> str:
    if file is not None:
        if not file.exists():
            console.print(f"[bold red]✗[/] File not found: {file}")
            raise typer.Exit(1)
        return file.read_text(encoding="utf-8")

    if not sys.stdin.isatty():
        return sys.stdin.read()

    initial = _get_initial_content(name)
    return open_in_editor(initial)


def _get_initial_content(name: str) -> str:
    """Pre-fill editor with staged or last committed content."""
    try:
        promptvc_dir = get_promptvc_dir()
        staged_path = promptvc_dir / ".staged" / f"{name}.txt"
        if staged_path.exists():
            return staged_path.read_text(encoding="utf-8")

        with get_connection() as conn:
            row = conn.execute(
                """SELECT v.content FROM versions v
                   JOIN prompts p ON p.id = v.prompt_id
                   WHERE p.name = ?
                   ORDER BY v.version_num DESC LIMIT 1""",
                (name,),
            ).fetchone()
            return row["content"] if row else ""
    except Exception:
        return ""

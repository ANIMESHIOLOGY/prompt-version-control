import sqlite3
import subprocess
from pathlib import Path

import typer

from promptvc.db.migrations import create_schema
from promptvc.utils.console import console


def run() -> None:
    """Initialize a .promptvc/ directory with SQLite store."""
    cwd = Path.cwd()
    promptvc_dir = cwd / ".promptvc"

    if promptvc_dir.exists():
        console.print("[yellow]⚠[/]  Already initialized in this directory.")
        raise typer.Exit(0)

    promptvc_dir.mkdir()
    (promptvc_dir / ".staged").mkdir()

    db_path = promptvc_dir / "store.db"
    conn = sqlite3.connect(str(db_path))
    create_schema(conn)
    conn.close()

    author = _detect_author()
    _write_config(promptvc_dir, author)
    _handle_gitignore(cwd)

    console.print("[bold green]✓[/] Initialized PromptVC store in [cyan].promptvc/[/]")


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
    import os

    return os.environ.get("USER", os.environ.get("USERNAME", ""))


def _write_config(promptvc_dir: Path, author: str) -> None:
    config_content = f"""[core]
environment = "dev"
author = "{author}"

[defaults]
model = "gpt-4o"
editor = ""

[display]
syntax_theme = "monokai"
"""
    (promptvc_dir / "config.toml").write_text(config_content, encoding="utf-8")


def _handle_gitignore(cwd: Path) -> None:
    if not (cwd / ".git").exists():
        return
    gitignore_path = cwd / ".gitignore"
    try:
        if gitignore_path.exists():
            content = gitignore_path.read_text(encoding="utf-8")
            if ".promptvc/" in content:
                return
            add = typer.confirm("Add .promptvc/ to .gitignore?", default=True)
            if add:
                with open(gitignore_path, "a", encoding="utf-8") as f:
                    f.write("\n.promptvc/\n")
                console.print("[dim]Added .promptvc/ to .gitignore[/]")
        else:
            add = typer.confirm("Create .gitignore with .promptvc/?", default=True)
            if add:
                gitignore_path.write_text(".promptvc/\n", encoding="utf-8")
                console.print("[dim]Created .gitignore with .promptvc/[/]")
    except Exception:
        pass

from typing import Optional

import typer

from promptvc.db.connection import get_promptvc_dir
from promptvc.utils.config import read_config, write_config
from promptvc.utils.console import check_init, console

VALID_ENVS = ("dev", "staging", "prod")


def run(
    action: Optional[str] = typer.Argument(None, help="Action: 'set'"),
    value: Optional[str] = typer.Argument(None, help="Environment: dev, staging, prod"),
) -> None:
    """Show or set the current environment (dev/staging/prod)."""
    check_init()

    if action is None:
        cfg = read_config()
        current = cfg.get("core", {}).get("environment", "dev")
        console.print(f"Current environment: [bold cyan]{current}[/]")
        return

    if action == "set":
        if value is None:
            console.print("[bold red]✗[/] Specify environment: dev, staging, or prod")
            raise typer.Exit(1)
        if value not in VALID_ENVS:
            console.print(
                f"[bold red]✗[/] Invalid environment [cyan]{value}[/]. "
                f"Use: {', '.join(VALID_ENVS)}"
            )
            raise typer.Exit(1)

        cfg = read_config()
        cfg.setdefault("core", {})["environment"] = value
        config_path = get_promptvc_dir() / "config.toml"
        write_config(cfg, config_path)
        console.print(f"[bold green]✓[/] Environment set to [bold cyan]{value}[/]")
    else:
        console.print(f"[bold red]✗[/] Unknown action [cyan]{action}[/]. Use: set")
        raise typer.Exit(1)

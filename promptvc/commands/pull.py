from typing import Optional

import typer

from promptvc.db.connection import get_connection
from promptvc.sync.serializer import import_from_dict
from promptvc.utils.config import read_config
from promptvc.utils.console import check_init, console


def run(
    remote: Optional[str] = typer.Argument(
        None, help="Gist ID / URL  or  s3://bucket/key  (uses config if omitted)"
    ),
    token: Optional[str] = typer.Option(
        None, "--token", help="GitHub PAT (or set GITHUB_TOKEN env var)"
    ),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile name"),
) -> None:
    """Pull a remote prompt store and merge it into local."""
    check_init()

    cfg = read_config()
    remote_cfg = cfg.get("remote", {})

    backend, remote_id = _resolve_remote(remote, remote_cfg)

    tok = token or remote_cfg.get("token") or None

    try:
        data = _fetch(backend, remote_id, tok, profile)
    except Exception as e:
        console.print(f"[bold red]✗[/] Pull failed: {e}")
        raise typer.Exit(1)

    with get_connection() as conn:
        counts = import_from_dict(conn, data)

    console.print(
        f"[bold green]✓[/] Merged from remote — "
        f"[bold]{counts['prompts']}[/] new prompt(s), "
        f"[bold]{counts['versions']}[/] new version(s)."
    )


def _resolve_remote(remote, remote_cfg):
    if remote is not None:
        if remote.startswith("s3://"):
            return "s3", remote[5:]
        return "gist", remote

    backend = remote_cfg.get("type", "")
    if not backend:
        console.print(
            "[bold red]✗[/] No remote configured. Pass a Gist ID or [cyan]s3://bucket/key[/]."
        )
        raise typer.Exit(1)

    if backend == "gist":
        gist_id = remote_cfg.get("gist_id", "")
        if not gist_id:
            console.print("[bold red]✗[/] No gist_id saved. Run [bold]promptvc push --gist[/] first.")
            raise typer.Exit(1)
        return "gist", gist_id

    if backend == "s3":
        b = remote_cfg.get("bucket", "")
        k = remote_cfg.get("key", "promptvc/store.json")
        if not b:
            console.print("[bold red]✗[/] No S3 bucket in config.")
            raise typer.Exit(1)
        return "s3", f"{b}/{k}"

    console.print(f"[bold red]✗[/] Unknown backend: [cyan]{backend}[/]")
    raise typer.Exit(1)


def _fetch(backend, remote_id, token, profile):
    if backend == "gist":
        from promptvc.sync.gist import pull as gist_pull
        return gist_pull(remote_id, token=token)

    if backend == "s3":
        from promptvc.sync.s3 import pull as s3_pull
        parts = remote_id.split("/", 1)
        bucket = parts[0]
        key = parts[1] if len(parts) > 1 else "promptvc/store.json"
        return s3_pull(bucket=bucket, key=key, profile=profile)

    raise ValueError(f"Unknown backend: {backend}")

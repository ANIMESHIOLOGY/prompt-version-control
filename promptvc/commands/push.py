from typing import Optional

import typer

from promptvc.db.connection import get_connection, get_promptvc_dir
from promptvc.sync.serializer import export_to_dict
from promptvc.utils.config import read_config, write_config
from promptvc.utils.console import check_init, console


def run(
    gist: bool = typer.Option(False, "--gist", help="Push to a private GitHub Gist"),
    token: Optional[str] = typer.Option(
        None, "--token", help="GitHub PAT (or set GITHUB_TOKEN env var)"
    ),
    bucket: Optional[str] = typer.Option(None, "--bucket", help="S3 bucket name"),
    key: str = typer.Option("promptvc/store.json", "--key", help="S3 object key"),
    profile: Optional[str] = typer.Option(None, "--profile", help="AWS profile name"),
) -> None:
    """Push local prompt store to a remote (GitHub Gist or S3)."""
    check_init()

    cfg = read_config()
    remote_cfg = cfg.get("remote", {})

    backend = "gist" if gist else ("s3" if bucket else remote_cfg.get("type", ""))
    if not backend:
        console.print(
            "[bold red]✗[/] No remote configured.\n"
            "  Gist: [bold]promptvc push --gist --token <PAT>[/]\n"
            "  S3:   [bold]promptvc push --bucket <name>[/]"
        )
        raise typer.Exit(1)

    with get_connection() as conn:
        data = export_to_dict(conn)

    prompt_count = len(data["prompts"])
    version_count = sum(len(p["versions"]) for p in data["prompts"])

    if backend == "gist":
        _push_gist(data, cfg, remote_cfg, token, prompt_count, version_count)
    elif backend == "s3":
        _push_s3(data, cfg, remote_cfg, bucket, key, profile, prompt_count, version_count)
    else:
        console.print(f"[bold red]✗[/] Unknown backend: [cyan]{backend}[/]")
        raise typer.Exit(1)


def _push_gist(data, cfg, remote_cfg, token, prompt_count, version_count):
    from promptvc.sync.gist import push as gist_push

    gist_id = remote_cfg.get("gist_id") or None
    tok = token or remote_cfg.get("token") or None
    try:
        new_id = gist_push(data, token=tok, gist_id=gist_id)
    except Exception as e:
        console.print(f"[bold red]✗[/] Push failed: {e}")
        raise typer.Exit(1)

    cfg.setdefault("remote", {}).update({"type": "gist", "gist_id": new_id})
    write_config(cfg, get_promptvc_dir() / "config.toml")

    console.print(
        f"[bold green]✓[/] Pushed [bold]{prompt_count}[/] prompts "
        f"([bold]{version_count}[/] versions) to Gist"
    )
    console.print(f"[dim]Gist ID : {new_id}[/]")
    console.print(f"[dim]Share   : https://gist.github.com/{new_id}[/]")


def _push_s3(data, cfg, remote_cfg, bucket, key, profile, prompt_count, version_count):
    from promptvc.sync.s3 import push as s3_push

    final_bucket = bucket or remote_cfg.get("bucket", "")
    final_key = key or remote_cfg.get("key", "promptvc/store.json")
    if not final_bucket:
        console.print("[bold red]✗[/] S3 bucket required. Pass [bold]--bucket <name>[/].")
        raise typer.Exit(1)

    try:
        s3_push(data, bucket=final_bucket, key=final_key, profile=profile)
    except Exception as e:
        console.print(f"[bold red]✗[/] Push failed: {e}")
        raise typer.Exit(1)

    cfg.setdefault("remote", {}).update(
        {"type": "s3", "bucket": final_bucket, "key": final_key}
    )
    write_config(cfg, get_promptvc_dir() / "config.toml")

    console.print(
        f"[bold green]✓[/] Pushed [bold]{prompt_count}[/] prompts "
        f"([bold]{version_count}[/] versions) to "
        f"[cyan]s3://{final_bucket}/{final_key}[/]"
    )

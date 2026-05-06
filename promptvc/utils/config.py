import sys
from pathlib import Path
from typing import Any, Dict


def _default_config() -> Dict[str, Any]:
    return {
        "core": {"environment": "dev", "author": ""},
        "defaults": {"model": "gpt-4o", "editor": ""},
        "display": {"syntax_theme": "monokai"},
    }


def read_config() -> Dict[str, Any]:
    try:
        from promptvc.db.connection import get_db_path

        config_path = get_db_path().parent / "config.toml"
        if not config_path.exists():
            return _default_config()

        if sys.version_info >= (3, 11):
            import tomllib

            with open(config_path, "rb") as f:
                return tomllib.load(f)
        else:
            import tomli

            with open(config_path, "rb") as f:
                return tomli.load(f)
    except Exception:
        return _default_config()


def write_config(config: Dict[str, Any], config_path: Path) -> None:
    lines = []
    for section, values in config.items():
        lines.append(f"[{section}]")
        for k, v in values.items():
            if isinstance(v, str):
                lines.append(f'{k} = "{v}"')
            elif isinstance(v, bool):
                lines.append(f"{k} = {str(v).lower()}")
            else:
                lines.append(f"{k} = {v}")
        lines.append("")
    config_path.write_text("\n".join(lines), encoding="utf-8")

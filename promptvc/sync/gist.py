import json
import os
from typing import Any, Dict, Optional

GIST_FILENAME = "promptvc-store.json"
GIST_API = "https://api.github.com/gists"


def _token(token: Optional[str]) -> str:
    t = token or os.environ.get("GITHUB_TOKEN", "")
    if not t:
        raise ValueError(
            "GitHub token required. Pass --token or set the GITHUB_TOKEN environment variable."
        )
    return t


def push(
    data: Dict[str, Any],
    token: Optional[str] = None,
    gist_id: Optional[str] = None,
) -> str:
    """Upload data to a private Gist. Creates one if gist_id is None. Returns gist_id."""
    import requests

    headers = {
        "Authorization": f"token {_token(token)}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "description": "promptvc shared prompt store",
        "public": False,
        "files": {GIST_FILENAME: {"content": json.dumps(data, indent=2, ensure_ascii=False)}},
    }

    if gist_id:
        resp = requests.patch(f"{GIST_API}/{gist_id}", json=payload, headers=headers, timeout=15)
    else:
        resp = requests.post(GIST_API, json=payload, headers=headers, timeout=15)

    resp.raise_for_status()
    return resp.json()["id"]


def pull(gist_id: str, token: Optional[str] = None) -> Dict[str, Any]:
    """Download and parse a Gist. gist_id may be a full URL."""
    import requests

    gist_id = gist_id.rstrip("/").split("/")[-1]
    headers = {"Accept": "application/vnd.github.v3+json"}
    t = token or os.environ.get("GITHUB_TOKEN", "")
    if t:
        headers["Authorization"] = f"token {t}"

    resp = requests.get(f"{GIST_API}/{gist_id}", headers=headers, timeout=15)
    resp.raise_for_status()

    files = resp.json().get("files", {})
    if GIST_FILENAME not in files:
        raise ValueError(
            f"Gist does not contain '{GIST_FILENAME}'. "
            "Make sure you're pointing at a promptvc Gist."
        )
    return json.loads(files[GIST_FILENAME]["content"])

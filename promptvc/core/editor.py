import os
import shutil
import subprocess
import sys
import tempfile


def _find_editor() -> str:
    editor = os.environ.get("EDITOR", "").strip()
    if editor:
        return editor

    if sys.platform == "win32":
        candidates = ["notepad"]
    else:
        candidates = ["nano", "vi", "vim"]

    for candidate in candidates:
        if shutil.which(candidate):
            return candidate

    raise RuntimeError(
        "No text editor found. Set the EDITOR environment variable "
        "(e.g. export EDITOR=nano)."
    )


def open_in_editor(initial_content: str = "") -> str:
    editor = _find_editor()

    with tempfile.NamedTemporaryFile(
        suffix=".txt", mode="w", delete=False, encoding="utf-8"
    ) as f:
        f.write(initial_content)
        tmp_path = f.name

    subprocess.call([editor, tmp_path])

    with open(tmp_path, "r", encoding="utf-8") as f:
        content = f.read()

    try:
        os.unlink(tmp_path)
    except OSError:
        pass

    return content

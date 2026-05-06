import difflib
from typing import List, Tuple


def unified_diff(old: str, new: str, old_label: str = "v_old", new_label: str = "v_new") -> str:
    old_lines = old.splitlines(keepends=True)
    new_lines = new.splitlines(keepends=True)
    diff = difflib.unified_diff(old_lines, new_lines, fromfile=old_label, tofile=new_label)
    return "".join(diff)


def side_by_side_diff(old: str, new: str) -> List[Tuple[str, str, str]]:
    """Return list of (tag, old_line, new_line) tuples for rich rendering."""
    matcher = difflib.SequenceMatcher(None, old.splitlines(), new.splitlines())
    result = []
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        old_chunk = old.splitlines()[i1:i2]
        new_chunk = new.splitlines()[j1:j2]
        max_len = max(len(old_chunk), len(new_chunk))
        for i in range(max_len):
            o = old_chunk[i] if i < len(old_chunk) else ""
            n = new_chunk[i] if i < len(new_chunk) else ""
            result.append((tag, o, n))
    return result

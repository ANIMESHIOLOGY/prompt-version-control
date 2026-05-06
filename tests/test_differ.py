from promptvc.core.differ import side_by_side_diff, unified_diff
from promptvc.core.hasher import sha256


def test_unified_diff_detects_changes() -> None:
    old = "line one\nline two\nline three\n"
    new = "line one\nline TWO\nline three\n"
    diff = unified_diff(old, new, "v1", "v2")
    assert "-line two" in diff
    assert "+line TWO" in diff


def test_unified_diff_identical_returns_empty() -> None:
    text = "same content\n"
    diff = unified_diff(text, text, "v1", "v2")
    assert diff == ""


def test_unified_diff_labels() -> None:
    diff = unified_diff("a\n", "b\n", "old_label", "new_label")
    assert "old_label" in diff
    assert "new_label" in diff


def test_side_by_side_returns_tuples() -> None:
    old = "a\nb\nc"
    new = "a\nB\nc"
    result = side_by_side_diff(old, new)
    assert isinstance(result, list)
    for item in result:
        assert len(item) == 3


def test_sha256_consistent() -> None:
    content = "hello prompt"
    assert sha256(content) == sha256(content)


def test_sha256_different_content() -> None:
    assert sha256("prompt A") != sha256("prompt B")


def test_sha256_is_hex_string() -> None:
    h = sha256("test")
    assert len(h) == 64
    assert all(c in "0123456789abcdef" for c in h)

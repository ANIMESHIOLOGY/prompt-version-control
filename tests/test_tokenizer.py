from promptvc.core.tokenizer import count_tokens


def test_returns_tuple() -> None:
    result = count_tokens("hello world")
    assert isinstance(result, tuple)
    assert len(result) == 2


def test_count_is_positive_integer() -> None:
    count, _ = count_tokens("hello world")
    assert isinstance(count, int)
    assert count > 0


def test_empty_string_zero_tokens() -> None:
    count, _ = count_tokens("")
    assert count == 0


def test_longer_text_more_tokens() -> None:
    short, _ = count_tokens("Hi.")
    long, _ = count_tokens(
        "You are a helpful assistant. Please summarize the following document "
        "in three concise sentences, preserving all key facts and dates."
    )
    assert long > short


def test_known_model_exact_count() -> None:
    count, is_exact = count_tokens("hello world", model="gpt-4o")
    assert is_exact is True
    assert count == 2


def test_unknown_model_falls_back_gracefully() -> None:
    count, _ = count_tokens("hello world this is a test", model="unknown-model-xyz-999")
    assert count > 0


def test_multiline_content() -> None:
    content = "Line one.\nLine two.\nLine three.\n"
    count, _ = count_tokens(content)
    assert count > 0


def test_different_models_same_content() -> None:
    c1, _ = count_tokens("summarize this", model="gpt-4o")
    c2, _ = count_tokens("summarize this", model="gpt-3.5-turbo")
    assert c1 > 0 and c2 > 0

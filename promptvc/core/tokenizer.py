from typing import Tuple


def count_tokens(content: str, model: str = "gpt-4o") -> Tuple[int, bool]:
    """Return (count, is_exact). is_exact=False means word-based fallback was used."""
    try:
        import tiktoken
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(content)), True
    except Exception:
        return len(content.split()), False

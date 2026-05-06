from dataclasses import dataclass
from typing import Optional


@dataclass
class Prompt:
    id: int
    name: str
    description: Optional[str]
    created_at: str
    updated_at: str


@dataclass
class Version:
    id: int
    prompt_id: int
    version_num: int
    content: str
    content_hash: str
    message: str
    environment: str
    token_count: Optional[int]
    model_hint: Optional[str]
    author: str
    created_at: str


@dataclass
class Tag:
    id: int
    version_id: int
    tag_name: str
    created_at: str

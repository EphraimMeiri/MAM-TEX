from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Note:
    kind: str
    label: str
    body: str
    target: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Event:
    kind: str
    text: str = ""
    note: Note | None = None
    meta: dict[str, Any] = field(default_factory=dict)


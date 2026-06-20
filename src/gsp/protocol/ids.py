"""Stable identifiers and object references for GSP protocol messages."""

from __future__ import annotations

from dataclasses import dataclass
import re
import uuid


_ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.:-]*$")


def validate_id(value: str) -> str:
    """Validate and return a protocol identifier."""
    if not isinstance(value, str):
        raise TypeError("protocol id must be a string")
    if not value:
        raise ValueError("protocol id must not be empty")
    if not _ID_RE.match(value):
        raise ValueError(f"invalid protocol id: {value!r}")
    return value


def new_id(prefix: str) -> str:
    """Create a stable-looking unique protocol id with a readable prefix."""
    validate_id(prefix)
    return f"{prefix}:{uuid.uuid4().hex}"


@dataclass(frozen=True, slots=True)
class ObjectRef:
    """Reference to an object owned by a GSP session."""

    kind: str
    id: str

    def __post_init__(self) -> None:
        validate_id(self.kind)
        validate_id(self.id)

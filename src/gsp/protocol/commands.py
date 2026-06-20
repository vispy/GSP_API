"""Command batch model for GSP sessions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping

from .ids import validate_id


class CommandKind(str, Enum):
    """Minimum command categories for the protocol spine."""

    INITIALIZE = "initialize"
    QUERY_CAPABILITIES = "query-capabilities"
    CREATE_RESOURCE = "create-resource"
    UPDATE_RESOURCE = "update-resource"
    CREATE_VISUAL = "create-visual"
    UPDATE_VISUAL = "update-visual"
    CREATE_TRANSFORM = "create-transform"
    UPDATE_TRANSFORM = "update-transform"
    SET_PANEL_STATE = "set-panel-state"
    SUBMIT_FRAME = "submit-frame"
    PANEL_QUERY = "panel-query"
    SHUTDOWN = "shutdown"


@dataclass(frozen=True, slots=True)
class ProtocolCommand:
    """One transport-independent protocol command."""

    kind: CommandKind
    target: str | None = None
    payload: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.target is not None:
            validate_id(self.target)


@dataclass(frozen=True, slots=True)
class CommandBatch:
    """Ordered command batch submitted to a GSP session."""

    session_id: str
    sequence: int
    commands: tuple[ProtocolCommand, ...]

    def __post_init__(self) -> None:
        validate_id(self.session_id)
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if not self.commands:
            raise ValueError("command batch must contain at least one command")

    @classmethod
    def single(cls, session_id: str, sequence: int, command: ProtocolCommand) -> "CommandBatch":
        """Create a batch containing a single command."""
        return cls(session_id=session_id, sequence=sequence, commands=(command,))

"""Transport contracts for GSP sessions."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from .capabilities import CapabilitySnapshot
from .commands import CommandBatch
from .diagnostics import Diagnostic
from .ids import validate_id


@dataclass(frozen=True, slots=True)
class InitializeResult:
    """Result returned when a protocol session is initialized."""

    session_id: str
    protocol_version: str
    capabilities: CapabilitySnapshot
    diagnostics: tuple[Diagnostic, ...] = ()

    def __post_init__(self) -> None:
        validate_id(self.session_id)
        if not self.protocol_version:
            raise ValueError("protocol_version must not be empty")
        if self.protocol_version not in self.capabilities.protocol_versions:
            raise ValueError("protocol_version must be advertised by capabilities")


class CommandStatus(str, Enum):
    """Outcome of one submitted command batch."""

    ACCEPTED = "accepted"
    REJECTED = "rejected"
    FAILED = "failed"


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Result returned after submitting a command batch."""

    sequence: int
    status: CommandStatus
    diagnostics: tuple[Diagnostic, ...] = ()
    events: tuple[object, ...] = ()
    scene_revision: int | None = None

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if not isinstance(self.status, CommandStatus):
            raise TypeError("status must be a CommandStatus")
        if self.status is not CommandStatus.ACCEPTED and not self.diagnostics:
            raise ValueError("rejected or failed command results require diagnostics")
        if self.scene_revision is not None and self.scene_revision < 0:
            raise ValueError("scene_revision must be non-negative")


class InProcessGSPServer(Protocol):
    """Minimal in-process server interface for the local fast path."""

    def initialize(self) -> InitializeResult:
        """Start or attach to a protocol session."""
        ...

    def capabilities(self) -> CapabilitySnapshot:
        """Return the current server capabilities."""
        ...

    def submit(self, batch: CommandBatch) -> CommandResult:
        """Submit a command batch without serialization."""
        ...

    def shutdown(self) -> None:
        """Close the session."""
        ...


@dataclass(slots=True)
class InProcessTransport:
    """Thin client-side wrapper around an in-process GSP server."""

    server: InProcessGSPServer
    _session_id: str | None = None
    _next_sequence: int = 0
    _closed: bool = False

    def initialize(self) -> InitializeResult:
        """Initialize the wrapped server and remember the session id."""
        if self._closed:
            raise RuntimeError("transport is closed")
        if self._session_id is not None:
            raise RuntimeError("transport is already initialized")
        result = self.server.initialize()
        self._session_id = result.session_id
        self._next_sequence = 0
        return result

    def capabilities(self) -> CapabilitySnapshot:
        """Return server capabilities."""
        if self._closed or self._session_id is None:
            raise RuntimeError("transport is not active")
        return self.server.capabilities()

    def submit(self, batch: CommandBatch) -> CommandResult:
        """Submit a batch after checking it targets the active session."""
        if self._session_id is None:
            raise RuntimeError("transport is not initialized")
        if batch.session_id != self._session_id:
            raise ValueError(f"batch session {batch.session_id!r} does not match active session {self._session_id!r}")
        if batch.sequence != self._next_sequence:
            raise ValueError(
                f"batch sequence {batch.sequence} does not match next sequence {self._next_sequence}"
            )
        result = self.server.submit(batch)
        if result.sequence != batch.sequence:
            raise RuntimeError("server result sequence does not match submitted batch")
        if result.status is CommandStatus.ACCEPTED:
            self._next_sequence += 1
        return result

    def shutdown(self) -> None:
        """Shutdown the wrapped server."""
        if self._closed:
            return
        self.server.shutdown()
        self._session_id = None
        self._closed = True

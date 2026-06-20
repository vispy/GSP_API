"""Transport contracts for GSP sessions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .capabilities import CapabilitySnapshot
from .commands import CommandBatch
from .ids import validate_id


@dataclass(frozen=True, slots=True)
class InitializeResult:
    """Result returned when a protocol session is initialized."""

    session_id: str
    capabilities: CapabilitySnapshot

    def __post_init__(self) -> None:
        validate_id(self.session_id)


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Result returned after submitting a command batch."""

    sequence: int
    accepted: bool
    diagnostics: tuple[str, ...] = ()
    events: tuple[object, ...] = ()

    def __post_init__(self) -> None:
        if self.sequence < 0:
            raise ValueError("sequence must be non-negative")
        if not self.accepted and not self.diagnostics:
            raise ValueError("rejected command results require diagnostics")


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

    def initialize(self) -> InitializeResult:
        """Initialize the wrapped server and remember the session id."""
        result = self.server.initialize()
        self._session_id = result.session_id
        return result

    def capabilities(self) -> CapabilitySnapshot:
        """Return server capabilities."""
        return self.server.capabilities()

    def submit(self, batch: CommandBatch) -> CommandResult:
        """Submit a batch after checking it targets the active session."""
        if self._session_id is None:
            raise RuntimeError("transport is not initialized")
        if batch.session_id != self._session_id:
            raise ValueError(f"batch session {batch.session_id!r} does not match active session {self._session_id!r}")
        return self.server.submit(batch)

    def shutdown(self) -> None:
        """Shutdown the wrapped server."""
        self.server.shutdown()
        self._session_id = None

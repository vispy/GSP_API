"""Capability and adaptation models for GSP servers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class TransportKind(str, Enum):
    """Known transport classes."""

    INPROC = "inproc"
    DEBUG_JSON = "debug-json"
    BINARY_IPC = "binary-ipc"
    NETWORK = "network"


class AdaptationOutcome(str, Enum):
    """How a server plans to handle a requested feature."""

    ACCEPT = "accept"
    SIMPLIFY = "simplify"
    DEACTIVATE = "deactivate"
    REJECT = "reject"


@dataclass(frozen=True, slots=True)
class AdaptationDecision:
    """Decision for one planned feature or command."""

    outcome: AdaptationOutcome
    diagnostic: str | None = None

    def __post_init__(self) -> None:
        if self.outcome != AdaptationOutcome.ACCEPT and not self.diagnostic:
            raise ValueError("non-accept adaptation decisions require a diagnostic")


@dataclass(frozen=True, slots=True)
class CapabilitySnapshot:
    """Renderer/server capabilities used before planning commands."""

    server_name: str
    protocol_versions: tuple[str, ...]
    transports: tuple[TransportKind, ...]
    buffer_dtypes: tuple[str, ...] = ()
    texture_formats: tuple[str, ...] = ()
    visual_families: tuple[str, ...] = ()
    transform_placements: tuple[str, ...] = ()
    query_modes: tuple[str, ...] = ()
    output_formats: tuple[str, ...] = ()
    extensions: tuple[str, ...] = ()
    max_buffer_bytes: int | None = None
    deterministic: bool | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.server_name:
            raise ValueError("server_name must not be empty")
        if not self.protocol_versions:
            raise ValueError("at least one protocol version is required")
        if not self.transports:
            raise ValueError("at least one transport kind is required")
        if self.max_buffer_bytes is not None and self.max_buffer_bytes < 0:
            raise ValueError("max_buffer_bytes must be non-negative")

    def supports_visual(self, family: str) -> bool:
        """Return whether a visual family is advertised."""
        return family in self.visual_families

    def supports_buffer_dtype(self, dtype: str) -> bool:
        """Return whether a buffer dtype is advertised."""
        return dtype in self.buffer_dtypes

    def adapt_visual(self, family: str) -> AdaptationDecision:
        """Return a minimal adaptation decision for a visual family."""
        if self.supports_visual(family):
            return AdaptationDecision(AdaptationOutcome.ACCEPT)
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"visual family {family!r} is not supported by {self.server_name}",
        )

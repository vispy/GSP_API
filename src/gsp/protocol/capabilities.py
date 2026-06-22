"""Capability and adaptation models for GSP servers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Iterable
from typing import Literal, TypeVar


class TransportKind(str, Enum):
    """Known transport classes."""

    INPROC = "inproc"
    DEBUG_JSON = "debug-json"
    BINARY_IPC = "binary-ipc"
    NETWORK = "network"


_T = TypeVar("_T")


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


AxisProviderStatus = Literal["strict", "adapted", "experimental", "unsupported"]
AxisProviderPolicy = Literal[
    "auto",
    "prefer_native",
    "require_native",
    "require_strict_gsp",
    "generated_primitives_only",
    "disabled",
]
AxisTickAuthority = Literal["gsp_resolved", "backend_resolved", "explicit_only"]
AxisQueryScopeRequirement = Literal["none", "data_only", "guides", "all_rendered"]


@dataclass(frozen=True, slots=True)
class AxisProviderCapability:
    """Capability declaration for one axis realization provider."""

    provider_id: str
    backend_id: str
    provider_status: AxisProviderStatus
    dimensions: tuple[str, ...] = ("x", "y")
    scales: tuple[str, ...] = ("linear",)
    supports_explicit_ticks: bool = False
    supports_auto_ticks_gsp_policy: bool = False
    supports_backend_auto_ticks: bool = False
    supports_tick_labels: bool = False
    supports_axis_labels: bool = False
    supports_title: bool = False
    supports_grid: bool = False
    supports_style_basic: bool = False
    supports_units: bool = False
    supports_datetime: bool = False
    supports_guide_query: bool = False
    supports_text_query: bool = False
    supports_visible_domain_readback: bool = False
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.provider_id:
            raise ValueError("provider_id must not be empty")
        if not self.backend_id:
            raise ValueError("backend_id must not be empty")
        if self.provider_status == "unsupported" and not self.diagnostics:
            raise ValueError("unsupported axis providers require diagnostics")
        for dimension in self.dimensions:
            if dimension not in ("x", "y"):
                raise ValueError("axis provider dimensions must be 'x' and/or 'y'")
        for scale in self.scales:
            if scale != "linear":
                raise ValueError("only linear axis scales are supported in this slice")

    @property
    def native(self) -> bool:
        """Return whether this provider is backend-native."""
        return self.provider_id in {"matplotlib.native.axes.v0", "datoviz.v04.panel_axis.wip"}


@dataclass(frozen=True, slots=True)
class AxisProviderRequest:
    """Request used to select an axis realization provider."""

    policy: AxisProviderPolicy = "auto"
    tick_authority: AxisTickAuthority = "gsp_resolved"
    query_scope_requirement: AxisQueryScopeRequirement = "none"


def select_axis_provider(
    providers: tuple[AxisProviderCapability, ...],
    request: AxisProviderRequest | None = None,
) -> AxisProviderCapability | None:
    """Select an axis provider using the small v0.2 policy surface."""
    request = request or AxisProviderRequest()
    supported = tuple(provider for provider in providers if provider.provider_status != "unsupported")
    if request.policy == "disabled":
        return None
    if request.policy == "generated_primitives_only":
        return _find_provider(supported, "gsp.reference.generated_primitives.v0")
    if request.policy == "require_native":
        return _first(provider for provider in supported if provider.native)
    if request.policy == "require_strict_gsp":
        return _first(provider for provider in supported if provider.provider_status == "strict")
    if request.policy == "prefer_native":
        native = _first(provider for provider in supported if provider.native)
        return native or _first(iter(supported))
    return _first(iter(supported))


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
    supports_extension_manifests: bool = False
    supports_virtual_data_sources: bool = False
    supports_tiled_image_sources: bool = False
    supports_in_memory_data_sources: bool = False
    supports_synthetic_data_sources: bool = False
    supports_local_file_data_sources: bool = False
    supports_client_fetch_data_sources: bool = False
    supports_server_fetch_data_sources: bool = False
    supports_remote_handle_data_sources: bool = False
    max_tiles_per_request: int = 0
    max_mosaic_pixels: int = 0
    max_buffer_bytes: int | None = None
    deterministic: bool | None = None
    axis_providers: tuple[AxisProviderCapability, ...] = ()
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
        if self.max_tiles_per_request < 0:
            raise ValueError("max_tiles_per_request must be non-negative")
        if self.max_mosaic_pixels < 0:
            raise ValueError("max_mosaic_pixels must be non-negative")

    def supports_visual(self, family: str) -> bool:
        """Return whether a visual family is advertised."""
        return family in self.visual_families

    def supports_buffer_dtype(self, dtype: str) -> bool:
        """Return whether a buffer dtype is advertised."""
        return dtype in self.buffer_dtypes

    def supports_query_mode(self, mode: str) -> bool:
        """Return whether a query/readback mode is advertised."""
        return mode in self.query_modes

    def supports_extension(self, extension: str) -> bool:
        """Return whether an extension capability is advertised."""
        return extension in self.extensions

    def axis_provider(self, provider_id: str) -> AxisProviderCapability | None:
        """Return an advertised axis provider by id."""
        return _find_provider(self.axis_providers, provider_id)

    def select_axis_provider(self, request: AxisProviderRequest | None = None) -> AxisProviderCapability | None:
        """Select an advertised axis provider."""
        return select_axis_provider(self.axis_providers, request)

    def adapt_visual(self, family: str) -> AdaptationDecision:
        """Return a minimal adaptation decision for a visual family."""
        if self.supports_visual(family):
            return AdaptationDecision(AdaptationOutcome.ACCEPT)
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"visual family {family!r} is not supported by {self.server_name}",
        )

    def adapt_query_mode(self, mode: str) -> AdaptationDecision:
        """Return a minimal adaptation decision for a query/readback mode."""
        if self.supports_query_mode(mode):
            return AdaptationDecision(AdaptationOutcome.ACCEPT)
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"query mode {mode!r} is not supported by {self.server_name}",
        )

    def adapt_extension(self, extension: str) -> AdaptationDecision:
        """Return a minimal adaptation decision for an extension capability."""
        if self.supports_extension(extension):
            return AdaptationDecision(AdaptationOutcome.ACCEPT)
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"extension {extension!r} is not supported by {self.server_name}",
        )


def _find_provider(providers: tuple[AxisProviderCapability, ...], provider_id: str) -> AxisProviderCapability | None:
    return _first(provider for provider in providers if provider.provider_id == provider_id)


def _first(items: Iterable[_T]) -> _T | None:
    for item in items:
        return item
    return None

"""Capability and adaptation models for GSP servers."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from collections.abc import Iterable
from typing import Literal, TypeVar

from .extensions import ExtensionManifest, validate_extension_manifest
from .query import QueryCoordinateSpace, QueryHitPolicy, QueryPayload, QueryRequest, QueryScope


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


class QueryOrderingGuarantee(str, Enum):
    """Ordering guarantees for query hits within or across scopes."""

    NONE = "none"
    SCOPE_RENDER_ORDER = "scope-render-order"
    GLOBAL_RENDER_ORDER = "global-render-order"


class QueryTargetKind(str, Enum):
    """Kind of target covered by one query capability entry."""

    VISUAL_FAMILY = "visual-family"
    GUIDE_ROLE = "guide-role"
    EXTENSION_VISUAL = "extension-visual"


@dataclass(frozen=True, slots=True)
class QueryTargetCapability:
    """Capability for querying one visual family, guide role, or extension target."""

    target_kind: QueryTargetKind
    target: str
    payloads: tuple[QueryPayload, ...] = ()
    payload_sets: tuple[tuple[QueryPayload, ...], ...] = ()
    extension_payload_kinds: tuple[str, ...] = ()
    supports_text_query: bool = False
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.target:
            raise ValueError("query target must not be empty")
        for payload_set in self.payload_sets:
            if not payload_set:
                raise ValueError("query payload_sets must not contain empty sets")
        for kind in self.extension_payload_kinds:
            if not kind:
                raise ValueError("extension payload kinds must not be empty")

    def supports_payloads(self, requested: tuple[QueryPayload, ...]) -> bool:
        """Return whether this target supports the requested applicable payloads."""
        if not requested:
            return True
        requested_set = set(requested)
        if self.payload_sets:
            return any(requested_set.issubset(set(payload_set)) for payload_set in self.payload_sets)
        if self.payloads:
            return requested_set.issubset(set(self.payloads))
        return True

    def supports_extension_payloads(self, requested: tuple[str, ...]) -> bool:
        """Return whether this target supports all requested extension payload kinds."""
        return set(requested).issubset(set(self.extension_payload_kinds))


@dataclass(frozen=True, slots=True)
class QueryScopeCapability:
    """Capability for querying a contribution scope."""

    scope: QueryScope
    coordinate_spaces: tuple[QueryCoordinateSpace, ...] = (QueryCoordinateSpace.PANEL, QueryCoordinateSpace.DATA)
    hit_policies: tuple[QueryHitPolicy, ...] = (QueryHitPolicy.FRONTMOST,)
    targets: tuple[QueryTargetCapability, ...] = ()
    ordering: QueryOrderingGuarantee = QueryOrderingGuarantee.NONE
    definitive_miss: bool = True
    provider_ids: tuple[str, ...] = ()
    diagnostics: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.coordinate_spaces:
            raise ValueError("query scope capability requires at least one coordinate space")
        if not self.hit_policies:
            raise ValueError("query scope capability requires at least one hit policy")
        for provider_id in self.provider_ids:
            if not provider_id:
                raise ValueError("query provider ids must not be empty")

    def supports_request(self, request: QueryRequest) -> AdaptationDecision:
        """Return whether this scope capability can satisfy a query request."""
        if request.scope != self.scope:
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                f"query scope {request.scope.value!r} is not covered by {self.scope.value!r}",
            )
        if request.coordinate_space not in self.coordinate_spaces:
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                f"query coordinate space {request.coordinate_space.value!r} is not supported for scope {self.scope.value!r}",
            )
        if request.hit_policy not in self.hit_policies:
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                f"query hit policy {request.hit_policy.value!r} is not supported for scope {self.scope.value!r}",
            )
        if request.hit_policy == QueryHitPolicy.ALL and self.ordering == QueryOrderingGuarantee.NONE:
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                f"query hit policy 'all' requires an ordering guarantee for scope {self.scope.value!r}",
            )
        if request.scope == QueryScope.ALL_RENDERED and self.ordering != QueryOrderingGuarantee.GLOBAL_RENDER_ORDER:
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                "query scope 'all-rendered' requires a global render-order guarantee",
            )
        unsupported_targets = tuple(
            target
            for target in self.targets
            if not target.supports_payloads(request.requested_payload)
            or not target.supports_extension_payloads(request.requested_extension_payload_kinds)
        )
        if unsupported_targets:
            target = unsupported_targets[0]
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                f"query target {target.target!r} cannot satisfy requested payloads for scope {self.scope.value!r}",
            )
        return AdaptationDecision(AdaptationOutcome.ACCEPT)


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


@dataclass(frozen=True, slots=True)
class QueryPlanningContext:
    """Scene/provider context needed to validate a query request."""

    selected_axis_provider: "AxisProviderCapability | None" = None
    guides_visible: bool = False
    text_query_required: bool = False


def query_scope_for_axis_requirement(requirement: AxisQueryScopeRequirement) -> QueryScope | None:
    """Map axis-provider query requirements to the unified query scope model."""
    if requirement == "none":
        return None
    if requirement == "data_only":
        return QueryScope.DATA
    if requirement == "guides":
        return QueryScope.GUIDES
    if requirement == "all_rendered":
        return QueryScope.ALL_RENDERED
    raise ValueError(f"unknown axis query scope requirement: {requirement!r}")


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
    query_capabilities: tuple[QueryScopeCapability, ...] = ()
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
    supported_data_source_localities: tuple[str, ...] = ()
    supported_credential_policies: tuple[str, ...] = ()
    supports_remote_fetch_descriptors: bool = False
    supports_server_side_fetch: bool = False
    supports_dynamic_extension_loading: bool = False
    supports_package_entry_points: bool = False
    supports_executable_extension_hooks: bool = False
    supports_custom_decoders: bool = False
    supports_runtime_shaders: bool = False
    cache_modes: tuple[str, ...] = ()
    security_redaction_profile: str | None = "gsp.s020.no-network"
    diagnostic_redaction: bool = True
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
        if not self.diagnostic_redaction:
            raise ValueError("S020 capability snapshots require diagnostic redaction")
        if self.supports_dynamic_extension_loading:
            raise ValueError("dynamic extension loading is not supported in S020")

    def supports_visual(self, family: str) -> bool:
        """Return whether a visual family is advertised."""
        return family in self.visual_families

    def supports_buffer_dtype(self, dtype: str) -> bool:
        """Return whether a buffer dtype is advertised."""
        return dtype in self.buffer_dtypes

    def supports_query_mode(self, mode: str) -> bool:
        """Return whether a query/readback mode is advertised."""
        return mode in self.query_modes

    def query_capability(self, scope: QueryScope) -> QueryScopeCapability | None:
        """Return an advertised typed query capability by scope."""
        return _first(capability for capability in self.query_capabilities if capability.scope == scope)

    def supports_query_scope(self, scope: QueryScope) -> bool:
        """Return whether a typed query scope is advertised."""
        return self.query_capability(scope) is not None

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

    def adapt_query_request(self, request: QueryRequest) -> AdaptationDecision:
        """Return an adaptation decision for a typed query request."""
        capability = self.query_capability(request.scope)
        if capability is None:
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                f"query scope {request.scope.value!r} is not supported by {self.server_name}",
            )
        return capability.supports_request(request)

    def adapt_query_request_for_scene(
        self,
        request: QueryRequest,
        context: QueryPlanningContext | None = None,
    ) -> AdaptationDecision:
        """Return a query decision after composing scene/provider constraints."""
        decision = self.adapt_query_request(request)
        if decision.outcome != AdaptationOutcome.ACCEPT:
            return decision

        context = context or QueryPlanningContext()
        if request.scope == QueryScope.GUIDES:
            return _adapt_guide_query_provider(request, context)
        if request.scope == QueryScope.ALL_RENDERED and context.guides_visible:
            return _adapt_guide_query_provider(request, context)
        return decision

    def adapt_extension(self, extension: str) -> AdaptationDecision:
        """Return a minimal adaptation decision for an extension capability."""
        if self.supports_extension(extension):
            return AdaptationDecision(AdaptationOutcome.ACCEPT)
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"extension {extension!r} is not supported by {self.server_name}",
        )

    def adapt_extension_manifest(self, manifest: ExtensionManifest) -> AdaptationDecision:
        """Return an adaptation decision for a static extension manifest."""
        try:
            validate_extension_manifest(manifest)
        except ValueError as exc:
            return AdaptationDecision(AdaptationOutcome.REJECT, str(exc))
        if not self.supports_extension_manifests:
            return AdaptationDecision(
                AdaptationOutcome.REJECT,
                f"extension manifests are not supported by {self.server_name}",
            )
        return self.adapt_extension(manifest.capability)


def _find_provider(providers: tuple[AxisProviderCapability, ...], provider_id: str) -> AxisProviderCapability | None:
    return _first(provider for provider in providers if provider.provider_id == provider_id)


def _first(items: Iterable[_T]) -> _T | None:
    for item in items:
        return item
    return None


def _adapt_guide_query_provider(request: QueryRequest, context: QueryPlanningContext) -> AdaptationDecision:
    provider = context.selected_axis_provider
    if provider is None:
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"query scope {request.scope.value!r} requires a selected axis provider for guide contributions",
        )
    if not provider.supports_guide_query:
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"query scope {request.scope.value!r} requires guide query support from axis provider {provider.provider_id!r}",
        )
    if context.text_query_required and not provider.supports_text_query:
        return AdaptationDecision(
            AdaptationOutcome.REJECT,
            f"query scope {request.scope.value!r} requires text query support from axis provider {provider.provider_id!r}",
        )
    return AdaptationDecision(AdaptationOutcome.ACCEPT)

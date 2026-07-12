"""Tests for the initial GSP protocol spine."""

import pytest

from gsp.protocol import (
    AdaptationOutcome,
    BufferResource,
    CapabilitySnapshot,
    CommandBatch,
    CommandKind,
    CommandResult,
    CommandStatus,
    Diagnostic,
    DiagnosticCategory,
    DiagnosticSeverity,
    InitializeResult,
    InProcessTransport,
    ProtocolCommand,
    PROTOCOL_VERSION,
    AxisProviderCapability,
    QueryPlanningContext,
    QueryHitPolicy,
    QueryOrderingGuarantee,
    QueryPayload,
    QueryRequest,
    QueryScope,
    QueryScopeCapability,
    QueryTargetCapability,
    QueryTargetKind,
    TILED_IMAGE_QUERY_PAYLOAD_KIND,
    ResourceUsage,
    TransportKind,
    new_id,
    validate_id,
    query_scope_for_axis_requirement,
)


def test_validate_id_rejects_invalid_values():
    """Protocol IDs are intentionally narrower than arbitrary strings."""
    assert validate_id("buffer:abc_123") == "buffer:abc_123"

    with pytest.raises(ValueError):
        validate_id("")

    with pytest.raises(ValueError):
        validate_id("1starts-with-number")

    assert PROTOCOL_VERSION == "0.2"


def test_new_id_uses_readable_prefix():
    """Generated IDs keep their object-family prefix."""
    generated = new_id("buffer")

    assert generated.startswith("buffer:")
    assert validate_id(generated) == generated


def test_capability_snapshot_adaptation_decision():
    """Unsupported behavior produces an explicit diagnostic."""
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32",),
        visual_families=("point",),
    )

    assert caps.supports_visual("point")
    assert caps.adapt_visual("point").outcome == AdaptationOutcome.ACCEPT

    rejected = caps.adapt_visual("image")
    assert rejected.outcome == AdaptationOutcome.REJECT
    assert rejected.diagnostic is not None
    assert caps.snapshot_id.startswith("capabilities:")
    assert caps.snapshot_id == CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        buffer_dtypes=("float32",),
        visual_families=("point",),
    ).snapshot_id


def test_structured_diagnostic_and_command_result_invariants():
    diagnostic = Diagnostic(
        code="protocol.sequence.invalid",
        severity=DiagnosticSeverity.ERROR,
        category=DiagnosticCategory.VALIDATION,
        message="sequence is invalid",
        operation_id="command:test",
        data={"expected": 1, "actual": 2},
    )
    rejected = CommandResult(
        sequence=2,
        status=CommandStatus.REJECTED,
        diagnostics=(diagnostic,),
    )
    assert rejected.status is CommandStatus.REJECTED
    assert rejected.diagnostics[0].code == "protocol.sequence.invalid"

    with pytest.raises(ValueError, match="require diagnostics"):
        CommandResult(sequence=2, status=CommandStatus.FAILED)

    with pytest.raises(ValueError, match="no whitespace"):
        Diagnostic(
            code="bad code",
            severity=DiagnosticSeverity.ERROR,
            category=DiagnosticCategory.VALIDATION,
            message="invalid",
        )


def test_capability_snapshot_query_mode_adaptation_decision():
    """Query support is advertised explicitly and rejects unsupported modes."""
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_modes=("panel-query", "point-item"),
    )

    assert caps.supports_query_mode("panel-query")
    assert caps.adapt_query_mode("point-item").outcome == AdaptationOutcome.ACCEPT

    rejected = caps.adapt_query_mode("image-texel")
    assert rejected.outcome == AdaptationOutcome.REJECT
    assert rejected.diagnostic is not None


def test_typed_query_capability_accepts_matching_request():
    """Typed query capabilities are the protocol-authoritative query planning surface."""
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_modes=("panel-query",),
        query_capabilities=(
            QueryScopeCapability(
                scope=QueryScope.DATA,
                hit_policies=(QueryHitPolicy.FRONTMOST, QueryHitPolicy.ALL),
                ordering=QueryOrderingGuarantee.SCOPE_RENDER_ORDER,
                targets=(
                    QueryTargetCapability(
                        target_kind=QueryTargetKind.VISUAL_FAMILY,
                        target="point",
                        payloads=(QueryPayload.IDENTITY, QueryPayload.COORDINATE, QueryPayload.COLOR),
                    ),
                ),
            ),
        ),
    )

    request = QueryRequest(
        id="query:points",
        panel_id="panel:main",
        coordinate=(0.0, 0.0),
        hit_policy=QueryHitPolicy.ALL,
        requested_payload=(QueryPayload.IDENTITY, QueryPayload.COLOR),
    )

    assert caps.supports_query_scope(QueryScope.DATA)
    assert caps.adapt_query_request(request).outcome == AdaptationOutcome.ACCEPT
    assert caps.supports_query_mode("panel-query")


def test_typed_query_capability_rejects_missing_scope_and_does_not_infer_all_rendered():
    """All-rendered must be explicitly advertised, not inferred from data plus guides."""
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(
            QueryScopeCapability(scope=QueryScope.DATA),
            QueryScopeCapability(scope=QueryScope.GUIDES),
        ),
    )

    rejected = caps.adapt_query_request(
        QueryRequest(id="query:all-rendered", panel_id="panel:main", coordinate=(0.0, 0.0), scope=QueryScope.ALL_RENDERED)
    )

    assert rejected.outcome == AdaptationOutcome.REJECT
    assert "all-rendered" in rejected.diagnostic


def test_typed_query_capability_rejects_unsupported_payload_and_extension_payload():
    """Requested payloads and extension payload kinds are required when present."""
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(
            QueryScopeCapability(
                scope=QueryScope.DATA,
                targets=(
                    QueryTargetCapability(
                        target_kind=QueryTargetKind.EXTENSION_VISUAL,
                        target="gsp.tiled-image",
                        payloads=(QueryPayload.IDENTITY, QueryPayload.COORDINATE),
                        extension_payload_kinds=(TILED_IMAGE_QUERY_PAYLOAD_KIND,),
                    ),
                ),
            ),
        ),
    )

    value_rejected = caps.adapt_query_request(
        QueryRequest(
            id="query:value",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            requested_payload=(QueryPayload.IDENTITY, QueryPayload.VALUE),
        )
    )
    extension_rejected = caps.adapt_query_request(
        QueryRequest(
            id="query:extension",
            panel_id="panel:main",
            coordinate=(0.0, 0.0),
            requested_extension_payload_kinds=("other-extension@0.1",),
        )
    )

    assert value_rejected.outcome == AdaptationOutcome.REJECT
    assert extension_rejected.outcome == AdaptationOutcome.REJECT


def test_all_rendered_query_capability_requires_global_ordering():
    """All-rendered support needs the strict global ordering guarantee."""
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(
            QueryScopeCapability(
                scope=QueryScope.ALL_RENDERED,
                ordering=QueryOrderingGuarantee.SCOPE_RENDER_ORDER,
            ),
        ),
    )

    rejected = caps.adapt_query_request(
        QueryRequest(id="query:all-rendered", panel_id="panel:main", coordinate=(0.0, 0.0), scope=QueryScope.ALL_RENDERED)
    )

    assert rejected.outcome == AdaptationOutcome.REJECT
    assert "global render-order" in rejected.diagnostic


def test_axis_query_scope_requirement_maps_to_query_scope():
    assert query_scope_for_axis_requirement("none") is None
    assert query_scope_for_axis_requirement("data_only") == QueryScope.DATA
    assert query_scope_for_axis_requirement("guides") == QueryScope.GUIDES
    assert query_scope_for_axis_requirement("all_rendered") == QueryScope.ALL_RENDERED


def test_query_planning_allows_data_scope_with_non_queryable_guides():
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(QueryScopeCapability(scope=QueryScope.DATA),),
    )
    provider = AxisProviderCapability(
        provider_id="datoviz.v04.panel_axis.wip",
        backend_id="datoviz",
        provider_status="adapted",
        supports_guide_query=False,
    )

    decision = caps.adapt_query_request_for_scene(
        QueryRequest(id="query:data", panel_id="panel:main", coordinate=(0.0, 0.0)),
        QueryPlanningContext(selected_axis_provider=provider, guides_visible=True),
    )

    assert decision.outcome == AdaptationOutcome.ACCEPT


def test_query_planning_rejects_guides_scope_with_non_queryable_axis_provider():
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(QueryScopeCapability(scope=QueryScope.GUIDES),),
    )
    provider = AxisProviderCapability(
        provider_id="datoviz.v04.panel_axis.wip",
        backend_id="datoviz",
        provider_status="adapted",
        supports_guide_query=False,
    )

    decision = caps.adapt_query_request_for_scene(
        QueryRequest(id="query:guides", panel_id="panel:main", coordinate=(0.0, 0.0), scope=QueryScope.GUIDES),
        QueryPlanningContext(selected_axis_provider=provider, guides_visible=True),
    )

    assert decision.outcome == AdaptationOutcome.REJECT
    assert "guide query support" in decision.diagnostic
    assert "datoviz.v04.panel_axis.wip" in decision.diagnostic


def test_query_planning_rejects_all_rendered_when_visible_guides_are_not_queryable():
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(
            QueryScopeCapability(
                scope=QueryScope.ALL_RENDERED,
                ordering=QueryOrderingGuarantee.GLOBAL_RENDER_ORDER,
            ),
        ),
    )
    provider = AxisProviderCapability(
        provider_id="datoviz.v04.panel_axis.wip",
        backend_id="datoviz",
        provider_status="adapted",
        supports_guide_query=False,
    )

    decision = caps.adapt_query_request_for_scene(
        QueryRequest(id="query:all-rendered", panel_id="panel:main", coordinate=(0.0, 0.0), scope=QueryScope.ALL_RENDERED),
        QueryPlanningContext(selected_axis_provider=provider, guides_visible=True),
    )

    assert decision.outcome == AdaptationOutcome.REJECT
    assert "guide query support" in decision.diagnostic


def test_query_planning_accepts_guides_scope_with_queryable_axis_provider():
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(QueryScopeCapability(scope=QueryScope.GUIDES),),
    )
    provider = AxisProviderCapability(
        provider_id="matplotlib.native.axes.v0",
        backend_id="matplotlib",
        provider_status="strict",
        supports_guide_query=True,
        supports_text_query=True,
    )

    decision = caps.adapt_query_request_for_scene(
        QueryRequest(id="query:guides", panel_id="panel:main", coordinate=(0.0, 0.0), scope=QueryScope.GUIDES),
        QueryPlanningContext(selected_axis_provider=provider, guides_visible=True, text_query_required=True),
    )

    assert decision.outcome == AdaptationOutcome.ACCEPT


def test_query_planning_rejects_text_query_when_axis_provider_lacks_text_query():
    caps = CapabilitySnapshot(
        server_name="test-server",
        protocol_versions=("0.1",),
        transports=(TransportKind.INPROC,),
        query_capabilities=(QueryScopeCapability(scope=QueryScope.GUIDES),),
    )
    provider = AxisProviderCapability(
        provider_id="matplotlib.native.axes.v0",
        backend_id="matplotlib",
        provider_status="strict",
        supports_guide_query=True,
        supports_text_query=False,
    )

    decision = caps.adapt_query_request_for_scene(
        QueryRequest(id="query:guides", panel_id="panel:main", coordinate=(0.0, 0.0), scope=QueryScope.GUIDES),
        QueryPlanningContext(selected_axis_provider=provider, text_query_required=True),
    )

    assert decision.outcome == AdaptationOutcome.REJECT
    assert "text query support" in decision.diagnostic


def test_buffer_resource_can_hold_memoryview_without_serialization():
    """The in-process path can carry direct memory without JSON/base64."""
    payload = bytearray(12)
    resource = BufferResource(
        id="buffer:positions",
        dtype="float32",
        shape=(3,),
        byte_length=12,
        usage=(ResourceUsage.ATTRIBUTE,),
        data=memoryview(payload),
    )

    assert resource.data is not None
    assert resource.data.obj is payload


def test_buffer_resource_rejects_non_contiguous_v0_1_buffers():
    """M002 deliberately keeps the first resource model contiguous-only."""
    with pytest.raises(ValueError, match="contiguous"):
        BufferResource(
            id="buffer:strided",
            dtype="float32",
            shape=(3,),
            byte_length=12,
            usage=(ResourceUsage.ATTRIBUTE,),
            contiguous=False,
        )


def test_command_batch_validation_and_single_helper():
    """Command batches are ordered and tied to a session."""
    command = ProtocolCommand(CommandKind.CREATE_RESOURCE, target="buffer:positions", payload={"dtype": "float32"})
    batch = CommandBatch.single("session:test", 7, command)

    assert batch.session_id == "session:test"
    assert batch.sequence == 7
    assert batch.commands == (command,)

    with pytest.raises(ValueError):
        CommandBatch("session:test", -1, (command,))

    with pytest.raises(ValueError):
        CommandBatch("session:test", 0, ())


class _FakeInProcessServer:
    def __init__(self):
        self.submitted: list[CommandBatch] = []
        self.closed = False
        self._capabilities = CapabilitySnapshot(
            server_name="fake",
            protocol_versions=("0.1",),
            transports=(TransportKind.INPROC,),
        )

    def initialize(self):
        return InitializeResult(
            session_id="session:fake",
            protocol_version="0.1",
            capabilities=self._capabilities,
        )

    def capabilities(self):
        return self._capabilities

    def submit(self, batch):
        self.submitted.append(batch)
        return CommandResult(sequence=batch.sequence, status=CommandStatus.ACCEPTED)

    def shutdown(self):
        self.closed = True


def test_inprocess_transport_checks_session_and_forwards_batch():
    """The transport wrapper enforces session identity before forwarding."""
    server = _FakeInProcessServer()
    transport = InProcessTransport(server)

    with pytest.raises(RuntimeError):
        transport.submit(CommandBatch.single("session:fake", 0, ProtocolCommand(CommandKind.QUERY_CAPABILITIES)))

    initialized = transport.initialize()
    assert initialized.session_id == "session:fake"

    batch = CommandBatch.single("session:fake", 0, ProtocolCommand(CommandKind.QUERY_CAPABILITIES))
    result = transport.submit(batch)

    assert result.status is CommandStatus.ACCEPTED
    assert server.submitted == [batch]

    with pytest.raises(ValueError, match="next sequence"):
        transport.submit(batch)

    with pytest.raises(ValueError, match="does not match"):
        transport.submit(CommandBatch.single("session:other", 2, ProtocolCommand(CommandKind.QUERY_CAPABILITIES)))

    transport.shutdown()
    assert server.closed

    transport.shutdown()
    with pytest.raises(RuntimeError, match="closed"):
        transport.initialize()

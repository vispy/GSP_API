"""Tests for the initial GSP protocol spine."""

import pytest

from gsp.protocol import (
    AdaptationOutcome,
    BufferResource,
    CapabilitySnapshot,
    CommandBatch,
    CommandKind,
    CommandResult,
    InitializeResult,
    InProcessTransport,
    ProtocolCommand,
    ResourceUsage,
    TransportKind,
    new_id,
    validate_id,
)


def test_validate_id_rejects_invalid_values():
    """Protocol IDs are intentionally narrower than arbitrary strings."""
    assert validate_id("buffer:abc_123") == "buffer:abc_123"

    with pytest.raises(ValueError):
        validate_id("")

    with pytest.raises(ValueError):
        validate_id("1starts-with-number")


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
        return InitializeResult(session_id="session:fake", capabilities=self._capabilities)

    def capabilities(self):
        return self._capabilities

    def submit(self, batch):
        self.submitted.append(batch)
        return CommandResult(sequence=batch.sequence, accepted=True)

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

    batch = CommandBatch.single("session:fake", 1, ProtocolCommand(CommandKind.QUERY_CAPABILITIES))
    result = transport.submit(batch)

    assert result.accepted
    assert server.submitted == [batch]

    with pytest.raises(ValueError, match="does not match"):
        transport.submit(CommandBatch.single("session:other", 2, ProtocolCommand(CommandKind.QUERY_CAPABILITIES)))

    transport.shutdown()
    assert server.closed

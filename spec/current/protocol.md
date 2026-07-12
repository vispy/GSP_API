# Protocol lifecycle

This chapter defines the transport-independent GSP 0.2 execution lifecycle. Python classes are one
binding of these records; their module layout is not protocol semantics.

## Version and compatibility

The protocol version is the pair `(major, minor)`. GSP 0.2 has major `0` and minor `2`.

| Rule | Requirement |
|---|---|
| `GSP-LIFE-001` | Initialization must negotiate one version supported by both peers before any state-changing command executes. |
| `GSP-LIFE-002` | A peer must reject an unknown major version. During major `0`, a minor-version change may be breaking and must be identified explicitly in release and migration records. |
| `GSP-LIFE-003` | Capabilities refine a negotiated version; they never silently change the meaning of an accepted field. |

## Roles

A **producer** submits operations. A **GSP server** owns session state and executes accepted operations through a backend adapter. A **transport** connects them without changing protocol meaning.

## Initialization

Initialization must return a validated session identifier and a `CapabilitySnapshot`. All subsequent command batches must target that active session.

```python
result = transport.initialize()
session_id = result.session_id
capabilities = result.capabilities
```

### Initialize request

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `client_name` | non-empty string | yes | Diagnostic identity of the producer. |
| `protocol_versions` | ordered tuple of version strings | yes | Versions acceptable to the producer, most preferred first. |
| `transport` | transport identifier | yes | Active exchange profile. |
| `requested_extensions` | tuple of extension IDs | no | Extensions requested for negotiation; default empty. |
| `metadata` | string-keyed JSON-compatible map | no | Non-semantic diagnostic metadata; default empty. |

### Initialize result

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `session_id` | validated identifier | yes | New active session identity. |
| `protocol_version` | version string | yes | Negotiated version. |
| `capabilities` | `CapabilitySnapshot` | yes | Immutable initial support envelope. |
| `diagnostics` | tuple of structured diagnostics | no | Negotiation notices; default empty. |

`GSP-LIFE-004`: initialization must be atomic. Failure creates no usable session and returns or
raises a structured initialization error. A successful result establishes sequence number zero as
the first valid submitted batch sequence unless the transport profile specifies an equivalent
explicit starting sequence.

## Session state machine

```text
NEW --initialize--> ACTIVE --shutdown--> CLOSED
 |                     |                    |
 +------failure------> FAILED <---fatal-----+
```

| State | Permitted operations |
|---|---|
| `NEW` | initialize only |
| `ACTIVE` | capability query, command submission, frame execution, query, shutdown |
| `CLOSED` | idempotent close inspection only; no submission |
| `FAILED` | diagnostic inspection and cleanup only |

`GSP-LIFE-005`: operations invalid for the current state must fail before backend execution.
Closing an already closed owner is idempotent. Submission, polling, query, or update after close is
an error rather than a successful no-op.

## Commands and batches

A `ProtocolCommand` has a `kind`, optional target identifier, and typed or structured payload. Accepted command categories include initialization, capability queries, resource and visual creation or update, transform state, panel state, frame submission, panel queries, and shutdown.

### Command record

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `kind` | registered command kind | yes | Operation semantics. |
| `target` | identifier or null | command-specific | Entity addressed by the operation. |
| `payload` | command-specific typed record | yes | Parameters validated for `kind`. Empty only when that command schema permits it. |

The core command kinds are registered in [Registries](registries.md). Unknown core kinds are
invalid. Extension command kinds require a negotiated extension manifest.

A `CommandBatch` must:

- carry one valid session identifier;
- have a non-negative sequence number;
- contain at least one command;
- preserve command order.

`GSP-LIFE-006`: sequence numbers are strictly increasing per session. Duplicate, decreasing, or
skipped sequences are rejected unless a negotiated transport profile defines replay semantics for
the exact case. Rejection does not advance the accepted sequence.

`GSP-LIFE-007`: validation covers the complete batch before its first externally visible mutation.
The default batch failure mode is atomic rejection. An implementation that supports partial batch
commit must advertise a separate capability and return per-command commit state; no such core GSP
0.2 capability is accepted.

The server must reject a batch for another session. A rejected `CommandResult` must include diagnostics; rejection must not be encoded as a successful no-op.

### Command result

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `sequence` | non-negative integer | yes | Sequence being acknowledged. |
| `status` | `accepted`, `rejected`, or `failed` | yes | Validation/planning/execution outcome. |
| `diagnostics` | tuple of `Diagnostic` | yes | Empty only for an accepted result with no notices. |
| `events` | tuple of typed events | no | Events emitted by accepted execution; default empty. |
| `scene_revision` | non-negative integer or null | no | Accepted scene revision after commit. |

`accepted` means the semantic operation committed. `rejected` means validation or capability
planning prevented execution. `failed` means execution began but the adapter/backend could not
complete it. Backend crashes and timeouts are failures, never unsupported results.

## Execution

Scene mutations establish semantic state. A frame operation requests execution or presentation of that state. Rendering must not silently reinterpret unsupported fields. Implementations may lower records eagerly or retain them internally, provided advertised semantics remain stable.

`GSP-LIFE-008`: accepted scene mutations increment a monotonic scene revision. A submitted frame
binds one scene revision, view revision set, resource revision set, capability snapshot ID, and
resolved layout snapshot where applicable. Results and queries derived from that frame report the
corresponding snapshot identities.

### Frame submission

| Field | Type | Required | Meaning |
|---|---|---:|---|
| `frame_id` | validated identifier | yes | Producer identity for this frame request. |
| `scene_revision` | non-negative integer | yes | Exact semantic state to execute. |
| `presentation` | `display`, `offscreen`, or `none` | yes | Requested operation class. |
| `output` | output descriptor or null | operation-specific | Size, format, and destination intent. |
| `deadline_ms` | positive finite number or null | no | Advisory deadline; not permission for partial semantics. |

An implementation may coalesce intermediate frames only when the producer requested a replaceable
presentation policy. Queries and readbacks tied to a frame are never silently redirected to a newer
frame.

## Shutdown

Shutdown closes the active session and releases its session-scoped state. Further submission requires a new initialization.

`GSP-LIFE-009`: shutdown is ordered after all previously accepted commands. The shutdown result
states whether pending work completed, was cancelled under an advertised policy, or failed.

`GSP-LIFE-010`: cleanup is deterministic and idempotent at the protocol-owner boundary. Backend
objects, windows, devices, callbacks, and event-loop handles are adapter-private and must not leak
through producer records.

## Failure taxonomy

| Failure class | Required result |
|---|---|
| Invalid record or state | rejected with validation diagnostic |
| Missing capability | rejected or explicitly deactivated during planning |
| Declared semantic approximation | accepted with adaptation diagnostic |
| Backend/API failure | failed with backend-execution diagnostic |
| Timeout or native signal | failed; never reclassified as unsupported |
| Stale snapshot | stale query/result or rejected mutation, as defined by the operation |

All diagnostics use the schema in [Capabilities and diagnostics](capabilities.md) and stable codes
from [Registries](registries.md).

!!! note "Current implementation boundary"
    The Python package implements these records and the in-process transport contract. It does not yet ship a complete Matplotlib or Datoviz server that executes every command category end to end.

# Transports and extensions

## Encoding independence

Protocol meaning is independent of transport and encoding. All transports preserve command order, identifiers, resource metadata, result states, diagnostics, and capability negotiation.

| Rule | Requirement |
|---|---|
| `GSP-XPORT-001` | A transport preserves record types, field values, ordering, identities, numeric meaning, result states, and diagnostics. |
| `GSP-XPORT-002` | Transport success only means exchange succeeded; it does not convert a rejected or failed protocol result into success. |
| `GSP-XPORT-003` | Size, timeout, authentication, and backpressure policies are explicit transport/profile limits. |

## In-process transport

`InProcessTransport` forwards native `CommandBatch` objects to an `InProcessGSPServer`. It may carry NumPy and memory-view-compatible payloads without mandatory serialization. This avoids mandatory JSON/base64 overhead but does not, by itself, guarantee zero-copy behavior.

### In-process ownership

The producer retains its local objects. The server accepts semantic values under documented copy or
borrow rules. Borrowed memory declares lifetime and immutability requirements; absent such a profile,
the server may copy.

`GSP-XPORT-004`: the in-process boundary performs the same validation, capability planning,
sequencing, diagnostics, and state transitions as any other transport. Direct calls are not a bypass.

## Debug JSON

Debug JSON is intended for fixtures, replay, diagnostics, and simple exchange. Typed binary arrays require explicit dtype, shape, byte-order, and validated base64 chunk rules. Debug encoding must not become the authority for in-memory protocol semantics.

### Debug typed array envelope

| Field | Type | Meaning |
|---|---|---|
| `dtype` | registered explicit dtype | scalar representation |
| `shape` | non-negative integer tuple | array dimensions |
| `byte_order` | little/big/not-applicable | numeric byte order |
| `encoding` | base64 | debug payload encoding |
| `chunks` | ordered bounded strings | complete payload chunks |
| `byte_length` | non-negative integer | decoded expected length |
| `checksum` | algorithm/value or null | optional fixture integrity |

`GSP-XPORT-005`: decoding validates metadata, chunk vocabulary/limits, decoded byte length, and
dtype×shape size before array construction. Unknown fields follow the fixture schema's explicit
forward-compatibility policy.

Binary IPC and production remote transports are reserved architectural classes until an implementation profile and conformance tests exist.

`GSP-XPORT-006`: reserved transport names are not advertised by a session without an accepted
profile. A legacy HTTP renderer that lacks current session/capability/query/diagnostic semantics is
not a GSP remote transport.

## Extensions

An extension declares a stable identifier, version, kind, schema, capability requirements, implementation declarations, fallback policy, and query contract where applicable. Static validation occurs before extension execution.

Unsupported extensions produce explicit diagnostics. A manifest must not authorize arbitrary code execution, credential lookup, network access, or filesystem access. These require separately accepted and advertised policies.

### ExtensionManifest

| Field | Type | Required |
|---|---|---:|
| `id` | reverse-domain-style stable identifier | yes |
| `version` | semantic version | yes |
| `kind` | registered extension kind | yes |
| `schema_id` | versioned schema identifier | yes |
| `requires` | capability/version constraints | yes, may be empty |
| `implementations` | declarative implementation descriptors | yes |
| `fallback` | reject/deactivate/adapt policy | yes |
| `query_contracts` | payload IDs and schemas | when applicable |
| `security` | requested effects/localities/policies | yes |

| Rule | Requirement |
|---|---|
| `GSP-EXT-001` | Manifest identity, version, schema, and dependencies validate before extension records are accepted. |
| `GSP-EXT-002` | A manifest is declarative and grants no execution effect by itself. Dynamic imports/hooks require a separate accepted security capability. |
| `GSP-EXT-003` | Extension record and query payload kinds are namespaced and versioned. Unknown required payloads reject; optional payload behavior is schema-defined. |
| `GSP-EXT-004` | Fallback is explicit and produces diagnostics for adaptation or deactivation. |

## Data-source extensions

Virtual data sources define bounded materialization and query behavior for data that should not be copied into ordinary buffers. Source descriptors, decoders, credentials, cache keys, and redaction rules remain explicit and capability-gated.

`GSP-EXT-005`: data-source extensions declare request bounds, availability/error states, cache
scope, cancellation behavior, decoder policy, and query payloads. They do not expose arbitrary
producer callbacks to a remote server.

`GSP-EXT-006`: the accepted no-network profile rejects server fetch, local-file access, package
entry points, executable hooks, custom runtime decoders, and runtime shaders unless a later profile
advertises each effect independently.

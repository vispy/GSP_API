# Transports and extensions

## Encoding independence

Protocol meaning is independent of transport and encoding. All transports preserve command order, identifiers, resource metadata, result states, diagnostics, and capability negotiation.

## In-process transport

`InProcessTransport` forwards native `CommandBatch` objects to an `InProcessGSPServer`. It may carry NumPy and memory-view-compatible payloads without mandatory serialization. This avoids mandatory JSON/base64 overhead but does not, by itself, guarantee zero-copy behavior.

## Debug JSON

Debug JSON is intended for fixtures, replay, diagnostics, and simple exchange. Typed binary arrays require explicit dtype, shape, byte-order, and validated base64 chunk rules. Debug encoding must not become the authority for in-memory protocol semantics.

Binary IPC and production remote transports are reserved architectural classes until an implementation profile and conformance tests exist.

## Extensions

An extension declares a stable identifier, version, kind, schema, capability requirements, implementation declarations, fallback policy, and query contract where applicable. Static validation occurs before extension execution.

Unsupported extensions produce explicit diagnostics. A manifest must not authorize arbitrary code execution, credential lookup, network access, or filesystem access. These require separately accepted and advertised policies.

## Data-source extensions

Virtual data sources define bounded materialization and query behavior for data that should not be copied into ordinary buffers. Source descriptors, decoders, credentials, cache keys, and redaction rules remain explicit and capability-gated.

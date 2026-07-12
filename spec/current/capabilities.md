# Capabilities and diagnostics

## Capability snapshot

Each session exposes a `CapabilitySnapshot` covering protocol versions, transports, resource formats, visual families, transform placements, query modes, output formats, extensions, and feature-specific limits.

Planning happens before execution. A producer must not infer support from backend name, imported symbols, screenshots, or unrelated capabilities.

## Outcomes

| Outcome | Required behavior |
|---|---|
| Strict | Execute the stated semantics without a declared deviation and with current conformance evidence. |
| Adapted | Execute a documented approximation and expose the adaptation. |
| Partial | Accept only an enumerated subset and reject requests outside it. |
| Unsupported | Reject or omit the capability deterministically. |
| Blocked | Withhold promotion because required correctness or stability evidence is absent. |

Adaptation must never silently discard a requested semantic field. Deactivation and simplification require structured explanation; fatal incompatibility rejects the operation.

## Diagnostics

A diagnostic identifies a stable code, severity, affected operation or entity, and explanatory payload. Diagnostics distinguish validation failure, unsupported capability, declared adaptation, stale state, execution failure, and security rejection.

Console logs may supplement diagnostics but do not replace them. A query miss is a valid result and must not be used to represent unsupported behavior or an execution error.

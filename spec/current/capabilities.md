# Capabilities and diagnostics

## Capability snapshot

Each session exposes a `CapabilitySnapshot` covering protocol versions, transports, resource formats, visual families, transform placements, query modes, output formats, extensions, and feature-specific limits.

Planning happens before execution. A producer must not infer support from backend name, imported symbols, screenshots, or unrelated capabilities.

### CapabilitySnapshot

| Field group | Required contents |
|---|---|
| identity | `snapshot_id`, `server_name`, negotiated protocol version |
| transport | active transport plus supported transport profiles |
| data | buffer dtypes, texture formats, localities, source kinds, limits |
| rendering | visual families plus feature-specific capability IDs |
| views | transform, layout, navigation, View2D/View3D capabilities |
| queries | scopes, hit policies, payload kinds, ordering guarantees |
| output | display/offscreen/publication formats and size policies |
| extensions | accepted extension IDs and versions |
| security | redaction and execution/fetch policies |
| metadata | backend/profile version and non-semantic evidence identifiers |

| Rule | Requirement |
|---|---|
| `GSP-CAP-001` | A capability snapshot is immutable and has a stable identity for its contents. Changed support or limits require a new snapshot ID. |
| `GSP-CAP-002` | Capability IDs are registered semantic strings. Backend function names and private implementation flags are not protocol capabilities. |
| `GSP-CAP-003` | A coarse family capability never implies optional fields, materials, queries, guides, layouts, outputs, or interaction capabilities. |
| `GSP-CAP-004` | Numeric limits are explicit and non-negative. Zero means unavailable only where the field contract says so; absence is not guessed as unlimited. |

## Outcomes

| Outcome | Required behavior |
|---|---|
| Strict | Execute the stated semantics without a declared deviation and with current conformance evidence. |
| Adapted | Execute a documented approximation and expose the adaptation. |
| Partial | Accept only an enumerated subset and reject requests outside it. |
| Unsupported | Reject or omit the capability deterministically. |
| Blocked | Withhold promotion because required correctness or stability evidence is absent. |

Adaptation must never silently discard a requested semantic field. Deactivation and simplification require structured explanation; fatal incompatibility rejects the operation.

### Planning record

For each requested semantic feature, planning produces:

| Field | Type | Meaning |
|---|---|---|
| `feature_id` | capability/requirement ID | Requested behavior. |
| `entity_id` | public entity ID or null | Affected record. |
| `outcome` | strict/adapted/deactivated/unsupported | Planned disposition. |
| `diagnostics` | tuple of `Diagnostic` | Required for every non-strict outcome. |
| `dependencies` | capability IDs | Exact support intersection used. |

`GSP-CAP-005`: planning evaluates the complete requested feature combination. Individually
supported fields do not prove their combination. An unsupported required feature rejects before
native execution under the default policy.

`GSP-CAP-006`: `blocked` and `not-assessed` are documentation/profile states, not executable success
outcomes. A runtime snapshot omits or rejects those capabilities.

## Diagnostics

A diagnostic identifies a stable code, severity, affected operation or entity, and explanatory payload. Diagnostics distinguish validation failure, unsupported capability, declared adaptation, stale state, execution failure, and security rejection.

Console logs may supplement diagnostics but do not replace them. A query miss is a valid result and must not be used to represent unsupported behavior or an execution error.

### Diagnostic

| Field | Type | Required/default |
|---|---|---|
| `code` | registered diagnostic code | required |
| `severity` | info/warning/error/fatal | required |
| `category` | validation/capability/adaptation/stale/execution/security | required |
| `message` | non-empty human-readable string | required |
| `operation_id` | command/query/frame ID or null | default null |
| `entity_id` | public semantic ID or null | default null |
| `feature_id` | capability/requirement ID or null | default null |
| `data` | typed, redacted JSON-compatible payload | default empty |

`GSP-CAP-007`: stable behavior is machine-readable through `code` and typed data; applications must
not need to parse message text. Diagnostic codes are never reused for different conditions.

`GSP-CAP-008`: backend exceptions, native signals, timeouts, and teardown failures are execution
failures. They cannot be converted into an unsupported capability after execution began.

`GSP-CAP-009`: diagnostic payloads comply with the negotiated redaction profile. Secrets, raw
credentials, sensitive local paths, DNS results, and private native handles are excluded or
replaced by stable redaction tokens.

## Capability dependency examples

| Requested operation | Minimum independent checks |
|---|---|
| point display | point geometry, coordinate space/view, color/size fields, presentation target |
| scalar image colorbar | scalar image, normalization, named colormap, colorbar guide, layout |
| strict 3D mesh | View3D projection, DATA/NDC placement, mesh material, opaque depth, culling |
| guide query | guide rendering, resolved guide layout, guide query scope/payload |
| mesh triangle pick | mesh render scope, query scope, identity payload, snapshot freshness; geometry/facing separately |

`GSP-CAP-010`: support tables and backend profiles use the same separation as runtime planning:
protocol acceptance, producer coverage, rendering, query/readback, output, and evidence are distinct.

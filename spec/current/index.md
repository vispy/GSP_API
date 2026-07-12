# Specification overview

This section is the GSP 0.2 consolidation draft. It provides the target reading order and accepted
high-level model, but it is not yet sufficient by itself to implement the protocol. Detailed field,
validation, diagnostic, and conformance rules remain authoritative in the accepted topic
specifications until requirement-level migration is recorded under `spec/requirements/`.

!!! warning "Specification consolidation in progress"
    Do not infer that an omitted field or rule has been removed. A breaking removal becomes
    effective only when the traceability registry records that disposition explicitly.

## How to read it

The words **must**, **must not**, **should**, and **may** describe requirements. Protocol acceptance and backend implementation are independent:

- A protocol rule defines valid meaning and data.
- A producer may or may not expose a convenience API for it.
- A backend may advertise strict, adapted, partial, or no support.
- A query capability is separate from the corresponding rendering capability.

## Specification map

| Chapter | Defines |
|---|---|
| [Protocol lifecycle](protocol.md) | Sessions, initialization, commands, batches, execution, and shutdown |
| [Scene model](scene.md) | Identifiers, panels, views, visuals, guides, and state relationships |
| [Resources and data](resources.md) | Buffers, textures, data locality, and virtual sources |
| [Visual semantics](visuals.md) | Shared visual rules and each accepted visual family |
| [Views, transforms, and layout](views-layout.md) | Coordinate spaces, View2D, View3D, navigation, and resolved layout |
| [Capabilities and diagnostics](capabilities.md) | Negotiation, adaptation, support states, and failures |
| [Queries and readback](queries.md) | Panel queries, result states, payloads, and snapshot coherence |
| [Transports and extensions](transports-extensions.md) | Encoding independence, local transport, manifests, and data sources |
| [Backend profiles](backend-profiles.md) | Current Matplotlib and Datoviz implementation posture |

## Authority and status

These chapters describe the target GSP 0.2 organization. Backend tables describe implementation
evidence and never redefine the protocol. GSP remains an experimental pre-1.0 prototype; GSP 0.2
may deliberately break prototype APIs when the change is recorded in the requirement registry,
specification, tests, and migration notes together.

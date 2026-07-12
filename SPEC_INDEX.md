# GSP Specification Index

This index identifies the GSP 0.2 specification consolidation. The concise `spec/current/`
chapters are the target organization and public reading path, but they remain a **consolidation
draft** until requirement-level traceability is complete. During this transition, accepted detailed
topic specifications retain normative authority for rules not yet migrated.

## GSP 0.2 consolidation draft

| Topic | Authoritative chapter |
|---|---|
| Scope, conformance language, and reading order | `spec/current/index.md` |
| Sessions, commands, batches, frames, and shutdown | `spec/current/protocol.md` |
| Identifiers, panels, views, visuals, guides, and state relationships | `spec/current/scene.md` |
| Buffers, textures, locality, and virtual data | `spec/current/resources.md` |
| Point, marker, segment, path, image, text, and mesh semantics | `spec/current/visuals.md` |
| Coordinate spaces, transforms, View2D, View3D, navigation, and layout | `spec/current/views-layout.md` |
| Capability negotiation, adaptation, and diagnostics | `spec/current/capabilities.md` |
| Panel queries, readback, payloads, and snapshot coherence | `spec/current/queries.md` |
| Transport independence, in-process exchange, debug JSON, and extensions | `spec/current/transports-extensions.md` |
| Matplotlib, Datoviz v0.4, and legacy implementation boundaries | `spec/current/backend-profiles.md` |
| Stable command, capability, diagnostic, and payload identifiers | `spec/current/registries.md` |

The documentation website publishes these files under its **Specification** navigation. Their
purpose is to provide a coherent semantic map while the detailed contracts are normalized.

## Supporting material

The topic files directly under `spec/` retain detailed validation tables, diagnostic vocabularies,
fixture requirements, and accepted semantic rules while that material is folded into the target
chapters. A rule remains normative in its accepted topic specification until the traceability
registry records its GSP 0.2 destination or explicit disposition. The source inventory lives under
`spec/requirements/`.

When wording conflicts, use the authority order in `AGENTS.md`: charter, architecture, this index,
accepted detailed topic specification, then implementation. Accepted ADRs explain rationale.
Conformance fixtures and backend evidence validate implementation claims but do not redefine
protocol semantics.

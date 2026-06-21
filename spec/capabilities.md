# GSP Capabilities - Draft

Every renderer/server reports a CapabilitySnapshot before planning.

Capability classes:

- protocol versions;
- resource limits;
- buffer/texture formats;
- render target formats;
- shader languages;
- visual-family support;
- transform placement support;
- readback/query support;
- output/export support;
- extension support;
- determinism guarantees.

Adaptation outcomes:

- accept;
- simplify with diagnostic;
- deactivate with diagnostic;
- reject with fatal diagnostic.

Unsupported behavior must not silently degrade.

M002 implementation note: `gsp.protocol.CapabilitySnapshot` exposes advertised protocol versions, transports, buffer dtypes, visual families, transform placements, query modes, output formats, extensions, and a minimal explicit adaptation decision helper.

M009 query hardening note: `CapabilitySnapshot.query_modes` is the coarse planning surface for
panel query/readback support. `supports_query_mode()` and `adapt_query_mode()` mirror visual-family
capability checks. A backend must not claim a query mode until it can return the corresponding
`QueryResult` status and payload semantics.

M011 extension/data-source note: `CapabilitySnapshot.extensions` advertises supported extension
contracts such as `gsp.tiled-image@0.1`. Additional booleans describe whether a backend supports
static extension manifests, virtual data sources, tiled image sources, and specific localities.
Unsupported extension contracts must reject with diagnostics via `adapt_extension()`.

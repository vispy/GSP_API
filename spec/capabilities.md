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

S015 query-scope note: `CapabilitySnapshot.query_capabilities` is the typed query planning surface.
The older string `query_modes` field remains as a v0.1 compatibility projection only. New planning
should prefer `query_capabilities` whenever present.

Typed query capabilities advertise:

- exact `QueryScope`: `data`, `guides`, or `all-rendered`;
- supported coordinate spaces;
- supported hit policies such as `frontmost` and `all`;
- query targets such as visual families, guide roles, and extension visuals;
- supported core payloads and extension payload kinds;
- ordering guarantees: none, scope render order, or global render order;
- relevant provider ids for guide/all-rendered support.

`all-rendered` must be explicitly advertised and requires a global render-order guarantee. It is not
inferred from separate `data` and `guides` capabilities.

Unsupported requested scope, hit policy, payload, extension payload, or ordering guarantee rejects
planning with a diagnostic. Direct query execution must not silently return partial results.

S015 planner composition note: typed query capability support is necessary but not always sufficient.
For guide and all-rendered queries, planning must intersect the global query capability with the
selected axis/guide provider capability:

- `data` scope can remain supported even when visible guides are rendered by a non-queryable provider;
- `guides` scope requires a selected provider with `supports_guide_query=True`;
- `guides` scope requiring guide text/label payloads also requires `supports_text_query=True`;
- `all-rendered` with visible guides requires global render-order support and a selected provider
  that can query those guide contributions;
- providers that render guides but cannot query them must reject guide/all-rendered planning with a
  diagnostic, not silently produce misses.

M011 extension/data-source note: `CapabilitySnapshot.extensions` advertises supported extension
contracts such as `gsp.tiled-image@0.1`. Additional booleans describe whether a backend supports
static extension manifests, virtual data sources, tiled image sources, and specific localities.
Unsupported extension contracts must reject with diagnostics via `adapt_extension()`.

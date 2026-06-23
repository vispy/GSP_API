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

M033 manifest adaptation note: `CapabilitySnapshot.adapt_extension_manifest()` first validates the
static manifest, then requires `supports_extension_manifests=True`, then adapts the manifest's
canonical capability string. This keeps manifest support explicit and prevents a backend from
silently accepting unadvertised extension contracts.

M035 final S017 review note: the Matplotlib reference capability surface and the v0.1 conformance
capability fixture both advertise `gsp.tiled-image@0.1`, static manifest support, virtual
data-source support, local tiled-image sources, synthetic locality, and bounded tile/mosaic limits.

## S020 remote-data and extension security capabilities

Capability snapshots must make dangerous behavior visibly absent. A renderer must not accept a
remote source, credential policy, cache mode, dynamic extension behavior, or query/readback payload
unless the capability snapshot advertises it and validation accepts the concrete request.

Reserved data-source capability fields:

- `data_sources.supported_kinds`;
- `data_sources.supported_source_localities`;
- `data_sources.supported_credential_policies`;
- `data_sources.preconfigured_resolvers`;
- `data_sources.remote_fetch_descriptors`;
- `data_sources.allowed_fetch_schemes`;
- `data_sources.allowed_fetch_methods`;
- `data_sources.redirect_policy`;
- `data_sources.network_egress_policy`;
- `data_sources.max_source_count`;
- `data_sources.max_tile_count_per_frame`;
- `data_sources.max_chunk_bytes`;
- `data_sources.max_decompressed_chunk_bytes`;
- `data_sources.max_total_materialized_bytes`;
- `data_sources.max_query_result_bytes`;
- `data_sources.max_prefetch_concurrency`;
- `data_sources.max_retries`;
- `data_sources.default_timeout_ms`;
- `data_sources.max_timeout_ms`;
- `data_sources.cache_modes`;
- `data_sources.cache_scopes`;
- `data_sources.supports_progressive_refinement`;
- `data_sources.supports_server_side_fetch`.

Reserved extension and security capability fields:

- `extensions.static_manifest_validation`;
- `extensions.dynamic_discovery`;
- `extensions.package_entry_points`;
- `extensions.executable_hooks`;
- `extensions.custom_decoders`;
- `extensions.runtime_shaders`;
- `extensions.allowed_extension_ids`;
- `extensions.manifest_schema_versions`;
- `security.redaction_profile`;
- `security.fixture_remote_sources_allowed`;
- `security.diagnostic_redaction`.

Conservative v0.2 posture:

- `data_sources.remote_fetch_descriptors.accepted=false`;
- `data_sources.supports_server_side_fetch.accepted=false`;
- `data_sources.supported_source_localities=["synthetic", "in-memory", "preconfigured-source"]`;
- `data_sources.supported_credential_policies=["none", "preconfigured"]`;
- `data_sources.cache_modes=["none", "session-memory"]`;
- `extensions.static_manifest_validation=true`;
- `extensions.dynamic_discovery=false`;
- `extensions.package_entry_points=false`;
- `extensions.executable_hooks=false`;
- `extensions.custom_decoders=false`;
- `extensions.runtime_shaders=false`.

Recommended S020 diagnostic codes:

- `GSP_SOURCE_LOCALITY_UNSUPPORTED`;
- `GSP_SOURCE_HANDLE_UNKNOWN`;
- `GSP_REMOTE_FETCH_DISABLED`;
- `GSP_SERVER_SIDE_FETCH_DISABLED`;
- `GSP_FETCH_DESCRIPTOR_REJECTED`;
- `GSP_URL_SCHEME_FORBIDDEN`;
- `GSP_URL_USERINFO_FORBIDDEN`;
- `GSP_URL_HOST_NOT_ALLOWED`;
- `GSP_URL_RESOLVES_PRIVATE`;
- `GSP_URL_REDIRECT_REJECTED`;
- `GSP_LOCAL_PATH_FORBIDDEN`;
- `GSP_LOCAL_PATH_TRAVERSAL`;
- `GSP_CREDENTIAL_POLICY_UNSUPPORTED`;
- `GSP_CREDENTIAL_REF_REJECTED`;
- `GSP_INLINE_SECRET_REJECTED`;
- `GSP_MANIFEST_SCHEMA_INVALID`;
- `GSP_MANIFEST_EXECUTION_FORBIDDEN`;
- `GSP_EXTENSION_DYNAMIC_LOADING_DISABLED`;
- `GSP_DECODER_PLUGIN_DISABLED`;
- `GSP_SHADER_EXTENSION_DISABLED`;
- `GSP_CHUNK_METADATA_INVALID`;
- `GSP_CHUNK_LIMIT_EXCEEDED`;
- `GSP_DECOMPRESSION_LIMIT_EXCEEDED`;
- `GSP_CACHE_POLICY_UNSUPPORTED`;
- `GSP_QUERY_SCOPE_VIOLATION`;
- `GSP_QUERY_RESULT_LIMIT_EXCEEDED`;
- `GSP_REPLAY_REDACTION_REQUIRED`.

These diagnostics reject fatally when they protect a security boundary.

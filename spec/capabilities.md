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

## S029/S034 resolved layout capabilities

Capability snapshots must distinguish semantic guide support, resolved layout support, raster
tolerance, and pixel parity. The layout capability surface includes:

- `layout.semantic_guides`;
- `layout.resolved_layout_produce`: `none | partial | full`;
- `layout.resolved_layout_consume`: `none | partial | full`;
- `layout.layout_strict`;
- `layout.raster_pixel_parity`.

Guide layout capabilities separately advertise native/resolved/adapted/unsupported behavior for
axes, panel titles, colorbars, legends, grid clipping, guide query, and all-rendered guide
contributions. Font capabilities separately advertise logical font pixels, font-family requests,
fallback reporting, text measurement, metrics profile, and rasterization parity. Render-target
capabilities separately advertise logical pixels, device scale, DPI metadata, and physical
framebuffer scaling.

Backends must reject unsupported layout tiers with diagnostics. They must not infer layout strictness
from semantic guide support or from a visually similar raster artifact.

## S027 transform/view capabilities

Transform capabilities must distinguish semantic support from placement. Accepted placement
vocabulary is `GPU_BACKEND`, `CPU_ADAPTER`, `SERVER_SIDE`, `CLIENT_SIDE`, `MIXED`, and
`UNSUPPORTED`. Placement is a reporting/adaptation property and must not change accepted semantics
except within declared tolerance.

Recommended S027 capability names include:

- `gsp.transform.affine2d@0.1`;
- `gsp.transform.inline-affine2d@0.1`;
- `gsp.view2d.linear@0.1`;
- `gsp.transform-query@0.1`;
- visual-family placement/support capabilities such as `gsp.transform.point@0.1`,
  `gsp.transform.path@0.1`, and `gsp.transform.mesh2d@0.1`.

Datoviz CPU pre-transform adaptation is acceptable only for bounded finite eager arrays, must be
reported, and must retain source coordinates if query inverse is advertised. Virtual or huge sources
must not be silently materialized to satisfy transform support.

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

## S022 HTTP single-resource `.npy` capabilities

ADR-0009 defines the first remote-access architecture target as a configured/mock HTTP access
mechanism that materializes a `.npy` typed array. Capability snapshots for this proof must keep
private resolver configuration out of the public surface.

Reserved S022 data-source capability fields:

- `data_sources.supported_source_contracts`;
- `data_sources.remote_access.scene_supplied_urls`;
- `data_sources.remote_access.configured_access_only`;
- `data_sources.remote_access.access_mechanisms`;
- `data_sources.decoders`;
- `data_sources.supported_materialization_targets`;
- `data_sources.supported_formats`;
- `data_sources.query_contracts`;
- `data_sources.preconfigured_resolvers[].access_mechanisms`;
- `data_sources.preconfigured_resolvers[].decoder_ids`;
- `data_sources.preconfigured_resolvers[].network_io`;
- `security.raw_urls_in_protocol`;
- `security.raw_credentials_in_protocol`;
- `security.resolver_outputs_in_replay`.

The first no-network/mock S022 capability posture is:

```json
{
  "data_sources": {
    "supported_source_localities": ["synthetic", "in-memory", "preconfigured-source"],
    "supported_source_contracts": [
      {
        "source_kind": "array",
        "contract_id": "gsp.source.array.v1",
        "formats": ["npy"],
        "decoder_ids": ["gsp.decoder.npy.v1"],
        "materialization_targets": ["array-resource"],
        "query_contracts": ["gsp.query.array-value.v1"],
        "max_rank": 3,
        "max_elements": 1048576,
        "max_decoded_bytes": 4194304
      }
    ],
    "supported_credential_policies": ["none"],
    "remote_fetch_descriptors": {"accepted": false},
    "supports_server_side_fetch": {"accepted": false, "reason": "s022-mock-fetch-only"},
    "remote_access": {
      "scene_supplied_urls": false,
      "configured_access_only": true,
      "access_mechanisms": [
        {
          "id": "http",
          "fetcher_ids": ["gsp.fetcher.http.mock.v1"],
          "network_io": false,
          "schemes": ["https"],
          "methods": ["GET"],
          "url_in_protocol": false,
          "host_policy": "admin-allowlist-private-address-reject",
          "redirect_policy": {"mode": "reject", "max_redirects": 0},
          "timeout_ms_max": 2000,
          "retries_max": 0,
          "response_bytes_max": 1048576,
          "content_encoding": ["identity"],
          "request_headers": "admin-fixed-safe-only",
          "cookies": false,
          "userinfo_allowed": false,
          "fragments_allowed": false,
          "query_strings_allowed": false,
          "dns_rebinding_protection": true
        }
      ]
    },
    "decoders": [
      {
        "decoder_id": "gsp.decoder.npy.v1",
        "format": "npy",
        "content_types": ["application/x-npy", "application/octet-stream"],
        "allow_pickle": false,
        "allow_object_dtype": false,
        "allow_structured_dtype": false,
        "allow_string_dtype": false,
        "allow_fortran_order": false,
        "allowed_dtypes": ["uint8", "uint16", "float32"],
        "allowed_npy_versions": ["1.0", "2.0"],
        "max_header_bytes": 4096,
        "max_rank": 3,
        "max_elements": 1048576,
        "max_decoded_bytes": 4194304
      }
    ],
    "preconfigured_resolvers": [
      {
        "resolver_id": "gsp.demo.http-resource-resolver",
        "source_kinds": ["array"],
        "source_ids": ["demo-http-npy-array"],
        "access_mechanisms": ["http"],
        "decoder_ids": ["gsp.decoder.npy.v1"],
        "credential_policies": ["none"],
        "network_io": false
      }
    ],
    "cache_modes": ["none", "session-memory"]
  },
  "security": {
    "redaction_profile": "gsp.s022.http-single-resource.mock",
    "diagnostic_redaction": true,
    "fixture_remote_sources_allowed": false,
    "raw_urls_in_protocol": false,
    "raw_credentials_in_protocol": false,
    "resolver_outputs_in_replay": false
  }
}
```

A future live HTTP capability may set `supports_server_side_fetch.accepted=true` and
`network_io=true` only after a separate review gate. Even then, it must keep
`scene_supplied_urls=false`, `configured_access_only=true`, `url_in_protocol=false`,
`redirect_policy.mode="reject"`, and `credential_policy="none"` until a later credential review.

S022 adds these recommended diagnostic codes:

- `GSP_SOURCE_CONTRACT_UNSUPPORTED`;
- `GSP_DECODER_UNSUPPORTED`;
- `GSP_CONTENT_TYPE_UNSUPPORTED`;
- `GSP_CONTENT_ENCODING_UNSUPPORTED`;
- `GSP_HTTP_STATUS_REJECTED`;
- `GSP_URL_FRAGMENT_FORBIDDEN`;
- `GSP_URL_QUERY_FORBIDDEN`;
- `GSP_URL_DNS_REBINDING_REJECTED`;
- `GSP_HTTP_TLS_VALIDATION_FAILED`;
- `GSP_HTTP_TIMEOUT`.

Existing S020 diagnostics remain preferred where they already express the violation. The new codes
cover source-contract selection, stable decoder ids, HTTP response policy, and URL validation gaps
that were not specific in S020.


## S024 TextVisual capability notes

Text rendering capabilities are explicit. Core support requires `visual.text` plus printable ASCII,
positions, RGBA alpha, logical pixel font size, anchors, and generic font roles. Unicode beyond ASCII,
multiline, baseline, rotation, per-item style, Datoviz text support, and text query/readback are
separate capability/diagnostic surfaces and must not be silently assumed.

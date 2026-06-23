Based on the uploaded S020 prompt and project constraints, here is the requested security pre-design. 

## 1. **Executive Recommendation**

* **S020 should be mostly architecture, spec, ADR, and negative-conformance work.** Do not implement real HTTP/S3/GCS/Zarr/OME-Zarr/COG/map-tile fetch yet.
* **For v0.2, support only administrator-preconfigured source handles, not arbitrary client-supplied remote fetch descriptors.** A client should be able to say “use source handle X,” not “fetch this URL.”
* **Keep `gsp.tiled-image@0.1` local proof as the safety baseline.** Preserve `synthetic` and `in-memory` as fully supported executable localities.
* **Add a reserved protocol model for future remote fetch, but default it to rejected.** This lets specs and fixtures define validation behavior before any network code exists.
* **Defer dynamic extension loading entirely.** Static manifest validation may be improved, but manifests must remain data-only and must not import Python packages, execute hooks, register shaders, or load decoders.
* **Credential support should be limited to `none` and tightly controlled `preconfigured`.** Raw secrets, signed URLs, authorization headers, cookies, API keys, and resolver outputs must never appear in scenes, manifests, fixtures, replay logs, diagnostics, or debug JSON.
* **Any server-side fetch feature must be allowlist/resolver-driven.** OWASP’s SSRF guidance treats user-controlled server-side fetching as dangerous because it can reach unintended internal/external resources and non-HTTP schemes; allowlists and network-layer controls are central defenses. ([OWASP Cheat Sheet Series][1])
* **Security-sensitive unsupported behavior should reject fatally, not simplify.** Simplification is acceptable for visual fidelity gaps, not for arbitrary URLs, credentials, dynamic code, path traversal, oversized chunks, unsafe redirects, or query-scope violations.
* **The first safe optional proof is a fake/no-network resolver.** It should validate preconfigured handles, credential-reference redaction, diagnostics, cache keys, and replay behavior without performing real network I/O.

## 2. **Threat Model**

**Assets**

* Server-local filesystem, environment variables, process credentials, SSH keys, cloud metadata credentials, package indexes, local network services, internal dashboards, object-store buckets, renderer caches, decoded chunks, query/readback results, debug/replay fixtures, and tenant-isolated data.
* GSP protocol integrity: scenes, visual semantics, extension manifests, source descriptors, capabilities, diagnostics, cache keys, query payloads, and replay fixtures.
* Local fast path integrity: in-process Python objects and arrays should remain possible without JSON/base64 serialization.

**Trust boundaries**

* Client ↔ local in-process server.
* Client ↔ subprocess server.
* Client ↔ remote renderer.
* Renderer ↔ external data source.
* Renderer ↔ credential resolver.
* Renderer ↔ cache.
* Static manifest data ↔ executable implementation.
* Debug/replay fixture ↔ real production source.

**Actors**

* Honest local researcher using synthetic or in-memory sources.
* Honest remote renderer administrator configuring allowed sources.
* Untrusted client submitting scene/source descriptors.
* Malicious extension publisher.
* Malicious data source returning malformed chunks.
* Malicious tenant trying to read another tenant’s cached or queried data.
* Accidental user who serializes credentials or private paths into a fixture.

**Top abuse cases**

* SSRF: client causes a remote renderer to fetch `http://169.254.169.254`, localhost, internal RFC1918 services, Unix socket bridges, cloud metadata endpoints, or non-HTTP schemes. OWASP notes SSRF is not limited to HTTP and can involve schemes such as `file://`, `gopher://`, `data://`, and others. ([OWASP Cheat Sheet Series][1])
* URL parser bypass: `https://expected.com@evil.com`, fragments, encoded hosts, redirects, DNS rebinding, IPv6 forms, octal/decimal IP forms, and IDNA/punycode confusion. OWASP testing guidance highlights userinfo, fragment, encoding, and parsing bypasses as SSRF-relevant cases. ([GitHub][2])
* Path traversal: `../../etc/passwd`, symlink escapes, absolute paths, Windows drive paths, UNC paths, and archive/member traversal.
* Decompression bombs and malformed metadata: tiny compressed tile expands into huge memory; chunk metadata claims impossible dimensions; pyramid levels overlap incorrectly.
* Cache poisoning: attacker stores chunk bytes under a key later reused by another source, credential, user, tenant, extension version, decoder version, or LOD.
* Resource exhaustion: unbounded prefetch, recursive redirects, retry storms, too many tiles, huge mosaics, unbounded concurrency, slowloris responses, and runaway query/readback.
* Supply-chain compromise: malicious dynamic plugin, dependency confusion, compromised package, or untrusted decoder. OWASP’s software supply-chain guidance explicitly includes dependency confusion, upstream compromise, code-signing theft, and CI/CD exploits among supply-chain threats. ([OWASP Cheat Sheet Series][3])
* Query/readback exfiltration: query returns pixels/chunks outside the declared viewport, source bounds, tenant, credential scope, or data-source contract.
* Fixture leakage: debug JSON or replay logs accidentally persist secrets, signed URLs, local paths, internal hostnames, credential refs, readback data, or resolver configuration.

## 3. **S020 In Scope**

S020 should produce durable design artifacts before runtime implementation.

**Architecture/spec artifacts**

* New ADR: **ADR-0005 Remote Data and Dynamic Extension Security Pre-Design**.
* Patch `spec/data_sources.md` with:

  * source descriptor model;
  * locality enum;
  * preconfigured resolver model;
  * future fetch descriptor model;
  * credential policy model;
  * cache policy model;
  * query/readback scoping rules;
  * explicit default rejection of arbitrary remote fetch.
* Patch `spec/extensions.md` with:

  * static-manifest-only rule;
  * prohibited dynamic loading behaviors;
  * manifest trust levels;
  * extension capability requirements;
  * data-only manifest validation requirements.
* Patch `spec/capabilities.md` with:

  * remote data capability fields;
  * extension capability fields;
  * resource limits;
  * credential/caching/query capabilities;
  * diagnostic codes.
* Patch `spec/conformance-fixtures.md` with:

  * redaction rules;
  * forbidden serialized fields;
  * negative fixtures for unsafe sources/extensions;
  * no-network conformance mode.
* Add task files for:

  * descriptor schema design;
  * resolver policy design;
  * fixture redaction;
  * diagnostics;
  * negative tests;
  * optional fake resolver proof.

**Optional safe implementation proofs**

* A **no-network mock resolver** that accepts a fixed administrator-configured source handle and returns deterministic synthetic/in-memory tiles.
* A **redaction pass** for debug-json/replay output.
* A **negative validation test suite** for rejected URL/path/credential/plugin cases.
* A **capability snapshot** proving that a server can advertise `remote_fetch_descriptors=false`, `dynamic_extension_loading=false`, and a small list of safe preconfigured handles.

No real network client is required for S020.

## 4. **S020 Out Of Scope**

Defer all of the following:

* Real HTTP, HTTPS, S3, GCS, Zarr, OME-Zarr, COG, map-tile, STAC, DVID, TileDB, or custom chunk API clients.
* Client-supplied arbitrary URL fetching.
* Server-side production fetch.
* Browser/WebGPU fetch path.
* Credential exchange, OAuth, browser login, token refresh, cloud IAM, AWS/GCP/Azure signing, or secret storage.
* Raw credential payloads.
* Signed URL handling as a first-class protocol feature.
* Dynamic Python package discovery.
* Python entry points.
* Package-manager integration.
* Plugin dependency solving.
* Executable manifest hooks.
* Runtime shader loading.
* Runtime backend extension loading.
* Custom data decoder execution.
* Transform callbacks supplied by third parties.
* Async prefetch, LRU cache, retry engine, or progressive refinement against real remote data.
* Datoviz-specific remote tiled-image implementation.
* User-facing VisPy2 remote/cloud API.
* Multi-tenant production renderer implementation.

## 5. **Recommended Protocol Model**

### Source descriptor fields

A future `DataSourceDescriptor` should be data-only and transport-independent:

```text
id
kind
extension_id
schema_version
logical_shape
logical_dtype
coordinate_space
bounds
chunk_scheme
lod_scheme
source_locality
source_ref
fetch_descriptor
credential_policy
credential_ref
materialization_policy
cache_policy
query_contract
integrity_policy
resource_hints
diagnostics_policy
```

Recommended meanings:

* `id`: scene/session-scoped stable identifier.
* `kind`: semantic source kind, for example `tiled-image`, `zarr-array`, `point-octree`.
* `extension_id`: extension that defines the source contract, for example `gsp.tiled-image@0.1`.
* `schema_version`: descriptor schema version.
* `logical_shape`: full logical array/image/domain shape; must be finite.
* `logical_dtype`: declared data type or channel model.
* `coordinate_space`: declared coordinate system.
* `bounds`: valid source-domain bounds.
* `chunk_scheme`: tile/chunk size, indexing, level layout, border/overlap policy.
* `lod_scheme`: LOD levels and downsampling semantics.
* `source_locality`: where executable data materialization is allowed.
* `source_ref`: opaque reference for preconfigured sources.
* `fetch_descriptor`: future direct/indirect fetch description; rejected by default in v0.2.
* `credential_policy`: `none` or `preconfigured` for v0.2.
* `credential_ref`: optional opaque resolver-scoped reference; never a secret.
* `materialization_policy`: viewport-only, bounded mosaic, full materialization forbidden/allowed, query-only.
* `cache_policy`: cache scope and bounds.
* `query_contract`: allowed query/readback payload schema and scope.
* `integrity_policy`: optional digest, generation ID, ETag-equivalent, immutable/public marker.
* `resource_hints`: client hints only; server capabilities and limits always win.
* `diagnostics_policy`: required diagnostic behavior for unsupported or unsafe behavior.

### Locality enum

Keep current values:

* `synthetic`: deterministic generated data; safe baseline.
* `in-memory`: caller-provided memory object/buffer/array; safe baseline.

Add reserved values:

* `preconfigured-source`: **safe for v0.2**. Client provides only an opaque source handle known to the server or test resolver.
* `local-file-sandboxed`: reserved. Only safe for single-user local mode with administrator/user-configured root, canonical path checks, no symlink escape, and no remote renderer. Not recommended as default v0.2.
* `client-materialized`: reserved. Client fetches or owns data externally, then submits bounded ordinary buffers/chunks. This avoids server SSRF but still needs resource limits.
* `server-resolved-remote`: future. Server resolver maps a source handle to remote data under administrator policy.
* `direct-remote-fetch`: future/discouraged. Client supplies URL-like fetch descriptor. Must be rejected unless an explicit capability and admin policy enable it.
* `browser-origin-fetch`: future. Browser/worker fetch subject to browser security model and GSP policy.

**v0.2 safe executable set:** `synthetic`, `in-memory`, and optionally `preconfigured-source` backed by a no-network mock or administrator-local resolver.

### Credential policy values

Recommended:

* `none`: no credentials are required or used.
* `preconfigured`: credentials, if any, are owned by server/admin resolver configuration; protocol payloads carry no raw secret.
* `preconfigured-ref`: optional refinement of `preconfigured`; client may select an opaque credential reference only if the server advertises this and authorizes the client/session/tenant to use it.
* `delegated`: future only; OAuth/user delegation/cloud IAM.
* `inline`: not a valid policy; any inline secret must be rejected.

For v0.2, prefer only `none` and `preconfigured`. Add `preconfigured-ref` only as a reserved spec term unless there is a concrete no-secret, no-network mock proof.

### Cache policy fields

```text
mode
scope
max_bytes
max_items
ttl_seconds
immutable
key_fields
poisoning_policy
eviction_policy
```

Recommended values:

* `mode`: `none`, `session-memory`, `private-persistent`, `shared-readonly`.
* `scope`: `session`, `user`, `tenant`, `public-immutable`.
* `ttl_seconds`: bounded; default small or absent.
* `immutable`: true only when digest/generation is stable.
* `key_fields`: source id/ref, resolver id, tenant, credential identity/version, extension id/version, decoder id/version, LOD, chunk coordinates, materialization parameters, content generation/digest.
* `poisoning_policy`: reject cache reuse across tenant/credential/source/version boundaries unless `public-immutable` and digest-bound.

For v0.2, support `none` and possibly `session-memory` only.

### Capability fields

A server capability snapshot should advertise:

```text
data_sources.supported_kinds
data_sources.supported_source_localities
data_sources.supported_credential_policies
data_sources.preconfigured_resolvers
data_sources.remote_fetch_descriptors
data_sources.allowed_fetch_schemes
data_sources.allowed_fetch_methods
data_sources.redirect_policy
data_sources.network_egress_policy
data_sources.max_source_count
data_sources.max_tile_count_per_frame
data_sources.max_chunk_bytes
data_sources.max_decompressed_chunk_bytes
data_sources.max_total_materialized_bytes
data_sources.max_query_result_bytes
data_sources.max_prefetch_concurrency
data_sources.max_retries
data_sources.default_timeout_ms
data_sources.max_timeout_ms
data_sources.cache_modes
data_sources.cache_scopes
data_sources.supports_progressive_refinement
data_sources.supports_server_side_fetch
extensions.static_manifest_validation
extensions.dynamic_discovery
extensions.package_entry_points
extensions.executable_hooks
extensions.custom_decoders
extensions.runtime_shaders
extensions.allowed_extension_ids
extensions.manifest_schema_versions
security.redaction_profile
security.fixture_remote_sources_allowed
security.diagnostic_redaction
```

For v0.2 defaults:

```text
remote_fetch_descriptors = false
supports_server_side_fetch = false
dynamic_discovery = false
package_entry_points = false
executable_hooks = false
custom_decoders = false
runtime_shaders = false
supported_source_localities = ["synthetic", "in-memory", "preconfigured-source"]
supported_credential_policies = ["none", "preconfigured"]
cache_modes = ["none", "session-memory"]
```

## 6. **Validation Rules**

### Manifest validation

* Manifest must be strict-schema validated before use.
* Manifest must be treated as untrusted data.
* Manifest must not contain executable Python references, import paths, entry-point groups, shell commands, URLs to load code, shader source, binary blobs, pickle payloads, or decoder callbacks.
* Manifest `id` must be namespaced and stable.
* Manifest `version` must be semantic.
* Manifest `kind` must be one of the declared extension kinds.
* Capability requirements must be explicit.
* Fallback and diagnostics policy must be explicit.
* Query/readback payload schemas must be explicit and bounded.
* Unknown fields should either be rejected or allowed only under an `x-` extension namespace that is never executable.
* Implementation declarations must describe already-built server capabilities, not instructions for loading code.

### Source descriptor validation

* `source_locality` must be supported by server capabilities.
* `kind` and `extension_id` must be known and compatible.
* Logical shape, tile size, chunk count, LOD count, channel count, and dtype must be finite and within capability limits.
* `source_ref` must be opaque and resolver-scoped for `preconfigured-source`.
* Unknown source handles must reject fatally.
* Client-provided paths are invalid unless `local-file-sandboxed` is explicitly enabled.
* Client-provided URLs are invalid unless future `direct-remote-fetch` is explicitly enabled.
* `materialization_policy` must not require full materialization unless the server advertises it and the declared size is within limits.
* Descriptor must not contain raw secrets, auth headers, cookies, signed URLs, environment variables, private keys, or credential resolver output.

### Fetch descriptor validation

For v0.2, any `fetch_descriptor` should reject by default with a fatal diagnostic.

For future guarded support:

* URL must be parsed by a single canonical parser.
* Scheme must be allowlisted; default future scheme should be `https` only.
* Userinfo in URLs must be forbidden.
* Fragments must be forbidden.
* Query parameters must be treated as sensitive and redacted in diagnostics.
* Redirects must default to disabled. If enabled, every redirect target must be revalidated.
* Host must match an administrator allowlist or resolver policy.
* DNS results must be checked against private, loopback, link-local, multicast, reserved, and metadata-service address ranges.
* DNS rebinding must be mitigated by binding validation to connection target or by resolver/network egress controls.
* Methods should be limited to `GET` and `HEAD`.
* Request headers must be resolver-owned and allowlisted.
* Response content type, content length, decoded length, tile dimensions, and decompression ratio must be bounded.
* Timeouts, retries, redirects, concurrency, and total bytes must be bounded.
* Archive/container formats must reject path traversal and nested expansion bombs.
* Network errors must not leak internal topology.

### Credential validation

* Raw secrets are never valid in protocol payloads.
* `credential_ref` is not a credential; it is an opaque selector.
* `credential_ref` must be resolver-scoped, tenant-scoped, and authorized for the session.
* Resolver must bind credential use to allowed source, host/bucket, operation, and credential audience.
* Ambient credentials from environment variables, cloud instance metadata, local config files, or default SDK chains must be disabled unless explicitly chosen by administrator resolver policy.
* Credential failure diagnostics must not reveal whether a secret exists, its value, its provider, or internal account identifiers.
* OWASP secrets guidance emphasizes centralized/standardized secrets management and least privilege; GSP should not become its own secret store. ([OWASP Cheat Sheet Series][4])

### Cache key validation

Cache keys must include at least:

```text
tenant/session scope
resolver id
source handle or canonical source identity
credential identity version or no-credential marker
extension id/version
source kind
logical generation/version/digest
LOD
chunk coordinates
requested channel/format
decoder version
materialization parameters
```

Rules:

* Do not share cache entries across tenants by default.
* Do not share cache entries across credentials by default.
* Do not share mutable remote content unless generation/digest/ETag-equivalent is part of the key.
* Do not let client-supplied cache keys override server-derived keys.
* Do not cache failed authorization as reusable content.
* Do not cache diagnostic bodies containing sensitive information.

### Resource limit validation

* Server capabilities define hard limits; client hints cannot raise them.
* Reject descriptors whose worst-case materialization exceeds limits.
* Reject chunk metadata whose declared dimensions overflow integer arithmetic.
* Reject decoded chunks above `max_decompressed_chunk_bytes`.
* Reject frame plans above `max_tile_count_per_frame`.
* Enforce total per-frame bytes, query bytes, and cache bytes.
* Enforce bounded prefetch, retry, and concurrency even for trusted preconfigured sources.

### Query/readback validation

* Query payload must be typed and schema-validated.
* Query scope must be limited to declared source bounds, viewport, panel, selection, and query contract.
* Query result size must be bounded.
* Query results must not expose server file paths, URLs, credentials, resolver config, environment variables, internal hostnames, tenant IDs, or cache internals.
* Extension query payloads must not be arbitrary Python objects; no pickle, object reprs, callbacks, or class paths.
* Out-of-scope query should reject fatally or return a typed diagnostic, not silently clip unless the query contract explicitly allows clipped results with diagnostics.

### Replay/debug serialization validation

Never serialize:

* Raw passwords, API keys, bearer tokens, SSH keys, cloud keys, certificates, cookies, auth headers, or session tokens.
* Signed URLs, presigned S3/GCS URLs, SAS URLs, query-string credentials, or temporary credentials.
* Credential resolver output.
* Unredacted credential references when they reveal provider/account/project/bucket/user identity.
* Absolute local paths, home directories, UNC paths, symlink-resolved paths, or server-internal mount paths.
* Internal hostnames, private IPs, metadata endpoint addresses, DNS resolution results, or network topology.
* Cross-tenant cache keys or cache contents.
* External restricted data chunks unless the fixture is explicitly a sanitized public fixture.
* Query/readback payloads outside declared fixture scope.
* Manifest fields that imply executable code.

Debug JSON should use stable redacted placeholders such as:

```text
credential_ref: "<redacted:credential-ref>"
source_ref: "<redacted:source-ref>"
url: "<redacted:url>"
local_path: "<redacted:path>"
```

Application logging should be designed deliberately for security events and operational debugging, but sensitive data must be excluded or redacted. OWASP’s logging guidance emphasizes application-level security logging as valuable, while secrets guidance warns against plaintext secret sprawl in configuration and tooling. ([OWASP Cheat Sheet Series][5])

## 7. **Dynamic Extensions Policy**

Recommendation: **defer dynamic extension loading entirely.**

Allowed in S020/v0.2:

* Static bundled manifests.
* Static test manifests.
* Explicitly provided manifest files for validation only.
* Offline manifest linter.
* Capability advertisement based on already-installed server code.
* Extension IDs and schemas used for diagnostics, fixtures, and conformance.

Not allowed:

* Python package import from manifest.
* Python entry-point discovery.
* Runtime plugin installation.
* Dependency solving.
* Manifest-declared callback execution.
* Manifest-declared decoder execution.
* Manifest-declared shader compilation/loading.
* Transform callbacks.
* Backend draw-call injection.
* Arbitrary class/module names in protocol payloads.
* Pickle/cloudpickle/dill payloads.
* Auto-discovery from `site-packages`.

A safe static discovery model worth adding:

```text
extension_registry:
  source = "builtin" | "configured-manifest-dir" | "test-fixture"
  manifests_are_data_only = true
  imports_allowed = false
  executable_hooks_allowed = false
  package_resolution_allowed = false
```

Rules:

* Configured manifest directories may be allowed only for local development/test.
* Static manifests from third parties may describe protocol contracts but cannot activate implementation code.
* A server may advertise “I implement extension X” only because its own trusted code already implements X.
* A manifest can require capabilities; it cannot create capabilities.

This keeps GSP aligned with secure software-development and supply-chain principles: reduce the executable attack surface, know what components are present, and avoid automatic consumption of untrusted dependencies. NIST’s SSDF frames secure software development as risk-based, integrated practices, and OWASP’s supply-chain guidance highlights dependency-related and build/deployment threats. ([NIST CSRC][6])

## 8. **Remote Fetch Policy**

Recommendation: **do not support real remote fetch descriptors next. Support only preconfigured source handles.**

### v0.2 policy

Client may submit:

```text
source_locality = "preconfigured-source"
source_ref = {
  resolver_id: "example.resolver",
  source_id: "public-demo-pyramid"
}
credential_policy = "none" | "preconfigured"
```

Client may not submit:

```text
url
headers
cookies
authorization
signed_url
s3_uri
gcs_uri
local_path
retry_policy that raises server limits
redirect_policy that raises server limits
credential material
```

The renderer resolves `resolver_id + source_id` through administrator/test configuration. The scene does not know the underlying URL/path/bucket.

### Future direct fetch policy, if ever enabled

* Default: disabled.
* Must require explicit server capability.
* Must require administrator policy.
* Must require host/source allowlist.
* Must reject private, loopback, link-local, multicast, reserved, and metadata-service addresses.
* Must reject `file://`, `ftp://`, `gopher://`, `data://`, `dict://`, `smb://`, `ssh://`, and custom schemes unless a specific resolver owns them.
* Must disallow URL userinfo.
* Must disallow fragments.
* Must canonicalize and revalidate IDNA/punycode hosts.
* Must revalidate every redirect.
* Must set `max_redirects`, ideally `0` by default.
* Must set connect timeout, read timeout, total timeout, max response bytes, max decoded bytes, and max decompression ratio.
* Must limit retries and use backoff with a strict total attempt cap.
* Must limit concurrency per session, source, tenant, and renderer.
* Must perform egress filtering below the application layer when possible.
* Must not expose internal network errors or resolved IPs in diagnostics.
* Must not follow redirects from allowed hosts to disallowed hosts.
* Must not allow arbitrary request headers.
* Must not use ambient SDK credential chains by default.

## 9. **Credential Policy**

`credential_policy=preconfigured` is safe only under strict rules.

### Safe meaning of `preconfigured`

* The server or resolver administrator owns the credential.
* The protocol payload does not contain the credential.
* The client cannot derive the credential.
* The client cannot redirect the credential to another host/source.
* The credential is scoped to a resolver, source, tenant, operation, and audience.
* The credential is least-privilege and read-only where possible.
* The resolver, not the scene, constructs authorization headers or SDK calls.
* Audit logs record use of the resolver/source/tenant/session, not the secret value.

### Opaque credential references

A payload may carry a `credential_ref` only if all are true:

* The server advertises `supports_credential_refs=true`.
* The credential ref was pre-registered out of band.
* The session principal is authorized to use it.
* The ref is bound to the resolver and source kind.
* The ref is not a URL, path, token, header value, or serialized secret.
* The ref is redacted from fixtures/logs by default.
* The server can reject unknown or unauthorized refs without revealing whether they exist.

Preferred v0.2 shape:

```text
credential_policy = "preconfigured"
credential_ref = absent
```

The source handle itself selects the resolver-owned credential. This is safer than letting clients select credential refs.

### Forbidden

* Raw secrets in scenes.
* Raw secrets in manifests.
* Raw secrets in debug JSON.
* Raw secrets in conformance fixtures.
* Raw secrets in diagnostics.
* Raw secrets in replay logs.
* Signed URLs as a substitute for credential references.
* Environment-default credentials unless explicitly configured by the resolver administrator.
* Cross-tenant credential reuse.
* User-controlled request headers.
* Credential-bearing cache keys visible to clients.

## 10. **Capability And Diagnostics Model**

Capabilities should make dangerous features visibly absent.

Example v0.2 capability posture:

```text
data_sources:
  supported_kinds:
    - gsp.tiled-image
  supported_source_localities:
    - synthetic
    - in-memory
    - preconfigured-source
  supported_credential_policies:
    - none
    - preconfigured
  remote_fetch_descriptors:
    accepted: false
  supports_server_side_fetch:
    accepted: false
  preconfigured_resolvers:
    - resolver_id: gsp.test.synthetic-resolver
      source_kinds: [gsp.tiled-image]
      credential_policies: [none]
      network_io: false
  limits:
    max_source_count: 16
    max_tile_count_per_frame: 1024
    max_chunk_bytes: bounded value chosen by implementation
    max_decompressed_chunk_bytes: bounded value chosen by implementation
    max_query_result_bytes: bounded value chosen by implementation
    max_prefetch_concurrency: 0
    max_retries: 0
  cache_modes:
    - none
    - session-memory

extensions:
  static_manifest_validation: true
  dynamic_discovery: false
  package_entry_points: false
  executable_hooks: false
  custom_decoders: false
  runtime_shaders: false
```

Recommended diagnostic codes:

```text
GSP_SOURCE_LOCALITY_UNSUPPORTED
GSP_SOURCE_HANDLE_UNKNOWN
GSP_REMOTE_FETCH_DISABLED
GSP_SERVER_SIDE_FETCH_DISABLED
GSP_FETCH_DESCRIPTOR_REJECTED
GSP_URL_SCHEME_FORBIDDEN
GSP_URL_USERINFO_FORBIDDEN
GSP_URL_HOST_NOT_ALLOWED
GSP_URL_RESOLVES_PRIVATE
GSP_URL_REDIRECT_REJECTED
GSP_LOCAL_PATH_FORBIDDEN
GSP_LOCAL_PATH_TRAVERSAL
GSP_CREDENTIAL_POLICY_UNSUPPORTED
GSP_CREDENTIAL_REF_REJECTED
GSP_INLINE_SECRET_REJECTED
GSP_MANIFEST_SCHEMA_INVALID
GSP_MANIFEST_EXECUTION_FORBIDDEN
GSP_EXTENSION_DYNAMIC_LOADING_DISABLED
GSP_DECODER_PLUGIN_DISABLED
GSP_SHADER_EXTENSION_DISABLED
GSP_CHUNK_METADATA_INVALID
GSP_CHUNK_LIMIT_EXCEEDED
GSP_DECOMPRESSION_LIMIT_EXCEEDED
GSP_CACHE_POLICY_UNSUPPORTED
GSP_QUERY_SCOPE_VIOLATION
GSP_QUERY_RESULT_LIMIT_EXCEEDED
GSP_REPLAY_REDACTION_REQUIRED
```

Security diagnostics should usually be fatal rejects. Do not simplify:

* remote fetch into local fetch;
* unauthorized source into empty source;
* credential failure into unauthenticated fetch;
* dynamic plugin into ignored manifest;
* out-of-scope query into clipped readback unless explicitly allowed by query contract.

Accept/simplify/deactivate are appropriate for visual fidelity gaps, not for security boundary failures.

## 11. **Conformance/Test Plan**

Minimum tests before runtime implementation:

### Manifest tests

* Static valid manifest accepted.
* Manifest with Python import path rejected.
* Manifest with entry-point declaration rejected.
* Manifest with executable hook rejected.
* Manifest with shader source/loading directive rejected.
* Manifest with decoder callback rejected.
* Manifest with unknown executable-looking fields rejected.
* Manifest with missing fallback/diagnostics/query contract rejected where applicable.

### Source descriptor tests

* `synthetic` tiled-image source accepted.
* `in-memory` tiled-image source accepted.
* `preconfigured-source` known mock handle accepted.
* `preconfigured-source` unknown handle rejected.
* `direct-remote-fetch` rejected by default.
* `server-resolved-remote` rejected unless advertised.
* `local-file-sandboxed` rejected unless explicitly advertised.
* Descriptor with raw URL rejected.
* Descriptor with local path rejected.
* Descriptor with oversized logical shape rejected.
* Descriptor with invalid chunk metadata rejected.
* Descriptor with unsupported credential policy rejected.

### SSRF/path negative tests

Even before real networking, validation fixtures should reject:

```text
http://127.0.0.1/
http://localhost/
http://169.254.169.254/
http://[::1]/
file:///etc/passwd
gopher://example.com/
data:text/plain,hello
https://allowed.example@evil.example/
https://evil.example#allowed.example
encoded/private IP variants
redirect-to-private fixture
```

These can be pure descriptor-validation fixtures; no network I/O is needed.

### Credential tests

* `credential_policy=none` accepted for current safe sources.
* `credential_policy=preconfigured` accepted only for advertised resolver/source.
* Inline `Authorization` header rejected.
* Inline cookie rejected.
* Inline API key rejected.
* Signed URL rejected or redacted/fatal.
* Unknown `credential_ref` rejected.
* Unauthorized `credential_ref` rejected without existence leak.
* Debug/replay redacts credential refs.

### Cache tests

* Cache key includes source handle, resolver, tenant/session, credential identity/version marker, extension version, LOD, chunk coordinate, and generation/digest marker.
* Cross-tenant cache reuse rejected.
* Cross-credential cache reuse rejected.
* Mutable source without generation/digest cannot use shared cache.
* Client-supplied cache key ignored/rejected.

### Resource tests

* Oversized compressed chunk rejected.
* Oversized decoded chunk rejected.
* Excessive tile count rejected.
* Excessive query result rejected.
* Retry/concurrency/prefetch above advertised limits rejected.
* Malformed pyramid metadata rejected.
* Integer overflow dimensions rejected.

### Query/readback tests

* Valid tiled-image query returns typed `TiledImageQueryPayload`.
* Query outside source bounds rejects or returns explicit diagnostic according to contract.
* Query result above size cap rejected.
* Query payload with server path/internal URL rejected.
* Extension payload schema mismatch rejected.
* Replay fixture contains only sanitized query payload.

### Fixture/replay tests

* Scene with raw secret fails fixture validation.
* Scene with signed URL fails fixture validation.
* Scene with private URL fails fixture validation.
* Scene with local absolute path fails shareable fixture validation.
* Diagnostic redaction is deterministic.
* No-network conformance suite passes without internet access.

## 12. **ADR/Spec Patch Plan**

### New ADR

Add **ADR-0005: Remote Data and Dynamic Extension Security Pre-Design**.

It should record:

* v0.2 supports preconfigured source handles only.
* Arbitrary remote fetch descriptors are reserved but rejected.
* Dynamic extension loading is deferred.
* Static manifests remain data-only.
* `credential_policy=preconfigured` means resolver-owned credentials, not protocol secrets.
* Debug/replay redaction is required.
* Security-sensitive unsupported behavior rejects fatally.
* No Datoviz implementation requirement is introduced.

### `spec/extensions.md`

Patch with:

* Manifest trust model.
* Static-only extension lifecycle.
* Prohibited executable fields.
* Allowed static discovery sources.
* Extension capability requirements.
* Dynamic loading rejection rules.
* Manifest diagnostics codes.
* Query payload schema rules.
* Statement that manifests can describe but not activate implementation.

### `spec/data_sources.md`

Patch with:

* Source descriptor model.
* Locality enum.
* `preconfigured-source` semantics.
* Future `fetch_descriptor` reserved schema.
* Default rejection of direct remote fetch.
* Credential policy model.
* Cache policy model.
* Materialization policy.
* Resource limit model.
* Query/readback scope model.
* Redaction requirements.
* Resolver ownership and authorization requirements.

### `spec/capabilities.md`

Patch with:

* Data-source capability fields.
* Resolver capability fields.
* Credential capability fields.
* Cache capability fields.
* Resource limit fields.
* Extension dynamic-loading capability fields.
* Security/redaction capability fields.
* Diagnostic code registry.

### `spec/conformance-fixtures.md`

Patch with:

* Fixture redaction profile.
* Forbidden serialized values.
* Negative fixture requirements.
* No-network test requirement.
* Sanitized preconfigured-source fixture format.
* Rule that credentialed/external data fixtures must not serialize data unless explicitly sanitized and public.
* Stable diagnostic expectations.

### Task files

Add S020 subtasks:

```text
S020-001 ADR-0005 remote data/security decision
S020-002 data source descriptor schema patch
S020-003 capability schema patch
S020-004 extension manifest security patch
S020-005 debug/replay redaction rules
S020-006 negative conformance fixtures
S020-007 no-network preconfigured resolver proof
S020-008 stop-condition checklist
```

### Documentation

Add a short documentation page:

```text
docs/security/remote-data-and-extensions.md
```

It should tell users:

* remote fetch is not implemented by default;
* arbitrary URLs are rejected;
* static manifests are not plugins;
* secrets do not belong in scenes or fixtures;
* preconfigured sources are administrator-controlled.

## 13. **Stop Conditions**

Implementation must stop and request another design review if any of these occur:

* A feature requires client-supplied arbitrary URLs.
* A feature requires raw secrets in scene/source descriptors.
* A feature requires signed URLs in fixtures or replay logs.
* A feature requires Python entry points, imports, callbacks, plugin packages, custom decoders, or runtime shaders.
* A feature relies on ambient cloud credentials or default SDK credential chains.
* The server cannot enforce host/source allowlists.
* The server cannot block private, loopback, link-local, reserved, or metadata-service addresses.
* Redirect validation cannot be made strict.
* Resource bounds cannot be enforced before materialization.
* Decoded size cannot be bounded before or during decode.
* Cache keys cannot isolate tenant, credential, source, resolver, extension version, and content generation.
* Query/readback cannot be scoped to declared source bounds.
* Debug-json/replay cannot reliably redact secrets and private source details.
* A remote renderer is multi-tenant but lacks tenant/session/cache isolation.
* Unsupported security behavior would silently degrade.
* Datoviz changes become necessary for the security proof.
* Matplotlib reference/conformance cannot represent the safe baseline.
* The safe local `gsp.tiled-image@0.1` proof would be broken.

## 14. **Open Questions**

* Should v0.2 enable `preconfigured-source` only for test/mock resolvers, or also for real local administrator configuration with no network?
* Should `local-file-sandboxed` be allowed for single-user local research, or deferred to avoid path traversal and fixture leakage complexity?
* Should clients ever be allowed to select `credential_ref`, or should credentials always be bound implicitly to `source_ref` by the resolver?
* What is the minimum resolver configuration format: Python object, TOML/YAML file, environment-free config, or test fixture only?
* Which remote source family should be designed first after S020: HTTP tile pyramid, OME-Zarr, Zarr, COG, map tiles, or point-cloud octree?
* Should future remote content require digest/generation metadata before shared caching is allowed?
* What redaction level should be default for local developer debug output versus shareable conformance fixtures?
* What authentication/authorization model identifies client, session, user, and tenant in a remote renderer?
* Should source handles be globally stable, server-local, session-local, or fixture-local?
* Should diagnostics reveal that a source exists but authorization failed, or always use indistinguishable rejection for unknown/unauthorized handles?
* Is there a project-owned namespace registry for extension IDs, or only reverse-DNS/static IDs?
* What is the eventual policy for public unauthenticated remote data: still resolver-only, or direct HTTPS allowlisted descriptors?
* What is the minimum security review required before enabling any actual network egress?

[1]: https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html "Server Side Request Forgery Prevention - OWASP Cheat Sheet Series"
[2]: https://github.com/OWASP/wstg/blob/master/document/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery.md "wstg/document/4-Web_Application_Security_Testing/07-Input_Validation_Testing/19-Testing_for_Server-Side_Request_Forgery.md at master · OWASP/wstg · GitHub"
[3]: https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html "Software Supply Chain Security - OWASP Cheat Sheet Series"
[4]: https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html "Secrets Management - OWASP Cheat Sheet Series"
[5]: https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html "Logging - OWASP Cheat Sheet Series"
[6]: https://csrc.nist.gov/projects/ssdf "Secure Software Development Framework | CSRC"

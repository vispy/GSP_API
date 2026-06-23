## 1. Executive Decision

**HTTP single-resource should be first.** The first S022 proof should exercise HTTP as an **access mechanism** behind an opaque, resolver-owned handle before attempting tile pyramids, Zarr, OME-Zarr, COG, map tiles, or point-cloud chunks. This keeps the proof small while still testing the hard architectural boundary: scene payloads name a stable source contract and decoder, while the resolver/admin configuration owns URL, host policy, limits, credentials, cache behavior, and fetcher choice. This directly addresses P007/Q060 while preserving the S020/S021 constraints in the uploaded packet.

**The first proof target should be an HTTP-backed `.npy` typed array**, not JPEG/PNG.

Rationale and tradeoffs:

| Option                               |   Decision | Reason                                                                                                                                                                                                                           |
| ------------------------------------ | ---------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| HTTP single-resource                 |    **Yes** | Smallest real remote-access architecture test. It validates access/source/decoder/adapter separation without tile addressing, LOD, tile caches, chunk indexes, or distributed dataset semantics.                                 |
| `.npy` typed array                   |  **First** | Best fit for scientific visualization, NumPy is already central to the Python ecosystem, the decoder can be bounded and deterministic with `allow_pickle=false`, and it migrates naturally toward Zarr/OME-Zarr chunk semantics. |
| JPEG/PNG image/texture               | **Second** | More immediately visual, but image codecs have larger security and dependency surface: decompression bombs, color modes, metadata, EXIF/ICC handling, native codec libraries, and format sniffing.                               |
| Tile pyramid / Zarr / OME-Zarr / COG |  **Later** | These should reuse the same access/fetch and decoder policy spine after the single-resource proof passes.                                                                                                                        |

The first proof should therefore be:

```text
preconfigured opaque source handle
→ resolver-owned HTTPS/mock-HTTP byte fetch
→ built-in gsp.decoder.npy.v1
→ bounded typed array resource
→ optional Matplotlib reference rendering for 2-D arrays
→ bounded array query/readback
```

No client-supplied URLs, credentials, headers, cookies, decoder imports, dynamic plugins, runtime shaders, or package-install instructions are allowed.

---

## 2. Layered Protocol Model

| Layer                  | Protocol Name/Field                                                                                                  | Resolver/Admin Config                                                                                                                          | Capability Field                                          | Renderer Adapter                                                 | Notes                                                                                                            |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------- | ---------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Access/fetch           | Scene uses `locality="preconfigured-source"` and `source_ref.resolver_id/source_id`. Scene does **not** include URL. | `access.mechanism="http"`, `fetcher_id`, private URL, method, host allowlist, redirect policy, TLS policy, byte limits, timeout, retry limits. | `data_sources.remote_access.access_mechanisms[]`          | None directly.                                                   | HTTP is not a source type. It is a resolver-owned byte access mechanism.                                         |
| Source contract        | `source_kind="array"`                                                                                                | `source_contract.kind="array"`, expected shape/dtype/channels/rank.                                                                            | `data_sources.supported_source_contracts[]`               | `array-resource`; optional semantic image view for 2-D arrays.   | Add or reserve a protocol source contract equivalent to `array`. Do not use `source_kind="http"`.                |
| Decoder                | `format="npy"`, `decoder_id="gsp.decoder.npy.v1"`                                                                    | `decoder.decoder_id`, `allowed_dtypes`, `max_rank`, `max_elements`, `max_decoded_bytes`, `allow_pickle=false`, `max_header_bytes`.             | `data_sources.decoders[]`                                 | Produces typed array materialization.                            | Decoder is built-in/trusted server capability, not scene-supplied code.                                          |
| Resolver policy        | `source_ref` opaque handle only.                                                                                     | Resolver maps authorized handle to access config, decoder config, credential policy, limits, cache policy, generation/digest policy.           | `data_sources.preconfigured_resolvers[]`                  | None directly.                                                   | Unknown and unauthorized handles should both return `GSP_SOURCE_HANDLE_UNKNOWN` externally to avoid enumeration. |
| Credential policy      | `credential_policy="none"` for first proof.                                                                          | First proof: no credentials. Future `preconfigured` requires another review unless already explicitly approved for a later stage.              | `supported_credential_policies=["none"]` for first proof. | None.                                                            | No `credential_ref`, inline secrets, auth headers, cookies, signed URLs, or ambient cloud credentials.           |
| Cache policy           | `cache_policy.mode` may be `"none"` or `"session-memory"`.                                                           | Resolver may force stricter mode. Private cache key includes tenant/session/source/decoder/policy/generation isolation.                        | `data_sources.cache_modes`                                | May reuse materialized resource within session.                  | No shared or persistent cache in first proof. No cache keys in debug/replay.                                     |
| Diagnostics            | Stable diagnostic codes only.                                                                                        | Resolver emits redacted diagnostics. Private audit may include more detail outside protocol artifacts.                                         | `security.redaction_profile`, `diagnostic_redaction=true` | Backends surface fatal diagnostics.                              | Security-sensitive unsupported behavior rejects fatally.                                                         |
| Materialization target | `materialization_policy="full"`, `materialization_target="array-resource"`                                           | Resolver verifies decoded array satisfies declared contract.                                                                                   | `supported_materialization_targets`                       | Matplotlib array adapter; future Datoviz texture/buffer adapter. | Datoviz implementation is not required for S022.                                                                 |
| Query/readback         | Future or first-proof optional: `array-value` query contract.                                                        | Resolver enforces bounds, dtype, result limits.                                                                                                | `query_contracts=["gsp.query.array-value.v1"]`            | Matplotlib reference can answer value queries.                   | Query scope must be clipped to declared shape.                                                                   |

---

## 3. First-Proof Descriptor Schema

### Scene-visible descriptor fields

Use this as the S022 v0.1 protocol schema. Current implementation may map `source_kind` to the existing `DataSourceDescriptor.kind` field internally, but the protocol should name the semantic source contract explicitly.

| Field                    | Required | Allowed first-proof values                                   | Lives in                    | Notes                                                                         |
| ------------------------ | -------: | ------------------------------------------------------------ | --------------------------- | ----------------------------------------------------------------------------- |
| `id`                     |      Yes | Stable source descriptor id, e.g. `"array_http_demo_001"`    | Scene payload, debug/replay | Scene-local identifier. Not a resolver handle.                                |
| `source_kind`            |      Yes | `"array"`                                                    | Scene payload               | New/explicit source contract. `"http"` is invalid.                            |
| `extension_id`           |       No | `null` or static extension id                                | Scene payload               | First proof should use built-in core source contract, so `null` is preferred. |
| `extension_version`      |       No | `null` or semantic version                                   | Scene payload               | Required only if source contract comes from a static manifest.                |
| `shape`                  |      Yes | Rank 2 or rank 3 array shape, e.g. `[4, 4]`, `[64, 64, 1]`   | Scene payload               | Must match resolver config and decoded `.npy` header exactly.                 |
| `dtype`                  |      Yes | First proof: `"uint8"`, `"uint16"`, `"float32"`              | Scene payload               | Keep small. Add more dtypes only by capability update.                        |
| `channels`               |      Yes | `1`, optionally `3` or `4` for rank-3 image-like arrays      | Scene payload               | For rank 2, `channels` must be `1`.                                           |
| `coordinate_system`      |      Yes | `"array-index"`                                              | Scene payload               | Do not imply geospatial, physical, or tiled coordinates.                      |
| `extent`                 |       No | `null` or numeric extent if rendered as image                | Scene payload               | Optional for Matplotlib display, not used for access.                         |
| `origin`                 |       No | `"upper"` or `"lower"`                                       | Scene payload               | Only relevant for image-like rendering.                                       |
| `locality`               |      Yes | `"preconfigured-source"`                                     | Scene payload               | Direct remote locality is not allowed in first proof.                         |
| `credential_policy`      |      Yes | `"none"`                                                     | Scene payload               | First proof is no-auth public/mock HTTP only.                                 |
| `source_ref.resolver_id` |      Yes | Opaque resolver id, e.g. `"gsp.demo.http-resource-resolver"` | Scene payload               | No URL, host, bucket, path, or account identity.                              |
| `source_ref.source_id`   |      Yes | Opaque source id, e.g. `"demo-http-npy-array"`               | Scene payload               | Resolver-owned handle. Unknown/unauthorized handles reject.                   |
| `format`                 |      Yes | `"npy"`                                                      | Scene payload               | Logical byte format name. Not MIME type.                                      |
| `decoder_id`             |      Yes | `"gsp.decoder.npy.v1"`                                       | Scene payload               | Stable id for trusted built-in decoder. Not import path.                      |
| `cache_policy.mode`      |       No | `"none"` or `"session-memory"`                               | Scene payload               | Resolver may force `"none"`.                                                  |
| `materialization_policy` |      Yes | `"full"`                                                     | Scene payload               | First proof materializes one bounded resource.                                |
| `materialization_target` |      Yes | `"array-resource"`                                           | Scene payload               | Optional later targets: `"texture-resource"`, `"image-visual"`.               |
| `metadata`               |       No | Non-sensitive `x-` metadata only                             | Scene payload               | Must reject URL-like, path-like, credential-like, or executable metadata.     |

### Resolver/admin-only configuration fields

These fields must never appear in scene payloads, manifests, replay JSON, public fixtures, or diagnostics. They may exist only in trusted resolver/admin configuration.

| Field                                        |          Required | Example value                                                             | Lives in                                                                          | Notes                                                                     |
| -------------------------------------------- | ----------------: | ------------------------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------- |
| `resolver_id`                                |               Yes | `"gsp.demo.http-resource-resolver"`                                       | Private resolver config; public capability may advertise id                       | Resolver identity.                                                        |
| `source_id`                                  |               Yes | `"demo-http-npy-array"`                                                   | Private resolver config; public capability may advertise only authorized demo ids | Opaque handle.                                                            |
| `authorized_tenants` / `authorized_sessions` |               Yes | Admin-specific selectors                                                  | Private resolver config                                                           | Must not leak in diagnostics.                                             |
| `source_contract.kind`                       |               Yes | `"array"`                                                                 | Private resolver config                                                           | Must match scene `source_kind`.                                           |
| `source_contract.shape`                      |               Yes | `[4, 4]`                                                                  | Private resolver config                                                           | Must match scene and decoded payload.                                     |
| `source_contract.dtype`                      |               Yes | `"float32"`                                                               | Private resolver config                                                           | Must match scene and decoded payload.                                     |
| `source_contract.channels`                   |               Yes | `1`                                                                       | Private resolver config                                                           | Must match scene.                                                         |
| `access.mechanism`                           |               Yes | `"http"`                                                                  | Private resolver config; public capability may advertise mechanism                | Access mechanism, not source type.                                        |
| `access.fetcher_id`                          |               Yes | `"gsp.fetcher.http.mock.v1"` first; `"gsp.fetcher.http.bounded.v1"` later | Private resolver config; public capability may advertise id                       | Trusted installed fetcher.                                                |
| `access.url`                                 | Yes for real HTTP | Private URL value                                                         | Private resolver config only                                                      | Never serialized to scenes, logs, diagnostics, fixtures, or replay.       |
| `access.method`                              |               Yes | `"GET"`                                                                   | Private resolver config; public capability may advertise allowed methods          | First proof only GET.                                                     |
| `access.allowed_hosts`                       | Yes for real HTTP | Admin exact host allowlist                                                | Private resolver config                                                           | Public capability says host allowlist exists, not hostnames.              |
| `access.require_https`                       |               Yes | `true`                                                                    | Private resolver config; public capability may advertise                          | Treat HTTPS as the only allowed live HTTP-family scheme.                  |
| `access.allow_redirects`                     |               Yes | `false`                                                                   | Private resolver config; public capability may advertise                          | First proof rejects all redirects.                                        |
| `access.timeout_ms`                          |               Yes | `2000` or lower admin value                                               | Private resolver config; public capability may advertise max                      | Hard upper bound.                                                         |
| `access.max_retries`                         |               Yes | `0`                                                                       | Private resolver config; public capability may advertise max                      | First proof should not retry automatically.                               |
| `access.max_response_bytes`                  |               Yes | e.g. `1048576`                                                            | Private resolver config; public capability may advertise max                      | Streaming hard cap.                                                       |
| `access.accepted_content_types`              |               Yes | `["application/x-npy", "application/octet-stream"]`                       | Private resolver config; public capability may advertise generic list             | MIME is checked but magic/header validation is authoritative.             |
| `access.accept_encoding`                     |               Yes | `"identity"`                                                              | Private resolver config; public capability may advertise                          | Reject compressed HTTP content encoding in first proof.                   |
| `decoder.decoder_id`                         |               Yes | `"gsp.decoder.npy.v1"`                                                    | Private resolver config; public capability may advertise                          | Built-in decoder id.                                                      |
| `decoder.allow_pickle`                       |               Yes | `false`                                                                   | Private resolver config; public capability may advertise                          | Non-negotiable.                                                           |
| `decoder.max_header_bytes`                   |               Yes | e.g. `4096`                                                               | Private resolver config; public capability may advertise max                      | Bounds `.npy` header parsing.                                             |
| `decoder.allowed_dtypes`                     |               Yes | `["uint8", "uint16", "float32"]`                                          | Private resolver config; public capability may advertise                          | No object/string/structured dtypes.                                       |
| `decoder.max_rank`                           |               Yes | `3`                                                                       | Private resolver config; public capability may advertise                          | Keep first proof small.                                                   |
| `decoder.max_elements`                       |               Yes | e.g. `1048576`                                                            | Private resolver config; public capability may advertise max                      | Prevents huge arrays.                                                     |
| `decoder.max_decoded_bytes`                  |               Yes | e.g. `4194304`                                                            | Private resolver config; public capability may advertise max                      | Separate from fetched byte cap.                                           |
| `decoder.allow_fortran_order`                |               Yes | `false`                                                                   | Private resolver config; public capability may advertise                          | First proof should accept C-contiguous arrays only.                       |
| `credential_policy`                          |               Yes | `"none"`                                                                  | Private resolver config; public capability may advertise                          | No credentials in first proof.                                            |
| `cache.mode`                                 |               Yes | `"none"` or `"session-memory"`                                            | Private resolver config; public capability may advertise allowed modes            | Resolver may override scene request downward.                             |
| `integrity.expected_digest`                  |          Optional | Private digest                                                            | Private resolver config only                                                      | Never expose digest if it could identify private source/config.           |
| `content_generation`                         |          Optional | Private opaque generation marker                                          | Private resolver config only                                                      | Used for cache isolation. Redact in public output unless explicitly safe. |

### Forbidden protocol fields

The following must be rejected if present in scenes, manifests, debug JSON fixtures, replay artifacts, or client-supplied descriptors:

```text
fetch_descriptor
url
uri
href
endpoint
host
port
path
bucket
object_key
signed_url
query
headers
cookies
authorization
credential_ref
credentials
secret
token
api_key
decoder_config
decoder_module
decoder_import
python_import
entry_point
package
pip
callback
hook
plugin
shader
shader_source
runtime_shader
cache_key
resolved_url
dns_result
ip_address
etag_from_resolver
private_digest
```

Unknown fields should reject unless they are under a documented, non-executable `x-` namespace and pass the sensitive-key, URL-like, and path-like validators.

### Positive descriptor example

```json
{
  "id": "array_http_demo_001",
  "source_kind": "array",
  "extension_id": null,
  "extension_version": null,
  "shape": [4, 4],
  "dtype": "float32",
  "channels": 1,
  "coordinate_system": "array-index",
  "extent": null,
  "origin": "upper",
  "locality": "preconfigured-source",
  "credential_policy": "none",
  "source_ref": {
    "resolver_id": "gsp.demo.http-resource-resolver",
    "source_id": "demo-http-npy-array"
  },
  "format": "npy",
  "decoder_id": "gsp.decoder.npy.v1",
  "cache_policy": {
    "mode": "none"
  },
  "materialization_policy": "full",
  "materialization_target": "array-resource",
  "metadata": {
    "x-purpose": "s022-http-single-resource-proof"
  }
}
```

### Rejected descriptor example 1: HTTP modeled as source type

```json
{
  "id": "bad_http_as_source_kind",
  "source_kind": "http",
  "locality": "preconfigured-source",
  "credential_policy": "none",
  "source_ref": {
    "resolver_id": "gsp.demo.http-resource-resolver",
    "source_id": "demo-http-npy-array"
  },
  "format": "npy",
  "decoder_id": "gsp.decoder.npy.v1"
}
```

Expected fatal diagnostic:

```text
GSP_SOURCE_CONTRACT_UNSUPPORTED
```

### Rejected descriptor example 2: client-supplied remote fetch

```json
{
  "id": "bad_client_url",
  "source_kind": "array",
  "shape": [4, 4],
  "dtype": "float32",
  "channels": 1,
  "locality": "direct-remote-fetch",
  "credential_policy": "none",
  "fetch_descriptor": {
    "url": "<redacted:url>"
  },
  "format": "npy",
  "decoder_id": "gsp.decoder.npy.v1"
}
```

Expected fatal diagnostics:

```text
GSP_SOURCE_LOCALITY_UNSUPPORTED
GSP_FETCH_DESCRIPTOR_REJECTED
GSP_REMOTE_FETCH_DISABLED
```

### Rejected descriptor example 3: credential ref and auth material

```json
{
  "id": "bad_credentials",
  "source_kind": "array",
  "shape": [4, 4],
  "dtype": "float32",
  "channels": 1,
  "locality": "preconfigured-source",
  "credential_policy": "preconfigured-ref",
  "credential_ref": "<redacted:credential-ref>",
  "source_ref": {
    "resolver_id": "gsp.demo.http-resource-resolver",
    "source_id": "demo-http-npy-array"
  },
  "headers": {
    "authorization": "<redacted:secret>"
  },
  "format": "npy",
  "decoder_id": "gsp.decoder.npy.v1"
}
```

Expected fatal diagnostics:

```text
GSP_CREDENTIAL_POLICY_UNSUPPORTED
GSP_CREDENTIAL_REF_REJECTED
GSP_INLINE_SECRET_REJECTED
```

### Rejected descriptor example 4: decoder plugin attempt

```json
{
  "id": "bad_decoder_plugin",
  "source_kind": "array",
  "shape": [4, 4],
  "dtype": "float32",
  "channels": 1,
  "locality": "preconfigured-source",
  "credential_policy": "none",
  "source_ref": {
    "resolver_id": "gsp.demo.http-resource-resolver",
    "source_id": "demo-http-npy-array"
  },
  "format": "npy",
  "decoder_id": "python.import:custom_decoder",
  "decoder_config": {
    "python_import": "some_package.some_decoder"
  }
}
```

Expected fatal diagnostics:

```text
GSP_DECODER_PLUGIN_DISABLED
GSP_MANIFEST_EXECUTION_FORBIDDEN
```

---

## 4. Capability Schema

### Public capability metadata

Public capability metadata may advertise support classes, limits, and authorized demo handles. It must not expose raw URLs, hostnames, paths, credentials, DNS results, cache keys, private digests, resolver internals, or account identities.

Example first-proof no-network/mock capability:

```json
{
  "data_sources": {
    "supported_source_localities": [
      "synthetic",
      "in-memory",
      "preconfigured-source"
    ],
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
    "remote_fetch_descriptors": {
      "accepted": false
    },
    "supports_server_side_fetch": {
      "accepted": false,
      "reason": "s022-mock-fetch-only"
    },
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
          "redirect_policy": {
            "mode": "reject",
            "max_redirects": 0
          },
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
        "content_types": [
          "application/x-npy",
          "application/octet-stream"
        ],
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
  "extensions": {
    "static_manifest_validation": true,
    "dynamic_discovery": false,
    "package_entry_points": false,
    "executable_hooks": false,
    "custom_decoders": false,
    "runtime_shaders": false
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

Example later live-HTTP capability, after the no-network proof passes and a review gate approves real I/O:

```json
{
  "data_sources": {
    "supports_server_side_fetch": {
      "accepted": true,
      "configured_only": true
    },
    "remote_access": {
      "scene_supplied_urls": false,
      "configured_access_only": true,
      "access_mechanisms": [
        {
          "id": "http",
          "fetcher_ids": ["gsp.fetcher.http.bounded.v1"],
          "network_io": true,
          "schemes": ["https"],
          "methods": ["GET"],
          "url_in_protocol": false,
          "host_policy": "admin-allowlist-private-address-reject",
          "redirect_policy": {
            "mode": "reject",
            "max_redirects": 0
          },
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
    }
  },
  "security": {
    "redaction_profile": "gsp.s022.http-single-resource.live",
    "diagnostic_redaction": true
  }
}
```

### Private resolver configuration

Private resolver configuration may contain raw access details, but those details must be excluded from public capability snapshots, scenes, manifests, fixtures, diagnostics, and replay artifacts.

Private-only fields include:

```text
access.url
access.allowed_hosts
access.private_ca_bundle
access.resolved_ip_candidates
access.connection_peer_ip
access.response_headers_raw
access.admin_request_headers
credentials.secret_material
credentials.account_identity
cache.private_key_material
cache.private_config_hash
integrity.expected_digest
content_generation
tenant authorization bindings
```

---

## 5. Decoder and Fetcher Pluggability Model

Fetchers and decoders are **trusted server capabilities**, not protocol payloads.

### Trusted identification

A fetcher is identified by a stable id:

```text
gsp.fetcher.http.mock.v1
gsp.fetcher.http.bounded.v1
```

A decoder is identified by a stable id:

```text
gsp.decoder.npy.v1
```

These ids mean: “the server already has this trusted implementation installed and configured.” They do **not** mean: “import this module,” “install this package,” or “load this plugin.”

### What scenes may reference

Scenes may reference only:

```text
source_kind
format
decoder_id
locality
credential_policy
source_ref.resolver_id
source_ref.source_id
cache_policy.mode
materialization_policy
materialization_target
shape
dtype
channels
coordinate_system
extent/origin when relevant
```

### What scenes and manifests must never contain

Scenes and manifests must never contain:

```text
executable code
Python import paths
package names as installation instructions
entry points
callbacks
hooks
dynamic plugin identifiers
decoder source code
arbitrary decoder configuration
runtime shaders
shader source
URLs
signed URLs
credentials
credential refs in first proof
request headers
cookies
local paths
object-store URIs
DNS results
cache keys
resolver outputs
```

### User-specific trusted configuration

User-specific access is allowed only through resolver/admin configuration:

```text
tenant/session/user authorization
→ allowed resolver_id/source_id pairs
→ resolver-owned access config
→ resolver-owned decoder config
→ resolver-owned limits/cache/integrity policy
```

The scene still receives only an opaque handle. Unauthorized and unknown handles should produce the same public fatal diagnostic, `GSP_SOURCE_HANDLE_UNKNOWN`, while private audit logs may distinguish unauthorized access if the deployment has a separate secure audit channel.

No user-specific executable payloads are allowed. User-specific does not mean user-supplied code; it means admin-configured policy scoped to a user, tenant, or session.

---

## 6. Validation and Rejection Rules

Security-sensitive failures must be fatal.

### Scene descriptor validation

| Rule                                                                 | Diagnostic                                                                                                 |
| -------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `source_kind` must be `"array"` for this proof.                      | `GSP_SOURCE_CONTRACT_UNSUPPORTED`                                                                          |
| `source_kind="http"` is invalid.                                     | `GSP_SOURCE_CONTRACT_UNSUPPORTED`                                                                          |
| `locality` must be `"preconfigured-source"`.                         | `GSP_SOURCE_LOCALITY_UNSUPPORTED`                                                                          |
| `fetch_descriptor` must be absent.                                   | `GSP_FETCH_DESCRIPTOR_REJECTED`                                                                            |
| Client-supplied remote fetch must remain disabled.                   | `GSP_REMOTE_FETCH_DISABLED`                                                                                |
| `source_ref` must contain known, authorized `resolver_id/source_id`. | `GSP_SOURCE_HANDLE_UNKNOWN`                                                                                |
| `credential_policy` must be `"none"` for first proof.                | `GSP_CREDENTIAL_POLICY_UNSUPPORTED`                                                                        |
| `credential_ref` must be absent.                                     | `GSP_CREDENTIAL_REF_REJECTED`                                                                              |
| Inline secrets, tokens, auth headers, cookies must be absent.        | `GSP_INLINE_SECRET_REJECTED`                                                                               |
| URL-like metadata must be absent.                                    | `GSP_URL_SCHEME_FORBIDDEN` or `GSP_FETCH_DESCRIPTOR_REJECTED`                                              |
| Path-like metadata must be absent.                                   | `GSP_LOCAL_PATH_FORBIDDEN`                                                                                 |
| Decoder id must be `"gsp.decoder.npy.v1"`.                           | `GSP_DECODER_PLUGIN_DISABLED` for plugin/import-like ids; `GSP_DECODER_UNSUPPORTED` for unknown stable ids |
| Executable manifest fields must be absent.                           | `GSP_MANIFEST_EXECUTION_FORBIDDEN`                                                                         |
| Unknown non-`x-` fields reject.                                      | `GSP_MANIFEST_SCHEMA_INVALID` or descriptor schema equivalent                                              |
| `shape`, `dtype`, `channels` must match resolver config.             | `GSP_CHUNK_METADATA_INVALID`                                                                               |
| `cache_policy.mode` must be `"none"` or `"session-memory"`.          | `GSP_CACHE_POLICY_UNSUPPORTED`                                                                             |

New diagnostic codes recommended for S022:

```text
GSP_SOURCE_CONTRACT_UNSUPPORTED
GSP_DECODER_UNSUPPORTED
GSP_CONTENT_TYPE_UNSUPPORTED
GSP_CONTENT_ENCODING_UNSUPPORTED
GSP_HTTP_STATUS_REJECTED
GSP_URL_FRAGMENT_FORBIDDEN
GSP_URL_QUERY_FORBIDDEN
GSP_URL_DNS_REBINDING_REJECTED
GSP_HTTP_TLS_VALIDATION_FAILED
GSP_HTTP_TIMEOUT
```

Use existing codes where possible; add the above only where existing S020 codes are too coarse.

### URL and SSRF validation

These rules apply to **resolver/admin configuration** and real HTTP fetcher operation. Scenes never provide URLs.

| Rule                                                                                                                                                                                               | Diagnostic                                                                 |
| -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| URL must parse as absolute, normalized URL in private resolver config.                                                                                                                             | `GSP_URL_SCHEME_FORBIDDEN` or private config error                         |
| Live first proof allows HTTPS only.                                                                                                                                                                | `GSP_URL_SCHEME_FORBIDDEN`                                                 |
| Userinfo is forbidden.                                                                                                                                                                             | `GSP_URL_USERINFO_FORBIDDEN`                                               |
| Fragments are forbidden.                                                                                                                                                                           | `GSP_URL_FRAGMENT_FORBIDDEN`                                               |
| Query strings are forbidden in first proof.                                                                                                                                                        | `GSP_URL_QUERY_FORBIDDEN`; use `GSP_INLINE_SECRET_REJECTED` if secret-like |
| Host must be exact-match admin allowlisted. No wildcard host allowlist in first proof.                                                                                                             | `GSP_URL_HOST_NOT_ALLOWED`                                                 |
| Literal IP hosts are forbidden unless a later review explicitly allows public IP literals.                                                                                                         | `GSP_URL_HOST_NOT_ALLOWED`                                                 |
| DNS results must reject loopback, private, link-local, multicast, unspecified, reserved, carrier-grade NAT, IPv6 ULA, and metadata-service addresses.                                              | `GSP_URL_RESOLVES_PRIVATE`                                                 |
| DNS rebinding must be prevented by resolving immediately before connect, approving every candidate, pinning the selected IP for the connection, and verifying the connected peer remains approved. | `GSP_URL_DNS_REBINDING_REJECTED`                                           |
| Redirects are rejected entirely in first proof.                                                                                                                                                    | `GSP_URL_REDIRECT_REJECTED`                                                |
| TLS certificate validation must be enabled.                                                                                                                                                        | `GSP_HTTP_TLS_VALIDATION_FAILED`                                           |
| HTTP method must be `GET`.                                                                                                                                                                         | `GSP_FETCH_DESCRIPTOR_REJECTED` or private config error                    |
| Response status must be 200.                                                                                                                                                                       | `GSP_HTTP_STATUS_REJECTED`                                                 |
| Timeout must be bounded by capability.                                                                                                                                                             | `GSP_HTTP_TIMEOUT`                                                         |
| Retries must be zero in first proof.                                                                                                                                                               | Private config error if configured otherwise                               |
| Connection pooling must not reuse connections across resolver/source/host policy boundaries.                                                                                                       | Private config error or fatal fetch diagnostic                             |

### Request headers and cookies

| Rule                                                                                                                                     | Diagnostic                                                                       |
| ---------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Scene-supplied headers reject.                                                                                                           | `GSP_FETCH_DESCRIPTOR_REJECTED`; `GSP_INLINE_SECRET_REJECTED` for sensitive keys |
| Scene-supplied cookies reject.                                                                                                           | `GSP_INLINE_SECRET_REJECTED`                                                     |
| Admin headers first proof limited to fixed safe headers such as `Accept`, `Accept-Encoding: identity`, and non-identifying `User-Agent`. | Private config error                                                             |
| `Authorization`, `Cookie`, `X-Api-Key`, bearer tokens, signed URL headers, and custom auth headers are forbidden in first proof.         | `GSP_INLINE_SECRET_REJECTED` or private config error                             |
| Ambient cloud credentials and default SDK credential chains are forbidden.                                                               | `GSP_CREDENTIAL_POLICY_UNSUPPORTED`                                              |

### Content-type, content-length, and byte limits

| Rule                                                                                      | Diagnostic                         |
| ----------------------------------------------------------------------------------------- | ---------------------------------- |
| Response `Content-Type` must be in resolver-configured allowlist.                         | `GSP_CONTENT_TYPE_UNSUPPORTED`     |
| `.npy` magic/header validation is authoritative even if content type is allowed.          | `GSP_CHUNK_METADATA_INVALID`       |
| `Content-Encoding` must be absent or `identity`.                                          | `GSP_CONTENT_ENCODING_UNSUPPORTED` |
| If `Content-Length` is present and exceeds `max_response_bytes`, reject before body read. | `GSP_CHUNK_LIMIT_EXCEEDED`         |
| If `Content-Length` is absent, stream with a hard byte cap and abort once exceeded.       | `GSP_CHUNK_LIMIT_EXCEEDED`         |
| Response body must not be logged or included in diagnostics.                              | `GSP_REPLAY_REDACTION_REQUIRED`    |
| Decoder output bytes must not exceed `max_decoded_bytes`.                                 | `GSP_DECOMPRESSION_LIMIT_EXCEEDED` |
| Materialized element count must not exceed `max_elements`.                                | `GSP_CHUNK_LIMIT_EXCEEDED`         |

### `.npy` decoder validation

`gsp.decoder.npy.v1` must be a built-in safe decoder with deterministic validation:

| Rule                                                                                                                                     | Diagnostic                                                                                                            |
| ---------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| Magic prefix must be valid `.npy`.                                                                                                       | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Version must be allowed, first proof `1.0` or `2.0`.                                                                                     | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Header length must be `<= max_header_bytes`.                                                                                             | `GSP_CHUNK_LIMIT_EXCEEDED`                                                                                            |
| Header parser must be non-executable. Do not use general `eval`.                                                                         | `GSP_MANIFEST_EXECUTION_FORBIDDEN` if executable path attempted; otherwise `GSP_CHUNK_METADATA_INVALID`               |
| Header keys must be exactly expected safe keys: `descr`, `fortran_order`, `shape`.                                                       | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| `fortran_order` must be `false` in first proof.                                                                                          | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Object dtype must reject.                                                                                                                | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Structured dtype must reject.                                                                                                            | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| String/unicode/void dtype must reject in first proof.                                                                                    | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Allowed dtypes first proof: `uint8`, `uint16`, `float32`.                                                                                | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Endianness must be native-neutral or little-endian for first proof. Big-endian requires later review or explicit byte-swap policy.       | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Rank must be 2 or 3 for image-like display; array resource may allow rank 1 only if capability says so. First fixture should use rank 2. | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Shape must match scene and resolver config exactly.                                                                                      | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Computed `prod(shape) * dtype.itemsize` must not overflow and must fit limits.                                                           | `GSP_CHUNK_LIMIT_EXCEEDED`                                                                                            |
| File must contain exactly the declared data payload after header. Trailing bytes reject.                                                 | `GSP_CHUNK_METADATA_INVALID`                                                                                          |
| Pickle must be disabled.                                                                                                                 | `GSP_INLINE_SECRET_REJECTED` is not appropriate; use `GSP_CHUNK_METADATA_INVALID` for object/pickle payload attempts. |

JPEG/PNG validation is **out of scope for first proof**. Any image decoder id should reject until a later design review defines image-specific validation for dimensions, channels, color modes, metadata stripping, decompression bombs, and dependency policy.

### Query/readback validation

| Rule                                                                               | Diagnostic                        |
| ---------------------------------------------------------------------------------- | --------------------------------- |
| Query coordinates must be within declared array bounds.                            | `GSP_QUERY_SCOPE_VIOLATION`       |
| Query result count must be bounded.                                                | `GSP_QUERY_RESULT_LIMIT_EXCEEDED` |
| Query payload must include source id, index coordinate, dtype, and value only.     | Schema validation diagnostic      |
| Query results must not include resolver URL, cache key, digest, or fetch metadata. | `GSP_REPLAY_REDACTION_REQUIRED`   |

---

## 7. Cache and Integrity Policy

### First-proof cache modes

Allowed:

```text
none
session-memory
```

Forbidden:

```text
shared-memory
persistent
cross-session
cross-tenant
browser-cache
http-cache-pass-through
filesystem-cache
object-store-cache
```

`none` should be the default. `session-memory` may be accepted only if the server can isolate cache entries by session and tenant.

### Cache-key isolation fields

The private cache key must include at least:

```text
tenant isolation id
session id
resolver_id
source_id
source authorization generation
source contract id/version
source_kind
declared shape/dtype/channels
access mechanism id
fetcher_id/version
private hash of resolver access config
credential policy
credential identity/version marker, if credentials are ever introduced
decoder_id/version
decoder policy hash
format
materialization_target
cache mode
byte limit policy
decoded-size limit policy
content generation marker or verified digest
```

The private cache key must not include raw URL, raw credentials, raw headers, or account identities directly. Use resolver-private keyed hashes for sensitive config components.

### Poisoning prevention

A cache entry may be stored only after all of the following pass:

```text
handle authorization
access policy validation
HTTP status validation
content-type validation
content-encoding validation
byte cap validation
decoder header validation
shape/dtype/channels contract validation
decoded-size validation
optional integrity digest validation
```

Do not cache failed fetches in the first proof. Do not share cache entries across tenants or sessions. Do not use HTTP cache headers as authority in first proof. Resolver config and content generation must invalidate session-memory cache entries when changed.

### Integrity rules

For no-network/mock fixtures, integrity can be deterministic by fixture resource id and expected decoded array.

For live HTTP, resolver/admin config may optionally include an expected digest. If `expected_digest` is configured, the fetched body must match before decoding or before storing in cache. If no digest is configured, cache must be session-only and bounded.

### Debug/replay omissions and redactions

Debug/replay output must omit or redact:

```text
raw URL
URL components
hostnames
paths
query strings
headers
cookies
credentials
credential refs
DNS results
peer IPs
TLS details that identify private infrastructure
raw response bodies
cache keys
private cache config hashes
private digests
resolver private config
authorization bindings
```

Allowed public debug fields:

```text
source_kind
format
decoder_id
resolver_id if public/authorized
source_id if public/authorized
cache_policy.mode
materialization_target
network_io true/false
redacted diagnostic code
limit class names and public numeric limits
```

Use existing placeholders:

```text
<redacted:credential-ref>
<redacted:source-ref>
<redacted:url>
<redacted:path>
<redacted:secret>
```

Add if needed:

```text
<redacted:cache-key>
<redacted:dns-result>
<redacted:http-header>
<redacted:digest>
```

---

## 8. Fixture and Conformance Strategy

### Start with no-network/mock fetch

The first S022 conformance package should use a mock HTTP fetcher:

```text
fetcher_id = "gsp.fetcher.http.mock.v1"
access.mechanism = "http"
network_io = false
```

The mock fetcher should return a configured response object from trusted test/admin configuration:

```text
status = 200
content_type = "application/x-npy"
content_encoding = "identity"
body = deterministic tiny .npy bytes
```

The serialized fixture must not include raw URLs. If URL policy must be tested, use symbolic test cases such as `"loopback-host-case"` or private in-memory unit vectors that assert redacted output, not tracked replay fixtures containing URLs.

### Positive fixtures

| Fixture                                | Purpose                                                                                                                         |
| -------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------- |
| `s022_http_mock_npy_array_success`     | Known opaque handle resolves through mock HTTP access to a tiny `.npy` array.                                                   |
| `s022_http_mock_array_materialization` | Materializes `array-resource` with exact shape, dtype, and values.                                                              |
| `s022_http_mock_matplotlib_reference`  | Renders a 2-D array through Matplotlib reference path.                                                                          |
| `s022_http_mock_array_query`           | Query/readback returns bounded value payload for valid index.                                                                   |
| `s022_http_mock_capability`            | Capability advertises HTTP access mechanism with `network_io=false`, configured-only access, `.npy` decoder, and no scene URLs. |
| `s022_http_mock_session_cache`         | Optional session-memory cache hit remains isolated to same session/source/decoder/policy.                                       |

### Negative fixtures

| Fixture                                       | Expected fatal diagnostics                                     |
| --------------------------------------------- | -------------------------------------------------------------- |
| Client supplies `fetch_descriptor`.           | `GSP_FETCH_DESCRIPTOR_REJECTED`, `GSP_REMOTE_FETCH_DISABLED`   |
| Client uses `locality="direct-remote-fetch"`. | `GSP_SOURCE_LOCALITY_UNSUPPORTED`, `GSP_REMOTE_FETCH_DISABLED` |
| Client uses `source_kind="http"`.             | `GSP_SOURCE_CONTRACT_UNSUPPORTED`                              |
| Unknown resolver handle.                      | `GSP_SOURCE_HANDLE_UNKNOWN`                                    |
| Unauthorized resolver handle.                 | Publicly `GSP_SOURCE_HANDLE_UNKNOWN`                           |
| `credential_ref` present.                     | `GSP_CREDENTIAL_REF_REJECTED`                                  |
| Inline secret/header/cookie present.          | `GSP_INLINE_SECRET_REJECTED`                                   |
| URL-like metadata present.                    | `GSP_URL_SCHEME_FORBIDDEN` or `GSP_FETCH_DESCRIPTOR_REJECTED`  |
| Path-like metadata present.                   | `GSP_LOCAL_PATH_FORBIDDEN`                                     |
| Decoder id looks like import path.            | `GSP_DECODER_PLUGIN_DISABLED`                                  |
| `decoder_config` contains executable fields.  | `GSP_MANIFEST_EXECUTION_FORBIDDEN`                             |
| Mock response content type not allowed.       | `GSP_CONTENT_TYPE_UNSUPPORTED`                                 |
| Mock response content encoding compressed.    | `GSP_CONTENT_ENCODING_UNSUPPORTED`                             |
| Mock response too large.                      | `GSP_CHUNK_LIMIT_EXCEEDED`                                     |
| `.npy` invalid magic/header.                  | `GSP_CHUNK_METADATA_INVALID`                                   |
| `.npy` object dtype or pickle-like payload.   | `GSP_CHUNK_METADATA_INVALID`                                   |
| `.npy` shape mismatch.                        | `GSP_CHUNK_METADATA_INVALID`                                   |
| `.npy` decoded bytes exceed limit.            | `GSP_DECOMPRESSION_LIMIT_EXCEEDED`                             |
| Query outside bounds.                         | `GSP_QUERY_SCOPE_VIOLATION`                                    |
| Query result too large.                       | `GSP_QUERY_RESULT_LIMIT_EXCEEDED`                              |

### Redaction fixtures

Redaction fixtures should assert that diagnostics and replay artifacts contain no:

```text
URL
host
path
query string
request header
cookie
authorization value
credential ref
DNS result
IP address
cache key
private digest
raw response body
resolver private config
```

They should assert the presence of redaction placeholders instead.

### Capability fixtures

One capability fixture should represent no-network/mock S022:

```text
HTTP mechanism advertised
network_io=false
scene_supplied_urls=false
configured_access_only=true
decoder_ids=["gsp.decoder.npy.v1"]
formats=["npy"]
credential_policies=["none"]
cache_modes=["none", "session-memory"]
redaction_profile="gsp.s022.http-single-resource.mock"
```

A later optional live capability fixture may exist only behind an explicit gate:

```text
network_io=true
fetcher_id="gsp.fetcher.http.bounded.v1"
scene_supplied_urls=false
configured_access_only=true
```

### Cache-key fixtures

Cache conformance should verify:

```text
same session + same resolver/source/decoder/policy can hit session-memory cache
different session misses
different tenant misses
different decoder policy misses
different source generation misses
debug output never exposes cache key
cache entry not stored after failed validation
```

### Optional real network smoke gate

Real network smoke tests must be disabled by default and require all of the following:

```text
no-network/mock conformance passes
URL/SSRF validation helpers pass
DNS rebinding protection implemented
TLS verification implemented
redirect rejection implemented
byte/time/retry limits implemented
redaction tests pass
admin config supplied out of band
no raw URL committed to fixture/replay files
credential_policy remains "none"
```

Live smoke tests should fetch only a tiny public `.npy` resource configured outside the repository or fixture corpus. If that cannot be done without exposing URLs or weakening redaction, skip live smoke and stop for review.

---

## 9. Stop Conditions

Another design review is required before continuing if any of the following become necessary:

1. Client-supplied arbitrary URLs, signed URLs, object-store URIs, or fetch descriptors.
2. Any credential mode beyond `credential_policy="none"` for the first HTTP proof.
3. Auth headers, cookies, bearer tokens, API keys, signed query strings, or ambient cloud credentials.
4. Redirect following.
5. Plain `http` live access instead of HTTPS-only access.
6. Private network, loopback, link-local, intranet, metadata-service, or local-file access.
7. Wildcard host allowlists or user-controlled hostnames.
8. DNS rebinding protection cannot be enforced.
9. TLS verification cannot be enforced.
10. Need for persistent, shared, cross-session, or cross-tenant cache.
11. Need to expose cache keys, DNS results, raw URLs, response headers, response bodies, digests, or resolver internals in diagnostics/replay.
12. Need for JPEG/PNG, compressed arrays, Zarr, OME-Zarr, COG, tile pyramids, map tiles, volume chunks, or point-cloud chunks.
13. Need for dynamic decoder plugins, Python imports, package entry points, callbacks, runtime shaders, or executable manifests.
14. Need for `.npy` object dtype, structured dtype, string dtype, pickle, Fortran-order arrays, unknown shape, or unbounded dtype/rank.
15. Need for automatic retry behavior beyond zero retries.
16. Need for decompression or HTTP content encodings other than identity.
17. Matplotlib reference conformance cannot validate the materialized array.
18. Query/readback cannot be bounded by declared shape and result limits.
19. Security-sensitive unsupported behavior would be simplified or silently deactivated instead of fatally rejected.
20. Real network I/O is requested before mock/no-network conformance and redaction pass.

---

## 10. Staged Implementation Plan

Implementation remains paused until this response is pasted or committed into durable project material and reviewed.

| Mission   | Title                                               | Scope                              | Deliverables                                                                                                                                                                                                                                                                                                                                       | Validation                                                               | Stop Conditions                                                                                    |
| --------- | --------------------------------------------------- | ---------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------- |
| S022-M059 | Accept first-proof ADR                              | Spec/ADR only                      | ADR declaring HTTP single-resource first and `.npy` typed array as first target. Explicitly states HTTP is access mechanism, not source type.                                                                                                                                                                                                      | ADR reviewed against S020/S021 hard stops.                               | Any desire to start with tiles, JPEG/PNG, Zarr, credentials, or live network before mock proof.    |
| S022-M060 | Protocol schema update                              | Spec only                          | Add `source_kind="array"`, `format`, `decoder_id`, `materialization_target`, and first-proof descriptor constraints. Mark forbidden fields.                                                                                                                                                                                                        | Schema examples validate; rejected examples produce planned diagnostics. | Current enum model cannot represent array without overloading `opaque` or `http`.                  |
| S022-M061 | Capability schema update                            | Spec only                          | Add public fields for `remote_access`, configured-only HTTP, decoder list, byte/decode limits, cache modes, redaction profile.                                                                                                                                                                                                                     | Capability fixture matches schema and exposes no private config.         | Capability snapshot would need to expose URL, host, credential, DNS, or cache internals.           |
| S022-M062 | HTTP resolver policy spec                           | Spec/ADR only                      | Define resolver/admin config fields, URL/SSRF policy, host allowlist, DNS rebinding protection, redirect rejection, TLS, content limits, and redaction.                                                                                                                                                                                            | Security review checklist passes on paper.                               | Any policy cannot be enforced deterministically.                                                   |
| S022-M063 | Diagnostic code update                              | Spec only                          | Add required S022 diagnostic codes: `GSP_SOURCE_CONTRACT_UNSUPPORTED`, `GSP_DECODER_UNSUPPORTED`, `GSP_CONTENT_TYPE_UNSUPPORTED`, `GSP_CONTENT_ENCODING_UNSUPPORTED`, `GSP_HTTP_STATUS_REJECTED`, `GSP_URL_FRAGMENT_FORBIDDEN`, `GSP_URL_QUERY_FORBIDDEN`, `GSP_URL_DNS_REBINDING_REJECTED`, `GSP_HTTP_TLS_VALIDATION_FAILED`, `GSP_HTTP_TIMEOUT`. | Negative fixture matrix maps every rejection to stable codes.            | Too many overlapping codes or inability to preserve existing S020 diagnostics.                     |
| S022-M064 | No-network mock HTTP fetcher contract               | No-network/mock validation         | Define or implement `gsp.fetcher.http.mock.v1` as a trusted test fetcher that returns configured response objects without network I/O.                                                                                                                                                                                                             | Tests prove no socket/path/network calls occur.                          | Mock requires raw URLs in serialized fixtures or performs network I/O.                             |
| S022-M065 | Built-in `.npy` decoder validation helper           | No-network implementation          | Implement/validate `gsp.decoder.npy.v1` with safe header parsing, dtype/shape/rank/byte limits, `allow_pickle=false`, no object/structured/string dtype.                                                                                                                                                                                           | Positive tiny array passes; invalid header/dtype/shape/size cases fail.  | Decoder needs pickle, object dtype, executable parsing, or unbounded allocation.                   |
| S022-M066 | Array materialization and Matplotlib reference path | No-network implementation          | Materialize decoded array as `array-resource`; optionally render rank-2 arrays with Matplotlib; add bounded array query payload.                                                                                                                                                                                                                   | Deterministic render/query fixture passes.                               | Backend requires Datoviz or cannot provide reference Matplotlib conformance.                       |
| S022-M067 | No-network conformance package                      | No-network fixtures                | Positive, negative, capability, redaction, cache-key, and query fixtures for mock HTTP `.npy`.                                                                                                                                                                                                                                                     | Full no-network fixture suite passes; replay contains no forbidden data. | Any fixture leaks URL, path, secret, DNS result, raw body, cache key, or resolver private config.  |
| S022-M068 | Session-memory cache proof                          | No-network/mock implementation     | Optional bounded session-memory cache for decoded arrays, with private isolated key and no failure caching.                                                                                                                                                                                                                                        | Same-session hit and cross-session/tenant miss fixtures pass.            | Need persistent/shared cache or cache key exposure.                                                |
| S022-M069 | Pre-network design gate                             | Review gate                        | Checklist confirming SSRF, DNS rebinding, TLS, redirects, timeouts, byte caps, content validation, and redaction are implemented and tested.                                                                                                                                                                                                       | Review approval recorded before real I/O.                                | Any network hard stop remains unresolved.                                                          |
| S022-M070 | Bounded live HTTP fetcher                           | Real HTTP I/O, disabled by default | Implement `gsp.fetcher.http.bounded.v1` behind admin opt-in only. HTTPS GET, exact host allowlist, no redirects, no credentials, identity encoding, byte/time caps.                                                                                                                                                                                | Unit tests for policy; no-network fixtures still default.                | Need credentials, redirects, query strings, private hosts, wildcard hosts, or raw URL diagnostics. |
| S022-M071 | Optional live smoke test                            | Opt-in integration only            | Out-of-band admin config points to tiny public `.npy`; no URL committed to fixtures/replay.                                                                                                                                                                                                                                                        | Smoke passes only when explicitly enabled; skipped otherwise.            | Cannot run without committing URL or weakening redaction.                                          |
| S022-M072 | Next-source-family review                           | Spec/ADR only                      | Decide next target: JPEG/PNG image/texture, tiled image over HTTP, Zarr chunk, or OME-Zarr.                                                                                                                                                                                                                                                        | New review reuses S022 access/decoder policy spine.                      | Any new decoder/access/source semantics are introduced without ADR/spec update.                    |

# GSP Conformance Fixtures - Draft

Conformance fixtures define stable semantic behavior for the v0.1 reference path.

## Schema authority

GSP has two distinct JSON-facing conformance artifacts:

| Artifact | Kind | Authority |
|---|---|---|
| Diagnostic report | `gsp.conformance.debug-json` | Non-authoritative debug/CI output. |
| Fixture schema | `gsp.conformance.fixture` | Authoritative fixture/replay schema. |

The diagnostic report must not become the compatibility contract. It exists for inspection,
debugging, and lightweight CI reports. It keeps `schema_authority=false`.

The authoritative fixture schema starts at `gsp.conformance.fixture@0.1.0` and targets GSP protocol
`0.1`.

JSON/base64 fixture support is optional transport/replay infrastructure. The local `inproc` desktop
path must continue to pass direct protocol objects, NumPy arrays, memoryviews, and backend handles
without mandatory JSON/base64 serialization.

## Fixture schema versioning

Fixture schema versioning and GSP protocol versioning are independent:

- `schema_kind="gsp.conformance.fixture"` identifies the authoritative fixture schema.
- `schema_version` versions the JSON fixture representation.
- `protocol.gsp_protocol_version` identifies the GSP protocol semantics under test.
- `protocol.compatible_protocol_range` describes compatible protocol versions.
- extension payloads version independently through payload kinds such as `gsp.guide-query@0.1`.
- fixture content changes increment `metadata.fixture_revision`; they do not necessarily change
  `schema_version`.

The first schema version is `0.1.0`.

Compatibility rules:

- readers must reject unknown major schema versions;
- readers may accept newer minor schema versions only when every `features_required` entry is
  recognized;
- unknown optional fields may be preserved or ignored;
- unknown required features must cause rejection;
- new array encodings, compression modes, external references, and materialization modes must be
  feature-gated.

## Authoritative fixture skeleton

The first authoritative fixture schema has these top-level sections:

| Section | Required | Purpose |
|---|---:|---|
| `schema_kind` | yes | Must be `gsp.conformance.fixture`. |
| `schema_version` | yes | Fixture schema version, initially `0.1.0`. |
| `metadata` | yes | Fixture identity, revision, title, stability, determinism, tags. |
| `protocol` | yes | GSP protocol version/range and transport notes. |
| `features_required` | yes | Required fixture-schema features a reader must understand. |
| `features_optional` | no | Optional feature declarations. |
| `capabilities` | yes | Capability surface required or exercised by the fixture. |
| `extension_manifests` | conditional | Required when extension payloads or sources appear. |
| `resources` | yes | Eager array resources and virtual source descriptors. |
| `scene` | yes | Panels, views, visuals, guides, and other semantic scene objects. |
| `queries` | yes | Query requests and expected results. |
| `backend_expectations` | yes | Backend pass/skip/xfail/fail expectations. |
| `outputs` | no | Optional semantic or rendered-output checks. |

## Resource skeleton

Replayable eager arrays will live under `resources.arrays`. M041 does not implement validation, but
the first slice reserves these fields for M042:

- `resource_id`;
- `array_id`;
- `kind`;
- `semantic_role`;
- `dtype`;
- `shape`;
- `byte_order`;
- `memory_order`;
- `encoding`;
- `compression`;
- `byte_length`;
- `checksum`;
- `data_base64`.

First-slice array validation is deferred to M042. The intended initial constraints are small,
deterministic, contiguous arrays only; `float32` and `uint8`; `memory_order="C"`;
`encoding="base64"`; `compression="none"`; SHA-256 over decoded uncompressed bytes.

M042 implements validation for this first slice. `uint8` chunks use
`byte_order="not-applicable"`; `float32` chunks use `byte_order="little"`. The validator rejects
unsupported dtypes, encodings, compression modes, memory orders, byte-length mismatches, checksum
mismatches, invalid base64, and missing required fields.

Virtual and tiled sources live under `resources.virtual_sources`. They describe logical source data,
tiling, bounds behavior, and deterministic materialization rules. They are not full eager buffers,
and huge virtual datasets must not be serialized as ordinary arrays.

## Query and extension payload skeleton

Fixture query records serialize the unified panel-query model:

- request id;
- panel id;
- coordinate space;
- coordinate;
- scope;
- hit policy;
- requested payloads.

Expected results serialize core `QueryResult` fields only. Extension-specific query data must use
versioned envelopes in `extension_payloads`. Core query results must not absorb extension-specific
fields.

Non-hit results must not include hit payload fields. `unsupported`, `stale`, `dropped`, and
`failed` require diagnostics.

## Backend expectation skeleton

Backend expectations distinguish policy from actual result:

| Value | Meaning |
|---|---|
| `pass` | Backend is expected to execute and satisfy all mandatory semantic checks. |
| `skip` | Backend is visible but not expected to execute due to missing runtime support/capability. |
| `xfail` | Backend is expected to execute but fail a known tracked requirement. |
| `fail` | Backend executed and failed a mandatory requirement. Usually an actual result, not a desired expectation. |

Matplotlib is the required reference backend for the first slice. Datoviz remains visible as `skip`
with a diagnostic until stable runtime query identity payloads exist.

## Non-normative fixture example

This example shows intended shape only. It is not a committed fixture file and is not a validation
contract for M041.

```json
{
  "schema_kind": "gsp.conformance.fixture",
  "schema_version": "0.1.0",
  "metadata": {
    "fixture_id": "gsp.fixtures.v0_1.point_image_guides_tiled",
    "fixture_revision": 1,
    "title": "Point/image/guide/tiled semantic conformance fixture",
    "stability": "draft-conformance",
    "deterministic": true
  },
  "protocol": {
    "gsp_protocol_version": "0.1",
    "compatible_protocol_range": ">=0.1 <0.2",
    "runtime_transport_required": false
  },
  "features_required": [
    "fixture.base64-array@0.1",
    "fixture.query-result@0.1",
    "fixture.backend-expectation@0.1"
  ],
  "features_optional": [
    "fixture.virtual-source@0.1"
  ],
  "capabilities": {
    "visual_families": ["point", "image"],
    "query": {
      "scopes": ["data", "guides", "all-rendered"],
      "hit_policies": ["frontmost", "all"],
      "payloads": ["identity", "coordinate", "color", "value"]
    }
  },
  "extension_manifests": [
    {
      "extension_id": "gsp.guides",
      "extension_version": "0.1",
      "payload_kinds": ["gsp.guide-query@0.1"]
    }
  ],
  "resources": {
    "arrays": [
      {
        "resource_id": "res.points.positions",
        "array_id": "arr.points.positions.xy",
        "kind": "buffer",
        "semantic_role": "point.positions.xy",
        "dtype": "float32",
        "shape": [2, 2],
        "byte_order": "little",
        "memory_order": "C",
        "encoding": "base64",
        "compression": "none",
        "byte_length": 16,
        "checksum": {
          "algorithm": "sha256",
          "scope": "decoded_uncompressed_bytes",
          "value": "<lowercase-hex-sha256>"
        },
        "data_base64": "<standard-base64>"
      }
    ],
    "virtual_sources": []
  },
  "scene": {
    "panels": [{"panel_id": "panel.main"}],
    "visuals": [
      {
        "visual_id": "visual.points.foreground",
        "family": "point",
        "panel_id": "panel.main",
        "resources": {"positions": "res.points.positions"}
      }
    ],
    "guides": []
  },
  "queries": [
    {
      "query_id": "query.point.frontmost",
      "request": {
        "panel_id": "panel.main",
        "coordinate_space": "data",
        "coordinate": [0.25, 0.25],
        "scope": "data",
        "hit_policy": "frontmost",
        "payloads": ["identity", "coordinate", "color", "value"]
      },
      "expected_result": {
        "request_id": "query.point.frontmost",
        "status": "hit",
        "hit": true,
        "panel_coordinate": [0.25, 0.25],
        "visual_family": "point",
        "visual_id": "visual.points.foreground",
        "item_id": 0,
        "extension_payloads": []
      }
    }
  ],
  "backend_expectations": {
    "matplotlib": {
      "expectation": "pass",
      "required": true,
      "diagnostic_required_on_non_pass": true
    },
    "datoviz": {
      "expectation": "skip",
      "required": false,
      "reason_code": "datoviz.runtime-query-identity-fields-unavailable",
      "diagnostic_required": true
    }
  },
  "outputs": {
    "semantic_replay": {
      "required": true
    }
  }
}
```

## M036 in-process replay harness

The first S018 replay layer is Python/in-process only. It replays existing conformance fixtures
without JSON/base64 serialization and returns semantic results for:

- capability snapshot identity and advertised extension surface;
- point-over-image query frontmost behavior;
- guide tick hit and guide miss behavior;
- local tiled-source clipped mosaic and typed query payload behavior.

This harness is not a transport encoding and is not a schema authority. JSON/base64 fixture files,
debug-json replay, backend matrices, and pixel/image comparison remain follow-up S018 work.

## M037 backend conformance matrix

The backend matrix is still Python/in-process. It records expected replay outcomes explicitly:

- `matplotlib`: `pass`, using the deterministic reference replay harness;
- `datoviz`: `skip`, with a diagnostic reason derived from the active Python binding state.

The Datoviz entry is intentionally present even before it can pass. This keeps conformance reports
honest: Datoviz is visible in the matrix, but skipped until a backend replay adapter can map stable
application visual IDs and define guide/tiled-source expectations.

This matrix is not a runtime certification suite and does not add JSON/base64 fixtures.

## M038 debug-json report

The debug-json report serializes the current semantic replay summary into JSON-safe dictionaries.
It is intended for inspection and lightweight report comparison only.

Required properties:

- includes backend outcomes from the conformance matrix;
- includes Matplotlib semantic replay query summaries;
- includes the Datoviz skip reason;
- omits NumPy arrays and memory buffers;
- sets `schema_authority=false`.

This report is not the versioned fixture schema and is not a base64 array transport.

## M039 diagnostic report hardening

`conformance_debug_report_json()` and `tools/conformance_debug_report.py` provide deterministic,
sorted, newline-terminated JSON output for diagnostics.

The report remains diagnostic:

- `schema_authority` stays `false`;
- output is stable enough for local inspection and CI logs;
- consumers must not treat the report shape as the versioned compatibility schema;
- array/base64 transport remains deferred.

## M040 versioned fixture schema decision packet

The future versioned fixture schema and array/base64 transport require architectural review before
implementation. The decision packet is `.agent/consultations/P005-versioned-conformance-fixture-schema.md`.

The consultation response is recorded in `.agent/consultations/P005-response.md`.
It recommends a separate authoritative `gsp.conformance.fixture` schema while keeping the current
`debug-json` report diagnostic and non-authoritative.

Next implementation should begin with an ADR/spec skeleton before any array transport, JSON fixture
files, or Datoviz conformance pass requirements are added.

## M041 fixture schema ADR and spec skeleton

ADR-0007 accepts a separate authoritative `gsp.conformance.fixture` schema beginning at version
`0.1.0`. This spec now defines the required top-level sections, fixture/protocol versioning rules,
resource/query/backend expectation skeletons, and a non-normative pseudo-JSON example.

Array transport validation, JSON fixture files, and Datoviz pass requirements remain deferred.

## M043 minimal JSON conformance fixture

`fixtures/conformance/minimal_v0_1.json` encodes the current point, image, guide, and tiled-source
semantic slice as `gsp.conformance.fixture@0.1`.

The fixture uses typed base64 chunks for eager point/image arrays. Guide ticks and labels remain
semantic JSON values. The tiled source is represented as a virtual source manifest, not a full eager
array.

`fixtures.conformance.json_fixture.replay_minimal_json_fixture()` validates the fixture and replays
it through the existing Matplotlib reference adapter. The Python/in-process fixtures remain the local
fast path.

## S020 security and redaction fixtures

S020 conformance adds a no-network security validation profile. Fixtures in this profile validate
that unsafe source descriptors, credentials, manifests, cache policies, and query/readback payloads
are rejected or redacted without performing network I/O.

Fixtures, replay logs, diagnostics, and debug JSON must never serialize:

- raw passwords, API keys, bearer tokens, SSH keys, cloud keys, certificates, cookies, auth headers,
  or session tokens;
- signed URLs, presigned S3/GCS URLs, SAS URLs, query-string credentials, or temporary credentials;
- credential resolver output;
- unredacted credential references that reveal provider, account, project, bucket, or user identity;
- absolute local paths, home directories, UNC paths, symlink-resolved paths, or server-internal mount
  paths;
- internal hostnames, private IPs, metadata endpoint addresses, DNS results, or network topology;
- cross-tenant cache keys or cache contents;
- restricted external chunks unless the fixture is explicitly sanitized and public;
- query/readback payloads outside declared fixture scope;
- manifest fields that imply executable code.

Stable redaction placeholders are:

- `<redacted:credential-ref>`;
- `<redacted:source-ref>`;
- `<redacted:url>`;
- `<redacted:path>`.

Minimum S020 negative fixture groups:

- static manifest with Python import path, entry point, executable hook, shader loading directive,
  decoder callback, or executable-looking unknown field;
- `preconfigured-source` with an unknown handle;
- `direct-remote-fetch`, `server-resolved-remote`, or `local-file-sandboxed` when not advertised;
- descriptors containing raw URL, object-store URI, local path, request headers, cookies, signed URL,
  inline secret, unsupported credential policy, or oversized logical/chunk metadata;
- SSRF-like fixture strings such as loopback, localhost, metadata-service, `file://`, `gopher://`,
  `data:`, URL userinfo, fragments, encoded private IP variants, and redirect-to-private targets;
- cache keys that cross tenant, credential, source, resolver, extension version, or generation
  boundaries;
- oversized decoded chunk, tile count, materialization, prefetch, retry, concurrency, or query result
  requests;
- query/readback outside declared source bounds or with extension payload schema mismatch.

A sanitized `preconfigured-source` fixture may carry only a resolver id, source id, source kind,
credential policy, no-network flag, and public deterministic test metadata. It must not serialize
the underlying URL, path, bucket, credential, resolver output, or restricted data.

Security diagnostics in these fixtures are stable expected results. Unsupported security behavior
must reject fatally rather than simplify or silently deactivate.

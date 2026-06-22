# Consultation Result: Versioned Conformance Fixture Schema

## Recommendation

* Create a **separate authoritative fixture schema** named `gsp.conformance.fixture`; do **not** graduate the current `gsp.conformance.debug-json` report into the compatibility contract. The debug report should remain diagnostic, deterministic, and explicitly non-authoritative. This follows the packet’s stated constraint that debug-json currently has `schema_authority=false` and omits array transport.

* Treat JSON fixtures as a **conformance, replay, debugging, and simple transport artifact**, not as the required runtime representation. The local desktop `inproc` path must continue to pass Python objects, NumPy arrays, memoryviews, and backend handles without mandatory JSON/base64 serialization.

* Define the first fixture schema slice around the current S018 semantic coverage: stable object IDs, capability snapshot, point visual, image visual, guides, unified panel queries, tiled-source semantic query behavior, Matplotlib pass, and Datoviz visible skip.

* Use a top-level fixture shape with explicit sections for `metadata`, `protocol`, `capabilities`, `extension_manifests`, `resources`, `scene`, `queries`, `backend_expectations`, and `outputs`.

* Represent ordinary eager arrays through a typed `resources.arrays` table. First-slice replayable eager arrays should use **base64-encoded contiguous bytes** with required dtype, shape, byte order, memory order, byte length, checksum, semantic role, and resource ID metadata.

* Do not use nested JSON arrays for ordinary buffer resources in the first slice. Small semantic lists such as guide ticks, extents, panel coordinates, and labels may remain normal JSON values because they are scene semantics, not transport buffers.

* Represent huge or virtual datasets as **virtual data source manifests**, not eager buffers. A tiled source fixture should describe logical data, tiling, materialization rules, query semantics, and optional deterministic local generator identity without pretending that the whole source is a `BufferResource`.

* Preserve extension boundaries by serializing extension query data inside versioned payload envelopes such as `gsp.guide-query@0.1` and `gsp.tiled-image@0.1.query`. Core query result fields must not absorb extension-specific fields.

* Backend certification should be capability-driven and honest: Matplotlib is expected to pass the first slice; Datoviz remains in the matrix as `skip` with a required diagnostic until stable runtime query identity payloads exist.

## Schema Shape

```jsonc
{
  "schema_kind": "gsp.conformance.fixture",
  "schema_version": "0.1.0",

  "metadata": {
    "fixture_id": "gsp.fixtures.v0_1.point_image_guides_tiled",
    "fixture_revision": 1,
    "title": "Point/image/guide/tiled semantic conformance fixture",
    "description": "Minimal v0.1 semantic replay fixture for Matplotlib reference conformance.",
    "stability": "draft-conformance",
    "created_by": "GSP conformance suite",
    "deterministic": true,
    "tags": ["v0.1", "semantic", "matplotlib-reference"]
  },

  "protocol": {
    "gsp_protocol_version": "0.1",
    "compatible_protocol_range": ">=0.1 <0.2",
    "required_transports": ["inproc", "debug-json"],
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
    "snapshot_id": "gsp.capability-snapshot.v0_1.reference",
    "visual_families": ["point", "image"],
    "query": {
      "coordinate_spaces": ["panel", "data"],
      "scopes": ["data", "guides", "all-rendered"],
      "hit_policies": ["frontmost", "all"],
      "payloads": ["identity", "coordinate", "color", "value"]
    },
    "resources": {
      "buffer": {
        "contiguous_required": true,
        "strided_attribute_views_allowed": true,
        "non_contiguous_ownership_supported": false
      },
      "virtual_data_source": true
    },
    "extensions": [
      {
        "payload_kind": "gsp.guide-query@0.1",
        "required": true
      },
      {
        "payload_kind": "gsp.tiled-image@0.1.query",
        "required": false
      }
    ]
  },

  "extension_manifests": [
    {
      "extension_id": "gsp.guides",
      "extension_version": "0.1",
      "payload_kinds": ["gsp.guide-query@0.1"],
      "capability_required": "guides.query@0.1"
    },
    {
      "extension_id": "gsp.tiled-image",
      "extension_version": "0.1",
      "payload_kinds": [
        "gsp.tiled-image@0.1.source",
        "gsp.tiled-image@0.1.query"
      ],
      "capability_required": "virtual-source.tiled-image@0.1"
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
        "shape": [3, 2],
        "byte_order": "little",
        "memory_order": "C",
        "encoding": "base64",
        "compression": "none",
        "byte_length": 24,
        "checksum": {
          "algorithm": "sha256",
          "scope": "decoded_uncompressed_bytes",
          "value": "<lowercase-hex-sha256>"
        },
        "data_base64": "<standard-base64>"
      }
    ],

    "virtual_sources": [
      {
        "source_id": "source.tiled.synthetic_rgba",
        "source_kind": "tiled-image",
        "payload_kind": "gsp.tiled-image@0.1.source",
        "logical": {
          "dtype": "uint8",
          "shape": [64, 64, 4],
          "color_model": "rgba8",
          "extent": [0.0, 0.0, 1.0, 1.0],
          "origin": "upper"
        },
        "tiling": {
          "tile_shape": [16, 16, 4],
          "addressing": "source-pixel-rect"
        },
        "materialization": {
          "mode": "synthetic-local",
          "generator_id": "gsp.fixtures.synthetic.rgba-tiled-image@0.1",
          "parameters": {
            "seed": 0
          }
        }
      }
    ]
  },

  "scene": {
    "panels": [
      {
        "panel_id": "panel.main",
        "pixel_rect": [0, 0, 640, 480],
        "data_rect": [0.0, 0.0, 1.0, 1.0]
      }
    ],

    "visuals": [
      {
        "visual_id": "visual.image.background",
        "family": "image",
        "panel_id": "panel.main",
        "z_index": 0,
        "extent": [0.0, 0.0, 1.0, 1.0],
        "origin": "upper",
        "resources": {
          "rgba": "res.image.rgba8"
        }
      },
      {
        "visual_id": "visual.points.foreground",
        "family": "point",
        "panel_id": "panel.main",
        "z_index": 10,
        "resources": {
          "positions": "res.points.positions",
          "colors": "res.points.colors",
          "sizes": "res.points.sizes"
        }
      }
    ],

    "guides": [
      {
        "guide_id": "guide.x.major",
        "panel_id": "panel.main",
        "axis": "x",
        "ticks": [0.0, 0.5, 1.0],
        "labels": ["0.0", "0.5", "1.0"],
        "grid_intent": true
      }
    ],

    "title": {
      "panel_id": "panel.main",
      "text": "Conformance fixture"
    }
  },

  "queries": [
    {
      "query_id": "query.point.frontmost",
      "request": {
        "panel_id": "panel.main",
        "coordinate_space": "panel",
        "coordinate": [320, 240],
        "scope": "all-rendered",
        "hit_policy": "frontmost",
        "payloads": ["identity", "coordinate", "color", "value"]
      },
      "expected_result": {
        "status": "hit",
        "hit": true,
        "panel_coordinate": [320, 240],
        "visual_family": "point",
        "visual_id": "visual.points.foreground",
        "item_id": "point.1",
        "data_coordinate": [0.5, 0.5],
        "extension_payloads": []
      }
    }
  ],

  "backend_expectations": {
    "matplotlib": {
      "expectation": "pass",
      "required": true,
      "capabilities_required": [
        "visual.point@0.1",
        "visual.image@0.1",
        "query.panel@0.1",
        "guides.query@0.1"
      ],
      "diagnostic_required_on_non_pass": true
    },
    "datoviz": {
      "expectation": "skip",
      "required": false,
      "reason_code": "datoviz.runtime-query-identity-fields-unavailable",
      "until_capability": "datoviz.query.identity-payload@0.1",
      "diagnostic_required": true
    }
  },

  "outputs": {
    "semantic_replay": {
      "required": true,
      "checks": [
        "visual_families",
        "extension_presence",
        "query_results",
        "tiled_mosaic_shape",
        "tiled_mosaic_source_rect"
      ]
    },
    "reference_rendering": {
      "backend": "matplotlib",
      "required": true,
      "comparison": "semantic-or-existing-reference-render",
      "image_hash_required": false
    },
    "debug_report": {
      "may_be_generated": true,
      "schema_authority": false,
      "report_kind": "gsp.conformance.debug-json"
    }
  }
}
```

Required first-slice sections should be:

* `schema_kind`
* `schema_version`
* `metadata`
* `protocol`
* `capabilities`
* `resources`
* `scene`
* `queries`
* `backend_expectations`

Optional first-slice sections should be:

* `extension_manifests`, though any extension payload used by the fixture must have a manifest entry
* `outputs`
* `resources.virtual_sources`, when tiled or virtual source behavior is covered
* `features_optional`

## Array Transport

First-slice array transport should be deliberately small and boring.

The first supported replayable eager array representation should be:

```jsonc
{
  "resource_id": "res.points.positions",
  "array_id": "arr.points.positions.xy",
  "kind": "buffer",
  "semantic_role": "point.positions.xy",

  "dtype": "float32",
  "shape": [3, 2],
  "byte_order": "little",
  "memory_order": "C",

  "encoding": "base64",
  "compression": "none",
  "byte_length": 24,

  "checksum": {
    "algorithm": "sha256",
    "scope": "decoded_uncompressed_bytes",
    "value": "<lowercase-hex-sha256>"
  },

  "data_base64": "<standard-base64>"
}
```

Required metadata fields:

* `resource_id`: stable resource identifier used by scene objects.
* `array_id`: stable identifier for the serialized array chunk.
* `kind`: first slice should support `buffer`; later slices may add `texture`, `parameter-block`, or chunked array kinds.
* `semantic_role`: stable role such as `point.positions.xy`, `point.colors.rgba8`, `point.sizes.scalar`, `image.rgba8`, or `tile.rgba8`.
* `dtype`: canonical dtype string. First slice should support only the dtypes needed by current fixtures: `float32` and `uint8`. Add `int32`, `uint32`, `float64`, and structured dtypes later only when required by fixtures.
* `shape`: JSON array of non-negative integer dimensions.
* `byte_order`: `little`, `big`, or `not-applicable`. First slice should require `little` for multi-byte numeric dtypes and `not-applicable` for `uint8`.
* `memory_order`: first slice should require `C`.
* `encoding`: first slice should support `base64` for replayable eager arrays and `omitted` only for non-replayable summaries.
* `compression`: first slice should require `none`.
* `byte_length`: decoded, uncompressed byte length.
* `checksum.algorithm`: first slice should require `sha256`.
* `checksum.scope`: must be `decoded_uncompressed_bytes`.
* `checksum.value`: lowercase hexadecimal digest.
* `data_base64`: standard padded base64 without line breaks when `encoding="base64"`.

Size and encoding rules:

* First-slice inline base64 should be used only for small deterministic fixture arrays.
* Recommended hard limit: `1 MiB` decoded bytes per array chunk and `4 MiB` decoded bytes per fixture file.
* Arrays above that limit must not be forced into inline base64. They should be represented later as external files, binary chunks, or virtual data sources.
* No compression in the first slice. `compression` must be present and must equal `none`.
* Checksums are over decoded uncompressed bytes, never over the base64 string.
* The decoded byte count must equal `prod(shape) * dtype.itemsize`.
* The fixture reader must reject byte-length mismatches, checksum mismatches, unsupported dtypes, unsupported memory orders, and unsupported encodings.
* Replayable input resources must not use `encoding="omitted"`.
* `encoding="omitted"` is allowed only for diagnostic outputs or semantic summaries where exact bytes are intentionally not part of the replay contract.

Recommended omitted summary shape:

```jsonc
{
  "resource_id": "res.large.not_replayed",
  "array_id": "arr.large.summary",
  "kind": "buffer",
  "semantic_role": "diagnostic.summary",
  "dtype": "uint8",
  "shape": [100000, 100000, 4],
  "encoding": "omitted",
  "omission_reason": "too-large-for-json-fixture",
  "summary": {
    "byte_length": 40000000000,
    "value_summary": "not required for this semantic fixture",
    "checksum_available": false
  }
}
```

Nested JSON arrays should not be used for `BufferResource` payloads in the first slice because they create dtype ambiguity, byte-order ambiguity, NaN/Inf ambiguity, unnecessary file size growth, and multiple equivalent encodings. Human-readable semantic values such as panel coordinates, guide ticks, extents, labels, scalar tolerances, and expected query coordinates may remain ordinary JSON.

Deferred array transport forms:

* External file references.
* Compressed chunks.
* Chunk tables for large arrays.
* Shared-memory or binary IPC references.
* Network resource URLs.
* Memory-mapped resources.
* Non-contiguous owned arrays.
* Structured dtypes.
* GPU-native texture upload blobs.
* Canonical JSON hashing of entire fixture files.

## Virtual Data Sources

Virtual and tiled data sources should be represented as logical source manifests, not eager buffers.

A tiled source fixture should describe:

```jsonc
{
  "source_id": "source.tiled.synthetic_rgba",
  "source_kind": "tiled-image",
  "payload_kind": "gsp.tiled-image@0.1.source",

  "logical": {
    "dtype": "uint8",
    "shape": [64, 64, 4],
    "color_model": "rgba8",
    "extent": [0.0, 0.0, 1.0, 1.0],
    "origin": "upper"
  },

  "tiling": {
    "tile_shape": [16, 16, 4],
    "addressing": "source-pixel-rect",
    "bounds_policy": "clip-to-source"
  },

  "materialization": {
    "mode": "synthetic-local",
    "generator_id": "gsp.fixtures.synthetic.rgba-tiled-image@0.1",
    "parameters": {
      "seed": 0
    }
  },

  "expected_semantics": {
    "viewport_mosaic_source_rect": [0, 0, 32, 32],
    "viewport_mosaic_shape": [32, 32, 4]
  }
}
```

The important distinction is that this object is a **source description**, not a buffer. It may produce arrays during local replay, but the fixture does not claim that the full logical source is resident, contiguous, serialized, or owned as a `BufferResource`.

First-slice virtual source rules:

* `source_kind="tiled-image"` is sufficient for the first slice.
* `payload_kind` must name the extension-owned source schema.
* Logical shape, dtype, extent, origin, tile shape, and bounds behavior must be explicit.
* Materialization should initially support deterministic local synthetic generators only.
* Expected conformance should check semantic behavior such as clipped source rect, mosaic shape, query payload identity, and value semantics where stable.
* Whole-source eager serialization must be rejected for large virtual sources.
* A scene image visual may reference either an eager array resource or a virtual source resource, but the two must be distinct resource kinds.

Later slices may add tile manifests that reference individual `array_id`s or external files, but that should not be required for the first schema slice.

## Query And Extension Payloads

Core query requests should serialize the unified panel-query model directly:

```jsonc
{
  "query_id": "query.point.frontmost",
  "request": {
    "panel_id": "panel.main",
    "coordinate_space": "panel",
    "coordinate": [320, 240],
    "scope": "all-rendered",
    "hit_policy": "frontmost",
    "payloads": ["identity", "coordinate", "color", "value"]
  }
}
```

Core expected results should serialize only core `QueryResult` fields:

```jsonc
{
  "expected_result": {
    "request_id": "query.point.frontmost",
    "status": "hit",
    "hit": true,
    "panel_coordinate": [320, 240],

    "visual_family": "point",
    "visual_id": "visual.points.foreground",
    "item_id": "point.1",

    "data_coordinate": [0.5, 0.5],
    "color": [255, 0, 0, 255],
    "value": 1.0,

    "extension_payloads": []
  }
}
```

Rules for query result serialization:

* Enum values must use protocol strings exactly.
* Non-hit results must not include hit payload fields such as `visual_family`, `visual_id`, `item_id`, `data_coordinate`, `color`, or `value`.
* `unsupported`, `stale`, `dropped`, and `failed` results must include a diagnostic.
* `miss` and `outside-panel` may include a diagnostic, but it is not required.
* `hit=true` is valid only with `status="hit"`.
* `hit=false` is required for all non-hit statuses.
* `panel_coordinate` should be echoed for all query results where the request reached a panel.
* `request_id` must match the query request ID.
* Query payload values must be JSON-safe. Large array-like query payloads must be represented through resource references, not embedded ad hoc arrays.

Extension payloads should be serialized in explicit envelopes:

```jsonc
{
  "extension_payloads": [
    {
      "payload_kind": "gsp.guide-query@0.1",
      "extension_id": "gsp.guides",
      "payload_schema_version": "0.1",
      "capability_required": "guides.query@0.1",
      "value": {
        "guide_id": "guide.x.major",
        "guide_kind": "tick",
        "axis": "x",
        "tick_value": 0.5,
        "label": "0.5"
      }
    }
  ]
}
```

For tiled image query payloads:

```jsonc
{
  "extension_payloads": [
    {
      "payload_kind": "gsp.tiled-image@0.1.query",
      "extension_id": "gsp.tiled-image",
      "payload_schema_version": "0.1",
      "capability_required": "virtual-source.tiled-image@0.1",
      "value": {
        "source_id": "source.tiled.synthetic_rgba",
        "source_rect": [0, 0, 32, 32],
        "texel": [12, 8],
        "value": [128, 64, 255, 255]
      }
    }
  ]
}
```

Extension rules:

* The fixture schema owns the envelope, not the extension-specific `value` internals.
* Each `payload_kind` must appear in `extension_manifests` unless it is declared as an opaque optional payload.
* Required extension payloads that cannot be understood by a backend should produce a backend `skip` or query `unsupported`, depending on whether the unsupported feature prevents fixture execution or only affects a particular query.
* Optional extension payloads may be preserved and reported without contributing to pass/fail.
* Unknown required extension payload kinds must not be silently ignored.
* Extension-specific query payloads must not be flattened into core `QueryResult`.

## Backend Expectations

Backend expectation entries should distinguish **declared expectation policy** from **actual result**.

Recommended expectation values:

* `pass`: the backend is expected to execute the fixture and satisfy every mandatory semantic check.
* `skip`: the backend is visible in the matrix but is not expected to execute the fixture because required runtime support, bindings, capabilities, or stable identity fields are unavailable.
* `xfail`: the backend is expected to execute the fixture but fail a known, tracked requirement. This should require an issue ID, reason code, and removal condition.
* `fail`: the backend executed the fixture and did not satisfy a mandatory requirement. This should be an actual result, not usually a desired expectation, except for negative validation fixtures in later slices.

Recommended schema:

```jsonc
{
  "backend_expectations": {
    "matplotlib": {
      "expectation": "pass",
      "required": true,
      "capabilities_required": [
        "visual.point@0.1",
        "visual.image@0.1",
        "query.panel@0.1",
        "guides.query@0.1"
      ],
      "tolerances": {
        "numeric_absolute": 0.0,
        "numeric_relative": 0.0,
        "color_rgba8_channel": 0
      },
      "diagnostic_required_on_non_pass": true
    },

    "datoviz": {
      "expectation": "skip",
      "required": false,
      "capabilities_required": [
        "visual.point@0.1",
        "visual.image@0.1",
        "query.panel@0.1"
      ],
      "missing_or_unstable": [
        "query.identity.visual_family",
        "query.identity.item_id",
        "query.tiled.texel",
        "query.value"
      ],
      "reason_code": "datoviz.runtime-query-identity-fields-unavailable",
      "until_capability": "datoviz.query.identity-payload@0.1",
      "diagnostic_required": true
    }
  }
}
```

Actual backend result shape:

```jsonc
{
  "backend": "datoviz",
  "actual_result": "skip",
  "fixture_id": "gsp.fixtures.v0_1.point_image_guides_tiled",
  "diagnostic": {
    "reason_code": "datoviz.runtime-query-identity-fields-unavailable",
    "message": "Datoviz runtime query identity payload fields are not stable for this fixture.",
    "missing_capabilities": [
      "query.identity.visual_family",
      "query.identity.item_id",
      "query.tiled.texel",
      "query.value"
    ],
    "backend_version": "0.4-dev",
    "adapter": "gsp.datoviz.replay-adapter"
  }
}
```

Certification rules:

* A backend can receive full v0.1 conformance only by passing all mandatory v0.1 fixtures for the required capability set.
* A backend can receive partial certification only for explicitly declared capability subsets.
* `skip` is honest and visible, but it is not a pass.
* If a backend declares a capability and then cannot satisfy the matching fixture, the result should be `fail`, not `skip`.
* `xfail` must include a tracked issue or named removal condition. Unexpected pass should be reported as `xpass` by tooling, prompting expectation cleanup.
* Required diagnostics for `skip`, `xfail`, and `fail` should include `reason_code`, human-readable `message`, backend identity, adapter identity, missing capabilities when applicable, and exception details when applicable.
* Matplotlib should be the required reference backend for the first slice.
* Datoviz should remain visible in the matrix as `skip` until stable runtime query identity fields are available.

## Versioning Policy

Fixture schema versioning and protocol versioning should be independent.

Rules:

* `schema_kind="gsp.conformance.fixture"` identifies the authoritative fixture schema.
* `schema_version` versions the JSON fixture representation.
* `protocol.gsp_protocol_version` versions the GSP semantics being tested.
* `compatible_protocol_range` states which protocol versions the fixture is intended to exercise.
* Extension payloads version independently through `payload_kind`, for example `gsp.guide-query@0.1`.
* Debug reports remain `gsp.conformance.debug-json` with `schema_authority=false`.

Recommended compatibility policy:

* Use semantic versioning for fixture schema versions: `MAJOR.MINOR.PATCH`.
* Patch versions may clarify wording, tighten invalid examples, or fix documentation without changing accepted valid fixtures.
* Minor versions may add optional fields, optional features, new optional sections, or new extension payload envelopes.
* Major versions may rename fields, remove fields, change required semantics, or alter validation behavior.
* A reader must reject unknown major versions.
* A reader may accept a newer minor version only if all entries in `features_required` are recognized.
* Unknown optional fields may be preserved or ignored, but unknown required features must cause rejection.
* Fixtures should pin an exact `schema_version` and include `fixture_revision` for content changes.
* Fixture content revisions are not schema revisions. Changing a point location, expected query result, or backend expectation increments `fixture_revision`, not necessarily `schema_version`.
* Array encodings, compression modes, external-file references, and virtual-source materialization modes should be feature-gated.
* Extension payload compatibility is governed by extension manifests and payload kind versions, not by the core fixture schema alone.

The first authoritative schema should be `gsp.conformance.fixture` version `0.1.0`, targeting GSP protocol `0.1`.

## First Implementation Missions

1. **M041 — Fixture schema ADR and spec skeleton**

   Goal: Commit the architectural decision and a minimal fixture schema spec for `gsp.conformance.fixture@0.1`.

   Acceptance criteria:

   * ADR states that debug-json remains diagnostic and non-authoritative.
   * Spec defines required top-level sections.
   * Spec defines fixture schema versioning versus GSP protocol versioning.
   * Spec states that JSON/base64 is not required for the `inproc` local desktop path.
   * Spec includes one non-normative pseudo-JSON example.

   Stop conditions:

   * Do not implement array transport yet.
   * Do not change the existing in-process replay harness.
   * Do not require Datoviz to pass.

2. **M042 — Typed base64 array chunk schema and validation**

   Goal: Add first-slice validation for contiguous base64 array chunks.

   Acceptance criteria:

   * Supports `float32` and `uint8`.
   * Requires `resource_id`, `array_id`, `semantic_role`, `dtype`, `shape`, `byte_order`, `memory_order`, `encoding`, `compression`, `byte_length`, `checksum`, and `data_base64`.
   * Requires `memory_order="C"` and `compression="none"`.
   * Validates decoded byte length and SHA-256 checksum.
   * Rejects unsupported dtype, missing checksum, wrong byte length, wrong checksum, unsupported memory order, and unsupported compression.
   * Existing in-process fixtures continue to run without serialization.

   Stop conditions:

   * Do not implement external file references.
   * Do not implement compression.
   * Do not implement non-contiguous resource ownership.
   * Do not serialize huge virtual datasets.

3. **M043 — Minimal JSON fixture for current S018 semantic slice**

   Goal: Encode the existing point, image, guide, and tiled semantic fixture as `gsp.conformance.fixture@0.1`.

   Acceptance criteria:

   * Fixture has stable IDs for panel, visuals, resources, arrays, guides, and queries.
   * Point positions, point colors, point sizes, and eager image data use typed base64 chunks where needed.
   * Guide ticks and labels remain semantic JSON values, not buffer arrays.
   * Query expectations match the current in-process replay semantics.
   * Matplotlib passes the JSON fixture through the replay adapter.
   * Existing debug-json report remains separately generated and still reports `schema_authority=false`.

   Stop conditions:

   * Do not replace Python/in-process fixtures as the fast path.
   * Do not require JSON fixtures for local desktop use.
   * Do not add VisPy2 producer API conformance yet.

4. **M044 — Query and extension payload envelope validation**

   Goal: Validate core query result shape and extension payload boundaries.

   Acceptance criteria:

   * Non-hit results are rejected if they contain hit payload fields.
   * `unsupported`, `stale`, `dropped`, and `failed` results require diagnostics.
   * `gsp.guide-query@0.1` payloads are serialized through extension envelopes.
   * `gsp.tiled-image@0.1.query` payloads are serialized through extension envelopes.
   * Unknown required extension payload kinds cause validation failure or backend skip.
   * Unknown optional extension payload kinds are preserved or ignored according to declared optionality.

   Stop conditions:

   * Do not generalize query-scope precedence beyond current tested semantics.
   * Do not flatten extension payload fields into core query results.
   * Do not implement Datoviz query pass requirements.

5. **M045 — Backend expectation schema and matrix integration**

   Goal: Replace ad hoc backend expectation semantics with explicit `pass`, `skip`, `xfail`, and `fail` rules.

   Acceptance criteria:

   * Matplotlib is marked `pass` and required for first-slice fixtures.
   * Datoviz is marked `skip` with a required diagnostic and removal condition.
   * Matrix output distinguishes expectation from actual result.
   * `skip`, `xfail`, and `fail` require structured diagnostics.
   * A backend claiming a capability but failing its fixture is reported as `fail`, not `skip`.
   * Partial support is reported by capability subset, not by vague backend-level success.

   Stop conditions:

   * Do not introduce public certification badges yet.
   * Do not require Datoviz full conformance.
   * Do not add new backend families.

6. **M046 — First virtual tiled-source fixture manifest**

   Goal: Represent the current tiled-source semantic fixture as a virtual source manifest without eager full-source serialization.

   Acceptance criteria:

   * Fixture includes `resources.virtual_sources`.
   * Tiled source declares logical shape, dtype, color model, extent, origin, tile shape, addressing, and clipping behavior.
   * Materialization uses a deterministic local synthetic generator ID.
   * Replay validates clipped source rect, mosaic shape, and typed tiled-image query payloads.
   * Full-source eager array serialization is not used.

   Stop conditions:

   * Do not implement network-backed sources.
   * Do not implement external tile file manifests.
   * Do not implement Datoviz tiled-source runtime conformance.
   * Do not serialize large virtual datasets as ordinary buffers.

## Explicit Deferrals

Do not implement the following in the first schema slice:

* Promotion of `gsp.conformance.debug-json` into an authoritative fixture schema.
* Mandatory JSON/base64 serialization for the local `inproc` desktop path.
* Datoviz conformance pass requirements.
* Datoviz query identity certification until stable `visual_family`, `item_id`, `texel`, and `value` fields exist.
* Production network transport.
* Binary IPC or shared-memory transport.
* External file array references.
* Compressed array chunks.
* Chunked large-array manifests.
* Memory-mapped arrays.
* Non-contiguous owned resources.
* GPU-native texture transport blobs.
* General structured dtype support.
* Nested JSON arrays for ordinary buffer resources.
* Huge virtual dataset eager serialization.
* General data/guides/all-rendered precedence beyond currently covered query tests.
* Perceptual image hashing or screenshot-based conformance.
* Full visual regression image baselines beyond existing Matplotlib reference behavior.
* VisPy2 producer API conformance fixtures.
* Datoviz rendering/query replay adapter certification.
* Extension schemas beyond `gsp.guide-query@0.1` and `gsp.tiled-image@0.1.query`.
* Fixture signing, canonical JSON hashing, or long-term artifact archival format.
* Public certification badges or compatibility branding.

## Decision Record Draft

**Title:** Adopt separate versioned conformance fixture schema with typed base64 array chunks

**Status:** Proposed

**Context:**
GSP needs a stable conformance fixture format for replay, backend certification, debugging, and future transport experiments. The current S018 harness uses Python/in-process fixtures and a deterministic debug-json report. The debug report is intentionally non-authoritative and omits array transport. GSP also requires a fast local in-process path that must not depend on JSON/base64 serialization. Large and virtual datasets must not be represented as ordinary eager buffers.

**Decision:**
Create a separate authoritative JSON schema named `gsp.conformance.fixture`, starting at schema version `0.1.0` and targeting GSP protocol `0.1`. Keep `gsp.conformance.debug-json` as diagnostic output with `schema_authority=false`.

The first fixture schema slice will include explicit metadata, protocol version, capability snapshot, extension manifests, resources, scene objects, queries, backend expectations, and outputs. Replayable eager arrays will be represented as typed contiguous base64 chunks with dtype, shape, byte order, memory order, encoding, compression, byte length, checksum, semantic role, and resource ID metadata. The first slice will support only small deterministic arrays needed by the current point/image fixture coverage.

Virtual and tiled data sources will be represented as source manifests with logical shape, tiling, materialization rules, and query semantics. They will not be serialized as full eager buffers. Extension query payloads will be preserved in versioned envelopes keyed by payload kind. Backend expectations will distinguish `pass`, `skip`, `xfail`, and `fail`, with structured diagnostics required for non-pass outcomes.

Matplotlib remains the required reference/conformance backend for the first slice. Datoviz remains visible in the backend matrix as `skip` until stable runtime query identity payload fields are available.

**Consequences:**
This preserves the in-process fast path while creating a stable fixture artifact for replay and certification. It prevents diagnostic debug output from accidentally becoming a protocol contract. It gives Codex agents concrete validation and test targets without forcing premature production transport decisions. It also leaves room for future external files, binary IPC, network transport, compression, and large virtual data handling.

**Follow-up missions:**
Implement the ADR/spec skeleton, typed base64 array validation, a minimal JSON fixture for the current S018 semantic slice, query and extension payload envelope validation, backend expectation matrix integration, and a first virtual tiled-source manifest fixture.

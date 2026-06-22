# ADR-0007 - Separate versioned conformance fixture schema

## Status

Accepted

## Context

S018 established Python/in-process conformance replay, an explicit backend conformance matrix, and a
deterministic debug-json report. The debug-json report is useful for inspection and CI diagnostics,
but it intentionally omits array transport and sets `schema_authority=false`.

GSP also has a standing architectural constraint: local desktop execution must use the direct
in-process path and must not require JSON/base64 serialization. JSON/base64 may support fixtures,
debugging, replay, and simple transport, but it is not the ordinary local runtime representation.

The project needs an authoritative fixture artifact for future replay and backend conformance work
without letting the diagnostic report accidentally become a compatibility contract.

This decision follows ChatGPT Pro consultation `P005`, recorded in
`.agent/consultations/P005-response.md`.

## Decision

GSP will define a separate authoritative JSON fixture schema named `gsp.conformance.fixture`.

The first schema version is `0.1.0`, targeting GSP protocol `0.1`.

`gsp.conformance.debug-json` remains diagnostic and non-authoritative. It must continue to expose
`schema_authority=false` and must not be treated as the compatibility schema.

The first fixture schema slice will define these top-level sections:

- `schema_kind`;
- `schema_version`;
- `metadata`;
- `protocol`;
- `features_required`;
- `features_optional`;
- `capabilities`;
- `extension_manifests`;
- `resources`;
- `scene`;
- `queries`;
- `backend_expectations`;
- `outputs`.

Replayable eager arrays will eventually use typed contiguous base64 chunks under
`resources.arrays`, with dtype, shape, byte order, memory order, encoding, compression, byte length,
checksum, semantic role, and resource ID metadata. That validation is a follow-up implementation
mission, not part of this ADR.

Virtual and tiled data sources are represented as source manifests, not eager full-source buffers.
Extension query payloads are represented in versioned envelopes keyed by payload kind.

Backend expectations distinguish `pass`, `skip`, `xfail`, and `fail`. Matplotlib is the required
reference backend for the first slice. Datoviz remains visible as `skip` until stable runtime query
identity payloads are available.

## In Scope

- Authoritative fixture schema identity: `gsp.conformance.fixture`.
- Schema version `0.1.0` and relationship to GSP protocol `0.1`.
- Required top-level schema sections.
- Separation of diagnostic debug-json from authoritative fixtures.
- Preservation of the in-process fast path.
- Non-normative skeleton and examples in `spec/conformance-fixtures.md`.

## Out of Scope

- Base64 array chunk validation.
- JSON fixture files.
- Fixture reader/replay implementation.
- External file references.
- Compression.
- Binary IPC or network transport.
- Datoviz conformance pass requirements.
- Public certification branding.

## Consequences

This creates a durable place for conformance fixtures without making local execution depend on
serialization. It also prevents debug-json output from becoming an accidental compatibility
contract.

Follow-up missions can now implement the schema incrementally:

- typed base64 array validation;
- minimal JSON fixture for the current S018 semantic slice;
- query and extension payload envelope validation;
- backend expectation matrix integration;
- virtual tiled-source fixture manifests.

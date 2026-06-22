# M042-TYPED-BASE64-ARRAY-CHUNK-VALIDATION - Typed base64 array chunk validation

## Mission

M042

## Goal

Add first-slice validation for contiguous base64 array chunks in
`gsp.conformance.fixture@0.1`.

## Acceptance

- Supports `float32` and `uint8`.
- Requires `resource_id`, `array_id`, `semantic_role`, `dtype`, `shape`, `byte_order`,
  `memory_order`, `encoding`, `compression`, `byte_length`, `checksum`, and `data_base64`.
- Requires `memory_order="C"` and `compression="none"`.
- Validates decoded byte length and SHA-256 checksum.
- Rejects unsupported dtype, missing checksum, wrong byte length, wrong checksum, unsupported memory
  order, and unsupported compression.
- Existing in-process fixtures continue to run without serialization.

## Stop conditions

Stop before external file references, compression, non-contiguous resource ownership, JSON fixture
files, or serialization of huge virtual datasets.

## Source

ChatGPT Pro response recorded in `.agent/consultations/P005-response.md`.

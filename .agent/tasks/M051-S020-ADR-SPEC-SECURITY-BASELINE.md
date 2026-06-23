# M051-S020-ADR-SPEC-SECURITY-BASELINE - S020 ADR/spec security baseline

## Mission

M051

## Goal

Consume the P006 ChatGPT Pro response and record the S020 remote data and dynamic extension security
baseline in durable project artifacts.

## Acceptance

- `.agent/consultations/P006-response.md` records the user-provided Pro response.
- A new ADR captures the accepted security pre-design decisions.
- `spec/data_sources.md` defines the reserved descriptor, locality, credential, cache,
  materialization, resource, and query/readback security model.
- `spec/extensions.md` defines the static-manifest-only dynamic extension policy.
- `spec/capabilities.md` defines conservative remote-data and extension security capability fields
  plus diagnostic codes.
- `spec/conformance-fixtures.md` defines redaction and no-network negative fixture requirements.
- A short docs page explains the user-facing remote data and extension policy.

## Stop conditions

Do not add real HTTP/S3/GCS/Zarr/OME-Zarr/COG/map-tile fetch, credential exchange, dynamic plugin
loading, runtime shader loading, custom decoder execution, or Datoviz remote-data requirements.

## Source

P006 ChatGPT Pro response in `.agent/consultations/P006-response.md`.

## Result

Completed. Added ADR-0008, S020 spec patches, a security docs page, and Mission Control records.

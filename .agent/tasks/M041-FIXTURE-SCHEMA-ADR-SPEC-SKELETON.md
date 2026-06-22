# M041-FIXTURE-SCHEMA-ADR-SPEC-SKELETON - Fixture schema ADR and spec skeleton

## Mission

M041

## Goal

Commit the architectural decision and a minimal fixture schema spec for
`gsp.conformance.fixture@0.1`.

## Acceptance

- ADR states that `gsp.conformance.debug-json` remains diagnostic and non-authoritative.
- Spec defines required top-level sections for the authoritative fixture schema.
- Spec defines fixture schema versioning versus GSP protocol versioning.
- Spec states that JSON/base64 is not required for the `inproc` local desktop path.
- Spec includes one non-normative pseudo-JSON example.

## Stop conditions

Stop before implementing array transport, changing the existing in-process replay harness,
requiring Datoviz to pass, or adding JSON fixture files.

## Source

ChatGPT Pro response recorded in `.agent/consultations/P005-response.md`.

## Result

Completed. ADR-0007 and `spec/conformance-fixtures.md` define the fixture schema decision and
skeleton without implementing array transport or JSON fixture files.

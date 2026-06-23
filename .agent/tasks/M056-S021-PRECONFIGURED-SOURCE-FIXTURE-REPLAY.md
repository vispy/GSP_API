# M056-S021-PRECONFIGURED-SOURCE-FIXTURE-REPLAY - Preconfigured-source fixture replay

## Mission

M056

## Goal

Wire the no-network preconfigured-source resolver proof into conformance fixture validation/replay.

## Acceptance

- A committed JSON fixture records S021 resolver capability metadata, known-handle materialization,
  unknown-handle rejection, and fetch-descriptor rejection.
- Fixture validation resolves the known handle through the proof resolver and checks deterministic
  tile data.
- Fixture validation checks rejection diagnostics for unsafe/unknown descriptors.
- The fixture is included in wheel/sdist package data.
- Tests cover successful validation and mismatch detection.

## Stop conditions

Do not add real network fetch, filesystem access, host resolution, object-store clients, credential
exchange, dynamic loading, runtime shaders, custom decoders, or Datoviz remote-data requirements.

## Source

M055 no-network preconfigured-source resolver proof.

## Result

Completed. Added S021 preconfigured-source JSON fixture records, a validator/replay helper, exports,
package-data inclusion, README coverage, and tests.

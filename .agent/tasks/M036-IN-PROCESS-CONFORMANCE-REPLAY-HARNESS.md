# M036-IN-PROCESS-CONFORMANCE-REPLAY-HARNESS - In-process conformance replay harness

## Mission

M036

## Goal

Start S018 with a bounded Python/in-process replay harness over existing conformance fixtures.

## Acceptance

- Replay uses direct protocol objects and NumPy arrays.
- Replay covers capability identity, point-over-image query, guide hit/miss queries, and local
  tiled-source clipped mosaic/query semantics.
- Tests assert stable semantic replay results.
- JSON/base64 fixture files and debug-json transport replay remain deferred.

## Stop conditions

Stop before adding JSON fixture schemas, base64 array encoding, pixel comparison, backend matrix
classification, or Datoviz runtime requirements.

## Result

Completed. `fixtures.conformance.replay.replay_conformance_fixtures()` returns semantic replay
results for the current v0.1 conformance baseline.

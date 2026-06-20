# GSP-HARDEN-003 - Tighten protocol and query tests

## Goal

Make current tests robust against accidental semantic drift in IDs, visual schemas, capabilities, resources, command batches, and query statuses.

## Mission

M006

## Expected output

- Additional or refined tests under `tests/`.

## Acceptance

- All tests pass.
- New tests specifically cover query hit/miss/outside/unsupported behavior where currently possible.
- New tests do not depend on Datoviz.

## Stop conditions

Stop if test changes require broad protocol redesign.

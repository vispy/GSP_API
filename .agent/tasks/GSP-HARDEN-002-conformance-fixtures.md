# GSP-HARDEN-002 - Add conformance fixture baseline

## Goal

Add or refine fixtures for point, image, point-over-image query, and basic capability snapshot.

## Mission

M006

## Expected output

- Fixture files under `fixtures/` or existing fixture directory.
- Tests that load/use these fixtures.

## Acceptance

- Fixtures exercise in-process protocol models.
- No mandatory JSON/base64 path is introduced.
- Tests pass.

## Stop conditions

Stop if fixture layout conflicts with current tests or protocol objects.

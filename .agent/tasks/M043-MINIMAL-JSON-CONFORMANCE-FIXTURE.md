# M043-MINIMAL-JSON-CONFORMANCE-FIXTURE - Minimal JSON conformance fixture

## Mission

M043

## Goal

Encode the existing point, image, guide, and tiled semantic fixture as
`gsp.conformance.fixture@0.1`.

## Acceptance

- Fixture has stable IDs for panel, visuals, resources, arrays, guides, and queries.
- Point positions, point colors, point sizes, and eager image data use typed base64 chunks where
  needed.
- Guide ticks and labels remain semantic JSON values, not buffer arrays.
- Query expectations match the current in-process replay semantics.
- Matplotlib passes the JSON fixture through the replay adapter.
- Existing debug-json report remains separately generated and still reports `schema_authority=false`.

## Stop conditions

Stop before replacing Python/in-process fixtures as the fast path, requiring JSON fixtures for local
desktop use, or adding VisPy2 producer API conformance.

## Source

ChatGPT Pro response recorded in `.agent/consultations/P005-response.md`.

## Result

Completed. `fixtures/conformance/minimal_v0_1.json` encodes the current semantic slice and
`fixtures.conformance.json_fixture.replay_minimal_json_fixture()` validates it through the
Matplotlib reference replay path without replacing in-process fixtures.

# M015-GUIDE-CONFORMANCE-FIXTURES - Guide/tick/title conformance fixtures

## Mission

M015

## Goal

Add deterministic conformance fixtures for the completed guide/tick/render/query reference slice.

## Acceptance

- Explicit x ticks, auto y ticks, guide labels, grids, and panel titles are represented in fixtures.
- Matplotlib reference rendering is checked semantically.
- Guide query fixtures cover hit, miss, and unsupported provider status.
- Fixtures remain Python/in-process and do not introduce JSON/base64 replay requirements.

## Stop conditions

Stop before adding general query-scope precedence or backend-native text/glyph picking.

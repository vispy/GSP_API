# M282 - S065 minimal public query entry point

## Status

Draft; promote after M281. Target repositories: `gsp`, `vispy2`.

## Goal

Make GSP's existing query model reachable through public sessions and VisPy2 without expanding the
release into comprehensive picking.

## Required scope

- Section 8 of `.agent/S065_TECHNICAL_BASELINE.md`.
- Extend `BackendSession`, both sessions, and provider conformance with scene-ID/latest-render query.
- Wire existing Matplotlib query support and proven Datoviz point/ray paths.
- Return structured unsupported results for unproven S065 visual payloads.
- Add `Figure.query()` without retaining session/backend state.
- Test multiple scene IDs, latest target, before-render, after-close, unknown ID, capability
  negotiation, hit/miss/unsupported, and existing query payload preservation.
- Add an installed-wheel point-query example and unsupported sphere/vector example.

## Acceptance

No backend-specific renderer object appears in the public API. Existing render/display return
values remain compatible. Matplotlib and Datoviz proven paths pass; unsupported paths are stable
data, not exceptions. Full source/wheel gates pass.

## Stop conditions

Stop if the API needs a native renderer handle, producer-retained session, comprehensive new pick
semantics, or false Datoviz primitive identity claims.


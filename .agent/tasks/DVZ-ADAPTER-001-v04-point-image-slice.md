# DVZ-ADAPTER-001 - Create Datoviz v0.4 point/image adapter slice

## Goal

Create a bounded Datoviz v0.4 protocol-renderer path for GSP point/image visuals.

## Mission

M007

## Acceptance

- Uses v0.4 C-shaped `dvz_*` API assumptions verified from `../datoviz/`.
- Does not use old v0.3 `datoviz.App` / `datoviz.visuals` APIs.
- Does not implement query.
- Tests skip cleanly if Datoviz v0.4 bindings are unavailable.

## Stop conditions

Stop if the Datoviz v0.4 API cannot be verified locally.

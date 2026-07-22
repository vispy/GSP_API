# M264 Datoviz v0.4 provider

Date: 2026-07-22

## Result

Curated the current Datoviz v0.4 capability, generated-API contract, protocol renderer, query
decoder, and development-source bootstrap into `/Users/cyrille/GIT/Viz/gsp` commit `8afa0e5`.
Added a lazy `gsp.backends` provider and backend-neutral session wrapper without adding a local path
or unpublished Datoviz artifact to package metadata.

Metadata-only discovery does not import Datoviz or initialize native resources. Explicit probing
loads the configured development checkout, validates the current generated API, and reports exact
availability diagnostics. Rendering supports the curated visual families, guides, transforms,
textures, capture, and bounded display lifecycle through `gsp.Scene`.

## Validation

- Datoviz provenance: `/Users/cyrille/GIT/Viz/datoviz` commit
  `be7f2a80354c25e85bab88c85f5ea7340975b569`.
- 150 Datoviz adapter/provider tests pass from source and again against installed wheels.
- The combined core/Matplotlib/Datoviz suite passes: 443 tests.
- Strict mypy passes for all 51 source files; Ruff passes.
- Installed-wheel native offscreen point capture succeeds.
- Installed-wheel Texture2D capture yields center RGBA `[0,255,0,255]` for nearest and
  `[128,128,128,255]` for linear at 801x601.
- Wheel SHA-256: `675edf044d778b7d64bd66c38b39c54a63a1fe623405437ade70f69d2646d116`.
- Sdist SHA-256: `37a420f605e4f49c088de86f4f4b8493c562c1384210d69803c9e58d10ef2376`.

The sibling Datoviz checkout was not modified; its pre-existing untracked paper artifacts remain
untouched. No remote, publication, tag, or release operation occurred. M265 is approved for the
VisPy2 producer migration.

# S057 GSP 0.2 release-candidate decision

Mission: M244

## Decision

**SHIP 0.2.0, conditional on explicit release-operation approval.**

The repository is ready to tag and publish as the pre-1.0 `gsp-vispy2` 0.2.0 source prototype. The
release operation remains deferred: this mission did not create a tag, GitHub release, or PyPI
upload.

## Package audit

- Project metadata, installed distribution, and `gsp_vispy2.__version__` report `0.2.0`.
- Producer profile identifies `gsp_vispy2@0.2` and protocol version `0.2`.
- Fresh wheel and source distribution build successfully.
- The wheel installs with dependencies into a clean Python 3.13.4 environment and imports the core,
  protocol, producer, and Matplotlib packages.
- The wheel contains 246 files, including `gsp_vispy2/session.py`, and contains no removed `vispy2`
  compatibility package.
- SHA-256 hashes are recorded in
  `artifacts/release/s057/release_candidate_manifest.json`.

## Visual and lifecycle evidence

- Matplotlib and Datoviz rendered the maintained scatter and flat-Lambert release samples.
- Visual inspection confirmed equivalent semantic geometry; Datoviz remains honestly classified
  `review.adapted` for title/layout/guide-query limitations.
- Bounded public Datoviz blocking and explicit polling examples completed cleanly.
- S053 and S056 provide repeated internal and public-wrapper lifecycle evidence; S056 recorded ten
  clean isolated public runs and zero timeouts.

## Validation

- full pytest with coverage: 666 passed, 2 skipped; 66% aggregate coverage;
- new public session module coverage: 93%;
- strict mypy: clean across 220 source files;
- Ruff: clean across source, tests, and examples;
- specification traceability, profiles, public-doc consistency, and focused documentation tests:
  clean;
- Matplotlib and Datoviz backend imports: clean;
- executable first-scene tutorial: clean;
- strict MkDocs build and compatibility redirects: clean;
- fresh wheel/sdist build and clean wheel install: clean.

The 66% aggregate coverage is below the release skill's aspirational 80% target. This is a known
repository-wide legacy/optional-module coverage characteristic rather than a regression in the new
session surface. It is not a blocker for this explicitly experimental pre-1.0 release.

## Release-facing corrections

The audit corrected stale changelog and producer-profile claims that still described public Datoviz
session execution as absent. The revised wording advertises only the bounded experimental partial
surface and preserves all deferred limitations. `RELEASE_NOTES.md` contains the candidate notes and
migration/backend boundaries.

## Required explicit approval

Before executing the deferred release mission, the owner must explicitly approve:

1. target version `0.2.0`;
2. annotated tag `v0.2.0`;
3. GitHub release creation from that tag;
4. publication of distribution `gsp-vispy2` to the intended PyPI target.

No credentials or publication configuration were inspected or changed by M244.

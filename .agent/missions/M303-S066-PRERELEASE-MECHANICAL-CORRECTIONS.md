# M303 - S066 pre-release mechanical corrections

## Status

Approved by the owner on 2026-07-30 and running under `local-main-codex`.

## Goal

Remove all non-architectural M302 blockers: restore supported-range CI, correct release-facing
claims, complete package metadata and licensing, establish the first-publication package boundary,
and refresh evidence.

## Scope

- VisPy2 raster test robustness;
- VisPy2 changelog and current documentation;
- GSP and VisPy2 package readmes, SPDX licensing, project URLs, and classifiers;
- GSP changelog;
- optional-provider conformance collection in the intended publication environment;
- defer ordinary `gsp-datoviz` and `vispy2[datoviz]` publication until an installable compatible
  Datoviz dependency exists;
- rebuild, inspect, install, and test candidate artifacts.

## Non-goals

Do not change `Panel` protocol semantics or producer capability identifiers before P038. Do not
tag, publish, push, or create PRs.

## Acceptance

- Complete source and installed-wheel suites pass under declared dependency ranges.
- Twine checks have no metadata warnings.
- Every published-candidate artifact contains correct license metadata.
- Release-facing documentation matches M300.
- The intended first-publication package set is explicit and internally installable.

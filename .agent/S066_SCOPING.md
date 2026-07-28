# S066 - Presentation Polish and Pre-release Audit

## Purpose

S066 improves first-experimental-release presentation and then audits the public API, examples,
documentation, packaging, and bounded backend claims without performing a release.

## First approved mission

M297 addresses the owner-identified Gallery 5 visual-quality issue by using the already accepted
S039 flat-Lambert contract. It may add only a small VisPy2 convenience for existing View3D light
fields and must not broaden material or lighting semantics.

## Later work

After M297 owner review, Mission Control should propose a separate pre-release audit covering:

- public API coherence and discoverability;
- example and documentation coverage;
- clean-wheel installation and supported Python environments;
- Matplotlib/Datoviz capability wording and fail-closed behavior;
- remaining bugs and release-blocking versus deferred feature gaps.

Version changes, tags, publication, release notes, and package upload remain excluded until the
owner separately approves an explicit release mission.

# S045 Scoping - Post-S044 Roadmap And Release Readiness

Generated: 2026-07-02

## Decision

Proceed first with a release-facing documentation and review-pack refresh. Do not run release
mechanics yet.

S044 completed the technical capability work for native Datoviz grid clipping proof consolidation
and backend-neutral View3D mesh triangle picking. The authoritative capability/spec files are current
through S044, but the release-facing surface still mostly describes the older S031/S033 release
candidate state.

## Current State

| Area | State | Notes |
|---|---|---|
| Protocol/spec authority | Current through S044 | `SPEC_INDEX.md`, `spec/backends/datoviz.md`, `spec/backend_capabilities_visuals.md`, and `spec/view3d_mesh_triangle_picking.md` include the S044 boundaries. |
| Release-facing docs | Stale after S033 | `CHANGELOG.md` and top-level `README.md` do not yet summarize S034-S044 layout, navigation, View3D, Lambert, grid clipping, and mesh-pick work. |
| Review examples | Present through S041/S042 | 3D review examples exist, but release-facing pointers and review-pack status need consolidation. |
| Datoviz grid clipping | Native verified | Verified separately from full guide strictness; must not imply all guide semantics are strict. |
| Datoviz mesh triangle picking | Not advertised | S044 has a public protocol and Matplotlib CPU oracle; Datoviz remains structured unsupported until public visual/triangle mapping and freshness are proven. |
| Release operation | Deferred | M131 remains blocked pending explicit target version, package version update, tag creation, and publication target. |

## Recommendation

Run M194 next as a local Mission Control implementation mission:

| Mission | State | Purpose |
|---|---|---|
| M194 | ready | Refresh release-facing docs, changelog, review-pack pointers, and validation wording for S034-S044. |
| M131 | deferred | Actual release mechanics after explicit approval. |

Do not open a new architecture consultation for M194. It should not change public semantics; it
should only make existing accepted work legible and release-reviewable.

## Optional Later Branches

| Branch | When |
|---|---|
| Datoviz native mesh-pick evidence spike | After M194, if the user wants more capability hardening before release. |
| Explicit release operation | After M194 and explicit user approval of version, tag, and publication target. |
| ChatGPT Pro consultation | Only if the next branch needs new public protocol semantics, Datoviz v0.4 API-break decisions, or a broader VisPy2 public API decision. |

## Stop Conditions

- Stop before tag creation, package version changes, publishing, PR creation, or force-pushes.
- Stop before advertising Datoviz `query.view3d.mesh_triangle_pick.v1`.
- Stop before editing the sibling Datoviz checkout unless explicitly approved.
- Stop and create a self-contained ChatGPT Pro packet if the work uncovers a public semantic
  conflict rather than a documentation/release-readiness gap.

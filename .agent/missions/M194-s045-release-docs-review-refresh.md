# M194 - S045 release-facing docs and review-pack refresh

## Stage

S045 - Post-S044 Roadmap And Release Readiness

## Status

Ready for local-main-codex.

## Summary

Refresh the release-facing project surface after S034-S044 so the repository can move toward
explicit release approval without losing traceability.

This is not a release operation.

## Deliverables

- Update `CHANGELOG.md` Unreleased sections to summarize accepted S034-S044 work and known
  limitations.
- Update top-level release-facing README wording if it is stale relative to the protocol/backend
  state.
- Refresh review/example pointers for the post-S041/S042 3D review material and any S044 query
  boundaries.
- Check that docs do not overclaim Datoviz mesh triangle picking, full guide strictness, strict
  opaque 3D depth, textures, perspective, or release packaging support.
- Run focused validation appropriate for docs/status changes.

## Acceptance

- Release-facing docs describe the current capability state through S044.
- Datoviz `query.view3d.mesh_triangle_pick.v1` remains explicitly unadvertised.
- M131 remains deferred pending explicit release approval.
- `tools/agentctl next` no longer points at stale completed S044 work.

## Stop Conditions

- Stop if this requires changing accepted protocol semantics rather than documenting them.
- Stop before tag creation, package version changes, publishing, PR creation, or force-pushes.
- Stop before editing sibling Datoviz.

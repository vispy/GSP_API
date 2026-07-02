# S045 Release-Facing Refresh

## Result

M194 refreshed the release-facing documentation baseline after S034-S044.

## Updated Surfaces

- `CHANGELOG.md` now summarizes the post-S031 protocol work: resolved layout, retained View2D
  navigation, View3D, flat Lambert mesh shading, Datoviz grid clipping, and S044 mesh triangle
  picking.
- `README.md` now points users to the protocol review examples and states the Datoviz v0.4
  capability-gated boundary.
- `examples/review/README.md` now records the query/capability boundaries for View3D ray readback,
  S044 mesh triangle picking, opaque depth, and Datoviz grid clipping.
- `docs/release_checklist.md` now uses the S045 baseline and names the post-S031 capabilities and
  stop conditions that release notes must preserve.

## Release Boundary

No version was changed, no tag was created, no package was built for publication, and nothing was
published.

M131 remains deferred until the user explicitly approves:

- target version;
- package-version update;
- annotated tag creation;
- publication target.

## Remaining Boundaries

- Datoviz v0.4 must not advertise `query.view3d.mesh_triangle_pick.v1`.
- Native Datoviz grid clipping remains independent from full guide strictness.
- Strict opaque 3D GPU depth, perspective projection, textures/UVs, smooth/Phong lighting, and
  public material resources remain deferred.

# M226 - S050 projected-NDC face culling protocol fixtures

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed.

## Summary

Implement the accepted P032/ADR-0030 protocol support and fixtures for strict projected-NDC
`MeshVisual.face_culling`, without advertising backend strict capability promotion.

## Required Context

- `adr/ADR-0030-mesh-face-culling-alpha-boundary.md`
- `spec/visuals/mesh_face_culling_alpha_s050.md`
- `spec/visuals/mesh.md`
- `spec/view3d.md`
- `spec/view3d_mesh_triangle_picking.md`
- `.agent/decisions/S050_mesh_face_culling_alpha_boundary.md`

## Deliverables

- Add or centralize canonical projected-NDC winding helpers for DATA and NDC `(N,3)` mesh triangles.
- Add focused protocol/fixture coverage for NDC3 winding, DATA projected winding, reversed `xlim`,
  reversed `ylim`, framebuffer-y trap, culling before depth, projected-degenerate diagnostics, and
  non-opaque alpha exclusion from strict paths.
- Keep renderer capability advertisements unchanged unless a backend passes the strict fixture gate.
- Preserve the existing `query.view3d.mesh_triangle_pick.v1` payload shape; do not add expanded
  query fields.

## Acceptance

- Fixtures encode the accepted projected-NDC culling semantics and alpha boundary.
- Existing `FaceCulling.NONE` behavior is unchanged.
- Unsupported backends do not silently ignore non-`NONE` culling in strict paths.
- No strict non-opaque alpha or expanded query payload behavior is accepted.

## Stop Conditions

- Stop before using backend-native front-face state, framebuffer coordinates, private Datoviz ids,
  or legacy material culling behavior as protocol authority.
- Stop if implementation requires mesh-local 3D transform semantics, transparent picking, or strict
  alpha blending.

## Result

Completed locally.

Implemented canonical projected-NDC face-culling helpers and capability names in
`gsp.protocol.mesh_culling`, exported them through `gsp.protocol`, and applied the rule to the
Matplotlib View3D mesh-triangle CPU reference picker before depth selection. The base
`query.view3d.mesh_triangle_pick.v1` payload shape is unchanged; projected-degenerate triangles miss
with a warning diagnostic, and non-opaque alpha remains unsupported for strict mesh picking.

Focused validation passed:

- `uv run pytest tests/test_view3d_protocol.py tests/test_matplotlib_protocol_query.py -q`
- `uv run mypy src/gsp/protocol/mesh_culling.py src/gsp/protocol/query.py src/gsp/protocol/__init__.py src/gsp_matplotlib/protocol_query.py --strict --show-error-codes`
- `GSP_BACKEND=matplotlib uv run python -c "import gsp; print('Matplotlib backend OK')"`
- `GSP_BACKEND=datoviz uv run python -c "import gsp; print('DatoViz backend OK')"`

Full-suite validation still has pre-existing Datoviz-side debt outside this mission: the fake
Datoviz navigation smoke lacks newly required v0.4 symbols, two visual-QA harness assertions still
expect older strict/adapted Datoviz statuses, and full-tree mypy still reports the existing
`src/gsp_datoviz/protocol_renderer.py:5172` generator literal mismatch.

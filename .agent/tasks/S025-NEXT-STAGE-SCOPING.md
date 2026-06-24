# S025 next stage scoping - Mesh and 3D Geometry

## Status

S025 is opened as the next visual-family stage after completed S024 Text/Glyph.

## Selected direction: Mesh and 3D Geometry

Potential deliverables:

- `MeshVisual` protocol contract;
- indexed geometry/resource ownership decisions;
- baseline vertex/face colors, normals, and material scope decisions;
- Matplotlib reference rendering where feasible;
- Datoviz v0.4 retained mesh API evidence and capability gates;
- visual QA cases for solid, indexed, per-vertex-color, and depth-ordering cases;
- item/face/vertex query/readback semantics if accepted.

## Consultation policy

Use ChatGPT Pro before committing public MeshVisual, material, lighting, 3D transform, or mesh query
semantics. M082 created the self-contained P010 packet at `.agent/consultations/P010-mesh-3d-protocol-semantics.md`. M083 and implementation missions remain
blocked or draft until the response is accepted into ADR/spec files.

## Deferred candidate: color mapping and colorbars

A later stage should cover scalar color mapping, colormap registries, normalization/clim policy, and
colorbars. Keep that separate from S025 unless P010 explicitly identifies a narrow mesh color-scalar
baseline that belongs in MeshVisual v1.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M082 | completed | Created S025 Mesh/3D scoping and P010 ChatGPT Pro consultation packet. |
| M083 | blocked | Convert P010 response into ADR/spec baseline before implementation. |
| M084 | draft | Implement MeshVisual protocol dataclass and validation after M083. |
| M085 | draft | Add Matplotlib MeshVisual reference rendering and QA smoke after M083/M084. |
| M086 | draft | Probe Datoviz v0.4 mesh capabilities before adapter implementation. |
| M087 | draft | Implement Datoviz MeshVisual adapter or structured unsupported report. |
| M088 | draft | Add VisPy2 mesh producer API and examples. |
| M089 | draft | Add mesh query/readback semantics and close S025. |

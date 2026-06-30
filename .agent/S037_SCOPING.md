# S037 Scoping - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

Status: active, gated by P021 ChatGPT Pro consultation.

## Purpose

S037 follows the completed S036 static `View3D` baseline. Its job is to decide and then implement
the next public 3D layer without accidentally turning legacy implementation details or backend
engine affordances into unstable public API.

The stage is gated by `.agent/consultations/P021-view3d-legacy-3d-dataviz-navigation-materials.md`.
Dependent implementation must wait until the P021 answer is pasted or committed.

## Current Baseline

S036 provides:

- static `Camera3D`, `OrthographicProjection3D`, and `View3D`;
- deterministic `View3DProjectionSnapshot` projection and unprojection helpers;
- Matplotlib adapted rendering for `(N, 3)` `MeshVisual` through 2D projection;
- structured Datoviz unsupported diagnostics for `(N, 3)` meshes;
- ray query payload readback, with 3D mesh picking deferred.

The observed Datoviz runtime message is expected under S036:

```text
DatovizV04Unsupported: mesh3d_coordinate_space_unsupported: Datoviz v0.4 MeshVisual strict adapter is limited to 2D positions until public View3D camera binding is implemented
```

## Legacy Reuse Candidates

The legacy `GSP_API` code contains useful implementation techniques but is not authoritative
against the current specs.

Reusable techniques:

- MVP matrix construction and homogeneous projection;
- view/world vertex derivation;
- NDC face-depth ordering for adapted rendering;
- screen-space triangle culling;
- face normal computation;
- flat Lambert/specular lighting helpers;
- textured triangle warping with Matplotlib images.

Relevant legacy files:

- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_depth.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_normal.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_phong.py`
- `src/gsp_matplotlib/renderer/matplotlib_renderer_mesh_textured.py`
- `src/gsp_matplotlib/utils/renderer_utils.py`
- `src/gsp/materials/*`
- `src/gsp/lights/*`
- `src/gsp/core/camera.py`

Do not reuse as public authority before P021:

- arbitrary matrix-first camera authoring;
- backend-native camera/controller objects;
- public light/material/texture schema;
- perspective semantics;
- scene graph/model loader semantics.

## Proposed Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M161 | completed | Create P021 consultation packet and S037 scoping baseline. |
| M162 | blocked | Integrate P021 answer into accepted decisions, ADR/spec updates, and revised mission acceptance. |
| M163 | draft | Extract safe legacy Matplotlib 3D helpers after the accepted decision clarifies scope. |
| M164 | draft | Probe Datoviz v0.4 public View3D/camera binding options and update capability gates. |
| M165 | draft | Implement public View3D navigation only if accepted by P021. |
| M166 | draft | Decide material/light/texture scope and add only the accepted minimal slice. |
| M167 | draft | Add examples, review cases, validation, and closeout for the accepted S037 scope. |

## Stop Conditions

Stop and return to the user if:

- P021 rejects public 3D navigation for this release track;
- P021 requires a public API incompatible with S036 `Camera3D`/`View3D`;
- Datoviz v0.4 only exposes private camera state or header symbols that cannot be bound safely;
- material/light/texture reuse requires introducing an unaccepted resource or scene-graph model;
- strict 3D picking or fragment-depth guarantees are requested without a separate accepted spec.

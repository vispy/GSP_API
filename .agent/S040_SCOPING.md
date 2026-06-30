# S040 Scoping - Datoviz Strict Flat Lambert Promotion

## Stage Goal

Decide whether Datoviz v0.4 can claim strict support for the already accepted S039 flat Lambert
face-normal semantics, and define the implementation route if it can.

## Context

S039 accepted a narrow backend-neutral material slice:

- `MeshVisual.shading="flat_lambert"`;
- DATA-space `(N,3)` triangle meshes in a resolved `View3D`;
- face normals only, either explicit `(F,3)` or deterministic `face_flat` generation;
- scalar `View3D.ambient_light_intensity`;
- one optional DATA-space `DirectionalLight3D`;
- `output.rgb = base.rgb * clamp(A + D, 0, 1)`;
- alpha passthrough, with non-opaque 3D alpha still non-strict.

Matplotlib already resolves the S039 material math on CPU as an adapted/reference path. Datoviz
currently rejects `flat_lambert` with `flat_lambert_unsupported` and does not advertise
`meshvisual.material.flat_lambert.v1`.

S040 is not a new public material design. It is a backend promotion decision for Datoviz only.

## Candidate Implementation Routes

| Route | Description | Key Risk |
|---|---|---|
| CPU-resolved per-face colors | Resolve exact S039 Lambert RGBA in the adapter, duplicate vertices if needed, upload unlit colors to existing Datoviz mesh path. | Must preserve one canonical color per face and avoid interpolation changing the result. |
| Native Datoviz lighting | Use Datoviz mesh normals/material/light if v0.4 exposes exact matching semantics. | Native coordinate spaces, color math, interpolation, and light direction semantics may diverge from S039. |
| Keep unsupported | Preserve current explicit rejection. | Datoviz remains behind Matplotlib for S039. |

## Recommended Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M176 | completed | Open S040, create P025 ChatGPT Pro consultation packet, and record the backend-promotion scope. |
| M177 | blocked | Convert P025 response into the Datoviz implementation/ADR plan or an explicit defer decision. |

## Stop Conditions

- Stop if implementation would require changing accepted S039 public semantics.
- Stop if Datoviz native material/light APIs cannot be proven to match S039 exactly.
- Stop if the route would advertise `meshvisual.material.flat_lambert.v1` without deterministic
  positive and negative fixtures.
- Stop if CPU-resolved colors would be interpolated or reordered in a way that breaks face-level
  Lambert semantics.
- Stop if implementation is requested before the P025 response is accepted into durable project
  authority.

## Recommendation

Proceed with P025 consultation first. The expected outcome is one of:

- implement CPU-resolved exact S039 colors in the Datoviz adapter and promote the capability;
- implement a native Datoviz material path only if exact semantic parity is demonstrated;
- keep Datoviz S039 flat Lambert unsupported and move to release preparation.

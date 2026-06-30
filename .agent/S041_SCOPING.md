# S041 Scoping - 3D Manual Review Pack

## Stage Goal

Add focused manual review coverage for the current public 3D stack across Matplotlib and Datoviz.

## Scope

S041 is a review and documentation stage, not a new public 3D protocol design.

In scope:

- Matplotlib vs Datoviz manual review commands for View3D examples.
- A richer lit mesh review scene using accepted S039/S040 `flat_lambert` semantics.
- Matplotlib live View3D orbit/pan/zoom review, described as arcball-style orbit for manual review.
- Datoviz static View3D plus CPU-resolved Lambert review after S040.
- Documentation of the boundary between public GSP View3D navigation and legacy/native Datoviz
  arcball demos.

Out of scope:

- Public Datoviz native arcball controller API.
- Public native Datoviz lighting/material API.
- Smooth normals, Phong/specular, textures, UVs, samplers, and multiple lights.

## Mission Stack

| Mission | State | Purpose |
|---|---|---|
| M179 | ready | Add 3D manual review example/docs and validate Matplotlib/Datoviz review commands. |

## Stop Conditions

- Stop if the work requires changing public View3D navigation semantics.
- Stop if native Datoviz arcball or material APIs would be presented as public support.
- Stop if Datoviz cannot render the accepted S040 CPU-resolved Lambert route in review mode.

# M278 - S065 SphereVisual end-to-end

## Status

Draft; promote after M277. Target repositories: `gsp`, `vispy2`; Datoviz is read-only evidence.

## Goal

Implement bounded DATA-space 3D analytic spheres and the high-level spheres API.

## Required scope

- Section 4 of `.agent/S065_TECHNICAL_BASELINE.md`.
- Strict protocol validation and View3D requirement.
- Datoviz accurate public sphere-impostor lowering with analytic depth evidence.
- Deterministic Matplotlib projected-circle adaptation with explicit limitations.
- `Axes3D.spheres(...)`, tests, installed-wheel example, and camera/depth review artifact.
- Capability and diagnostic tests must prevent Matplotlib adaptation from claiming analytic depth.

## Locks

- Same shared protocol/backend/producer regions as M277; run sequentially.

## Acceptance

Multiple radii/colors, perspective and orthographic views, near/far ordering, invalid inputs, and
capability negotiation pass. Datoviz capture demonstrates nearer-surface depth behavior. Full
repository and wheel gates pass.

## Stop conditions

Stop if sphere radius semantics cannot remain DATA units or if strict behavior needs exposing
Datoviz render modes/material state.


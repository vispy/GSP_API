# S065 - Camera and priority visual completeness

Date: 2026-07-23

Status: approved by the project owner. M274 is approved first; M275-M284 are authorized sequential
follow-ups and must be promoted only after their declared dependencies pass review.

## Objective

Make the fresh GSP and VisPy2 repositories credible for a first experimental release whose honest
claim is:

> A backend-neutral high-level Python API for representative scientific 2D and 3D rendering,
> including a powerful semantic camera, the priority Datoviz visual families, capability-aware
> Matplotlib and Datoviz execution, and a minimal durable query entry point.

The owner prioritizes visual coverage and camera quality over comprehensive picking. The priority
new visual families are pixel, sphere, vector, and a bounded generic primitive. Existing text is a
priority hardening target. Low-level glyph and volume support are deferred.

## Authority and repositories

Authority remains in `vispy/GSP_API` Mission Control. Implementation occurs in:

| Repository key | Path | Ownership |
|---|---|---|
| `mission-control` | `/Users/cyrille/GIT/Viz/GSP_API` | plans, missions, decisions, run evidence |
| `gsp` | `/Users/cyrille/GIT/Viz/gsp` | protocol, capabilities, sessions, Matplotlib/Datoviz adapters |
| `vispy2` | `/Users/cyrille/GIT/Viz/vispy2` | high-level producer, public examples, user documentation |
| `datoviz` | `/Users/cyrille/GIT/Viz/datoviz` | read-only upstream dependency and API evidence |

Planning baselines are GSP `e2e7ac5`, VisPy2 `7cffafb`, and Datoviz
`be7f2a80354c25e85bab88c85f5ea7340975b569`. Workers must re-read the actual heads at launch and
stop on unexpected dirty state or incompatible upstream API drift.

## Approved architectural boundary

The detailed contract is `.agent/S065_TECHNICAL_BASELINE.md`. Medium workers must implement that
contract rather than inventing alternative public models.

Key decisions:

1. Preserve `Axes` as the 2D API and add a distinct `Axes3D`.
2. Use `vp.subplots(projection="3d")` for the first high-level 3D entry point.
3. Reuse GSP `Camera3D`, `View3D`, orthographic/perspective projection, and navigation reducers.
4. Make Datoviz the strict GPU target and Matplotlib the deterministic reference/adaptation target.
5. Add semantic `PixelVisual`, `SphereVisual`, `VectorVisual`, and bounded `PrimitiveVisual`
   contracts; do not expose Datoviz slots, shaders, pipelines, handles, or item-state bitfields.
6. Harden `TextVisual` and define screen-facing 3D billboard labels; do not expose glyph atlases.
7. Add a minimal session query entry point targeting the most recent render of a scene ID.
8. Keep unsupported query payloads explicit. Do not block release on comprehensive picking.

## Mission sequence

| Mission | Initial state | Scope | Depends on |
|---|---|---|---|
| M274 | approved | Make `agentctl` safely launch missions across the sibling repositories. | S064 |
| M275 | draft | Add VisPy2 `Axes3D`, static camera/projection API, camera fitting, and 3D mesh journey. | M274 |
| M276 | draft | Complete retained and interactive camera behavior in both backends. | M275 |
| M277 | draft | Implement PixelVisual through protocol, both backends, VisPy2, tests, and example. | M276 |
| M278 | draft | Implement SphereVisual end to end. | M277 |
| M279 | draft | Implement VectorVisual end to end. | M278 |
| M280 | draft | Implement bounded PrimitiveVisual end to end. | M279 |
| M281 | draft | Harden 2D text and add capability-gated 3D billboard text. | M280 |
| M282 | draft | Add minimal public session and VisPy2 query entry points. | M281 |
| M283 | draft | Build documentation, capability matrix, and installed-wheel example gallery. | M282 |
| M284 | draft | Run integrated qualification and prepare the human visual/camera review checkpoint. | M283 |

The sequence is intentionally conservative. Shared protocol exports, scene unions, render
dispatchers, and producer files overlap heavily, so implementation missions run one at a time.

## Human checkpoints

The owner is not required for routine implementation, tests, or artifact generation. Work pauses:

- after M276 for live camera interaction acceptance if automated evidence cannot prove usability;
- at M284 for the complete gallery and live camera review;
- before any public API or semantic deviation from the approved technical baseline;
- before release/version/tag/publication operations.

Visual artifacts must be presented with exact example commands and backend/capability status.
Automated pixel comparisons support but do not replace owner acceptance.

## Stage-wide validation

Every implementation mission must:

- add focused positive, negative, capability, and unsupported-path tests;
- pass repository pytest, strict mypy, Ruff, and `git diff --check`;
- preserve core import isolation and lazy backend discovery;
- build affected wheels and test them outside the source checkout;
- run the relevant example from installed wheels;
- record exact commits, commands, results, adaptations, and deferred behavior.

M284 repeats the complete installed-wheel matrix and GitHub Actions qualification.

## Exclusions

S065 does not include volume rendering, low-level glyph/atlas APIs, broad materials, raw shaders,
arbitrary GPU state, legends, broad Matplotlib compatibility, comprehensive picking, remote
transport, version changes, tags, releases, package publication, force pushes, history rewrites, or
edits to the Datoviz repository.

## Stop conditions

Stop rather than improvise if:

- the accepted camera or visual semantics cannot map to either backend without silent divergence;
- a new visual requires backend handles or raw draw-call state in GSP or VisPy2;
- Datoviz bindings needed by the accepted slice are absent or unsafe;
- strict behavior would require modifying Datoviz;
- a worker needs a public API or capability identifier not defined by the technical baseline;
- a source repository is dirty, has an unexpected remote/head, or needs a force push;
- path locks conflict with another active run;
- installed-wheel validation fails after reasonable mission-local fixes.


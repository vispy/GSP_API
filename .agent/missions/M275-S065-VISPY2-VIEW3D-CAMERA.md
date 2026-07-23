# M275 - S065 VisPy2 View3D and static camera

## Status

Completed. Integrated as GSP commit `c39b046` and VisPy2 commit `60077e8`; closeout evidence is in
`.agent/S065_M275_STATIC_VIEW3D.md`.

## Goal

Implement the accepted `Axes3D` producer and static camera/projection journey, including camera fit
and at least one 3D mesh rendered by both backends.

## Contract

Follow sections 1-2 of `.agent/S065_TECHNICAL_BASELINE.md` exactly. Do not redesign GSP camera
semantics. Keep one axes per Figure and preserve every existing 2D call.

## Work

- Extend scene/view validation only where required to enforce exactly one 2D or 3D view.
- Add `Axes3D`, typed `subplots(projection=...)` overloads, camera/projection getters/setters,
  reducer-backed orbit/pan/zoom/reset, deterministic `fit_camera`, 3D mesh, title, attachments, and
  scene emission.
- Add numeric camera-fit tests for perspective, orthographic, reversed/degenerate bounds, invalid
  inputs, revision changes, and reset.
- Render installed-wheel 3D mesh examples through Matplotlib and Datoviz.
- Document capability requirements and explicit errors.

## Locks

- `gsp`: core scene/view3d validation, Matplotlib/Datoviz 3D mesh tests only
- `vispy2`: `src/vispy2/**`, `tests/**`, initial 3D example/docs

## Acceptance

All existing tests remain green; strict mypy/Ruff pass. Built `gsp-core`, both adapters, and VisPy2
wheels install together. An installed-wheel script creates perspective and orthographic scenes,
renders deterministic Matplotlib PNGs, and renders/captures Datoviz without source imports.

## Stop conditions

Stop on a need for backend state in Figure/Axes3D, a new camera model, silent camera adaptation, or
Datoviz modification.

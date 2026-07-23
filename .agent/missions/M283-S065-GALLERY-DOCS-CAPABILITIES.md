# M283 - S065 installed-wheel gallery, documentation, and capability matrix

## Status

Draft; promote after M282. Target repositories: `gsp`, `vispy2`.

## Goal

Turn the completed feature slice into inspectable user journeys and an exact support matrix.

## Required scope

- Implement all seven examples in section 9 of the technical baseline.
- Run examples from built wheels outside both source trees.
- Produce deterministic Matplotlib artifacts and isolated Datoviz captures.
- Add onboarding, 2D/3D API, camera, visual-family, query, capability, and backend-limitation docs.
- Generate a matrix with rows for every visual/camera/query example and columns for protocol,
  VisPy2, Matplotlib, Datoviz, strict/adapted/unsupported status, test, artifact, and diagnostic.
- Verify every README/doc code block or mark non-executable pseudocode explicitly.

## Acceptance

A new user can install local wheels and run every documented noninteractive example. Live examples
have exact controls and cleanup instructions. Links, imports, terminology, capabilities, and
limitations match code. Strict docs build if configured, tests, typing, lint, and diff checks pass.

## Stop conditions

Stop rather than editing capability claims to hide a backend failure. Record missing behavior as a
finding for Mission Control.


# M284 - S065 integrated qualification and human review

## Status

Draft; promote after M283. Target repositories: `gsp`, `vispy2`; Datoviz is read-only evidence.

## Goal

Qualify the complete feature tranche and hand the owner a compact visual/camera review pack.

## Required scope

- Run full pytest, strict mypy, Ruff, diff checks, docs validation, package builds, import isolation,
  lazy discovery, and all installed-wheel examples.
- Exercise Matplotlib and Datoviz from clean environments at exact commits.
- Run at least 25 isolated Datoviz lifecycle iterations for static and live 3D cases.
- Regenerate the complete gallery and capability matrix.
- Prepare a review index containing artifact thumbnails/paths, exact live commands, expected
  controls, known adaptations, and a checklist for each priority visual and camera behavior.
- Do not mark S065 complete until the owner records acceptance or actionable findings.

## Acceptance

Automated gates are green, repository worktrees are clean, local/remote handling is explicit, and
the review pack covers 2D, 3D, camera, pixel, sphere, vector, primitive, text, mesh, and minimal
query. Owner acceptance closes S065; findings open bounded follow-up missions.

## Exclusions

No version change, tag, release, publication, force push, merge to main, or Datoviz edit.


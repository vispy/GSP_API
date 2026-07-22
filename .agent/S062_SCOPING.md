# S062 proposal - Clean GSP and VisPy2 repository bootstrap

Date: 2026-07-22

Status: draft; awaiting explicit project-owner approval.

## Objective

Create local fresh-root `gsp` and `vispy2` repositories from the approved S061 manifest, implement
the backend provider/session boundary, and prove the separated distributions using built wheels.
Keep both repositories unpublished and preserve `GSP_API` as the migration authority.

## Proposed sequence

| Mission | State | Scope |
|---|---|---|
| M261 | draft | Create both local Git repositories with fresh roots, licenses, provenance, manifests, and package/workspace skeletons. |
| M262 | draft | Curate `gsp-core`, remove its Matplotlib dependency, restore core tests, and build an isolated wheel. |
| M263 | draft | Implement lazy `gsp.backends` discovery/session SPI and migrate `gsp-matplotlib` as the first provider. |
| M264 | draft | Migrate the Datoviz v0.4 adapter as a second provider with source-development and RC3 publication boundaries. |
| M265 | draft | Migrate and rename the producer to `vispy2`, add `Figure.to_scene()`, and remove all concrete adapter imports. |
| M266 | draft | Validate built-wheel combinations, cross-backend examples, provenance, documentation, and close the local bootstrap. |

## Local target paths

- `/Users/cyrille/GIT/Viz/gsp`
- `/Users/cyrille/GIT/Viz/vispy2`

Both paths were absent at S061 closeout. M261 must stop if either becomes occupied or if a target is
not an empty newly initialized repository created by the mission.

## Required package topology

```text
gsp repository
  packages/gsp-core         -> distribution gsp-core, import gsp
  packages/gsp-matplotlib   -> distribution gsp-matplotlib, import gsp_matplotlib
  packages/gsp-datoviz      -> distribution gsp-datoviz, import gsp_datoviz

vispy2 repository
  distribution vispy2       -> import vispy2
```

Dependency direction is `vispy2 -> gsp-core` and each adapter `-> gsp-core`. Core must not depend on
an adapter or producer. VisPy2 must not import a concrete adapter.

## Guardrails

- Do not create GitHub repositories, add remotes, push, tag, publish, or modify repository visibility.
- Do not modify or archive `GSP_API`; read it only through the recorded baseline/provenance.
- Do not copy legacy branches or filtered ancestry into either new repository.
- Do not copy archive-only components wholesale.
- Every imported file records source commit/path/blob and exact-versus-derived status.
- `import gsp` and metadata discovery must not import native backends or create graphics resources.
- Datoviz publication remains blocked until a normally installable RC3-compatible artifact passes
  all native and installed-wheel gates.
- Stop if `gsp-core` requires Matplotlib, Datoviz, network, Pydantic, or legacy object packages.
- Stop if tests pass only from editable/source-tree imports.

## Completion boundary

S062 ends with two clean local repositories and built-wheel evidence. Creating `vispy/gsp` and
`vispy/vispy2` on GitHub, configuring remotes, pushing histories, and releasing packages require a
later explicit external-publication mission.


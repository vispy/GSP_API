# Release Checklist and Tag Policy

Status: S045 release-readiness refresh, 2026-07-02.

This repository is still a research prototype at version `0.1.0`. The checklist below defines what
"release-ready" means for a local validation tag or future package publication. It is policy only;
it does not publish artifacts or create a tag.

## Current Release Baseline

- Package name: `gsp`
- Current version: `0.1.0`
- Python: `>=3.13,<4.0`
- Primary validation backend: Matplotlib reference path
- Optional backend paths:
  - legacy Datoviz wrapper via `pip install -e ".[datoviz-legacy]"`
  - Datoviz v0.4 adapter work remains capability-gated and is not declared as a package dependency
  - network renderer requires its server process and remote renderer configuration
- Current capability baseline:
  - release-facing docs must reflect accepted work through S044;
  - Matplotlib remains the reference for layout, navigation, View3D, Lambert shading, and S044
    mesh-triangle-pick CPU oracle behavior;
  - Datoviz v0.4 support is advertised only through runtime capability gates and structured
    unsupported diagnostics.
- Public fixture data included in release artifacts:
  - `fixtures/conformance/minimal_v0_1.json`

## Required Validation Before Any Tag

Run from the repository root:

```bash
PYTHONPATH=. uv run mypy src/ --strict --show-error-codes
PYTHONPATH=. uv run pytest -q
uv run mkdocs build --strict
uv build
python -m json.tool .agent/status.json >/dev/null
git diff --check
```

For release-candidate confidence, also run:

```bash
PYTHONPATH=. uv run python tools/run_all_examples.py
PYTHONPATH=. uv run python tools/check_expected_output.py
```

The example runner validates standalone public examples on the Matplotlib renderer path by default.
It intentionally excludes examples that require an external server or a two-step session setup.
Optional Datoviz, network, or session replay checks must be recorded separately with the exact
environment and dependency setup.

For post-S031 protocol work, also review the S034-S045 Mission Control records and focused
validation notes before tagging. They cover resolved layout, retained View2D navigation, static and
live View3D, Lambert mesh shading, Datoviz grid clipping, and S044 mesh triangle picking.

## Release Notes Checklist

Before tagging, update `CHANGELOG.md` by moving the relevant `Unreleased` entries under the target
version heading.

Required release note sections:

- Added
- Changed
- Fixed
- Validation
- Backend support
- Known limitations

Backend support must explicitly distinguish:

- Matplotlib reference backend;
- optional legacy Datoviz wrapper;
- capability-gated Datoviz v0.4 adapter work;
- network renderer server requirements.

Known limitations must explicitly mention that Datoviz v0.4 does not advertise
`query.view3d.mesh_triangle_pick.v1`, that strict opaque 3D GPU depth remains unproven, and that
native grid clipping is not full guide strictness.

## Tag Policy

- Do not tag automatically from an agent run.
- Use annotated tags only, e.g. `v0.1.1`, after explicit user approval.
- The tag commit must have a clean worktree and passing required validation.
- The version in `pyproject.toml`, release notes, and tag name must agree.
- Do not force-push or rewrite release tags.
- Do not publish to PyPI from Mission Control unless the user explicitly asks for publication and
  confirms credentials, version, package name, and artifact target.

Recommended local validation tag flow:

```bash
git status --short
PYTHONPATH=. uv run mypy src/ --strict --show-error-codes
PYTHONPATH=. uv run pytest -q
uv run mkdocs build --strict
uv build
git tag -a vX.Y.Z -m "Release vX.Y.Z"
```

Publishing remains a separate, explicit operation after artifact inspection.

## Stop Conditions

Stop before tagging or publishing if any of these are true:

- validation fails;
- package version and tag version disagree;
- Datoviz support wording implies v0.4 wheel support before an actual compatible release artifact;
- Datoviz support wording implies mesh-triangle-pick, strict opaque 3D GPU depth, perspective,
  textures, or full guide strictness before those claims are evidence-backed;
- release notes do not mention optional backend constraints;
- the worktree contains unrelated uncommitted changes;
- credentials or private token handling would be required.

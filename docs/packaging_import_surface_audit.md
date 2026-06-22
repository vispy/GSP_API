# Packaging, Import Surface, and Examples Audit

Status: M044 completed, S019 kickoff audit.

## Scope

This audit records the first S019 pass over packaging metadata, public import surfaces,
documentation entry points, example documentation, and validation commands. It does not make
dependency policy changes or rename public packages.

## Findings

### Packaging Metadata

- `pyproject.toml` has an empty project description. This is acceptable for local development but
  not for a release artifact.
- Runtime dependencies include developer and validation tools such as `mypy`, `pytest`, and `ruff`.
  These should be reviewed for movement into the dev dependency group before packaging.
- `datoviz (>=0.3.2,<0.4.0)` is pinned as a runtime dependency while the active adapter work targets
  Datoviz v0.4-dev capability probing. S019 needs an explicit packaging policy for legacy Datoviz,
  v0.4-dev smoke validation, and optional backend installs.
- `mpl3d` is installed from a Git URL at runtime. This is fragile for repeatable package installs and
  should either become an optional/dev dependency or be replaced with a release artifact strategy.
- The versioned conformance fixture `fixtures/conformance/minimal_v0_1.json` is outside `src/`.
  If fixtures are intended to ship in wheels, package-data inclusion needs an explicit check.

### Import Surface

- `src/gsp/__init__.py` describes the package as "Graphic Scene Protocol"; current stage language
  and Mission Control use "Graphics Server Protocol". The project name should be made consistent
  before release-facing docs are updated.
- Backend packages perform renderer registration at import time. This is useful for legacy examples
  but should be documented as a public side effect, or split into explicit registration helpers for
  package consumers that need import-only behavior.
- `gsp_datoviz.__init__` deliberately tolerates missing legacy Datoviz imports and exposes a no-op
  registration function. This behavior should be covered by a lightweight import-surface test before
  dependency cleanup.
- `vispy2.__init__` exposes the producer convenience API directly. S019 docs should distinguish this
  API from the lower-level `gsp.protocol` objects and from legacy `gsp.core` examples.

### Docs And Examples

- `README.md` documents `GSP_RENDERER`, while `examples/README.md` documents `GSP_BACKEND`.
  Existing philosophy docs also reference `GSP_RENDERER`. S019 should decide and apply one canonical
  environment variable or explicitly document both if both are supported.
- `README.md` links to `docs/philosophy/*.md` paths that are not present in the working tree. The
  active MkDocs source lives under `mkdocs_source/philosophy/`, with older prompt material under
  `docs/philosophy/prompts/`.
- `examples/README.md` lists `session_record_example.py` and `session_player_example.py`, but the
  files are currently named `session_01_record_example.py` and `session_02_player_example.py`.
- `examples/README.md` says all examples work with both Matplotlib and Datoviz. That overstates the
  current state, especially with Datoviz v0.4-dev adapter work and internal examples.
- `examples/README.md` names agent skills such as `docs-examples-gsp` and `test-validate-gsp` as if
  they were repository commands. User-facing docs should point to repo commands instead.
- `Makefile` has a `pyright` lint target, but `pyright` is not listed in `pyproject.toml` dependency
  groups. The lint story needs to be made installable or documented as externally supplied.

## Follow-Up Missions

- M045: packaging metadata, dependency policy, package-data inclusion, and import-surface smoke
  checks.
- M046: README, MkDocs entry point, example index, and backend environment variable consistency.

## Stop Conditions

- Do not rename the installed project or top-level packages in the audit mission.
- Do not drop Datoviz or `mpl3d` dependencies until S019 records a replacement install strategy.
- Do not change the public `vispy2` producer API while doing packaging and docs cleanup.

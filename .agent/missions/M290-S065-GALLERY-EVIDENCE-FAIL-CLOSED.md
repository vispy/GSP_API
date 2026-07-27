# M290 - S065 fail-closed gallery evidence correction

## Status

Completed and accepted through M292 on 2026-07-27. The fail-closed validator, exact provenance,
freshness checks, and capability sets all passed the final exact-wheel native run.

## Baseline

- GSP `48e1fb0` correctly limits consumed-layout Datoviz omission to non-queryable titles and emits
  one unsupported diagnostic per render.
- VisPy2 `a521242` removes public `Figure.render`, keeps protocol-only `Figure.resolve_layout`, and
  contains the schema-2 gallery draft.
- These commits are reviewable checkpoints, not final acceptance.

## Required corrections

### Exact capability sets

- Add `pixelvisual.v1` whenever Gallery 3 contains `PixelVisual`; retain
  `pixelvisual.positions3d.data.view3d.v1`.
- Replace the union/superset gallery capability test with exact per-gallery expected sets for
  Galleries 2, 3, and 4. Gallery 3 must explicitly contain both pixel capabilities plus
  orthographic, primitive, indexed, and triangle-strip capabilities.
- Keep all generic provider requirements and every existing View3D assertion.

### Exact runtime and logical import provenance

- Derive the runtime descriptor from the interpreter supplied by `--python`, preferably as part of
  the existing import-isolation subprocess. Never describe the harness interpreter implicitly.
- Validate the probe shape and types before using it.
- Normalize only a verified final `<package>/__init__.py` suffix. A parent directory earlier in the
  path named `gsp` or `vispy2` must not affect the result.
- Add tests for a differing probe runtime and paths such as
  `/temporary/gsp/build/site-packages/gsp/__init__.py`.

### Exact wheel hashes

- Make the validator accept four explicit named wheel inputs for `gsp-core`, `gsp-matplotlib`,
  `gsp-datoviz`, and `vispy2`.
- Reject missing, duplicate, unknown, nonexistent, or non-wheel inputs.
- Store only stable project names and SHA-256 values in the manifest; never store wheel paths.
- Update the copyable gallery validation command and prose so the wheel-hash claim is executable
  and truthful.

### Fresh output and Pillow

- Render all fourteen outputs into a new temporary capture directory, validate them there, build
  the manifest there, and publish/copy them to `--output-dir` only after the entire run succeeds.
  Never validate pre-existing output files or silently accept stale PNGs.
- Add a focused test proving pre-existing output cannot satisfy a run and failed validation does
  not publish a new manifest.
- Use the established offline exact-project-wheel model: install/unpack only the four newly built
  project wheels into an isolated project site, run from outside both source trees with that site
  first on `PYTHONPATH`, and use the prequalified GSP Python environment only for third-party
  dependencies. Assert all four project imports come from the isolated wheel site and Pillow is
  importable. This is project-wheel isolation, not a claim that third-party dependencies were
  rebuilt.

### GSP diagnostic regression

- Add a two-title consumed-layout test proving one unsupported-title diagnostic is appended for the
  accepted render, not one duplicate per guide.

## Required validation

- Focused GSP title tests and VisPy2 gallery-contract tests.
- Full GSP and VisPy2 pytest suites, complete strict source mypy, strict validator mypy, Ruff,
  provider probes, docs/link validation, and `git diff --check`.
- Build all four exact wheels from the candidate committed heads.
- Run project-wheel isolation and producer-only isolation without native Datoviz presentation.
- Run seven Matplotlib captures at exactly 800x600 and exercise schema-2 manifest generation with
  the real wheel hashes.
- Do not invoke native Datoviz presentation in the worker sandbox.
- Commit coherent corrections separately in each changed writable repository.

## Acceptance

- Independent source/static review issues an unconditional ACCEPT.
- Exact per-gallery capability tests include `pixelvisual.v1`.
- Runtime/import/wheel provenance is truthful and portable.
- Stale artifacts cannot satisfy validation.
- Exact project-wheel imports and Pillow availability are proven.

## Stop conditions

- Stop rather than weakening any assertion.
- Stop on new public semantics, a source/spec conflict, or need for a Datoviz edit.
- Stop before native Datoviz presentation in the sandbox.
- Do not push, merge, tag, release, publish, create a PR, or change package versions.

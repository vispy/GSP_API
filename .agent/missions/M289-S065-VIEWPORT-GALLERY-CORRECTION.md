# M289 - S065 viewport gallery correction and static qualification

## Status

Approved for execution after the stopped M288 run. Execute directly with the pinned
`codex-ucl-gpt-5.6-sol-medium` provider. The worker is already the launched implementation worker;
do not call `agentctl`, launch another worker, or act as Mission Control.

## Baseline

The canonical `gsp` and `vispy2` heads contain explicit, non-accepted WIP checkpoints from M288:

- `gsp` `eb97d38` (`wip: allow shared viewport title omission`);
- `vispy2` `ce623f3` (`wip: add shared viewport gallery evidence`).

M287 and its resolved viewport contract remain accepted. Datoviz is read-only evidence.

## Goal

Correct the M288 source/API defects and fully qualify all non-native behavior so Mission Control can
perform native gallery capture outside the worker sandbox without making architectural decisions.

## Required corrections

### VisPy2 public boundary

- Remove public `Figure.render(...)->Any` and its public test. VisPy2 must not expose or retain a
  backend renderer/result.
- Keep `Figure.resolve_layout(session, **kwargs) -> ResolvedLayoutSnapshot`. It may delegate
  directly to the caller-owned session internally, extract only the protocol snapshot, and return
  only that snapshot.
- Gallery-internal `gallery_shared_layout.py` may call
  `session.render(figure.to_scene(), layout_snapshot=..., target=...)` because the caller owns the
  session and the helper is not public VisPy2 API. Backend-result inspection must stay in that
  example helper.
- Keep strict typing; declare fake-session result attributes in `__init__`.

### Capability coverage

- Preserve and test the existing View3D capability assertions for galleries 2-4:
  perspective/orthographic projection, mesh, pixel, sphere, vector, billboard text, primitive,
  indexed primitive, and triangle strip.
- Do not weaken a capability, viewport, projection, anchor, raster-bound, or image-dimension
  assertion.

### Datoviz title boundary

- Consumed-layout Datoviz may omit panel text only when every panel text guide has
  `role is PanelTextRole.TITLE` and
  `query_policy is GuideQueryPolicy.NON_QUERYABLE`.
- Record the existing unsupported title diagnostic for each accepted render, without claiming title
  rendering.
- Continue rejecting subtitle guides, queryable title guides, axis guides, and colorbar guides
  before native resource creation.
- Add positive non-queryable-title and negative subtitle/queryable-title tests.

### Portable evidence

- Keep schema-2 layout/projection evidence and all strict comparisons.
- Generate a portable runtime description such as `CPython 3.13.4 macOS arm64`; do not store the
  interpreter's absolute path.
- Normalize exact-wheel import provenance to logical paths such as
  `isolated-wheel-site/gsp/__init__.py` and
  `isolated-wheel-site/vispy2/__init__.py`.
- Ensure generated/committed Markdown and JSON contain no host-absolute paths.
- Ensure Pillow is available in the exact validation environment and the validator remains typed and
  lint-clean.
- Explicitly document that exact shared `plot_rect` equality proves an unsupported Datoviz title
  neither resizes nor shifts the data viewport.

## Required validation

- Run focused tests while correcting.
- Run the complete GSP pytest suite, strict mypy across the complete GSP source set, Ruff, backend
  imports/provider probes, and `git diff --check`.
- Run the complete VisPy2 pytest suite, strict mypy, Ruff, docs/link checks, wheel build, and
  producer-only/exact-wheel isolation checks that do not invoke Datoviz native presentation.
- Validate a Matplotlib gallery smoke at exactly 800x600 and exercise the evidence/manifest schema
  without absolute paths.
- Do not attempt Datoviz native capture in the sandbox; M288 proved that environment reproducibly
  hangs before a frame. Mission Control owns the subsequent unsandboxed native qualification.
- Commit coherent corrections separately in `gsp` and `vispy2`.

## Acceptance

- No backend-specific renderer/result escapes through the VisPy2 public `Figure` API.
- Datoviz title omission is limited to non-queryable titles and all negative guide tests pass.
- Existing capability assertions and schema-2 geometry checks are present and tested.
- Generated provenance is portable by construction.
- All required non-native/full static gates pass.
- Independent read-only supervision issues an unconditional source/static ACCEPT.

## Stop conditions

- Stop on a source/spec conflict or if correction requires new public protocol semantics.
- Stop rather than weaken assertions.
- Stop before any Datoviz repository edit or any sandboxed native Datoviz capture.
- Stop on unrelated dirty state, path-lock conflict, or a need for credentials.
- Do not push, merge, tag, release, publish, create a PR, or change package versions.

## R20260726-201012-M289 supervision result

The useful corrections are preserved in `gsp` commit `48e1fb0` and VisPy2 commit `a521242`.
They are checkpoints, not accepted closeout. Green evidence included 788 GSP tests, 73 VisPy2
tests, strict mypy, Ruff, provider probes, docs/link validation, seven Matplotlib 800x600 captures,
four wheel builds, and project-wheel isolation.

Independent review rejected the checkpoint because Gallery 3 still omitted `pixelvisual.v1`, the
runtime description came from the harness rather than `--python`, logical import normalization
selected the first package-named path component, and schema 2 omitted exact wheel hashes. Review
also requested fail-closed fresh capture publication and a documented exact-project-wheel
environment where Pillow is available. M290 owns these bounded corrections.

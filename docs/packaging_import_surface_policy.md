# Packaging and Import Surface Policy

Status: M045 baseline.

## Packaging

- The installable project is named `gsp`.
- Release metadata must describe GSP as backend-agnostic scene and protocol tooling for scientific
  visualization.
- The wheel must explicitly include all public top-level packages:
  `gsp`, `gsp_datoviz`, `gsp_extra`, `gsp_matplotlib`, `gsp_network`, `gsp_pydantic`, `vispy2`, and
  `fixtures`.
- The minimal versioned conformance fixture `fixtures/conformance/minimal_v0_1.json` is package
  data and must be readable through `importlib.resources`.

## Dependency Groups

- Runtime dependencies are libraries imported by installed packages during supported use.
- Test, lint, and type-check tools belong in the dev dependency group.
- The vendored `gsp_extra.mpl3d` source is used directly; the external `mpl3d` Git dependency is not
  part of the default runtime dependency set.

## Datoviz

- Legacy Datoviz wrapper support is optional and exposed as the `datoviz-legacy` extra, pinned to
  `datoviz>=0.3.2,<0.4.0`.
- Datoviz v0.4-dev adapter work remains capability-gated in code and validated by local smoke tests.
  It is not declared as a package dependency until a compatible install artifact exists.
- Importing `gsp_datoviz` must remain useful without Datoviz installed: the v0.4 protocol modules
  should stay importable, while legacy renderer registration reports the missing Datoviz wrapper.

## Import Surface

- Importing `gsp`, `vispy2`, and protocol-facing backend helpers should not require Datoviz.
- Importing `gsp_matplotlib` and `gsp_network` preserves the legacy renderer-registration side
  effect.
- Changing backend registration semantics requires explicit tests and user-facing documentation.

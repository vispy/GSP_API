# M262 gsp-core curation and isolation

Date: 2026-07-22

## Result

Curated the formal protocol into `/Users/cyrille/GIT/Viz/gsp` commit `a0d76b7`. The new
`gsp-core==0.2.0a1` distribution contains 26 source files, current specification/ADR authority, and a
protocol-only test subset.

The source Matplotlib dependency in canonical color mapping was removed. Six exact accepted S026
RGBA8 lookup tables are packaged as backend-independent protocol data with documented provenance.

## Validation

- 164 protocol tests pass from the built installed wheel.
- Strict mypy passes for all 26 core source files.
- Ruff passes.
- Wheel and sdist build successfully.
- Installed metadata requires only `numpy>=2.3,<3`.
- `import gsp` loads neither Matplotlib nor Datoviz.
- Wheel SHA-256: `24666356ccf9f2418c4ab1f433b8e3220feb3466822f2f5a3fffb2872cf6cab3`.
- Sdist SHA-256: `aaf77ce31be2a7514e340c58605a72228ac9bbdba15e0dedb5e390f1d044cb43`.

The repository remains clean and has no remote.


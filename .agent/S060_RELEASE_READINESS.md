# S060 package and release-readiness evidence

Date: 2026-07-22

## Provenance

| Field | Value |
|---|---|
| GSP validation commit | `1edd46e` plus this evidence-only record |
| GSP branch | `main` |
| Package | `gsp-vispy2 0.2.0` |
| Python | `>=3.13,<4.0`; validation used 3.14.6 |
| Datoviz source | `be7f2a80354c25e85bab88c85f5ea7340975b569` |
| Datoviz describe | `v0.4.0rc2-15-gbe7f2a803` |

The GSP and Datoviz worktrees were not modified by package or runtime validation. The existing
untracked Datoviz paper outputs remained untouched.

## Package artifacts

`uv build` created both distributions from the current source in a temporary directory:

| Artifact | Size | Files | SHA-256 |
|---|---:|---:|---|
| `gsp_vispy2-0.2.0-py3-none-any.whl` | 451 KiB | 247 | `53ea1376ef14e48837cbccc21d2f189cb00b1c0d480689e33366a6c4d898106b` |
| `gsp_vispy2-0.2.0.tar.gz` | 339 KiB | 247 | `c09473c06a89481790037588db0b09dcc0a6254d2f6a1dba14bcf2c6ee5ada46` |

The wheel metadata reports the expected name, version, Python range, dependencies, README, and
legacy Datoviz extra. A fresh isolated environment installed the wheel with declared dependencies
and imported `gsp`, `gsp_vispy2`, `gsp_matplotlib`, and `gsp_datoviz` from site-packages. The wheel
contains the current protocol, VisPy2 producer, and Datoviz adapter modules. Build artifacts remain
temporary and were not added to the repository.

## Validation

- full pytest with coverage: 680 passed, 2 skipped, 66% aggregate coverage;
- strict mypy: clean across 221 source files;
- Ruff and `git diff --check`: clean;
- specification traceability, profile consistency, public-doc consistency, and strict MkDocs: clean;
- Matplotlib and exact local-source Datoviz imports: clean;
- fresh Texture2D checkpoint: 9/9 native cases rendered, all eight linear-filter numeric probes
  within tolerance, current example inspection passed, and 241 focused tests passed.

The 66% aggregate coverage is the repository-wide legacy-inclusive baseline and remains below the
release skill's aspirational 80% target. The current protocol, producer, and active adapters have
materially higher focused coverage; no project policy currently makes 80% aggregate coverage a
release gate.

## Dependency boundary

Datoviz v0.4 is intentionally absent from normal package dependencies. The `datoviz-legacy` extra
still targets v0.3, while the current adapter is validated against a local post-RC2 development
checkout. A compatible Datoviz v0.4 release artifact has not yet been validated or declared.

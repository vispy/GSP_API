# S033 Release Audit - Post-S032

Generated: 2026-06-27

## Result

Post-S032 release preparation is complete. The tree is ready for human artifact review and explicit
release approval, subject to the normal release policy.

No tag was created, no package version was changed, and nothing was published.

## Finding

The release-facing changelog limitation text was narrower than the current regenerated capability
matrix. It mentioned Datoviz guide/View2D adapted rows but omitted the four adapted Datoviz text
rows.

Fixed in `CHANGELOG.md` by documenting that current Datoviz v0.4 adapted review rows include text
anchor/placement/unicode verification gates as well as guide panel-title and guide/all-rendered
query gaps.

## Current Artifacts

Primary all-cases sheet:

`artifacts/visual_qa/s031/full-review-pack-legacy/contact_sheets/s028_all_cases.png`

Diagnostic linear-light all-cases sheet:

`artifacts/visual_qa/s031/full-review-pack-linear/contact_sheets/s028_all_cases.png`

## Current Datoviz Matrix

| Status | Datoviz count |
|---|---:|
| strict | 23 |
| adapted | 6 |
| unsupported | 0 |

Adapted rows:

- `text/basic_ndc`
- `text/anchor_grid_ndc`
- `text/data_vs_ndc`
- `text/multiline_unicode_smoke`
- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

## Validation

- `python -m json.tool .agent/status.json >/dev/null`: passed.
- `git diff --check`: passed.
- `uv run mkdocs build --strict`: passed, with the existing upstream MkDocs Material 2.0 warning.

Full code validation remains the S032 validation baseline:

- `uv run pytest -q`: 411 passed, 2 skipped.
- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: clean.
- backend import smoke checks for Matplotlib and Datoviz passed.

## Next Gate

M131 remains blocked. Before release operations, the user must explicitly approve:

- target version;
- package-version update, if any;
- annotated tag creation;
- publication target, if any.

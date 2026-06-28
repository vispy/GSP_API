# M132 - API review examples and backend comparison runner

## Stage

S033 - Datoviz Guide Strictness and Release Decision

## Status

Completed by local-main-codex.

## Summary

Create a small user-facing example pack for reviewing the GSP protocol/API shape and comparing
Matplotlib and Datoviz v0.4 live or captured output. This mission is documentation/example work,
not a release operation.

## Deliverables

- `examples/review/` with concise, readable API-review examples.
- A shared review runner supporting Matplotlib and Datoviz backends, live display, and captured artifacts.
- A convenience command under `tools/` to run one or all review examples for comparison.
- `examples/review/README.md` with copy-paste commands and known Datoviz/offscreen notes.
- Update the main examples index to point reviewers to the new pack.

## Acceptance

- At least four review examples are present and runnable through the shared CLI.
- Matplotlib capture path works locally for all examples.
- Datoviz live path is wired through the existing v0.4 protocol renderer.
- Datoviz capture failures or disabled offscreen support are reported as explicit artifacts, not hidden.
- The mission status records validation and remaining review risks.

## Stop Condition

Stop before changing public API semantics if examples reveal a conflict with the charter/spec, or if
Datoviz comparison requires risky unsupported native behavior.

## Plan

1. Record mission and update Mission Control status.
2. Add review example runner and first examples.
3. Add comparison tooling and documentation.
4. Validate the Matplotlib path and lightweight CLI behavior.
5. Mark mission complete with validation notes.

## Result

Completed. Added `examples/review/` with six small API-review examples, a shared backend runner, and `tools/compare-review-examples` for Matplotlib/Datoviz comparison artifacts.

Validation performed:

- `uv run python -m py_compile examples/review/_review_runner.py examples/review/[0-9]*.py tools/compare-review-examples`
- `uv run ruff check examples/review tools/compare-review-examples`
- Matplotlib capture smoke for all six review examples
- `tools/compare-review-examples examples/review/01_scatter_basic.py` confirms Matplotlib renders and Datoviz capture writes an explicit unsupported artifact when offscreen capture is not opted in

Remaining review notes:

- Datoviz live comparison should be reviewed manually with `--backend datoviz --live`.
- Datoviz PNG capture remains opt-in via `--datoviz-offscreen` or `GSP_DATOVIZ_QA_ENABLE_OFFSCREEN=1` because native offscreen setup can be environment-sensitive.

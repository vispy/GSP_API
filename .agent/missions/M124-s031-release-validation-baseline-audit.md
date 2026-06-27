# M124 - S031 release validation baseline audit

## Stage

S031 - Release-Candidate Stabilization and Roadmap Reset

## Status

Completed by local-main-codex.

## Summary

Run the release validation baseline from `docs/release_checklist.md` and classify any failures into
small follow-up missions before release-note or closeout work.

## Scope

- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`
- `PYTHONPATH=. uv run pytest -q`
- `uv run mkdocs build --strict`
- `uv build`
- `python -m json.tool .agent/status.json >/dev/null`
- `git diff --check`
- Optional release-candidate confidence checks only if the required baseline is clean:
  `tools/run_all_examples.py` and `tools/check_expected_output.py`.

## Deliverables

- Validation report with exact commands and results.
- Scoped follow-up missions for each actionable failure, if any.
- Updated Mission Control recommendations.

## Acceptance

- Required validation commands are run or explicitly marked unavailable with the reason.
- Failures are not hidden by broad environment assumptions.
- No code, docs, or release-note fixes are bundled into this audit unless they are trivial
  control-plane corrections.
- The next mission is clear: either M125 release-note/backend wording audit or a failure-specific
  remediation mission.

## Result

Required validation passed:

- `PYTHONPATH=. uv run mypy src/ --strict --show-error-codes`: success, 206 source files.
- `PYTHONPATH=. uv run pytest -q`: 403 passed, 2 skipped.
- `uv run mkdocs build --strict`: passed; MkDocs Material emitted its upstream MkDocs 2.0 warning.
- `uv build`: built `dist/gsp-0.1.0.tar.gz` and `dist/gsp-0.1.0-py3-none-any.whl`.
- `python -m json.tool .agent/status.json >/dev/null`: passed.
- `git diff --check`: passed.

Optional release-candidate confidence checks:

- `PYTHONPATH=. uv run python tools/run_all_examples.py`: initially found eager optional Datoviz
  legacy imports in Matplotlib-only examples and a live-window block in `protocol_live_window.py`.
  These were fixed narrowly; rerun passed all 56 Matplotlib-path examples.
- `PYTHONPATH=. uv run python tools/check_expected_output.py`: passed, 3 expected files matched.

M125 is ready for release-note and backend-support wording audit.

## Stop Condition

Stop if validation requires external credentials, package publication, release tagging, force-push,
or changing Datoviz support policy. Stop and create a consultation packet if failures imply a public
API compatibility decision or accepted-spec conflict.

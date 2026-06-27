# M125 - S031 release notes and backend-support wording audit

## Stage

S031 - Release-Candidate Stabilization and Roadmap Reset

## Status

Completed by local-main-codex.

## Summary

After M124, audit release-facing text so `CHANGELOG.md`, README/docs, backend capability wording,
and known limitations accurately describe the validated state.

## Deliverables

- Release-note checklist against `docs/release_checklist.md`.
- Backend-support wording audit distinguishing Matplotlib, optional legacy Datoviz, capability-gated
  Datoviz v0.4, and network renderer requirements.
- Follow-up patches or missions for any release-facing drift.

## Result

Completed the release-facing wording audit:

- `CHANGELOG.md` now includes the required `Fixed`, `Backend support`, and `Known limitations`
  sections under `Unreleased`.
- `README.md` now describes GSP as backend-agnostic scene/protocol tooling with Matplotlib as the
  reference backend and Datoviz/network as optional paths.
- Backend-support wording preserves the release checklist distinctions for Matplotlib, optional
  legacy Datoviz, capability-gated Datoviz v0.4, and network renderer requirements.

Validation:

- `uv run mkdocs build --strict`: passed; MkDocs Material emitted its upstream MkDocs 2.0 warning.
- `uv build`: passed.
- `PYTHONPATH=. uv run pytest tests/test_import_surface.py -q`: 5 passed, 1 skipped.
- `python -m json.tool .agent/status.json >/dev/null`: passed.
- `git diff --check`: passed.

M126 is ready for S031 closeout.

## Stop Condition

Stop before changing package version, creating a release heading, tagging, or publishing unless the
user explicitly approves a target version and release operation.

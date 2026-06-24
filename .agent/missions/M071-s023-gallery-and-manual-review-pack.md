# M071 - S023 gallery and manual review pack

## Stage

S023 - Visual Families v1 and Manual Visual QA Foundation

## Status

Completed.

## Summary

Produce user-facing examples and a final manual review artifact pack for S023 visual families.

## Planned Deliverables

- Examples for marker, segment, path, and updated point/image protocol examples.
- Combined gallery command or script using formal protocol scenes.
- Final contact sheets and manual review notes templates.
- README/docs update explaining how to run the visual QA suite.

## Completed

- Added VisPy2 protocol examples for marker, segment, path, and scalar image visuals.
- Updated `examples/README.md` with S023 protocol examples and visual QA run instructions.
- Added MkDocs page `mkdocs_source/s023_visual_qa.md` and linked it from `mkdocs.yml`.
- Regenerated the final S023 visual QA pack under `artifacts/visual_qa/s023/latest-local/`; all Matplotlib and Datoviz cases rendered.
- Verified examples write PNG outputs under `examples/output/`.

## Acceptance

A human can run one command and inspect all S023 cases. Examples construct GSP protocol scenes and
do not call backend APIs directly.

## Stop Condition

Stop if examples bypass the protocol producer path or call Matplotlib/Datoviz implementation APIs
directly.

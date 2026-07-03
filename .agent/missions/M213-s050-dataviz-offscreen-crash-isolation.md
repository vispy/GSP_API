# M213 - S050 Datoviz offscreen crash isolation

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

Isolate Datoviz offscreen review-pack crashes so evidence-producing runs can fail structurally
without killing the parent process or leaving ambiguous partial artifacts.

## Required Context

- `.agent/S050_DATOVIZ_COLORBAR_EXPLICIT_TICK_PROOF.md`
- `.agent/S050_DATOVIZ_RETAINED_VIEW3D_DEPTH_PROOF.md`
- `tools/run_datoviz_visual_review_pack.sh`
- `src/gsp/qa/visual/review_pack.py`
- `src/gsp/qa/visual/runner.py`
- `tests/test_visual_qa_harness.py`

## Deliverables

- Decide whether the crash isolation belongs in the shell wrapper, the Python review-pack runner, or
  a separate subprocess helper.
- Make opt-in Datoviz offscreen runs report native crashes as structured artifacts when possible.
- Preserve successful Datoviz artifacts only when the child process exits cleanly.
- Keep the sibling Datoviz checkout read-only.

## Stop Conditions

- Stop before editing `/home/cyrille/GIT/Viz/datoviz`.
- Stop before treating partial PNG output from a crashed Datoviz process as promotion evidence.
- Stop if native crash isolation requires credentials, package publication, or manual build-system
  intervention.

## Result

Completed locally. See `.agent/S050_DATOVIZ_OFFSCREEN_CRASH_ISOLATION.md`.

Outcome: `datoviz-offscreen-opt-in` review packs now run Datoviz in a child process and merge only
clean child artifacts. Nonzero child exits become structured Datoviz error rows, and child staging
is discarded. Real M206/M210 retry runs now exit cleanly in the parent and expose coordinate-space
enum compatibility blockers instead of parent-process crashes.

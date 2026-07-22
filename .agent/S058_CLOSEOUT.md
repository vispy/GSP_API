# S058 closeout - Datoviz v0.4-dev rolling compatibility and RC3 feedback

Date: 2026-07-22

S058 established a clean rolling-development baseline against Datoviz `v0.4-dev` commit
`71c444cee65a6b4bb825ba4e0a4e448036707037` and added a repeatable exact-provenance checkpoint for
later RC3 commits.

## Outcome

- The maintained S028 matrix has 53 strict, seven adapted, and zero crashed rows.
- Four rows improved versus the latest pre-RC baseline and none regressed.
- Public session lifecycle evidence passed 10/10; the internal five-mode matrix passed 25/25.
- Full GSP validation passed with 666 tests and two skips, strict mypy, Ruff, and backend imports.
- `tools/run_datoviz_v04dev_checkpoint.sh` reproduces provenance verification, native replay,
  comparison, lifecycle, and 168 focused tests in one bounded command.

## Capability decision and post-closeout follow-up

The original rolling checkpoint made no capability changes. A same-day follow-up against Datoviz
`be7f2a80354c25e85bab88c85f5ea7340975b569` added the missing public field-slot sampling API and
proved the bounded S050 Texture2D path. GSP now capability-gates and renders RGBA8 textures with
per-vertex UVs, nearest/clamp/no-mipmap sampling, top-row/high-v origin adaptation, linear-color
upload, vertex-color multiplication, the unlit material model, and retained DATA-space View3D.

The S050 review pack rendered all five Datoviz Texture2D cases with no unsupported or crashed
Datoviz rows. Datoviz also supports linear sampling, but GSP continues to request nearest because
linear filtering is outside the current S050 protocol profile. Canonical mesh-triangle identity and
rich live image payloads remain blocked by incomplete public Datoviz semantics or runtime evidence.

## Next trigger

Run the rolling checkpoint after a Datoviz runtime, scene API, generated binding, query, guide, or
session-lifecycle change. Open a narrow adapter mission only when that comparison produces a new
runtime-proven semantic capability or a regression requiring compatibility work.

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

## Capability decision

No GSP capability changes in this stage. Guide execution is now crash-free but remains adapted.
Texture2D mesh sampling, canonical mesh-triangle identity, and rich live image payloads remain
blocked by incomplete public Datoviz semantics or runtime evidence.

## Next trigger

Run the rolling checkpoint after a Datoviz runtime, scene API, generated binding, query, guide, or
session-lifecycle change. Open a narrow adapter mission only when that comparison produces a new
runtime-proven semantic capability or a regression requiring compatibility work.

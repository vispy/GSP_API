# M048-RELEASE-READINESS-DOCS-POLISH - Release-readiness docs polish

## Mission

M048

## Goal

Close the remaining release-facing documentation drift after strict mypy closure.

## Acceptance

- Release-facing docs consistently use "Graphics Server Protocol" per `PROJECT_CHARTER.md`.
- Datoviz support wording distinguishes the Matplotlib reference path, optional legacy Datoviz
  wrapper support, and capability-gated Datoviz v0.4 adapter work.
- `examples/README.md` lists the shipped public example scripts and no longer shows stale constructor
  or `viewport.add_visual()` patterns.
- MkDocs strict build and the standard test/type/build validation surface remain green.

## Stop conditions

Stop before changing runtime backend selection, adding new examples, publishing artifacts, or making
Datoviz v0.4 release/support claims beyond local capability-gated adapter work.

## Source

S019 recommendation after M047 strict mypy closure.

## Result

Completed. Updated release-facing docs and examples guide wording, added missing mesh/protocol/image
examples to the example index, replaced the stale common-pattern snippet with current render API
usage, and validated the docs/test/type/build surface.

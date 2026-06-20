# P001 - Extensions and virtual data-source v0.1 scope

## Question for ChatGPT Pro

We have a working GSP v0.1 vertical slice with point/image visuals, Matplotlib reference rendering, and reference panel query. We want to add an extension system and virtual data-source model for huge remote datasets such as tiled cloud images and map layers.

Please define the minimal v0.1 architecture for:

- extension manifests;
- virtual data sources;
- data locality;
- server-side fetch;
- local fake tiled-image proof;
- security boundaries;
- what must be explicitly out of scope.

## Context files to provide

- PROJECT_CHARTER.md
- ARCHITECTURE.md
- adr/ADR-0003-gsp-v0.1-vertical-slice.md
- spec/extensions.md
- spec/data_sources.md
- spec/resources.md
- spec/visuals/image.md
- spec/query.md

## Expected output

- Recommended architecture.
- Minimal v0.1 scope.
- Required protocol objects.
- Required tests/fixtures.
- Stop conditions.
- Task list for Codex agents.
- Explicit non-goals.

## Blocked work

Do not implement M011 beyond documentation until this consultation is answered.

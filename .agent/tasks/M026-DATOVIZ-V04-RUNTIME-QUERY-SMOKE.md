# M026-DATOVIZ-V04-RUNTIME-QUERY-SMOKE - Datoviz v0.4 runtime query smoke and capability promotion

## Mission

M026

## Goal

Gate Datoviz v0.4 query capability promotion on Python-visible runtime query bindings.

## Acceptance

- Missing query binding pieces produce explicit diagnostics.
- `panel-query` is advertised only when query request, queue, poll, and decodable result bindings exist.
- `point-item` and `image-texel` remain unadvertised.
- Runtime smoke skips cleanly when the active Datoviz binding is incomplete.

## Stop conditions

Stop before real GPU/offscreen runtime query execution, point/image mode promotion, application-id
mapping, or Datoviz repository edits.

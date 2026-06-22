# M032-TILED-SOURCE-VIEWPORT-SEMANTICS-HARDENING - Tiled-source viewport semantics hardening

## Mission

M032

## Goal

Harden the local-only tiled-image proof so viewport source rectangles behave deterministically at
source edges for materialization, Matplotlib rendering, and query payloads.

## Acceptance

- Partially out-of-bounds source rectangles are clipped against source bounds.
- Rendered Matplotlib extent is clipped consistently with the materialized mosaic.
- Queries use the same clipped extent and clipped source rectangle as rendering.
- Tests cover partial edge mosaics, clipped render extent, clipped query miss, and clipped query hit.

## Stop conditions

Stop before adding remote fetch, credentials, async cache/prefetch/retry behavior, dynamic plugin
loading, or Datoviz tiled-source upload support.

## Result

Completed in the local reference path. `ViewportTileRequest` now permits negative x/y origins for
partial edge requests while still requiring positive size. The fake provider clips requests to
source bounds, and Matplotlib render/query helpers now use the clipped source rectangle to compute
the displayed extent and query payload coordinates.

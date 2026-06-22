# M034-TILED-SOURCE-CONFORMANCE-FIXTURE-COVERAGE - Tiled-source conformance fixture coverage

## Mission

M034

## Goal

Add deterministic tiled-source fixtures to the existing Python/in-process conformance package so S018
can build replay support from a stable local baseline.

## Acceptance

- Conformance fixtures expose a static tiled-image manifest, source, provider, clipped mosaic
  request, query, extent, and visual id.
- Tests lock manifest/source linkage, clipped mosaic output, tile ordering, Matplotlib clipped
  extent, and typed tiled-image query payload coordinates/value.
- Fixture docs list tiled-source coverage and keep JSON/base64 replay deferred.

## Stop conditions

Stop before adding JSON fixture schemas, base64 array encoding, remote fetch, credentials, plugin
loading, cache/prefetch behavior, or Datoviz tiled-source upload support.

## Result

Completed. The conformance package now includes `tiled_image_source_fixture()` and
`tiled_source_scene()` alongside point/image/guide fixtures.

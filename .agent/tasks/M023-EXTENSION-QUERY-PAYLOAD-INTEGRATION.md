# M023-EXTENSION-QUERY-PAYLOAD-INTEGRATION - Extension query payload integration

## Mission

M023

## Goal

Wire typed extension query payloads into scoped Matplotlib/reference query routing.

## Acceptance

- Tiled-image extension payload hits are available through `data` scoped queries.
- Extension hits participate in `all-rendered` bounded render-order sorting.
- Unsupported requested extension payload kinds return `unsupported`.
- The tiled-image payload kind is a named protocol constant and matches returned query results.

## Stop conditions

Stop before Datoviz runtime query implementation, dynamic extension loading, remote data transport,
or broader virtual data-source hardening.

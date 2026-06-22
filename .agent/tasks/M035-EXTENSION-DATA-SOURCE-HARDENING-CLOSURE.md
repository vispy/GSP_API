# M035-EXTENSION-DATA-SOURCE-HARDENING-CLOSURE - Extension data-source hardening closure

## Mission

M035

## Goal

Close S017 by aligning reference backend and conformance capabilities with the tiled-source support
implemented in M032-M034.

## Acceptance

- Matplotlib reference capabilities advertise `gsp.tiled-image@0.1` and static manifest support.
- Matplotlib reference capabilities advertise virtual/tiled/synthetic data-source support and
  bounded tile/mosaic limits.
- The v0.1 conformance capability fixture advertises the same extension/data-source surface.
- Tests lock the advertised capability surface.

## Stop conditions

Stop before implementing S018 replay mechanics, JSON/base64 fixture schemas, remote fetch,
credentials, dynamic plugins, cache/prefetch behavior, or Datoviz tiled-source support.

## Result

Completed. S017 is closed and Mission Control is advanced to S018.

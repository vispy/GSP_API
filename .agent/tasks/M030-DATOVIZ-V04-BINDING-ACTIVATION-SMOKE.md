# M030-DATOVIZ-V04-BINDING-ACTIVATION-SMOKE - Datoviz v0.4-dev binding activation smoke

## Mission

M030

## Goal

Provide a durable way to activate and smoke-test the local Datoviz v0.4-dev Python facade from GSP.

## Acceptance

- Smoke harness imports the v0.4-dev wheel-stage facade when environment paths are supplied.
- Smoke reports facade, sampled-field, capture, and query readiness independently.
- Adapter point/image setup succeeds against the v0.4 facade.
- Query readiness remains gated with a clear diagnostic when `DvzQueryResult._fields_` is missing.

## Stop conditions

Stop before Datoviz repository edits, GSP lockfile upgrade to 0.4-dev, mandatory GPU/headless
capture, or any query-readiness claim while live query results are not Python-decodable.

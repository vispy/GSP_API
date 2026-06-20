# GSP-HARDEN-004 - Add conformance README

## Goal

Document how the current conformance baseline works and how Matplotlib acts as the reference backend.

## Mission

M006

## Expected output

- `tests/conformance/README.md` or `fixtures/README.md`, depending on current repo layout.

## Acceptance

- Explains point/image/query baseline.
- Explains local fast path.
- Explains what is intentionally not yet covered.

## Stop conditions

Stop if no clear conformance directory exists; propose placement instead.

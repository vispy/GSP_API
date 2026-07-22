# M263 - S062 provider SPI and Matplotlib adapter

## Stage

S062 - Clean GSP And VisPy2 Repository Bootstrap

## Status

Approved; M262 completed.

## Summary

Implement lazy backend discovery and backend-neutral sessions in `gsp-core`, then migrate
`gsp-matplotlib` as the first `gsp.backends` provider and restore reference conformance.

## Acceptance

- Entry-point enumeration is side-effect-free and rejects duplicate names.
- Provider/plugin and protocol compatibility are checked deterministically.
- Explicit backend selection never silently falls back or adapts.
- Matplotlib is optional, discoverable only when installed, and passes reference tests from wheels.

## Stop conditions

Stop if core imports Matplotlib, discovery eagerly imports adapters, sessions leak native objects into
semantic records, or adaptation occurs without explicit policy and diagnostics.

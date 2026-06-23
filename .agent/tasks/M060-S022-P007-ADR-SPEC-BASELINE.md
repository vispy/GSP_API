# M060-S022-P007-ADR-SPEC-BASELINE - P007 ADR/spec baseline

## Mission

M060

## Goal

Record the P007 ChatGPT Pro decision in durable architecture artifacts before any HTTP access or
decoder implementation work begins.

## Acceptance

- `.agent/consultations/P007-response.md` records the user-provided ChatGPT Pro response.
- An ADR accepts HTTP single-resource as the first remote access architecture test.
- The ADR accepts `.npy` typed array as the first proof target.
- Specs separate access/fetch, source contract, decoder, resolver policy, cache policy,
  capabilities, diagnostics, and renderer adapter/materialization target.
- Specs explicitly forbid protocol-level executable payloads, import paths, callbacks, package
  installation instructions, dynamic plugins, raw URLs, credentials, headers, cookies, local paths,
  DNS results, cache keys, and resolver private config.
- Specs define first-proof descriptor fields, capability fields, validation/rejection rules, cache
  and redaction policy, fixture strategy, and stop conditions.
- Next implementation missions remain no-network/mock-first and design-gated before real HTTP I/O.

## Stop conditions

Stop if the work requires any HTTP fetch, URL parsing, credential handling, decoder execution,
network I/O, dynamic loading, Datoviz remote-data work, or production remote-source behavior.

## Source

P007 ChatGPT Pro response in `.agent/consultations/P007-response.md`.

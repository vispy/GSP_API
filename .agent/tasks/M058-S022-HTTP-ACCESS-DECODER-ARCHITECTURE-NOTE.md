# M058-S022-HTTP-ACCESS-DECODER-ARCHITECTURE-NOTE - HTTP access and decoder architecture note

## Mission

M058

## Goal

Record the S022 framing that HTTP is the first access mechanism to evaluate, but source contracts and
decoders must remain separately pluggable through trusted resolver/server configuration.

## Acceptance

- A durable document records that HTTP does not imply tile pyramid.
- The document separates access/fetch, source contract, decoder, resolver policy, and renderer
  adapter layers.
- The document records the safe pluggability model: server/admin configured fetchers and decoders,
  not executable protocol payloads.
- The document recommends an HTTP single-resource proof as the first consultation target.
- No implementation is added.

## Stop conditions

Do not add fetchers, decoders, HTTP clients, URL parsing, credential handling, dynamic loading, or
production remote-source behavior.

## Result

Completed. Added `docs/security/s022_http_access_decoder_architecture_note.md`.

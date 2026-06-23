# M058 - S022 HTTP access and decoder architecture note

## Stage

S022 - Remote source family selection and consultation

## Status

Completed by local-main-codex.

## Summary

Recorded the S022 starting position: HTTP is the first access mechanism to evaluate, but it must be
separated from source contracts, decoder selection, resolver policy, and renderer adapters. The note
recommends an HTTP single-resource proof as the first consultation target and keeps tile pyramids as
a later specialization.

## Deliverables

- `docs/security/s022_http_access_decoder_architecture_note.md`

## Stop Condition

No remote fetch, decoder, credential, URL parsing, dynamic loading, or production remote-source
implementation was added.

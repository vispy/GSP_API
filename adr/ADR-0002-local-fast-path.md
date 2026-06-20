# ADR-0002 - Local path must avoid mandatory serialization

Status: accepted initial decision

## Decision

Local desktop GSP execution must use a direct in-process path with no mandatory JSON/base64 serialization.

## Rationale

The primary local GPU use case must be fast. JSON/base64 are appropriate for fixtures, debugging, simple transport, and replay, not for ordinary local rendering.

## Consequences

The protocol model and transport encoding must remain separate.

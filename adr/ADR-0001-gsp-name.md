# ADR-0001 - GSP means Graphics Server Protocol

Status: accepted initial decision

## Decision

Use **Graphics Server Protocol** as the expansion of GSP.

## Rationale

The project is inspired by LSP-style client/server sessions, capability negotiation, requests, notifications, diagnostics, and extensible backends. The server may be local/in-process or remote.

## Consequences

The protocol must not be tied to one wire encoding. A local in-process server is a valid server.

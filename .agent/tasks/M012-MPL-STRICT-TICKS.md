# M012-MPL-STRICT-TICKS - Deterministic auto-linear tick resolver

## Mission

M012

## Goal

Implement a backend-independent deterministic resolver for `auto-linear-nice-v0`.

## Expected output

- Pure protocol/reference resolver code.
- Tests for small, large, negative, positive, crossing-zero, and degenerate domains.
- No dependency on Matplotlib locators.

## Acceptance

- Resolver output is stable across test runs.
- Invalid/non-finite limits fail explicitly.
- Degenerate limits are expanded deterministically.

## Stop conditions

Stop if the resolver needs backend-native locator output or an ADR-level change to `TickSpec`.


# M012-EXPLICIT-TICK-PASSTHROUGH - Preserve explicit ticks and labels

## Mission

M012

## Goal

Ensure explicit tick values and labels are preserved exactly at the protocol/reference layer.

## Expected output

- Resolver support for `TickSpecKind.EXPLICIT`.
- Tests for explicit values with labels and explicit values without labels.
- Validation that label count matches value count.

## Acceptance

- Explicit values are returned unchanged.
- Explicit labels are returned unchanged.
- Missing labels are generated deterministically from values.

## Stop conditions

Stop if explicit ticks require backend-specific provider behavior.


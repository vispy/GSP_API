# M014-GUIDE-QUERY-SUPPORT - Bounded reference guide query helper

## Mission

M014

## Goal

Add deterministic reference query behavior for semantic guide contributions.

## Acceptance

- Tick guide hits report guide id, role, axis dimension, tick value, and text value when available.
- Guide misses return `miss`.
- Providers without guide query support return `unsupported`.

## Stop conditions

Stop before adding general query scope precedence or backend-native text/glyph picking.


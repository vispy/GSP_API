# M208 - S050 Datoviz TextVisual strictness proof

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Ready.

## Summary

Use focused fixtures and review artifacts to decide which adapted Datoviz TextVisual rows can move
toward strict rendering without changing the public TextVisual contract.

## Stop Conditions

- Stop before changing TextVisual anchor, multiline, Unicode, or DATA coordinate public semantics
  without a consultation packet.
- Stop before claiming text query/readback support.
- Stop if Datoviz cannot report enough font/layout behavior to distinguish baseline/top/bottom and
  multiline anchor semantics.

# M081 - S024 TextVisual query/readback integration

## Stage

S024 - Text/Glyph Visuals v1

## Status

Draft.

## Summary

Add item-level text query payloads behind explicit `query.text` capability after rendering exists.

## Stop Condition

Stop if query cannot preserve public `visual_id` and `item_index`, or if implementation drifts into
glyph-level hit testing.

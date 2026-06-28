# M135 - S034 guide style fields

## Stage

S034 - Resolved Layout and Guide Geometry Foundation

## Status

Completed by local-main-codex.

## Summary

Implement the P016 guide style field slice by adding logical-pixel style records to semantic guide
objects and wiring the supported subset into the Matplotlib reference renderer.

## Deliverables

- `AxisGuideStyle` with logical-pixel fields for axis label font size, tick label font size, tick
  length, tick width, tick label padding, axis label padding, grid width, and guide margin.
- `PanelTextGuideStyle` with logical-pixel title font size and guide margin.
- `AxisGuide.style` and `PanelTextGuide.style` default records preserving existing constructors.
- Matplotlib conversion of supported style fields from logical pixels to points by figure DPI.
- Tests for validation and Matplotlib rendering behavior.

## Acceptance

- Existing guide constructors remain compatible.
- Negative/non-finite style values reject during protocol validation.
- Matplotlib applies style values through DPI-aware px-to-point conversion.

## Stop Condition

Stop before claiming full resolved style readback. This mission adds semantic style fields and
Matplotlib rendering support; richer resolved style readback belongs with a later layout snapshot
schema expansion.

## Result

Completed. Guide style fields are protocol-owned logical-pixel hints, and Matplotlib maps the
supported fields into native title, label, tick, and grid artist properties.

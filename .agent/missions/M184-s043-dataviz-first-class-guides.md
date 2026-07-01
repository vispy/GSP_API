# M184 - S043 Datoviz first-class guide objects

## Stage

S043 - Datoviz Panel Frame, Guide Strictness, And Retained View3D

## Status

Draft.

## Summary

Make Datoviz axes, titles, tick labels, axis labels, grids, legends, and colorbars semantic guide
objects with layout, query, and contribution identity.

## Deliverables

- `DvzGuide` descriptors for axes, titles, legends, colorbars, text guides, and grid/tick roles.
- Guide layout boxes and anchors in `DvzPanelFrameSnapshot`.
- Guide hit query returning snapshot id, guide id, role, hit part, box, tick index/data value, and
  label where applicable.
- All-rendered contribution enumeration for guide outputs.
- Python guide API exposure.
- Native tests for guide boxes, hit testing, contribution enumeration, dense ticks, reversed domains,
  multi-panel layout, colorbar/legend boxes, and snapshot id equality.

## Acceptance

- Guide render/query/readback/contribution paths can share one snapshot id.
- Title, tick label, axis label, legend, and colorbar boxes are inspectable.
- Grid clipping remains true plot clipping/scissor/equivalent clipping.

## Stop Conditions

- Stop if guides remain generated geometry with no durable guide identity.
- Stop if query/readback cannot return the same snapshot id used by render.
- Stop if all-rendered output omits guide contributions.

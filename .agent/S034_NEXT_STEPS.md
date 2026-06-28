# S034 Next Steps

## Recommendation

Close S034 with an honest Matplotlib-first layout foundation, then choose whether to start a
separate Datoviz proof stage or proceed to release with Datoviz guide layout remaining adapted.

## Current Position

Matplotlib now has the usable S034 foundation:

- resolved layout snapshot production;
- layout-aware guide and all-rendered query integration;
- render-result `layout_snapshot_id` reporting through VisPy2 and lower-level Matplotlib protocol
  rendering;
- S034 visual QA fixtures for title, axis label, tick label, grid clip, resized viewport, and
  device-scale metadata;
- conservative `layout_strict=false` until readback and promotion criteria are complete.

Datoviz remains deliberately conservative:

- no `ResolvedLayoutSnapshot` production or consumption;
- no guide query or all-rendered guide contribution support;
- grid clipping to resolved `plot_rect_px` is explicitly unsupported pending native API proof;
- panel title rendering remains adapted screen text, not layout-strict guide geometry.

## Recommended Sequence

1. **M146: Matplotlib resolved layout readback closure**

   Add a small readback/report helper around `ResolvedLayoutSnapshot` so render, query, QA report,
   and readback all expose the same `layout_snapshot_id`. Keep `layout_strict=false` unless the
   promotion criteria are explicitly satisfied.

2. **S034 closeout note**

   Record what S034 completed and what remains out of scope:

   - Matplotlib: snapshot production, render-result reporting, guide query, QA snapshot artifacts,
     resized viewport proof, and device-scale metadata.
   - Datoviz: adapted/unsupported for resolved layout strictness.
   - No backend promoted to full `layout_strict`.

3. **Choose the next stage**

   Option A: **Datoviz layout proof stage**

   - Audit actual Datoviz APIs for grid clipping, title layout, guide picking/query, and
     device-scale reporting.
   - Only promote capabilities when runtime/API evidence proves the semantics.

   Option B: **Release path**

   - Keep Datoviz guide layout classified as adapted/unsupported where appropriate.
   - Ship the current capability posture and defer native layout strictness.

## Not Recommended

Do not pursue `M130 Optional Datoviz adapted-row strict promotion proof` as a promotion step in its
current form. Recent S034 work makes the contract clearer: adapted rows should remain adapted unless
Datoviz proves guide geometry, query, and layout snapshot semantics.

Do not invent a `LegendGuide` inside S034. Legend layout should wait for an accepted protocol object
or a separate scoped design decision.

# M127 - Datoviz policy-only View2D compatibility

## Stage

S032 - Datoviz v0.4 compatibility refresh

## Status

Completed by local-main-codex.

## Summary

Update the GSP Datoviz v0.4 adapter after the sibling Datoviz checkout made `DvzPanelView2D`
policy-only. GSP must use `dvz_panel_set_domain()` as the data-domain carrier, keep
`dvz_panel_set_view2d()` for fitting/aspect policy, refresh stale capability/spec wording, and
regenerate review artifacts that demonstrate Matplotlib/Datoviz visual agreement.

## Deliverables

- Adapter and fake-facade tests updated for policy-only `DvzPanelView2D`.
- Stale `dvz_panel_data_to_visual_positions()` capability/docs references removed or downgraded.
- Datoviz backend spec refreshed for the current v0.4-dev contract.
- Visual QA review pack regenerated with Matplotlib and Datoviz artifacts, including an `all_cases`
  contact sheet.
- Validation notes recorded with unsupported/adapted Datoviz row counts and image-comparison
  observations.

## Result

Completed in S032. See `.agent/S032_CLOSEOUT.md`.

## Stop Condition

Stop if the local Datoviz facade cannot expose `dvz_panel_set_domain()`, `dvz_panel_set_view2d()`,
and panel axes through the current checkout, or if visual QA shows broad Datoviz regressions that
cannot be explained by accepted capability gates.

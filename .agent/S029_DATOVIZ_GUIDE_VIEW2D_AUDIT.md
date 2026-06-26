# S029 Datoviz Guide/View2D Unsupported Closure

Updated: 2026-06-26

## Scope

Mission M118 audited the Datoviz guide/View2D rows in the S029 review pack:

- `guide/view2d_auto_grid`
- `guide/view2d_reversed_explicit`

Both rows remain `unsupported` for Datoviz in S029.

## Decision

| Row | Decision | Blocker |
|---|---|---|
| `guide/view2d_auto_grid` | `unsupported` | Datoviz native axes can be configured with backend auto ticks, labels, and optional grid, but the review pack has no rendered Datoviz artifact proving GSP auto-tick/grid alignment with `View2D` data visuals; panel title placement and guide query remain unsupported. |
| `guide/view2d_reversed_explicit` | `unsupported` | Explicit GSP tick values/labels are not wired through the Datoviz axis guide review-pack path; strict reversed-domain axis/grid placement, panel title placement, and guide query remain unverified or unsupported. |

No row is promoted to `adapted` or `strict`. Rendering support remains `false`, and
`query_supported` remains `false`.

## Evidence

- The current review-pack Datoviz guide logs report `axis_guide_render_unsupported`.
- `src/gsp_datoviz/capabilities.py` declares the Datoviz axis provider as `adapted`, with backend
  native ticks only, no strict explicit GSP ticks, no guide query, no text query, no title support,
  and reversed `View2D` axes explicitly unverified.
- `src/gsp_datoviz/protocol_renderer.py` has a bounded `configure_view2d_axes()` proof for backend
  auto ticks, grid, and axis labels, but it rejects explicit GSP ticks and is not wired into the
  S029 guide review-pack path.
- `tests/test_datoviz_v04_protocol_renderer.py` covers the adapted native axis proof and the explicit
  tick rejection.
- `tests/test_visual_qa_harness.py` now asserts row-specific unsupported metadata for both guide
  rows.

## Deferred

Strict Datoviz guide rendering requires rendered evidence for axis tick positions, explicit tick
labels, grid placement, axis labels, panel title placement, reversed `View2D` domains, and guide
query/all-rendered query semantics. These remain future work.

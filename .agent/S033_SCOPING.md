# S033 Scoping - Datoviz Guide Strictness and Release Decision

Generated: 2026-06-27

## Decision

Proceed to release preparation as the default next branch. Keep the remaining Datoviz rows adapted
rather than trying to promote them to strict before release preparation.

Strict promotion remains possible, but it should be a separate optional proof mission because the
remaining adapted rows are documented semantic gaps, not rendering failures.

## Current Review State

Primary artifact:

`artifacts/visual_qa/s031/full-review-pack-legacy/contact_sheets/s028_all_cases.png`

Diagnostic linear-light artifact:

`artifacts/visual_qa/s031/full-review-pack-linear/contact_sheets/s028_all_cases.png`

Datoviz status counts from the regenerated S031 review packs:

| Status | Count |
|---|---:|
| strict | 23 |
| adapted | 6 |
| unsupported | 0 |

Combined matrix counts:

| Status | Count |
|---|---:|
| strict | 52 |
| adapted | 6 |
| unsupported | 0 |

## Adapted Datoviz Rows

| Case | Family | Reason | Blocking gap |
|---|---|---|---|
| `text/basic_ndc` | text | `datoviz_rendered_pending_promotion_audit` | Default BASELINE text-anchor semantics are not strictly verified. |
| `text/anchor_grid_ndc` | text | `datoviz_rendered_pending_promotion_audit` | Baseline, top, center, and bottom text-box anchors need focused fixtures. |
| `text/data_vs_ndc` | text | `datoviz_rendered_pending_promotion_audit` | DATA and NDC text placement is only proven under the identity `[-1,+1]` review-pack view. |
| `text/multiline_unicode_smoke` | text | `datoviz_rendered_pending_promotion_audit` | Unicode fallback and multiline BASELINE anchoring remain unverified. |
| `guide/view2d_auto_grid` | guide | `datoviz_axis_guide_adapted_review` | Backend-native auto ticks are used; panel title and guide/all-rendered query semantics are unsupported. |
| `guide/view2d_reversed_explicit` | guide | `datoviz_axis_guide_adapted_review` | Strict explicit tick identity is binding-dependent; panel title and guide/all-rendered query semantics are unsupported. |

## Mission Batch

| Mission | State | Action |
|---|---|---|
| M129 | ready | Run post-S032 release-preparation audit; verify docs, validation, artifacts, and release checklist remain coherent after S032. |
| M130 | draft | Optional strict promotion proof for adapted Datoviz rows, if the user wants to harden before release preparation. |
| M131 | blocked | Actual release operation. Requires explicit approval for target version, version update, tag creation, and publication target. |

## ChatGPT Pro

No ChatGPT Pro consultation is needed for the release-preparation branch because no new strictness,
architecture, or protocol claim is being made.

Create a consultation packet before M130 if strict promotion would require new public guide/text
semantics, undocumented Datoviz behavior, or a policy change to the capability taxonomy.

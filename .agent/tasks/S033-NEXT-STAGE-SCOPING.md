# S033 Next Stage Scoping

## Goal

Decide the next branch after S032:

- promote Datoviz guide rows from adapted to strict where evidence supports it;
- keep guide rows adapted and proceed to release preparation;
- or open a focused guide semantics implementation batch.

## Current Facts

- S032 is closed.
- Regenerated S031 legacy and linear review packs both report Datoviz `strict=23`,
  `adapted=6`, `unsupported=0`.
- Guide rows remain adapted because title layout and guide/all-rendered query semantics are not yet
  strict contract behavior.
- The current Datoviz v0.4-dev adapter uses panel domains as the data-domain carrier and treats
  `DvzPanelView2D` as policy-only.

## Primary Artifacts

- Legacy all-cases sheet:
  `artifacts/visual_qa/s031/full-review-pack-legacy/contact_sheets/s028_all_cases.png`
- Linear-light diagnostic all-cases sheet:
  `artifacts/visual_qa/s031/full-review-pack-linear/contact_sheets/s028_all_cases.png`
- Compatibility closeout: `.agent/S032_CLOSEOUT.md`

## Proposed Mission Batch

| Mission | State | Purpose |
|---|---|---|
| M128 | completed | Scope Datoviz guide strictness and decide release vs hardening. |
| M129 | completed | Ran a post-S032 release-preparation audit without tagging or publishing. |
| M130 | draft | Optional strict-promotion proof for adapted Datoviz text and guide rows. |
| M131 | blocked | Release operation, only after explicit user approval of version/tag/publish target. |

## Stop Conditions

- Stop before creating tags, version bumps, publication artifacts, or public strict-support claims.
- Stop and create a ChatGPT Pro packet if guide strictness requires new architecture, protocol
  semantics, or uncertain Datoviz API interpretation.

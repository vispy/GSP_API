# M128 - S033 guide strictness scoping and release decision plan

## Stage

S033 - Datoviz Guide Strictness and Release Decision

## Status

Completed by local-main-codex.

## Summary

Open S033 as a bounded planning mission after S032. The goal is to decide whether the next work
should promote Datoviz guide rows from adapted to strict, keep them adapted and proceed toward a
release, or create a small focused implementation batch for remaining guide semantics.

This mission must use the S032 policy-only Datoviz `DvzPanelView2D` outcome as current authority:
GSP data domains flow through `dvz_panel_set_domain()`, while `dvz_panel_set_view2d()` is a
fitting/aspect/padding policy call. Older handoff wording that treats `DvzPanelView2D.data_x/data_y`
as the primary GSP data-domain carrier is superseded unless fresh Datoviz API evidence reverses
that conclusion.

## Deliverables

- Audit the six adapted Datoviz rows from the regenerated S031 review packs.
- Identify which guide gaps are contract gaps, implementation gaps, or intentionally adapted
  backend behavior.
- Decide whether ChatGPT Pro consultation is needed before any public strictness claim.
- Draft the next mission batch, likely one of:
  - strict guide promotion proof;
  - release preparation with guide rows documented as adapted;
  - focused guide query/title implementation.
- Record stop conditions for tag/version/publish work.

## Acceptance

- Mission Control has an actionable S033 next-step table.
- The release-vs-hardening branch is explicit.
- The latest review artifact paths are recorded.
- No external worker is launched until a mission is approved.
- No tag, version bump, publish, or public Datoviz strict-guide support claim is made.

## Stop Condition

Stop if strict-guide promotion depends on ambiguous protocol semantics, undocumented Datoviz
behavior, or broad public API design. In that case create a self-contained ChatGPT Pro consultation
packet and pause dependent implementation.

## Result

Completed. See `.agent/S033_SCOPING.md`.

Decision: proceed by default to post-S032 release preparation with Datoviz adapted rows documented as
adapted. Do not attempt strict promotion as the default path.

Next missions:

- M129 ready: post-S032 release-preparation audit.
- M130 draft: optional strict promotion proof for adapted Datoviz rows.
- M131 blocked: explicit release operation, requiring user approval for version, tag, and publish
  target.

# M110-S028 - Datoviz guide capability report and closeout

## Mission

M110

## Goal

Document Datoviz guide/View2D capability status and close S028 after implementation and QA align.

## Status

Completed.

## Deliverables

- Datoviz guide/View2D capability or unsupported report.
- Structured diagnostics for unsupported guide query/readout behavior.
- Mission Control closeout records for S028.

## Acceptance

- Datoviz does not claim unverified strict guide/View2D support.
- S028 is closed only after spec, reference behavior, QA, and producer records align.

## Closeout

- Added the S028 Datoviz guide/View2D capability report to `spec/backends/datoviz.md`.
- Kept the Datoviz v0.4 axis provider at `adapted`, with explicit GSP tick values/labels,
  strict reversed-domain proof, guide query, and all-rendered guide query reported as unsupported
  or unverified by structured diagnostics.
- Tightened Datoviz query diagnostics so `guides` and `all-rendered` scopes report guide-query
  deferral explicitly instead of falling through to a generic data-scope message.
- Added focused tests protecting the adapted provider status and guide-query deferral.
- Closed S028 without opening the next stage prematurely.

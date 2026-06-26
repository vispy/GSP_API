# M106-S028 - Guide/View2D spec reconciliation

## Mission

M106

## Goal

Make the guide/tick/query specs explicit about consuming deterministic `View2D`, including reversed
axes, before implementation missions run.

## Status

Ready.

## Deliverables

- Add or update focused guide/View2D spec text.
- Record reversed-axis tick/grid/query/readout rules.
- Update S028 Mission Control status and unblock implementation missions if no conflict remains.

## Acceptance

- `tools/agentctl next` lists M106 as the recommended next mission.
- S028 specs are precise enough for worker-sized implementation tasks.
- Deferred layout, nonlinear, 3D, and controller semantics remain out of scope.

## Stop Conditions

- Stop on unresolved spec conflict.
- Stop if a new public architecture decision is required.

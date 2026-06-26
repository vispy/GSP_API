# M106-S028 - Guide/View2D spec reconciliation

## Mission

M106

## Goal

Make the guide/tick/query specs explicit about consuming deterministic `View2D`, including reversed
axes, before implementation missions run.

## Status

Completed.

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

## Result

- Specs now state that reversed `View2D` limits are valid guide domains.
- Auto ticks resolve over the finite numeric interval spanned by the limits, while rendering/query
  placement uses the original `View2D` orientation.
- Explicit ticks and labels pass through exactly.
- Guide rendering, guide query, all-rendered guide contributions, and readouts use the same
  `View2D` snapshot.
- M107 is unblocked for tick resolver and Matplotlib reference behavior implementation.

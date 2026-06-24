# M090-S026 - S026 color mapping and colorbars scoping consultation

## Mission

M090

## Goal

Open S026 around color mapping, colorbars, and scalar data semantics, and create the ChatGPT Pro
consultation packet required before public protocol semantics are frozen.

## Status

Completed.

## Deliverables

- Create `.agent/consultations/P011-color-mapping-colorbars-scalar-semantics.md`.
- Record the selected S026 scope and non-goals.
- Keep implementation blocked until the P011 response is available.

## Acceptance

- Mission output is committed or explicitly reported as blocked.
- Mission Control status is updated before closeout.
- Validation is proportional to the touched surface.

## Stop Conditions

- Stop if the work starts committing public colormap, normalization, scalar-color, colorbar, or
  color-scale semantics before P011 is answered and converted into ADR/spec updates.

## Completed

- Created `.agent/consultations/P011-color-mapping-colorbars-scalar-semantics.md`.
- Recorded S026 as color mapping/colorbars/scalar data semantics with implementation blocked pending
  P011.
- Added open question Q090 for the ChatGPT Pro consultation result.
- Validation: `tools/agentctl brief`; `tools/agentctl next`; `git diff --check`.

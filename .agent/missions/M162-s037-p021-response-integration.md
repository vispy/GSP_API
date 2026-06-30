# M162 - S037 P021 response integration

## Stage

S037 - Legacy 3D Reuse, Datoviz View3D Binding, and Public 3D Interaction

## Status

Completed by local-main-codex.

## Summary

Integrate the ChatGPT Pro answer into durable project authority before changing public 3D API,
Datoviz View3D binding behavior, or material/light/texture semantics.

## Deliverables

- Decision record summarizing accepted and rejected P021 recommendations.
- ADR/spec updates for the accepted S037 scope.
- Updated capability vocabulary and backend support wording.
- Revised mission acceptance criteria for M163-M167.

## Acceptance

- The P021 response is pasted or committed before work starts.
- Any public navigation contract is explicit about camera ownership, snapshot freshness, query
  semantics, and backend-retained state.
- Datoviz v0.4 behavior is specified as supported, adapted, or unsupported with diagnostics.
- Materials, lights, textures, perspective, and 3D picking stay deferred unless explicitly accepted.

## Stop Condition

Stop if the response is ambiguous about public API shape or would conflict with S036 authority.

## Result

Completed. Archived the pasted answer as `.agent/consultations/P021-response.md`, accepted S037 as
View3D navigation plus Datoviz View3D binding, deferred public materials/lights/textures, and added
ADR-0024, `.agent/decisions/S037_view3d_navigation_datoviz_contracts.md`,
`spec/view3d_navigation.md`, and backend capability wording updates.

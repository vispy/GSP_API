# M087-S025 - S025 Datoviz MeshVisual renderer or unsupported report

## Mission

M087

## Goal

Implement the Datoviz MeshVisual adapter when evidence supports it, otherwise produce structured unsupported diagnostics.

## Status

Draft.

## Deliverables

- Map accepted MeshVisual fields to retained Datoviz v0.4 APIs.
- Use explicit capability gates for unsupported normals/materials/3D features.
- Add smoke coverage for PNG or unsupported reports.

## Acceptance

- Mission output is committed or explicitly reported as blocked.
- Mission Control status is updated before closeout.
- Validation is proportional to the touched surface.

## Stop Conditions

- Stop if this requires legacy Datoviz paths or unverified material/ownership semantics.

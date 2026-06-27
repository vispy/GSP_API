# S031 next stage scoping - Release-Candidate Stabilization and Roadmap Reset

## Status

S031 opens after S030 closed the Datoviz Guide Axis Proof with all review-pack backend rows
classified as strict or adapted and no unsupported rows.

## Selected direction

Run a bounded release-candidate stabilization stage before adding more protocol surface:

- keep tagging and publication out of agent execution unless the user gives explicit separate
  approval;
- validate the current Matplotlib/reference package surface with the release checklist from
  `docs/release_checklist.md`;
- treat optional Datoviz v0.4 support as capability-gated until compatible release artifacts and
  support wording are proven;
- preserve S030's adapted guide classification unless Datoviz title/query semantics are proven or a
  future accepted contract excludes them;
- turn validation failures into small missions instead of broad refactors.

## Consultation policy

No ChatGPT Pro consultation is required for the initial release-candidate stabilization pass. This
stage applies existing release, backend, capability, and visual QA policy.

Create a ChatGPT Pro packet only if validation exposes a durable architecture question, such as a
public API compatibility break, release-versioning strategy change, Datoviz support contract change,
or a conflict between release-facing docs and accepted specs/ADRs.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M123 | completed | Opened S031, selected the stabilization direction, and created the mission batch. |
| M124 | completed | Release validation baseline passed; optional example confidence checks passed after narrow example-runner remediation. |
| M125 | completed | Audited and updated changelog, README, and backend-support wording after M124 results. |
| M126 | ready | Regenerate/inspect final review artifacts and close S031 with a release-candidate decision. |

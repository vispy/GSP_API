# S065 intent - human-guided product-quality audit

Date recorded: 2026-07-22

Status: superseded by the approved `.agent/S065_SCOPING.md` and
`.agent/S065_TECHNICAL_BASELINE.md`.

## Purpose

Before any release work, review the fresh GSP and VisPy2 repositories carefully for code defects,
example quality, documentation clarity, and feature coverage. Automated checks support this work but
do not replace owner judgment about usability, visuals, interaction, or priorities.

## Required human checkpoints

1. The owner selects the examples, user journeys, and feature areas that matter most.
2. Mission Control prepares small runnable review packs; the owner reviews visual and interactive
   behavior and records acceptance or concerns.
3. Findings are classified as bugs, documentation gaps, feature gaps, or intentional limitations.
4. The owner approves priorities before implementation batches begin.
5. Each bounded fix batch returns to the owner for review before the next batch starts.
6. Public API, protocol-semantic, architecture, or broad compatibility changes require separate
   approval and, where appropriate, a ChatGPT Pro consultation.

## Expected audit sequence

- Public API and implementation consistency audit.
- Example execution and human visual/interaction review across applicable backends.
- Specification-to-implementation and capability-claim coverage audit.
- New-user documentation, installation, tutorial, and API-reference review.
- Prioritized findings backlog followed by separately approved fix batches.

## Explicit exclusions

No version selection, tag, GitHub release, package publication, broad API redesign, or unapproved
external worker launch belongs to this intent. S065 missions should be created only when the owner
returns and approves a concrete audit plan.

## Resume prompt

Ask Mission Control to scope S065 from this intent note and begin with owner selection of the first
examples, workflows, and feature areas to review.

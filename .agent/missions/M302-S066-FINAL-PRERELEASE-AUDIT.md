# M302 - S066 final pre-release API, documentation, packaging, and gap audit

## Status

Approved by the owner and completed on 2026-07-30 under `local-main-codex`.

## Goal

Produce an evidence-backed go/no-go assessment for the fresh-root GSP and VisPy2 repositories
without requiring manual review.

## Scope

- public API and import surfaces;
- examples and documentation consistency;
- canonical specification and capability claims;
- package metadata, wheel/sdist builds, and isolated installation;
- source tests, strict typing, lint, documentation builds, and relevant native Datoviz smoke;
- remaining feature gaps classified as blocker, required before stable release, or honest deferral.

## Repositories and locks

- `gsp`, `vispy2`, and `datoviz`: read-only audit inputs;
- `mission-control`: writable only under `.agent` for the mission and audit report.

## Acceptance

- Exact commits and environments are recorded.
- Current failures are separated from environment mistakes and known baselines.
- Package artifacts are built and imported in an isolated temporary environment.
- Public claims are checked against specifications, capabilities, implementation, tests, and
  examples.
- The report gives a clear go/no-go verdict and a prioritized follow-up plan.

## Stop conditions

Stop before versions, tags, publication, pushes, PRs, public API redesign, Datoviz source changes,
or broad implementation fixes. Record discovered defects for separately traceable correction work.

# M245 - S058 Datoviz v0.4-dev rolling baseline

## Stage

S058 - Datoviz v0.4-dev Rolling Compatibility And RC3 Feedback

## Status

Completed.

## Summary

Run the maintained GSP Datoviz compatibility, visual, query, and public-session evidence against the
exact local sibling `v0.4-dev` revision and compare the results with the most recent committed
baselines. This mission gathers evidence and may harden the test harness, but it does not promote
capabilities merely because symbols exist.

## Deliverables

- Record Datoviz branch, commit, describe output, dirty state, package version, and imported module.
- Run the Datoviz v0.4 facade/API smoke and focused adapter tests.
- Replay the maintained visual compatibility matrix with isolated native cases.
- Run bounded public session examples and repeated blocking/polling lifecycle checks.
- Classify results as unchanged, improved, regressed, or newly available.
- Recommend the first bounded RC3-facing follow-up mission.

## Acceptance

- Every native run is tied to exact source and import provenance.
- Native crashes remain process-isolated and are reported rather than masked.
- Capability claims remain conservative and evidence-backed.
- Focused tests, strict typing for touched code, Ruff for touched code, and `git diff --check` pass.

## Path Locks

- `.agent/S058_*`
- `.agent/missions/M245-*`
- `.agent/status.json`
- `artifacts/visual_qa/s058/**`
- Datoviz replay/test tooling only if a concrete harness defect is found

## Stop Conditions

- Stop before editing the sibling Datoviz repository.
- Stop before changing public GSP protocol semantics or promoting a capability without runtime proof.
- Stop if a native crash is not contained by the existing subprocess boundary.
- Stop before tagging, publishing, pushing, or changing package dependencies.

## Approval

The project owner explicitly approved S058 and its M245 baseline in the active Mission Control
conversation on 2026-07-22.

## Result

Completed against Datoviz `v0.4-dev` commit `71c444cee65a6b4bb825ba4e0a4e448036707037`.
The S028 matrix finished with 53 strict, seven adapted, and zero crashed rows; comparison with the
latest pre-RC baseline found four improvements and zero regressions. Public lifecycle evidence
passed 10/10 and the five-mode internal lifecycle matrix passed 25/25. Full pytest, strict mypy,
Ruff, imports, JSON validation, and `git diff --check` passed. See
`.agent/S058_M245_ROLLING_BASELINE.md`.
